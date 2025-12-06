"""
Клавиатуры для онбординга.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.localization import get_text


def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора языка интерфейса.

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("lang_russian", "ru"),
                    callback_data="lang:ru",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("lang_ukrainian", "uk"),
                    callback_data="lang:uk",
                )
            ],
        ]
    )
    return keyboard


def get_level_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """
    Клавиатура выбора уровня чешского.

    Args:
        language: Язык интерфейса

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("level_beginner", language),
                    callback_data="level:beginner",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("level_intermediate", language),
                    callback_data="level:intermediate",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("level_advanced", language),
                    callback_data="level:advanced",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("level_native", language),
                    callback_data="level:native",
                )
            ],
        ]
    )
    return keyboard

