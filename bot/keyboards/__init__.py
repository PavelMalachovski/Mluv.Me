"""
Модуль клавиатур для Telegram бота.
"""

from .onboarding import get_language_keyboard, get_level_keyboard
from .settings import (
    get_corrections_keyboard,
    get_reset_confirm_keyboard,
    get_style_keyboard,
    get_voice_speed_keyboard,
)

__all__ = [
    "get_language_keyboard",
    "get_level_keyboard",
    "get_voice_speed_keyboard",
    "get_corrections_keyboard",
    "get_style_keyboard",
    "get_reset_confirm_keyboard",
]

