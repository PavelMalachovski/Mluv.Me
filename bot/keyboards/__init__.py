"""
Модуль клавиатур для Telegram бота.

Language Immersion: UI на чешском, выбираем только родной язык.
"""

from .onboarding import get_language_keyboard, get_level_keyboard, get_native_language_keyboard
from .settings import (
    get_clear_history_confirm_keyboard,
    get_corrections_keyboard,
    get_reset_confirm_keyboard,
    get_reset_full_confirm_keyboard,
    get_style_keyboard,
    get_voice_speed_keyboard,
)

__all__ = [
    "get_language_keyboard",  # Legacy alias
    "get_native_language_keyboard",
    "get_level_keyboard",
    "get_voice_speed_keyboard",
    "get_corrections_keyboard",
    "get_style_keyboard",
    "get_reset_confirm_keyboard",
    "get_reset_full_confirm_keyboard",
    "get_clear_history_confirm_keyboard",
]


