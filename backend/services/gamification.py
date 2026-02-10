"""
Система геймификации для мотивации пользователей.

Реализует:
- Начисление звезд за сообщения и достижения
- Streak система (последовательные дни обучения)
- Daily Stars Challenge
- Бонусы за качество и регулярность
"""

from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.repositories import StatsRepository, UserRepository

logger = structlog.get_logger(__name__)


class GamificationService:
    """
    Сервис геймификации для мотивации пользователей.

    Attributes:
        stats_repo: Репозиторий для работы со статистикой
        user_repo: Репозиторий для работы с пользователями
    """

    # Константы для начисления звезд
    BASE_STARS_PER_MESSAGE = 1
    BONUS_HIGH_SCORE = 1  # За correctness_score > 80%
    BONUS_STREAK_7 = 2  # За 7 дней streak
    BONUS_STREAK_30 = 5  # За 30 дней streak
    DAILY_CHALLENGE_MESSAGES = 5  # Количество сообщений для daily challenge
    DAILY_CHALLENGE_REWARD = 5  # Звезды за daily challenge

    HIGH_SCORE_THRESHOLD = 80  # Порог для бонуса за качество

    def __init__(
        self, stats_repo: StatsRepository, user_repo: UserRepository
    ):
        """
        Инициализация сервиса геймификации.

        Args:
            stats_repo: Репозиторий статистики
            user_repo: Репозиторий пользователей
        """
        self.stats_repo = stats_repo
        self.user_repo = user_repo
        self.logger = logger.bind(service="gamification")

    def calculate_stars_for_message(
        self, correctness_score: int, current_streak: int
    ) -> int:
        """
        Рассчитать количество звезд за сообщение.

        Args:
            correctness_score: Оценка правильности (0-100)
            current_streak: Текущий streak пользователя

        Returns:
            int: Количество заработанных звезд
        """
        stars = self.BASE_STARS_PER_MESSAGE

        # Бонус за высокую оценку
        if correctness_score >= self.HIGH_SCORE_THRESHOLD:
            stars += self.BONUS_HIGH_SCORE
            self.logger.debug(
                "high_score_bonus",
                correctness_score=correctness_score,
            )

        # Бонус за streak
        if current_streak >= 30:
            stars += self.BONUS_STREAK_30
            self.logger.debug(
                "streak_30_bonus",
                current_streak=current_streak,
            )
        elif current_streak >= 7:
            stars += self.BONUS_STREAK_7
            self.logger.debug(
                "streak_7_bonus",
                current_streak=current_streak,
            )

        return stars

    async def award_stars(
        self,
        db: AsyncSession,
        user_id: int,
        stars_amount: int,
    ) -> dict:
        """
        Начислить звезды пользователю.

        Args:
            db: Сессия БД
            user_id: ID пользователя
            stars_amount: Количество звезд для начисления

        Returns:
            dict: {
                "stars_earned": int,
                "total_stars": int,
                "available_stars": int
            }
        """
        # Получаем текущие звезды
        stars_obj = await self.stats_repo.get_user_stars(user_id)

        if stars_obj is None:
            # Если нет записи, создаем с нулями
            current_total = 0
            current_available = 0
            current_lifetime = 0
        else:
            current_total = stars_obj.total
            current_available = stars_obj.available
            current_lifetime = stars_obj.lifetime

        # Начисляем
        new_total = current_total + stars_amount
        new_available = current_available + stars_amount
        new_lifetime = current_lifetime + stars_amount

        # Обновляем в БД
        await self.stats_repo.update_user_stars(
            user_id=user_id,
            total=new_total,
            available=new_available,
            lifetime=new_lifetime,
        )

        self.logger.info(
            "stars_awarded",
            user_id=user_id,
            stars_earned=stars_amount,
            new_total=new_total,
        )

        return {
            "stars_earned": stars_amount,
            "total_stars": new_total,
            "available_stars": new_available,
        }

    def get_user_timezone(self, timezone_str: str | None) -> ZoneInfo:
        """
        Получить timezone пользователя.

        Args:
            timezone_str: Строка timezone (например, "Europe/Prague")

        Returns:
            ZoneInfo: Timezone объект
        """
        try:
            if timezone_str:
                return ZoneInfo(timezone_str)
        except Exception as e:
            self.logger.warning(
                "invalid_timezone",
                timezone_str=timezone_str,
                error=str(e),
            )

        # По умолчанию UTC
        return ZoneInfo("UTC")

    def get_user_date(self, timezone_str: str | None = None) -> date:
        """
        Получить текущую дату пользователя с учётом его timezone.

        Args:
            timezone_str: Строка timezone пользователя

        Returns:
            date: Текущая дата в timezone пользователя
        """
        tz = self.get_user_timezone(timezone_str)
        return datetime.now(tz).date()

    async def update_streak(
        self,
        db: AsyncSession,
        user_id: int,
        timezone_str: str | None = None,
    ) -> dict:
        """
        Обновить streak пользователя.

        Args:
            db: Сессия БД
            user_id: ID пользователя
            timezone_str: Timezone пользователя

        Returns:
            dict: {
                "current_streak": int,
                "max_streak": int,
                "streak_updated": bool
            }
        """
        user_date = self.get_user_date(timezone_str)

        # Получаем статистику за сегодня
        today_stats = await self.stats_repo.get_daily_stats(
            user_id=user_id,
            date_value=user_date,
        )

        # Получаем статистику за вчера
        yesterday = user_date - timedelta(days=1)
        yesterday_stats = await self.stats_repo.get_daily_stats(
            user_id=user_id,
            date_value=yesterday,
        )

        # Получаем общую статистику пользователя
        user_stats = await self.stats_repo.get_user_summary(user_id=user_id)
        current_streak = user_stats.get("current_streak", 0)
        max_streak = user_stats.get("max_streak", 0)

        # Логика streak:
        # 1. Если сегодня уже есть сообщения - streak уже обновлен
        # 2. Если вчера был streak - продолжаем
        # 3. Если вчера не было - начинаем новый

        streak_updated = False

        if today_stats and today_stats.get("messages_count", 0) == 1:
            # Первое сообщение сегодня - обновляем streak
            if yesterday_stats and yesterday_stats.get("streak_day", 0) > 0:
                # Продолжаем streak — берём streak из вчерашнего дня + 1
                new_streak = yesterday_stats["streak_day"] + 1
            else:
                # Начинаем новый streak
                new_streak = 1

            # Обновляем max streak если нужно
            new_max_streak = max(max_streak, new_streak)

            # Сохраняем в daily_stats
            await self.stats_repo.update_daily(
                user_id=user_id,
                date_value=user_date,
                streak_day=new_streak,
            )

            # Обновляем в таблице пользователя (через user_repo)
            # Это можно сделать через обновление user settings или отдельное поле

            current_streak = new_streak
            max_streak = new_max_streak
            streak_updated = True

            self.logger.info(
                "streak_updated",
                user_id=user_id,
                new_streak=new_streak,
                max_streak=new_max_streak,
            )

        return {
            "current_streak": current_streak,
            "max_streak": max_streak,
            "streak_updated": streak_updated,
        }

    async def check_daily_challenge(
        self,
        db: AsyncSession,
        user_id: int,
        timezone_str: str | None = None,
    ) -> dict:
        """
        Проверить выполнение Daily Challenge.

        Daily Challenge: отправить 5 голосовых сообщений за день.
        Награда: 5 дополнительных звезд.

        Args:
            db: Сессия БД
            user_id: ID пользователя
            timezone_str: Timezone пользователя

        Returns:
            dict: {
                "challenge_completed": bool,
                "messages_today": int,
                "messages_needed": int,
                "bonus_stars": int
            }
        """
        user_date = self.get_user_date(timezone_str)

        # Получаем статистику за сегодня
        today_stats = await self.stats_repo.get_daily_stats(
            user_id=user_id,
            date_value=user_date,
        )

        messages_today = today_stats.get("messages_count", 0) if today_stats else 0

        # Проверяем выполнение
        challenge_completed = messages_today >= self.DAILY_CHALLENGE_MESSAGES
        bonus_stars = 0

        # Если достигли ровно 5 сообщений - начисляем бонус
        if messages_today == self.DAILY_CHALLENGE_MESSAGES:
            bonus_stars = self.DAILY_CHALLENGE_REWARD
            await self.award_stars(db, user_id, bonus_stars)

            self.logger.info(
                "daily_challenge_completed",
                user_id=user_id,
                messages_today=messages_today,
                bonus_stars=bonus_stars,
            )

        return {
            "challenge_completed": challenge_completed,
            "messages_today": messages_today,
            "messages_needed": self.DAILY_CHALLENGE_MESSAGES,
            "bonus_stars": bonus_stars,
        }

    async def process_message_gamification(
        self,
        db: AsyncSession,
        user_id: int,
        correctness_score: int,
        timezone_str: str | None = None,
    ) -> dict:
        """
        Обработать геймификацию для сообщения (звезды + streak + challenge).

        Args:
            db: Сессия БД
            user_id: ID пользователя
            correctness_score: Оценка правильности
            timezone_str: Timezone пользователя

        Returns:
            dict: {
                "stars_earned": int,
                "total_stars": int,
                "current_streak": int,
                "max_streak": int,
                "daily_challenge": dict
            }
        """
        # Обновляем streak
        streak_info = await self.update_streak(db, user_id, timezone_str)

        # Рассчитываем звезды
        stars_amount = self.calculate_stars_for_message(
            correctness_score, streak_info["current_streak"]
        )

        # Начисляем звезды
        stars_info = await self.award_stars(db, user_id, stars_amount)

        # Проверяем daily challenge
        challenge_info = await self.check_daily_challenge(
            db=db,
            user_id=user_id,
            timezone_str=timezone_str,
        )

        self.logger.info(
            "message_gamification_processed",
            user_id=user_id,
            stars_earned=stars_info["stars_earned"],
            current_streak=streak_info["current_streak"],
        )

        return {
            "stars_earned": stars_info["stars_earned"],
            "total_stars": stars_info["total_stars"],
            "current_streak": streak_info["current_streak"],
            "max_streak": streak_info["max_streak"],
            "daily_challenge": challenge_info,
        }

