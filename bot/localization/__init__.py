"""
Модуль локализации для Telegram бота.

Концепция: Language Immersion (Ponoření do jazyka)
- Весь интерфейс теперь на чешском
- Чешский язык - основной
- ru, uk хранятся для обратной совместимости
"""

from .ru import TEXTS_RU
from .uk import TEXTS_UK
from .cs import TEXTS_CS

# Словарь всех локализаций (для обратной совместимости)
LOCALIZATIONS = {
    "ru": TEXTS_RU,
    "uk": TEXTS_UK,
    "cs": TEXTS_CS,
}


def get_text(key: str, language: str = "cs", **kwargs) -> str:
    """
    Получить локализованный текст.

    Language Immersion: по умолчанию возвращает чешский текст.

    Args:
        key: Ключ текста
        language: Язык (cs по умолчанию, ru/uk для обратной совместимости)
        **kwargs: Параметры для форматирования текста

    Returns:
        Локализованный текст
    """
    # Всегда используем чешский (Language Immersion)
    texts = TEXTS_CS

    # Получаем текст по ключу
    text = texts.get(key, f"[Missing: {key}]")

    # Форматируем с параметрами если есть
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass

    return text


def get_text_native(key: str, native_language: str = "ru", **kwargs) -> str:
    """
    Получить текст на родном языке пользователя.

    Используется только для объяснений ошибок.

    Args:
        key: Ключ текста
        native_language: Родной язык (ru/uk/pl/sk)
        **kwargs: Параметры для форматирования текста

    Returns:
        Локализованный текст на родном языке
    """
    texts = LOCALIZATIONS.get(native_language, TEXTS_RU)
    text = texts.get(key, f"[Missing: {key}]")

    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass

    return text


def get_days_word(count: int) -> str:
    """
    Получить правильное склонение слова "den" на чешском.

    Language Immersion: всегда чешский.

    Args:
        count: Количество дней

    Returns:
        Правильное склонение (den/dny/dní)
    """
    # Чешский: 1 den, 2-4 dny, 5+ dní
    if count % 10 == 1 and count % 100 != 11:
        return get_text("days_1")  # den
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return get_text("days_2")  # dny
    else:
        return get_text("days_5")  # dní


def get_native_language_name(native_language: str) -> str:
    """
    Получить название родного языка на чешском.

    Args:
        native_language: Код языка (ru/uk/pl/sk)

    Returns:
        Название языка на чешском
    """
    names = TEXTS_CS.get("native_lang_names", {})
    return names.get(native_language, native_language)


__all__ = [
    "get_text",
    "get_text_native",
    "get_days_word",
    "get_native_language_name",
    "LOCALIZATIONS",
    "TEXTS_CS",
]


