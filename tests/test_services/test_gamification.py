"""
Тесты для GamificationService.
"""

from datetime import date
from backend.services.gamification import GamificationService


class TestGamificationService:
    """Тесты для сервиса геймификации."""

    def test_calculate_stars_for_message_base(self):
        """Тест базового начисления звезд."""
        service = GamificationService(None, None)

        stars = service.calculate_stars_for_message(
            correctness_score=50, current_streak=0
        )

        assert stars == 1  # Только базовая звезда

    def test_calculate_stars_for_message_high_score(self):
        """Тест бонуса за высокую оценку."""
        service = GamificationService(None, None)

        stars = service.calculate_stars_for_message(
            correctness_score=85, current_streak=0
        )

        assert stars == 2  # База + бонус за score > 80

    def test_calculate_stars_for_message_streak_7(self):
        """Тест бонуса за 7 дней streak."""
        service = GamificationService(None, None)

        stars = service.calculate_stars_for_message(
            correctness_score=50, current_streak=7
        )

        assert stars == 3  # База + бонус за 7 дней

    def test_calculate_stars_for_message_streak_30(self):
        """Тест бонуса за 30 дней streak."""
        service = GamificationService(None, None)

        stars = service.calculate_stars_for_message(
            correctness_score=90, current_streak=30
        )

        # База + score bonus + streak 30 bonus
        assert stars == 7  # 1 + 1 + 5

    def test_get_user_date_default_timezone(self):
        """Тест получения даты с timezone по умолчанию."""
        service = GamificationService(None, None)

        user_date = service.get_user_date(None)

        assert isinstance(user_date, date)

    def test_get_user_date_specific_timezone(self):
        """Тест получения даты с конкретным timezone."""
        service = GamificationService(None, None)

        user_date = service.get_user_date("Europe/Prague")

        assert isinstance(user_date, date)

    def test_get_user_date_invalid_timezone(self):
        """Тест получения даты с некорректным timezone (fallback to UTC)."""
        service = GamificationService(None, None)

        user_date = service.get_user_date("Invalid/Timezone")

        assert isinstance(user_date, date)


class TestGamificationConstants:
    """Тесты констант геймификации."""

    def test_constants_defined(self):
        """Проверка что все константы определены."""
        service = GamificationService(None, None)

        assert hasattr(service, "BASE_STARS_PER_MESSAGE")
        assert hasattr(service, "BONUS_HIGH_SCORE")
        assert hasattr(service, "BONUS_STREAK_7")
        assert hasattr(service, "BONUS_STREAK_30")
        assert hasattr(service, "HIGH_SCORE_THRESHOLD")
        assert hasattr(service, "DAILY_CHALLENGE_MESSAGES")
        assert hasattr(service, "DAILY_CHALLENGE_REWARD")

    def test_constants_values(self):
        """Проверка значений констант."""
        service = GamificationService(None, None)

        assert service.BASE_STARS_PER_MESSAGE == 1
        assert service.HIGH_SCORE_THRESHOLD == 80
        assert service.DAILY_CHALLENGE_MESSAGES == 5
        assert service.DAILY_CHALLENGE_REWARD == 5


