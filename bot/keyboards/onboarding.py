"""
Клавиатуры для онбординга.

Language Immersion: UI на чешском, выбираем только родной язык.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.localization import get_text


def get_native_language_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора родного языка (для объяснений ошибок).

    Language Immersion: UI остается на чешском.

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("native_russian"),  # 🇷🇺 Ruština
                    callback_data="native:ru",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("native_ukrainian"),  # 🇺🇦 Ukrajinština
                    callback_data="native:uk",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("native_polish"),  # 🇵🇱 Polština
                    callback_data="native:pl",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("native_slovak"),  # 🇸🇰 Slovenština
                    callback_data="native:sk",
                )
            ],
        ]
    )
    return keyboard


def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Legacy: клавиатура выбора языка (для обратной совместимости).

    Returns:
        Inline клавиатура
    """
    return get_native_language_keyboard()


def get_level_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора уровня чешского.

    Language Immersion: Все тексты на чешском.

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("level_beginner"),  # 🌱 Začátečník
                    callback_data="level:beginner",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("level_intermediate"),  # 📚 Středně pokročilý
                    callback_data="level:intermediate",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("level_advanced"),  # 🎓 Pokročilý
                    callback_data="level:advanced",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("level_native"),  # 🏆 Rodilý mluvčí
                    callback_data="level:native",
                )
            ],
        ]
    )
    return keyboard


