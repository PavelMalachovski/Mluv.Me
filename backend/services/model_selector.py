"""
AdaptiveModelSelector - умный выбор модели GPT по сложности запроса.

Анализирует текст пользователя и выбирает оптимальную модель:
- gpt-4o-mini: для простых приветствий, коротких ответов
- gpt-4o: для сложных вопросов, детального анализа
"""

import re
from typing import Literal

import structlog

logger = structlog.get_logger(__name__)

# Типы моделей
ModelType = Literal["gpt-4o", "gpt-4o-mini"]

# Причины выбора модели
ModelReason = Literal[
    "simple_greeting",
    "simple_answer",
    "polite_phrase",
    "detailed_corrections",
    "native_level",
    "long_text",
    "complex_question",
    "default_fast",
]


class AdaptiveModelSelector:
    """
    Умный выбор модели для баланса цена/качество/скорость.

    Стратегия:
    1. Простые фразы (приветствия, да/нет) → gpt-4o-mini (экономия 50%)
    2. detailed corrections → gpt-4o (лучший анализ)
    3. native level → gpt-4o (сложнее ошибки)
    4. Длинный текст (>100 слов) → gpt-4o
    5. Сложные вопросы → gpt-4o
    6. По умолчанию → gpt-4o-mini
    """

    # Паттерны для быстрого ответа (gpt-4o-mini)
    SIMPLE_GREETINGS = frozenset([
        "ahoj", "čau", "nazdar", "dobrý den", "dobré ráno", "dobrý večer",
        "dobrou noc", "pa pa", "na shledanou", "měj se", "sbohem",
    ])

    SIMPLE_ANSWERS = frozenset([
        "ano", "ne", "možná", "nevím", "rozumím", "nerozumím",
        "dobře", "ok", "fajn", "super", "výborně", "skvěle",
    ])

    POLITE_PHRASES = frozenset([
        "děkuji", "děkuju", "díky", "mockrát děkuji",
        "prosím", "není zač", "rádo se stalo",
        "promiň", "promiňte", "omlouvám se", "pardon",
    ])

    # Regex для обнаружения сложных вопросов
    COMPLEX_QUESTION_PATTERNS = [
        re.compile(r"\?.*\?", re.IGNORECASE),  # Два и более вопроса
        re.compile(
            r"\b(proč|jak|kdy|kde|kdo)\b.*\b(proč|jak|kdy|kde|kdo)\b",
            re.IGNORECASE
        ),  # Множественные вопросительные слова
    ]

    def __init__(self) -> None:
        self.logger = logger.bind(service="model_selector")

    def _normalize_text(self, text: str) -> str:
        """Нормализовать текст для сравнения."""
        return text.lower().strip().rstrip("?!.,;:")

    def _is_simple_greeting(self, text: str) -> bool:
        """Проверить, является ли текст простым приветствием."""
        normalized = self._normalize_text(text)

        # Проверяем точное совпадение
        if normalized in self.SIMPLE_GREETINGS:
            return True

        # Проверяем начало текста (приветствие + что-то ещё)
        for greeting in self.SIMPLE_GREETINGS:
            if normalized.startswith(greeting) and len(normalized) < 50:
                return True

        return False

    def _is_simple_answer(self, text: str) -> bool:
        """Проверить, является ли текст простым ответом."""
        normalized = self._normalize_text(text)
        return normalized in self.SIMPLE_ANSWERS

    def _is_polite_phrase(self, text: str) -> bool:
        """Проверить, является ли текст вежливой фразой."""
        normalized = self._normalize_text(text)

        for phrase in self.POLITE_PHRASES:
            if normalized.startswith(phrase):
                return True

        return False

    def _is_complex_question(self, text: str) -> bool:
        """Проверить, содержит ли текст сложные вопросы."""
        for pattern in self.COMPLEX_QUESTION_PATTERNS:
            if pattern.search(text):
                return True
        return False

    def select_model(
        self,
        user_text: str,
        czech_level: str,
        corrections_level: str,
        history_length: int = 0,
    ) -> tuple[ModelType, ModelReason]:
        """
        Выбрать оптимальную модель на основе анализа текста.

        Args:
            user_text: Текст пользователя
            czech_level: Уровень чешского (beginner, intermediate, advanced, native)
            corrections_level: Уровень исправлений (minimal, balanced, detailed)
            history_length: Длина истории разговора

        Returns:
            tuple[ModelType, ModelReason]: (название модели, причина выбора)
        """
        word_count = len(user_text.split())

        # 1. Простые приветствия - всегда mini
        if self._is_simple_greeting(user_text):
            self.logger.info(
                "model_selected",
                model="gpt-4o-mini",
                reason="simple_greeting",
                text_preview=user_text[:30],
            )
            return "gpt-4o-mini", "simple_greeting"

        # 2. Простые ответы (да/нет/может) - mini
        if self._is_simple_answer(user_text):
            self.logger.info(
                "model_selected",
                model="gpt-4o-mini",
                reason="simple_answer",
            )
            return "gpt-4o-mini", "simple_answer"

        # 3. Вежливые фразы (спасибо, извините) - mini
        if self._is_polite_phrase(user_text):
            self.logger.info(
                "model_selected",
                model="gpt-4o-mini",
                reason="polite_phrase",
            )
            return "gpt-4o-mini", "polite_phrase"

        # 4. Detailed corrections - полная модель для лучшего анализа
        if corrections_level == "detailed":
            self.logger.info(
                "model_selected",
                model="gpt-4o",
                reason="detailed_corrections",
            )
            return "gpt-4o", "detailed_corrections"

        # 5. Native level - нужна лучшая модель для тонких ошибок
        if czech_level == "native":
            self.logger.info(
                "model_selected",
                model="gpt-4o",
                reason="native_level",
            )
            return "gpt-4o", "native_level"

        # 6. Длинный текст (>100 слов) - полная модель
        if word_count > 100:
            self.logger.info(
                "model_selected",
                model="gpt-4o",
                reason="long_text",
                word_count=word_count,
            )
            return "gpt-4o", "long_text"

        # 7. Сложные вопросы - полная модель
        if self._is_complex_question(user_text):
            self.logger.info(
                "model_selected",
                model="gpt-4o",
                reason="complex_question",
            )
            return "gpt-4o", "complex_question"

        # 8. По умолчанию - быстрая модель
        self.logger.info(
            "model_selected",
            model="gpt-4o-mini",
            reason="default_fast",
        )
        return "gpt-4o-mini", "default_fast"


# Singleton instance
model_selector = AdaptiveModelSelector()
