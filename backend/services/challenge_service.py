"""
Challenge Service.
Сервис для управления ежедневными и еженедельными челленджами.

Поддерживаемые типы целей:
- messages: Количество отправленных сообщений
- high_accuracy_messages: Сообщения с >80% точностью
- saved_words: Сохранённые слова
- topic_message: Сообщение на определённую тему
- streak_days: Дни streak подряд
- weekly_messages: Сообщения за неделю
- weekly_accuracy: Средняя точность за неделю
- weekly_saved_words: Сохранённые слова за неделю
"""

from datetime import datetime, date, timedelta, timezone
from typing import Any
import random
from zoneinfo import ZoneInfo

import structlog
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.challenge import Challenge, UserChallenge, TopicMessageCount
from backend.models.stats import DailyStats, Stars
from backend.models.word import SavedWord
from backend.models.message import Message

logger = structlog.get_logger()


class ChallengeService:
    """
    Сервис для работы с челленджами.

    Генерирует ежедневные и еженедельные челленджи,
    отслеживает прогресс и начисляет награды.
    """

    async def get_daily_challenge(
        self,
        session: AsyncSession,
        user_id: int,
        user_date: date,
    ) -> dict[str, Any]:
        """
        Получить ежедневный челлендж для пользователя.

        Челлендж генерируется детерминистически на основе user_id и даты,
        чтобы у одного пользователя был один челлендж в день.

        Args:
            session: Сессия БД
            user_id: ID пользователя
            user_date: Дата пользователя

        Returns:
            Информация о челлендже с прогрессом
        """
        # Получаем все активные ежедневные челленджи
        result = await session.execute(
            select(Challenge).where(
                and_(
                    Challenge.type == "daily",
                    Challenge.is_active
                )
            )
        )
        daily_challenges = list(result.scalars().all())

        if not daily_challenges:
            return {"error": "No daily challenges available"}

        # Детерминистический выбор на основе user_id и даты
        seed = hash(f"{user_id}:{user_date}")
        random.seed(seed)
        challenge = random.choice(daily_challenges)

        # Получаем или создаём запись прогресса
        user_challenge = await self._get_or_create_user_challenge(
            session, user_id, challenge.id, user_date
        )

        # Вычисляем текущий прогресс
        progress = await self._calculate_progress(
            session, user_id, challenge, user_date
        )

        # Обновляем прогресс
        user_challenge.progress = progress
        if progress >= challenge.goal_value and not user_challenge.completed:
            user_challenge.completed = True
            user_challenge.completed_at = datetime.now(timezone.utc)

        await session.flush()

        return {
            "id": challenge.id,
            "code": challenge.code,
            "type": challenge.type,
            "title": challenge.title_cs,
            "description": challenge.description_cs,
            "goal_type": challenge.goal_type,
            "goal_topic": challenge.goal_topic,
            "goal_value": challenge.goal_value,
            "reward_stars": challenge.reward_stars,
            "progress": progress,
            "completed": user_challenge.completed,
            "reward_claimed": user_challenge.reward_claimed,
            "expires_at": (user_date + timedelta(days=1)).isoformat(),
        }

    async def get_weekly_challenges(
        self,
        session: AsyncSession,
        user_id: int,
        user_date: date,
    ) -> list[dict[str, Any]]:
        """
        Получить еженедельные челленджи для пользователя.

        Args:
            session: Сессия БД
            user_id: ID пользователя
            user_date: Текущая дата

        Returns:
            Список еженедельных челленджей с прогрессом
        """
        # Определяем начало недели (понедельник)
        week_start = user_date - timedelta(days=user_date.weekday())

        # Получаем все активные еженедельные челленджи
        result = await session.execute(
            select(Challenge).where(
                and_(
                    Challenge.type == "weekly",
                    Challenge.is_active
                )
            )
        )
        weekly_challenges = list(result.scalars().all())

        challenges_data = []
        for challenge in weekly_challenges:
            # Получаем или создаём запись прогресса
            user_challenge = await self._get_or_create_user_challenge(
                session, user_id, challenge.id, week_start
            )

            # Вычисляем прогресс за неделю
            progress = await self._calculate_weekly_progress(
                session, user_id, challenge, week_start, user_date
            )

            # Обновляем прогресс
            user_challenge.progress = progress
            if progress >= challenge.goal_value and not user_challenge.completed:
                user_challenge.completed = True
                user_challenge.completed_at = datetime.now(timezone.utc)

            challenges_data.append({
                "id": challenge.id,
                "code": challenge.code,
                "type": challenge.type,
                "title": challenge.title_cs,
                "description": challenge.description_cs,
                "goal_type": challenge.goal_type,
                "goal_value": challenge.goal_value,
                "reward_stars": challenge.reward_stars,
                "progress": progress,
                "completed": user_challenge.completed,
                "reward_claimed": user_challenge.reward_claimed,
                "week_start": week_start.isoformat(),
                "expires_at": (week_start + timedelta(days=7)).isoformat(),
            })

        await session.flush()
        return challenges_data

    async def _get_or_create_user_challenge(
        self,
        session: AsyncSession,
        user_id: int,
        challenge_id: int,
        challenge_date: date,
    ) -> UserChallenge:
        """Получить или создать запись прогресса челленджа."""
        result = await session.execute(
            select(UserChallenge).where(
                and_(
                    UserChallenge.user_id == user_id,
                    UserChallenge.challenge_id == challenge_id,
                    UserChallenge.date == challenge_date
                )
            )
        )
        user_challenge = result.scalar_one_or_none()

        if not user_challenge:
            user_challenge = UserChallenge(
                user_id=user_id,
                challenge_id=challenge_id,
                date=challenge_date,
                progress=0,
                completed=False,
                reward_claimed=False,
            )
            session.add(user_challenge)
            await session.flush()

        return user_challenge

    async def _calculate_progress(
        self,
        session: AsyncSession,
        user_id: int,
        challenge: Challenge,
        target_date: date,
    ) -> int:
        """Вычислить прогресс для ежедневного челленджа."""
        goal_type = challenge.goal_type

        if goal_type == "messages":
            return await self._count_daily_messages(session, user_id, target_date)

        elif goal_type == "high_accuracy_messages":
            return await self._count_high_accuracy_messages(session, user_id, target_date)

        elif goal_type == "saved_words":
            return await self._count_daily_saved_words(session, user_id, target_date)

        elif goal_type == "topic_message":
            return await self._count_topic_messages(
                session, user_id, target_date, challenge.goal_topic
            )

        return 0

    async def _calculate_weekly_progress(
        self,
        session: AsyncSession,
        user_id: int,
        challenge: Challenge,
        week_start: date,
        current_date: date,
    ) -> int:
        """Вычислить прогресс для еженедельного челленджа."""
        goal_type = challenge.goal_type
        week_end = week_start + timedelta(days=6)

        if goal_type == "streak_days":
            return await self._get_current_streak(session, user_id)

        elif goal_type == "weekly_messages":
            return await self._count_weekly_messages(session, user_id, week_start, week_end)

        elif goal_type == "weekly_accuracy":
            return await self._get_weekly_accuracy(session, user_id, week_start, week_end)

        elif goal_type == "weekly_saved_words":
            return await self._count_weekly_saved_words(session, user_id, week_start, week_end)

        return 0

    async def _count_daily_messages(
        self, session: AsyncSession, user_id: int, target_date: date
    ) -> int:
        """Подсчитать сообщения за день."""
        result = await session.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.user_id == user_id,
                    Message.role == "user",
                    func.date(Message.created_at) == target_date
                )
            )
        )
        return result.scalar() or 0

    async def _count_high_accuracy_messages(
        self, session: AsyncSession, user_id: int, target_date: date
    ) -> int:
        """Подсчитать сообщения с высокой точностью (>80%)."""
        result = await session.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.user_id == user_id,
                    Message.role == "user",
                    func.date(Message.created_at) == target_date,
                    Message.correctness_score >= 80
                )
            )
        )
        return result.scalar() or 0

    async def _count_daily_saved_words(
        self, session: AsyncSession, user_id: int, target_date: date
    ) -> int:
        """Подсчитать сохранённые слова за день."""
        result = await session.execute(
            select(func.count(SavedWord.id))
            .where(
                and_(
                    SavedWord.user_id == user_id,
                    func.date(SavedWord.created_at) == target_date
                )
            )
        )
        return result.scalar() or 0

    async def _count_topic_messages(
        self,
        session: AsyncSession,
        user_id: int,
        target_date: date,
        topic: str,
    ) -> int:
        """Подсчитать сообщения на определённую тему за день."""
        # Для ежедневных тематических челленджей считаем минимум 1 если тема обсуждалась
        result = await session.execute(
            select(TopicMessageCount.count)
            .where(
                and_(
                    TopicMessageCount.user_id == user_id,
                    TopicMessageCount.topic == topic,
                    func.date(TopicMessageCount.updated_at) == target_date
                )
            )
        )
        count = result.scalar()
        return 1 if count and count > 0 else 0

    async def _get_current_streak(self, session: AsyncSession, user_id: int) -> int:
        """Получить текущий streak."""
        result = await session.execute(
            select(DailyStats.streak_day)
            .where(DailyStats.user_id == user_id)
            .order_by(DailyStats.date.desc())
            .limit(1)
        )
        return result.scalar() or 0

    async def _count_weekly_messages(
        self,
        session: AsyncSession,
        user_id: int,
        week_start: date,
        week_end: date,
    ) -> int:
        """Подсчитать сообщения за неделю."""
        result = await session.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.user_id == user_id,
                    Message.role == "user",
                    func.date(Message.created_at) >= week_start,
                    func.date(Message.created_at) <= week_end
                )
            )
        )
        return result.scalar() or 0

    async def _get_weekly_accuracy(
        self,
        session: AsyncSession,
        user_id: int,
        week_start: date,
        week_end: date,
    ) -> int:
        """Получить среднюю точность за неделю."""
        result = await session.execute(
            select(func.avg(Message.correctness_score))
            .where(
                and_(
                    Message.user_id == user_id,
                    Message.role == "user",
                    Message.correctness_score.isnot(None),
                    func.date(Message.created_at) >= week_start,
                    func.date(Message.created_at) <= week_end
                )
            )
        )
        avg = result.scalar()
        return int(avg) if avg else 0

    async def _count_weekly_saved_words(
        self,
        session: AsyncSession,
        user_id: int,
        week_start: date,
        week_end: date,
    ) -> int:
        """Подсчитать сохранённые слова за неделю."""
        result = await session.execute(
            select(func.count(SavedWord.id))
            .where(
                and_(
                    SavedWord.user_id == user_id,
                    func.date(SavedWord.created_at) >= week_start,
                    func.date(SavedWord.created_at) <= week_end
                )
            )
        )
        return result.scalar() or 0

    async def update_challenge_progress(
        self,
        session: AsyncSession,
        user_id: int,
        event_type: str,
        event_data: dict[str, Any],
        timezone_str: str = "Europe/Prague",
    ) -> dict[str, Any] | None:
        """
        Обновить прогресс челленджей на основе события.

        Args:
            session: Сессия БД
            user_id: ID пользователя
            event_type: Тип события (message, save_word, topic_message)
            event_data: Данные события
            timezone_str: Timezone пользователя

        Returns:
            Информация о завершённых челленджах или None
        """
        try:
            tz = ZoneInfo(timezone_str)
        except Exception:
            tz = ZoneInfo("Europe/Prague")

        user_date = datetime.now(tz).date()

        # Получаем ежедневный челлендж
        daily = await self.get_daily_challenge(session, user_id, user_date)
        weekly_list = await self.get_weekly_challenges(session, user_id, user_date)

        completed_challenges = []

        # Проверяем ежедневный челлендж
        if daily.get("completed") and not daily.get("reward_claimed"):
            completed_challenges.append({
                "type": "daily",
                "challenge": daily,
            })

        # Проверяем еженедельные челленджи
        for weekly in weekly_list:
            if weekly.get("completed") and not weekly.get("reward_claimed"):
                completed_challenges.append({
                    "type": "weekly",
                    "challenge": weekly,
                })

        return {
            "completed_challenges": completed_challenges,
            "daily_progress": daily,
            "weekly_progress": weekly_list,
        } if completed_challenges else None

    async def claim_challenge_reward(
        self,
        session: AsyncSession,
        user_id: int,
        challenge_id: int,
        challenge_date: date,
    ) -> dict[str, Any]:
        """
        Получить награду за выполненный челлендж.

        Args:
            session: Сессия БД
            user_id: ID пользователя
            challenge_id: ID челленджа
            challenge_date: Дата челленджа

        Returns:
            Информация о полученной награде
        """
        # Получаем запись прогресса
        result = await session.execute(
            select(UserChallenge)
            .where(
                and_(
                    UserChallenge.user_id == user_id,
                    UserChallenge.challenge_id == challenge_id,
                    UserChallenge.date == challenge_date
                )
            )
        )
        user_challenge = result.scalar_one_or_none()

        if not user_challenge:
            return {"error": "Challenge progress not found"}

        if not user_challenge.completed:
            return {"error": "Challenge not completed"}

        if user_challenge.reward_claimed:
            return {"error": "Reward already claimed"}

        # Получаем информацию о челлендже
        challenge_result = await session.execute(
            select(Challenge).where(Challenge.id == challenge_id)
        )
        challenge = challenge_result.scalar_one_or_none()

        if not challenge:
            return {"error": "Challenge not found"}

        # Начисляем награду
        stars_result = await session.execute(
            select(Stars).where(Stars.user_id == user_id)
        )
        stars = stars_result.scalar_one_or_none()

        if stars:
            stars.total += challenge.reward_stars
            stars.available += challenge.reward_stars
            stars.lifetime += challenge.reward_stars
            stars.updated_at = datetime.now(timezone.utc)
        else:
            stars = Stars(
                user_id=user_id,
                total=challenge.reward_stars,
                available=challenge.reward_stars,
                lifetime=challenge.reward_stars
            )
            session.add(stars)

        # Отмечаем награду полученной
        user_challenge.reward_claimed = True

        await session.flush()

        logger.info(
            "challenge_reward_claimed",
            user_id=user_id,
            challenge_id=challenge_id,
            stars_reward=challenge.reward_stars,
        )

        return {
            "success": True,
            "stars_earned": challenge.reward_stars,
            "total_stars": stars.total,
            "challenge_title": challenge.title_cs,
        }

    async def get_all_challenges(
        self,
        session: AsyncSession,
        user_id: int,
        timezone_str: str = "Europe/Prague",
    ) -> dict[str, Any]:
        """
        Получить все челленджи пользователя (дневные и недельные).

        Args:
            session: Сессия БД
            user_id: ID пользователя
            timezone_str: Timezone пользователя

        Returns:
            Все челленджи с прогрессом
        """
        try:
            tz = ZoneInfo(timezone_str)
        except Exception:
            tz = ZoneInfo("Europe/Prague")

        user_date = datetime.now(tz).date()

        daily = await self.get_daily_challenge(session, user_id, user_date)
        weekly = await self.get_weekly_challenges(session, user_id, user_date)

        # Подсчитываем статистику
        completed_today = 1 if daily.get("completed") else 0
        completed_week = sum(1 for w in weekly if w.get("completed"))

        return {
            "daily_challenge": daily,
            "weekly_challenges": weekly,
            "stats": {
                "daily_completed": completed_today,
                "weekly_completed": completed_week,
                "weekly_total": len(weekly),
            },
            "current_date": user_date.isoformat(),
        }


# Singleton instance
challenge_service = ChallengeService()
