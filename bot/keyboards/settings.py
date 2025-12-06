"""
Клавиатуры для настроек.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.localization import get_text


def get_voice_speed_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """
    Клавиатура выбора скорости голоса.

    Args:
        language: Язык интерфейса

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("voice_speed_very_slow", language),
                    callback_data="voice_speed:very_slow",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("voice_speed_slow", language),
                    callback_data="voice_speed:slow",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("voice_speed_normal", language),
                    callback_data="voice_speed:normal",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("voice_speed_native", language),
                    callback_data="voice_speed:native",
                )
            ],
        ]
    )
    return keyboard


def get_corrections_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """
    Клавиатура выбора уровня исправлений.

    Args:
        language: Язык интерфейса

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("corrections_minimal", language),
                    callback_data="corrections:minimal",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("corrections_balanced", language),
                    callback_data="corrections:balanced",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("corrections_detailed", language),
                    callback_data="corrections:detailed",
                )
            ],
        ]
    )
    return keyboard


def get_style_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """
    Клавиатура выбора стиля общения.

    Args:
        language: Язык интерфейса

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("style_friendly", language),
                    callback_data="style:friendly",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("style_tutor", language),
                    callback_data="style:tutor",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("style_casual", language),
                    callback_data="style:casual",
                )
            ],
        ]
    )
    return keyboard


def get_reset_confirm_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения сброса разговора.

    Args:
        language: Язык интерфейса

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("reset_yes", language),
                    callback_data="reset:yes",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("reset_no", language),
                    callback_data="reset:no",
                )
            ],
        ]
    )
    return keyboard

