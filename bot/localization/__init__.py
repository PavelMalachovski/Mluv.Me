"""
Модуль локализации для Telegram бота.

Поддерживаемые языки:
- ru: Русский
- uk: Українська
- cs: Čeština (Неделя 3)
"""

from typing import Optional

from .ru import TEXTS_RU
from .uk import TEXTS_UK
from .cs import TEXTS_CS

# Словарь всех локализаций
LOCALIZATIONS = {
    "ru": TEXTS_RU,
    "uk": TEXTS_UK,
    "cs": TEXTS_CS,
}


def get_text(key: str, language: str = "ru", **kwargs) -> str:
    """
    Получить локализованный текст.

    Args:
        key: Ключ текста
        language: Язык (ru или uk)
        **kwargs: Параметры для форматирования текста

    Returns:
        Локализованный текст
    """
    # Получаем тексты для языка (по умолчанию русский)
    texts = LOCALIZATIONS.get(language, TEXTS_RU)

    # Получаем текст по ключу
    text = texts.get(key, f"[Missing: {key}]")

    # Форматируем с параметрами если есть
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass

    return text


def get_days_word(count: int, language: str = "ru") -> str:
    """
    Получить правильное склонение слова "день/дні/den".

    Args:
        count: Количество дней
        language: Язык (ru, uk, cs)

    Returns:
        Правильное склонение
    """
    # Чешский: 1 den, 2-4 dny, 5+ dní
    if language == "cs":
        if count % 10 == 1 and count % 100 != 11:
            return get_text("days_1", language)  # den
        elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
            return get_text("days_2", language)  # dny
        else:
            return get_text("days_5", language)  # dní
    elif language == "uk":
        if count % 10 == 1 and count % 100 != 11:
            return get_text("days_1", language)
        elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
            return get_text("days_2", language)
        else:
            return get_text("days_5", language)
    else:  # ru
        if count % 10 == 1 and count % 100 != 11:
            return get_text("days_1", language)
        elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
            return get_text("days_2", language)
        else:
            return get_text("days_5", language)


__all__ = ["get_text", "get_days_word", "LOCALIZATIONS"]


