"""
Pydantic схемы для перевода слов.
"""

from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class WordTranslationRequest(BaseModel):
    """
    Схема для запроса перевода слова.

    Attributes:
        word: Слово для перевода (чешское)
        target_language: Язык перевода (ru или uk)
    """

    model_config = ConfigDict(
        validate_assignment=False,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    word: str = Field(description="Слово для перевода (чешское)")
    target_language: Literal["ru", "uk"] = Field(
        default="ru", description="Язык перевода"
    )


class WordTranslationResponse(BaseModel):
    """
    Схема для ответа с переводом слова.

    Attributes:
        word: Исходное слово
        translation: Перевод слова
        target_language: Язык перевода
        phonetics: Фонетическая транскрипция (если доступна)
    """

    model_config = ConfigDict(
        validate_assignment=False,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    word: str = Field(description="Исходное слово")
    translation: str = Field(description="Перевод слова")
    target_language: Literal["ru", "uk"] = Field(description="Язык перевода")
    phonetics: str | None = Field(
        default=None, description="Фонетическая транскрипция"
    )


class SaveWordRequest(BaseModel):
    """
    Схема для запроса сохранения слова.

    Attributes:
        user_id: ID пользователя
        word_czech: Чешское слово
        translation: Перевод слова
        context_sentence: Контекстное предложение (опционально)
        phonetics: Фонетическая транскрипция (опционально)
    """

    model_config = ConfigDict(
        validate_assignment=False,
        str_strip_whitespace=True,
    )

    user_id: int = Field(description="ID пользователя")
    word_czech: str = Field(description="Чешское слово")
    translation: str = Field(description="Перевод слова")
    context_sentence: str | None = Field(
        default=None, description="Контекстное предложение"
    )
    phonetics: str | None = Field(
        default=None, description="Фонетическая транскрипция"
    )
