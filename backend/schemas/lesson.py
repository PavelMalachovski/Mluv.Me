"""
Pydantic схемы для lesson endpoints (обработка голосовых сообщений).
"""

from typing import Literal

from pydantic import BaseModel, Field


class MistakeSchema(BaseModel):
    """
    Схема для одной ошибки в речи.

    Attributes:
        original: Оригинальный текст (с ошибкой)
        corrected: Исправленный текст
        explanation: Объяснение ошибки на языке пользователя
    """

    original: str = Field(description="Оригинальный текст с ошибкой")
    corrected: str = Field(description="Исправленный текст")
    explanation: str = Field(description="Объяснение ошибки")


class CorrectionSchema(BaseModel):
    """
    Схема для исправлений от Хонзика.

    Attributes:
        corrected_text: Полный исправленный текст
        mistakes: Список ошибок с объяснениями
        correctness_score: Оценка правильности (0-100)
        suggestion: Совет от Хонзика
    """

    corrected_text: str = Field(description="Исправленный текст")
    mistakes: list[MistakeSchema] = Field(description="Список ошибок")
    correctness_score: int = Field(
        ge=0, le=100, description="Оценка правильности (0-100)"
    )
    suggestion: str = Field(description="Совет от Хонзика")


class DailyChallengeSchema(BaseModel):
    """
    Схема для Daily Challenge.

    Attributes:
        challenge_completed: Выполнен ли челлендж
        messages_today: Количество сообщений сегодня
        messages_needed: Нужно сообщений для выполнения
        bonus_stars: Бонусные звезды (если челлендж только что выполнен)
    """

    challenge_completed: bool = Field(description="Выполнен ли челлендж")
    messages_today: int = Field(description="Сообщений сегодня")
    messages_needed: int = Field(description="Нужно для выполнения")
    bonus_stars: int = Field(description="Бонусные звезды")


class LessonProcessRequest(BaseModel):
    """
    Запрос на обработку голосового сообщения.

    Attributes:
        user_id: ID пользователя (telegram_id)

    Note:
        Аудио файл передается через multipart/form-data отдельно
    """

    user_id: int = Field(description="Telegram ID пользователя")


class LessonProcessResponse(BaseModel):
    """
    Ответ после обработки голосового сообщения.

    Attributes:
        transcript: Транскрипция голосового сообщения
        honzik_response_text: Текстовый ответ Хонзика
        honzik_response_audio: Base64 encoded аудио ответ (или URL)
        corrections: Исправления и оценка
        formatted_mistakes: Отформатированные ошибки для отображения
        formatted_suggestion: Отформатированная подсказка
        stars_earned: Звезды заработанные за это сообщение
        total_stars: Всего звезд у пользователя
        current_streak: Текущий streak
        max_streak: Максимальный streak
        daily_challenge: Информация о daily challenge
        words_total: Всего слов в сообщении
        words_correct: Правильных слов
    """

    transcript: str = Field(description="Транскрипция речи")
    honzik_response_text: str = Field(description="Текстовый ответ Хонзика")
    honzik_response_audio: bytes = Field(
        description="Аудио ответ Хонзика (bytes)"
    )
    corrections: CorrectionSchema = Field(description="Исправления")
    formatted_mistakes: str = Field(
        description="Отформатированные ошибки для отображения"
    )
    formatted_suggestion: str = Field(
        description="Отформатированная подсказка"
    )

    # Геймификация
    stars_earned: int = Field(description="Звезды за сообщение")
    total_stars: int = Field(description="Всего звезд")
    current_streak: int = Field(description="Текущий streak")
    max_streak: int = Field(description="Максимальный streak")
    daily_challenge: DailyChallengeSchema = Field(
        description="Информация о daily challenge"
    )

    # Статистика
    words_total: int = Field(description="Всего слов")
    words_correct: int = Field(description="Правильных слов")

    class Config:
        """Конфигурация модели."""

        json_schema_extra = {
            "example": {
                "transcript": "Ahoj, jak se máš? Já jsem dobře.",
                "honzik_response_text": "Nazdar! Mám se skvěle, díky! "
                "Tvoje čeština je už docela dobrá!",
                "corrections": {
                    "corrected_text": "Ahoj, jak se máš? Mám se dobře.",
                    "mistakes": [
                        {
                            "original": "Já jsem dobře",
                            "corrected": "Mám se dobře",
                            "explanation": "В чешском языке не говорят "
                            "'já jsem dobře', правильно 'mám se dobře'",
                        }
                    ],
                    "correctness_score": 85,
                    "suggestion": "Отлично! Попробуй использовать "
                    "больше разговорных выражений.",
                },
                "formatted_mistakes": "📝 Исправления от Хонзика:\n\n"
                "1. ❌ Já jsem dobře\n   ✅ Mám se dobře\n   "
                "💡 В чешском не говорят...",
                "formatted_suggestion": "\n💬 Совет от Хонзика: Отлично!",
                "stars_earned": 2,
                "total_stars": 15,
                "current_streak": 3,
                "max_streak": 5,
                "daily_challenge": {
                    "challenge_completed": False,
                    "messages_today": 2,
                    "messages_needed": 5,
                    "bonus_stars": 0,
                },
                "words_total": 7,
                "words_correct": 6,
            }
        }


class VoiceSettingsSchema(BaseModel):
    """
    Настройки для генерации голосового ответа.

    Attributes:
        voice: Голос (alloy, onyx, и т.д.)
        speed: Скорость речи
    """

    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = (
        Field(default="alloy", description="Голос для TTS")
    )
    speed: Literal["very_slow", "slow", "normal", "native"] = Field(
        default="normal", description="Скорость речи"
    )

