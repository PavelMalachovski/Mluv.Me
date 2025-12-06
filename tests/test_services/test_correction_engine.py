"""
Тесты для CorrectionEngine.
"""

import pytest
from backend.services.correction_engine import CorrectionEngine


class TestCorrectionEngine:
    """Тесты для движка исправлений."""

    @pytest.fixture
    def engine(self):
        """Fixture для CorrectionEngine."""
        return CorrectionEngine()

    def test_calculate_words_stats(self, engine):
        """Тест расчета статистики по словам."""
        text = "Ahoj jak se máš dnes"
        mistakes_count = 1

        result = engine.calculate_words_stats(text, mistakes_count)

        assert result["words_total"] == 5
        assert result["words_correct"] == 4

    def test_calculate_words_stats_no_mistakes(self, engine):
        """Тест расчета когда нет ошибок."""
        text = "Perfektní text"
        mistakes_count = 0

        result = engine.calculate_words_stats(text, mistakes_count)

        assert result["words_total"] == 2
        assert result["words_correct"] == 2

    def test_normalize_correctness_score_valid(self, engine):
        """Тест нормализации валидной оценки."""
        assert engine.normalize_correctness_score(85) == 85
        assert engine.normalize_correctness_score(0) == 0
        assert engine.normalize_correctness_score(100) == 100

    def test_normalize_correctness_score_out_of_range(self, engine):
        """Тест нормализации оценки вне диапазона."""
        assert engine.normalize_correctness_score(150) == 100
        assert engine.normalize_correctness_score(-10) == 0

    def test_normalize_correctness_score_invalid_type(self, engine):
        """Тест нормализации некорректного типа."""
        assert engine.normalize_correctness_score("invalid") == 0
        assert engine.normalize_correctness_score(None) == 0

    def test_format_mistakes_for_display_no_mistakes(self, engine):
        """Тест форматирования когда нет ошибок."""
        mistakes = []
        result = engine.format_mistakes_for_display(mistakes, "ru")

        assert "Отлично" in result
        assert "ошибок не найдено" in result.lower()

    def test_format_mistakes_for_display_with_mistakes_ru(self, engine):
        """Тест форматирования ошибок на русском."""
        mistakes = [
            {
                "original": "já jsem dobře",
                "corrected": "mám se dobře",
                "explanation": "В чешском не говорят 'já jsem dobře'",
            }
        ]

        result = engine.format_mistakes_for_display(mistakes, "ru")

        assert "Исправления" in result
        assert "já jsem dobře" in result
        assert "mám se dobře" in result
        assert "В чешском" in result

    def test_format_mistakes_for_display_with_mistakes_uk(self, engine):
        """Тест форматирования ошибок на украинском."""
        mistakes = [
            {
                "original": "chybný text",
                "corrected": "správný text",
                "explanation": "Пояснення українською",
            }
        ]

        result = engine.format_mistakes_for_display(mistakes, "uk")

        assert "Виправлення" in result
        assert "chybný text" in result
        assert "správný text" in result

    def test_format_suggestion_empty(self, engine):
        """Тест форматирования пустой подсказки."""
        result = engine.format_suggestion("", "ru")
        assert result == ""

    def test_format_suggestion_with_text_ru(self, engine):
        """Тест форматирования подсказки на русском."""
        suggestion = "Отлично! Продолжай практиковаться."
        result = engine.format_suggestion(suggestion, "ru")

        assert "Совет от Хонзика" in result
        assert suggestion in result

    def test_format_suggestion_with_text_uk(self, engine):
        """Тест форматирования подсказки на украинском."""
        suggestion = "Чудово! Продовжуй практикуватися."
        result = engine.format_suggestion(suggestion, "uk")

        assert "Порада від Хонзіка" in result
        assert suggestion in result

    def test_validate_honzik_response_valid(self, engine):
        """Тест валидации корректного ответа."""
        response = {
            "honzik_response": "Ahoj!",
            "corrected_text": "Corrected",
            "mistakes": [],
            "correctness_score": 85,
            "suggestion": "Keep going!",
        }

        assert engine.validate_honzik_response(response) is True

    def test_validate_honzik_response_missing_field(self, engine):
        """Тест валидации с отсутствующим полем."""
        response = {
            "honzik_response": "Ahoj!",
            "corrected_text": "Corrected",
            # Отсутствует mistakes
            "correctness_score": 85,
            "suggestion": "Keep going!",
        }

        assert engine.validate_honzik_response(response) is False

    def test_validate_honzik_response_invalid_score(self, engine):
        """Тест валидации с некорректной оценкой."""
        response = {
            "honzik_response": "Ahoj!",
            "corrected_text": "Corrected",
            "mistakes": [],
            "correctness_score": 150,  # Вне диапазона
            "suggestion": "Keep going!",
        }

        assert engine.validate_honzik_response(response) is False

    def test_process_honzik_response_success(self, engine):
        """Тест полной обработки ответа."""
        response = {
            "honzik_response": "Skvělý! Jak se máš?",
            "corrected_text": "Ahoj, jak se máš?",
            "mistakes": [
                {
                    "original": "ják",
                    "corrected": "jak",
                    "explanation": "Правильно без ударения",
                }
            ],
            "correctness_score": 90,
            "suggestion": "Отлично!",
        }

        original_text = "Ahoj ják se máš"

        result = engine.process_honzik_response(response, original_text, "ru")

        assert result["honzik_response"] == response["honzik_response"]
        assert result["corrected_text"] == response["corrected_text"]
        assert result["correctness_score"] == 90
        assert result["mistakes_count"] == 1
        assert result["words_total"] == 4
        assert result["words_correct"] == 3
        assert "ják" in result["formatted_mistakes"]
        assert "Совет" in result["formatted_suggestion"]

    def test_process_honzik_response_invalid(self, engine):
        """Тест обработки некорректного ответа."""
        response = {
            "honzik_response": "Ahoj!",
            # Отсутствуют обязательные поля
        }

        with pytest.raises(ValueError):
            engine.process_honzik_response(response, "test", "ru")

