"""
Star Shop handler — spend earned stars on in-app items.

Commands:
  /shop — show star shop catalog with inline buttons
  Callback: shop:shield, shop:premium, shop:scenario:<id>, shop:back
"""

import structlog
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.localization import get_text
from bot.services.api_client import APIClient

router = Router()
logger = structlog.get_logger(__name__)

# Scenario display names (Czech immersion)
SCENARIO_NAMES: dict[str, str] = {
    "na_cizinecke_policii": "Na cizinecké policii",
    "pracovni_pohovor": "Pracovní pohovor",
    "telefonni_hovor": "Telefonní hovor",
}


def _build_catalog_text(catalog: dict) -> str:
    """Build the shop catalog message text."""
    stars = catalog["available_stars"]
    items = catalog["items"]
    shield = items["streak_shield"]
    premium = items["trial_premium"]
    scenarios = items["scenario_unlocks"]

    lines = [get_text("shop_header", stars=stars), ""]

    # Streak Shield
    shield_status = ""
    if shield["active"]:
        shield_status = " ✅"
    lines.append(
        f"🛡 <b>{get_text('shop_streak_shield')}</b> — {shield['cost']}⭐{shield_status}"
    )
    lines.append(f"   {get_text('shop_streak_shield_desc')}")
    lines.append("")

    # Trial Premium
    premium_status = ""
    if premium["already_pro"]:
        premium_status = " ✅"
    lines.append(
        f"💎 <b>{get_text('shop_trial_premium')}</b> — {premium['cost']}⭐{premium_status}"
    )
    lines.append(f"   {get_text('shop_trial_premium_desc')}")
    lines.append("")

    # Scenarios
    if scenarios:
        lines.append(f"🎭 <b>{get_text('shop_scenarios_header')}</b>")
        for sc in scenarios:
            name = SCENARIO_NAMES.get(sc["scenario_id"], sc["scenario_id"])
            status = " ✅" if sc["unlocked"] else ""
            lines.append(f"   • {name} — {sc['cost']}⭐{status}")
        lines.append("")

    return "\n".join(lines)


def _build_catalog_keyboard(catalog: dict) -> InlineKeyboardMarkup:
    """Build the shop catalog inline keyboard."""
    items = catalog["items"]
    shield = items["streak_shield"]
    premium = items["trial_premium"]
    scenarios = items["scenario_unlocks"]

    buttons: list[list[InlineKeyboardButton]] = []

    # Streak Shield button
    if not shield["active"]:
        buttons.append([
            InlineKeyboardButton(
                text=f"🛡 {get_text('shop_streak_shield')} — {shield['cost']}⭐",
                callback_data="shop:shield",
            )
        ])

    # Trial Premium button
    if not premium["already_pro"]:
        buttons.append([
            InlineKeyboardButton(
                text=f"💎 {get_text('shop_trial_premium')} — {premium['cost']}⭐",
                callback_data="shop:premium",
            )
        ])

    # Scenario buttons (only show unlockable ones)
    for sc in scenarios:
        if not sc["unlocked"]:
            name = SCENARIO_NAMES.get(sc["scenario_id"], sc["scenario_id"])
            buttons.append([
                InlineKeyboardButton(
                    text=f"🎭 {name} — {sc['cost']}⭐",
                    callback_data=f"shop:scenario:{sc['scenario_id']}",
                )
            ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ──────────── /shop command ────────────


@router.message(Command("shop"))
async def command_shop(message: Message, api_client: APIClient) -> None:
    """Show the star shop catalog."""
    telegram_id = message.from_user.id

    catalog = await api_client.get_star_shop(telegram_id)
    if not catalog:
        await message.answer(get_text("error_backend"))
        return

    text = _build_catalog_text(catalog)
    keyboard = _build_catalog_keyboard(catalog)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


# ──────────── Buy Streak Shield ────────────


@router.callback_query(F.data == "shop:shield")
async def handle_buy_shield(callback: CallbackQuery, api_client: APIClient) -> None:
    """Buy a streak shield."""
    telegram_id = callback.from_user.id
    await callback.answer()

    result = await api_client.buy_streak_shield(telegram_id)
    if not result:
        await callback.message.answer(get_text("error_backend"))
        return

    if result.get("success"):
        text = get_text(
            "shop_purchase_success",
            item=get_text("shop_streak_shield"),
            cost=result["cost"],
            remaining=result["remaining_stars"],
        )
    elif result.get("error") == "already_active":
        text = get_text("shop_shield_already_active")
    elif result.get("error") == "insufficient_stars":
        text = get_text(
            "shop_insufficient_stars",
            cost=result.get("cost", 100),
            available=result.get("available", 0),
        )
    else:
        text = get_text("error_backend")

    await callback.message.answer(text, parse_mode="HTML")

    # Refresh the catalog
    await _refresh_catalog(callback, api_client)


# ──────────── Buy Trial Premium ────────────


@router.callback_query(F.data == "shop:premium")
async def handle_buy_premium(callback: CallbackQuery, api_client: APIClient) -> None:
    """Buy 1-day Pro trial."""
    telegram_id = callback.from_user.id
    await callback.answer()

    result = await api_client.buy_trial_premium(telegram_id)
    if not result:
        await callback.message.answer(get_text("error_backend"))
        return

    if result.get("success"):
        text = get_text(
            "shop_purchase_success",
            item=get_text("shop_trial_premium"),
            cost=result["cost"],
            remaining=result["remaining_stars"],
        )
    elif result.get("error") == "already_pro":
        text = get_text("shop_already_pro")
    elif result.get("error") == "insufficient_stars":
        text = get_text(
            "shop_insufficient_stars",
            cost=result.get("cost", 500),
            available=result.get("available", 0),
        )
    else:
        text = get_text("error_backend")

    await callback.message.answer(text, parse_mode="HTML")
    await _refresh_catalog(callback, api_client)


# ──────────── Unlock Scenario ────────────


@router.callback_query(F.data.startswith("shop:scenario:"))
async def handle_unlock_scenario(
    callback: CallbackQuery, api_client: APIClient
) -> None:
    """Unlock a premium scenario with stars."""
    telegram_id = callback.from_user.id
    scenario_id = callback.data.split(":", 2)[2]
    await callback.answer()

    result = await api_client.unlock_scenario(telegram_id, scenario_id)
    if not result:
        await callback.message.answer(get_text("error_backend"))
        return

    name = SCENARIO_NAMES.get(scenario_id, scenario_id)

    if result.get("success"):
        text = get_text(
            "shop_scenario_unlocked",
            scenario=name,
            cost=result.get("cost", 0),
            remaining=result.get("remaining_stars", 0),
        )
    elif result.get("error") == "insufficient_stars":
        text = get_text(
            "shop_insufficient_stars",
            cost=result.get("cost", 0),
            available=result.get("available", 0),
        )
    else:
        text = get_text("error_backend")

    await callback.message.answer(text, parse_mode="HTML")
    await _refresh_catalog(callback, api_client)


# ──────────── Back to catalog ────────────


@router.callback_query(F.data == "shop:back")
async def handle_shop_back(callback: CallbackQuery, api_client: APIClient) -> None:
    """Return to the shop catalog."""
    await callback.answer()
    await _refresh_catalog(callback, api_client)


# ──────────── Helper ────────────


async def _refresh_catalog(
    callback: CallbackQuery, api_client: APIClient
) -> None:
    """Refresh the shop catalog message after a purchase."""
    telegram_id = callback.from_user.id
    catalog = await api_client.get_star_shop(telegram_id)
    if not catalog:
        return

    text = _build_catalog_text(catalog)
    keyboard = _build_catalog_keyboard(catalog)

    try:
        await callback.message.edit_text(
            text, reply_markup=keyboard, parse_mode="HTML"
        )
    except Exception:
        # Message hasn't changed or can't be edited — ignore
        pass
