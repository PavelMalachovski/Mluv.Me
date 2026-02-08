"""
Движок для обработки и форматирования исправлений от Хонзика.

Реализует:
- Парсинг JSON ответа от GPT
- Расчет correctness_score
- Форматирование ошибок и объяснений
- Обработка edge cases (пустой ответ, некорректный JSON)
"""

import structlog

logger = structlog.get_logger(__name__)


class CorrectionEngine:
    """
    Движок для обработки исправлений и оценки правильности.
    """

    def __init__(self):
        """Инициализация движка исправлений."""
        self.logger = logger.bind(service="correction_engine")

    def calculate_words_stats(
        self, text: str, mistakes_count: int
    ) -> dict[str, int]:
        """
        Рассчитать статистику по словам.

        Args:
            text: Оригинальный текст пользователя
            mistakes_count: Количество ошибок

        Returns:
            dict: {
                "words_total": int,
                "words_correct": int
            }
        """
        words = text.split()
        words_total = len(words)

        # Простое приближение: количество правильных слов
        # = общее количество - количество ошибок
        words_correct = max(0, words_total - mistakes_count)

        return {
            "words_total": words_total,
            "words_correct": words_correct,
        }

    def normalize_correctness_score(self, score: int | float) -> int:
        """
        Нормализовать оценку правильности в диапазон 0-100.

        Args:
            score: Оценка от GPT

        Returns:
            int: Нормализованная оценка (0-100)
        """
        try:
            score = int(score)
            return max(0, min(100, score))
        except (ValueError, TypeError):
            self.logger.warning(
                "invalid_score_format",
                score=score,
            )
            return 0

    def format_mistakes_for_display(
        self, mistakes: list[dict], native_language: str = "ru"
    ) -> str:
        """
        Форматировать список ошибок для отображения пользователю.

        Новая концепция: Language Immersion.
        - Заголовок на чешском
        - Объяснения на простом чешском + перевод на родной язык

        Args:
            mistakes: Список ошибок от Хонзика
            native_language: Родной язык для перевода (ru/uk/pl/sk)

        Returns:
            str: Отформатированный текст с ошибками
        """
        if not mistakes:
            # Похвала на чешском (Language Immersion)
            return "🎉 Výborně! Žádné chyby!"

        # Заголовок на чешском
        formatted = "📝 Opravy od Honzíka:\n\n"

        for i, mistake in enumerate(mistakes, 1):
            original = mistake.get("original", "")
            corrected = mistake.get("corrected", "")

            # Новый формат с двумя объяснениями
            explanation_cs = mistake.get("explanation_cs", "")
            explanation_native = mistake.get("explanation_native", "")

            # Fallback на старый формат (для совместимости)
            if not explanation_cs and "explanation" in mistake:
                explanation_cs = mistake.get("explanation", "")
                explanation_native = ""

            formatted += f"{i}. ❌ {original}\n"
            formatted += f"   ✅ {corrected}\n"
            if explanation_cs:
                formatted += f"   💡 {explanation_cs}\n"
            formatted += "\n"

        return formatted.strip()

    def format_suggestion(self, suggestion: str, native_language: str = "ru") -> str:
        """
        Форматировать подсказку от Хонзика.

        Теперь на чешском (Language Immersion).

        Args:
            suggestion: Подсказка от Хонзика
            native_language: Родной язык (для будущих переводов)

        Returns:
            str: Отформатированная подсказка
        """
        if not suggestion:
            return ""

        # Заголовок на чешском
        return f"\n💬 Tip od Honzíka: {suggestion}"

    def validate_honzik_response(self, response: dict) -> bool:
        """
        Валидировать ответ от Хонзика.

        Args:
            response: Ответ от HonzikPersonality

        Returns:
            bool: True если валидный, False иначе
        """
        required_fields = [
            "honzik_response",
            "corrected_text",
            "mistakes",
            "correctness_score",
            "suggestion",
        ]

        for field in required_fields:
            if field not in response:
                self.logger.error(
                    "missing_required_field",
                    field=field,
                )
                return False

        # Проверка типов
        if not isinstance(response["honzik_response"], str):
            self.logger.error("invalid_honzik_response_type")
            return False

        if not isinstance(response["mistakes"], list):
            self.logger.error("invalid_mistakes_type")
            return False

        score = response["correctness_score"]
        if not isinstance(score, (int, float)) or not (0 <= score <= 100):
            self.logger.error("invalid_score", score=score)
            return False

        return True

    def process_honzik_response(
        self, response: dict, original_text: str, native_language: str = "ru"
    ) -> dict:
        """
        Обработать ответ от Хонзика и подготовить данные для сохранения.

        Args:
            response: Ответ от HonzikPersonality
            original_text: Оригинальный текст пользователя
            native_language: Родной язык пользователя (ru/uk/pl/sk)

        Returns:
            dict: Обработанные данные {
                "honzik_response": str,
                "corrected_text": str,
                "formatted_mistakes": str,
                "formatted_suggestion": str,
                "correctness_score": int,
                "words_total": int,
                "words_correct": int,
                "mistakes_count": int
            }

        Raises:
            ValueError: Если ответ не валидный
        """
        if not self.validate_honzik_response(response):
            raise ValueError("Invalid Honzik response")

        mistakes = response["mistakes"]
        mistakes_count = len(mistakes)

        # Рассчитываем статистику по словам
        words_stats = self.calculate_words_stats(original_text, mistakes_count)

        # Нормализуем оценку
        score = self.normalize_correctness_score(response["correctness_score"])

        # Форматируем для отображения (чешский UI с переводами)
        formatted_mistakes = self.format_mistakes_for_display(
            mistakes, native_language
        )
        formatted_suggestion = self.format_suggestion(
            response["suggestion"], native_language
        )

        self.logger.info(
            "processed_honzik_response",
            correctness_score=score,
            mistakes_count=mistakes_count,
            words_total=words_stats["words_total"],
        )

        # Fallback for corrected_text if None/empty - use original text
        corrected_text = response.get("corrected_text")
        if not corrected_text:
            self.logger.warning(
                "corrected_text_fallback_to_original",
                original_text=original_text[:50] if original_text else "",
            )
            corrected_text = original_text

        return {
            "honzik_response": response["honzik_response"],
            "corrected_text": corrected_text,
            "formatted_mistakes": formatted_mistakes,
            "formatted_suggestion": formatted_suggestion,
            "correctness_score": score,
            "words_total": words_stats["words_total"],
            "words_correct": words_stats["words_correct"],
            "mistakes_count": mistakes_count,
        }


