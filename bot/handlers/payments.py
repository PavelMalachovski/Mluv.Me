"""
Telegram Stars payment handlers.

Full flow:
  1. User hits daily limit → inline keyboard with Star products
  2. User taps product → bot sends invoice (sendInvoice)
  3. Telegram sends pre_checkout_query → we confirm
  4. Telegram processes payment → successful_payment callback
  5. We record payment + activate/extend Pro subscription
"""

import structlog
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from bot.services.api_client import APIClient

logger = structlog.get_logger(__name__)
router = Router()

# ──────────── Products ────────────

PRODUCTS = {
    "pro_7d": {
        "label": "⭐ Pro na 7 dní",
        "description": "7 dní neomezeného přístupu ke všem funkcím Mluv.Me",
        "stars": 150,
        "days": 7,
    },
    "pro_30d": {
        "label": "💎 Pro na 30 dní",
        "description": "30 dní neomezeného přístupu ke všem funkcím Mluv.Me",
        "stars": 500,
        "days": 30,
    },
}


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard with available subscription products."""
    buttons = []
    for product_id, product in PRODUCTS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{product['label']} — {product['stars']}⭐",
                callback_data=f"buy:{product_id}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_limit_reached_text(msg_type: str = "text") -> str:
    """Text shown when daily limit is reached."""
    if msg_type == "voice":
        return (
            "⚠️ <b>Denní limit hlasových zpráv vyčerpán</b>\n\n"
            "S plánem Free máš 4 hlasové zprávy denně.\n\n"
            "🌟 Odemkni <b>Pro</b> pro neomezený přístup:"
        )
    return (
        "⚠️ <b>Denní limit textových zpráv vyčerpán</b>\n\n"
        "S plánem Free máš 5 textových zpráv denně.\n\n"
        "🌟 Odemkni <b>Pro</b> pro neomezený přístup:"
    )


# ──────────── Buy callback (user taps product) ────────────

@router.callback_query(F.data.startswith("buy:"))
async def handle_buy(callback: CallbackQuery) -> None:
    """
    User tapped a product button → send invoice via Telegram Stars.
    """
    product_id = callback.data.split(":", 1)[1]
    product = PRODUCTS.get(product_id)

    if not product:
        await callback.answer("Produkt nenalezen", show_alert=True)
        return

    await callback.answer()

    # Send invoice using Telegram Stars (XTR currency)
    await callback.message.answer_invoice(
        title=product["label"],
        description=product["description"],
        payload=product_id,                    # will come back in successful_payment
        currency="XTR",                        # Telegram Stars
        prices=[
            LabeledPrice(label=product["label"], amount=product["stars"]),
        ],
    )

    logger.info(
        "invoice_sent",
        user_id=callback.from_user.id,
        product=product_id,
        stars=product["stars"],
    )


# ──────────── Pre-checkout (Telegram asks: "confirm?") ────────────

@router.pre_checkout_query()
async def handle_pre_checkout(pre_checkout: PreCheckoutQuery) -> None:
    """
    Telegram asks us to confirm the payment before processing.
    We always confirm (product was already validated when sending invoice).
    """
    product_id = pre_checkout.invoice_payload
    product = PRODUCTS.get(product_id)

    if not product:
        await pre_checkout.answer(ok=False, error_message="Neznámý produkt")
        return

    await pre_checkout.answer(ok=True)
    logger.info(
        "pre_checkout_confirmed",
        user_id=pre_checkout.from_user.id,
        product=product_id,
    )


# ──────────── Successful payment ────────────

@router.message(F.successful_payment)
async def handle_successful_payment(
    message: Message, api_client: APIClient
) -> None:
    """
    Payment completed! Activate/extend Pro subscription.
    """
    payment = message.successful_payment
    product_id = payment.invoice_payload
    product = PRODUCTS.get(product_id)
    telegram_id = message.from_user.id
    charge_id = payment.telegram_payment_charge_id

    logger.info(
        "payment_successful",
        user_id=telegram_id,
        product=product_id,
        charge_id=charge_id,
        total_amount=payment.total_amount,
        currency=payment.currency,
    )

    # Call backend to record payment + activate subscription
    try:
        result = await api_client.activate_subscription(
            telegram_id=telegram_id,
            product_id=product_id,
            charge_id=charge_id,
        )

        if result and result.get("success"):
            _expires = result.get("expires_at", "")
            days = product["days"] if product else "?"
            await message.answer(
                f"🎉 <b>Platba úspěšná!</b>\n\n"
                f"Máš <b>Pro přístup</b> na {days} dní.\n"
                f"Neomezené textové i hlasové zprávy, "
                f"všechny scénáře a další funkce!\n\n"
                f"Tak pojďme na to! 🇨🇿",
                parse_mode="HTML",
            )
        else:
            # Payment processed by Telegram, but backend failed
            logger.error(
                "subscription_activation_failed",
                user_id=telegram_id,
                product=product_id,
                result=result,
            )
            await message.answer(
                "✅ Platba přijata, ale nastala chyba při aktivaci.\n"
                "Kontaktuj nás — opravíme to co nejdříve!",
            )
    except Exception as e:
        logger.error(
            "payment_processing_error",
            user_id=telegram_id,
            error=str(e),
        )
        await message.answer(
            "✅ Platba přijata, ale nastala chyba.\n"
            "Tvé peníze jsou v bezpečí — kontaktuj nás!",
        )


# ──────────── /subscribe command ────────────

@router.message(F.text == "/subscribe")
async def handle_subscribe_command(message: Message) -> None:
    """Show subscription options."""
    await message.answer(
        "🌟 <b>Mluv.Me Pro</b>\n\n"
        "Neomezené textové i hlasové zprávy\n"
        "Všechny scénáře a mini-hry\n"
        "Oba konverzační partneři (Honzík & paní Nováková)\n"
        "Podrobné opravy a gramatika\n"
        "Spaced repetition pro slovíčka\n\n"
        "Vyber si plán:",
        parse_mode="HTML",
        reply_markup=get_subscription_keyboard(),
    )
