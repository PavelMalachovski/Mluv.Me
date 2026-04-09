"""
Telegram Stars & Tribute (card) payment handlers.

Stars flow (XTR):
  1. User taps Stars product → bot sends invoice with currency=XTR
  2. Telegram processes → pre_checkout → successful_payment

Tribute flow (CZK via card):
  1. User taps Card product → bot sends invoice with provider_token + currency=CZK
  2. Tribute processes card → pre_checkout → successful_payment
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

from bot.config import config
from bot.services.api_client import APIClient

logger = structlog.get_logger(__name__)
router = Router()

# ──────────── Products ────────────

PRODUCTS = {
    "pro_7d": {
        "label": "⭐ Pro na 7 dní",
        "description": "7 dní neomezeného přístupu ke všem funkcím Mluv.Me",
        "stars": 150,
        "czk": 79,
        "days": 7,
    },
    "pro_30d": {
        "label": "💎 Pro na 30 dní",
        "description": "30 dní neomezeného přístupu ke všem funkcím Mluv.Me",
        "stars": 500,
        "czk": 249,
        "days": 30,
    },
}


def _tribute_available() -> bool:
    """Check if Tribute provider token is configured."""
    return bool(config.tribute_api_key)


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard with available subscription products."""
    buttons = []

    # Card payments via Tribute (if configured)
    if _tribute_available():
        for product_id, product in PRODUCTS.items():
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"💳 {product['label']} — {product['czk']} Kč",
                        callback_data=f"buy_card:{product_id}",
                    )
                ]
            )

    # Stars payments (always available)
    for product_id, product in PRODUCTS.items():
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{product['label']} — {product['stars']}⭐",
                    callback_data=f"buy:{product_id}",
                )
            ]
        )

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
        payload=product_id,  # will come back in successful_payment
        currency="XTR",  # Telegram Stars
        prices=[
            LabeledPrice(label=product["label"], amount=product["stars"]),
        ],
    )

    logger.info(
        "stars_invoice_sent",
        user_id=callback.from_user.id,
        product=product_id,
        stars=product["stars"],
    )


# ──────────── Buy via Tribute (card payment) ────────────


@router.callback_query(F.data.startswith("buy_card:"))
async def handle_buy_card(callback: CallbackQuery) -> None:
    """
    User tapped a card product button → send invoice via Tribute provider.
    """
    product_id = callback.data.split(":", 1)[1]
    product = PRODUCTS.get(product_id)

    if not product:
        await callback.answer("Produkt nenalezen", show_alert=True)
        return

    if not _tribute_available():
        await callback.answer("Platba kartou není dostupná", show_alert=True)
        return

    await callback.answer()

    # Amount in smallest unit: CZK → haléře (× 100)
    amount_cents = product["czk"] * 100

    await callback.message.answer_invoice(
        title=product["label"],
        description=product["description"],
        payload=f"card:{product_id}",
        provider_token=config.tribute_api_key,
        currency="CZK",
        prices=[
            LabeledPrice(label=product["label"], amount=amount_cents),
        ],
    )

    logger.info(
        "card_invoice_sent",
        user_id=callback.from_user.id,
        product=product_id,
        czk=product["czk"],
    )


# ──────────── Pre-checkout (Telegram asks: "confirm?") ────────────


@router.pre_checkout_query()
async def handle_pre_checkout(pre_checkout: PreCheckoutQuery) -> None:
    """
    Telegram asks us to confirm the payment before processing.
    Works for both Stars (XTR) and Tribute (card) payments.
    """
    raw_payload = pre_checkout.invoice_payload
    # Card payments use "card:pro_7d" format, Stars use "pro_7d"
    product_id = raw_payload.split(":", 1)[1] if raw_payload.startswith("card:") else raw_payload
    product = PRODUCTS.get(product_id)

    if not product:
        await pre_checkout.answer(ok=False, error_message="Neznámý produkt")
        return

    await pre_checkout.answer(ok=True)
    logger.info(
        "pre_checkout_confirmed",
        user_id=pre_checkout.from_user.id,
        product=product_id,
        currency=pre_checkout.currency,
    )


# ──────────── Successful payment ────────────


@router.message(F.successful_payment)
async def handle_successful_payment(message: Message, api_client: APIClient) -> None:
    """
    Payment completed! Activate/extend Pro subscription.
    Works for both Stars (XTR) and Tribute (card) payments.
    """
    payment = message.successful_payment
    raw_payload = payment.invoice_payload
    telegram_id = message.from_user.id
    charge_id = payment.telegram_payment_charge_id

    # Determine provider and product_id from payload
    is_card = raw_payload.startswith("card:")
    product_id = raw_payload.split(":", 1)[1] if is_card else raw_payload
    product = PRODUCTS.get(product_id)
    provider = "tribute" if is_card else "telegram_stars"

    logger.info(
        "payment_successful",
        user_id=telegram_id,
        product=product_id,
        provider=provider,
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
            provider=provider,
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
    card_note = "\n💳 Platba kartou • ⭐ Telegram Stars\n" if _tribute_available() else ""
    await message.answer(
        "🌟 <b>Mluv.Me Pro</b>\n\n"
        "Neomezené textové i hlasové zprávy\n"
        "Všechny scénáře\n"
        "Oba konverzační partneři (Honzík & paní Nováková)\n"
        "Podrobné opravy a gramatika\n"
        "Spaced repetition pro slovíčka\n\n"
        f"{card_note}"
        "Vyber si plán:",
        parse_mode="HTML",
        reply_markup=get_subscription_keyboard(),
    )
