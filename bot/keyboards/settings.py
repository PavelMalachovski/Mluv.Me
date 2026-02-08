"""
Клавиатуры для настроек.

Language Immersion: Все тексты на чешском.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.localization import get_text


def get_voice_speed_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора скорости голоса.

    Language Immersion: Все на чешском.

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("voice_speed_very_slow"),
                    callback_data="voice_speed:very_slow",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("voice_speed_slow"),
                    callback_data="voice_speed:slow",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("voice_speed_normal"),
                    callback_data="voice_speed:normal",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("voice_speed_native"),
                    callback_data="voice_speed:native",
                )
            ],
        ]
    )
    return keyboard


def get_corrections_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора уровня исправлений.

    Language Immersion: Все на чешском.

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("corrections_minimal"),
                    callback_data="corrections:minimal",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("corrections_balanced"),
                    callback_data="corrections:balanced",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("corrections_detailed"),
                    callback_data="corrections:detailed",
                )
            ],
        ]
    )
    return keyboard


def get_style_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора стиля общения.

    Language Immersion: Все на чешском.

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("style_friendly"),
                    callback_data="style:friendly",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("style_tutor"),
                    callback_data="style:tutor",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("style_casual"),
                    callback_data="style:casual",
                )
            ],
        ]
    )
    return keyboard


def get_reset_confirm_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения сброса разговора.

    Language Immersion: Все на чешском.

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("reset_yes"),
                    callback_data="reset:yes",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("reset_full"),
                    callback_data="reset:full",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("reset_no"),
                    callback_data="reset:no",
                )
            ],
        ]
    )
    return keyboard


def get_reset_full_confirm_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения ПОЛНОГО сброса.

    Language Immersion: Все на чешском.

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("reset_full_yes"),
                    callback_data="reset:full_yes",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("reset_no"),
                    callback_data="reset:no",
                )
            ],
        ]
    )
    return keyboard


def get_clear_history_confirm_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения удаления истории переписки.

    Language Immersion: Все на чешском.

    Returns:
        Inline клавиатура
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("clear_history_yes"),
                    callback_data="clear_history:yes",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("clear_history_no"),
                    callback_data="clear_history:no",
                )
            ],
        ]
    )
    return keyboard
