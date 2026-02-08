"""
Achievement Service V2.
Расширенный сервис для проверки и выдачи достижений.

Поддерживает категории:
- streak: Последовательные дни
- messages: Количество сообщений
- vocabulary: Сохранённые слова
- accuracy: Точность ответов
- stars: Собранные звёзды
- review: Освоенные слова
- thematic: Тематические (пиво, еда, история, путешествия)
- time: Временные (утро, ночь, выходные)
- quality: Качество (серии правильных ответов, прогресс)
- challenge: Выполненные челленджи
"""

from datetime import datetime, date, timedelta
from typing import Any
from enum import Enum
from zoneinfo import ZoneInfo

import structlog
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.achievement import Achievement, UserAchievement
from backend.models.challenge import TopicMessageCount, UserChallenge
from backend.models.user import User
from backend.models.word import SavedWord
from backend.models.stats import DailyStats, Stars
from backend.models.message import Message

logger = structlog.get_logger()


class AchievementCategory(str, Enum):
    """Achievement categories."""
    STREAK = "streak"
    MESSAGES = "messages"
    VOCABULARY = "vocabulary"
    ACCURACY = "accuracy"
    STARS = "stars"
    REVIEW = "review"
    THEMATIC = "thematic"
    TIME = "time"
    QUALITY = "quality"
    CHALLENGE = "challenge"


# Ключевые слова для определения тем
TOPIC_KEYWORDS = {
    "beer": [
        "pivo", "plzeň", "hospoda", "pijte", "čepované", "ležák",
        "pivovar", "pilsner", "kozel", "budvar", "staropramen",
        "točené", "půllitr", "koruna", "piva", "pivko"
    ],
    "food": [
        "jídlo", "knedlík", "svíčková", "guláš", "restaurace", "jíst",
        "kuchyně", "večeře", "oběd", "snídaně", "bramborák", "smažený",
        "řízek", "vepřo", "knedlo", "zelo", "trdelník", "párek", "klobása"
    ],
    "history": [
        "praha", "hrad", "karel", "historie", "středověk", "most",
        "kostel", "katedrála", "zámek", "palác", "revoluce", "válka",
        "husité", "masaryk", "václav", "republika", "království"
    ],
    "travel": [
        "letadlo", "vlak", "cestování", "dovolená", "turista", "hotel",
        "letiště", "nádraží", "metro", "tramvaj", "autobus", "taxi",
        "cesta", "výlet", "průvodce", "mapa", "památky"
    ],
    "culture": [
        "divadlo", "kino", "film", "hudba", "koncert", "muzeum",
        "galerie", "výstava", "kniha", "literatura", "umění",
        "smetana", "dvořák", "kafka", "čapek", "havel"
    ],
}


class AchievementService:
    """
    Расширенный сервис для работы с достижениями.

    Проверяет условия и выдает достижения пользователям,
    включая тематические, временные и качественные достижения.
    """

    async def check_achievements(
        self,
        session: AsyncSession,
        user: User,
        category: AchievementCategory | None = None,
        current_value: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Проверить и разблокировать достижения для пользователя.

        Args:
            session: Сессия базы данных
            user: Пользователь
            category: Категория для проверки (если не указана - все)
            current_value: Текущее значение для категории

        Returns:
            Список новых разблокированных достижений
        """
        newly_unlocked = []

        # Получаем достижения для категории
        query = select(Achievement)
        if category:
            query = query.where(Achievement.category == category.value)

        result = await session.execute(query)
        achievements = result.scalars().all()

        # Получаем уже разблокированные достижения
        unlocked_query = select(UserAchievement.achievement_id).where(
            UserAchievement.user_id == user.id
        )
        unlocked_result = await session.execute(unlocked_query)
        unlocked_ids = set(unlocked_result.scalars().all())

        for achievement in achievements:
            if achievement.id in unlocked_ids:
                continue

            # Вычисляем текущее значение на основе категории
            value = current_value
            if value is None:
                value = await self._get_category_value(session, user, achievement)

            # Проверяем порог
            if value >= achievement.threshold:
                # Разблокируем достижение
                user_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=achievement.id,
                    progress=value,
                )
                session.add(user_achievement)

                # Начисляем звёзды
                if achievement.stars_reward > 0:
                    await self._award_stars(session, user.id, achievement.stars_reward)

                newly_unlocked.append({
                    "id": achievement.id,
                    "code": achievement.code,
                    "name": achievement.name,
                    "description": achievement.description,
                    "icon": achievement.icon,
                    "category": achievement.category,
                    "stars_reward": achievement.stars_reward,
                })

                logger.info(
                    "achievement_unlocked",
                    user_id=user.id,
                    achievement_code=achievement.code,
                    stars_reward=achievement.stars_reward,
                )

        if newly_unlocked:
            await session.flush()

        return newly_unlocked

    async def _get_category_value(
        self,
        session: AsyncSession,
        user: User,
        achievement: Achievement,
    ) -> int:
        """Получить текущее значение для категории достижения."""
        category = achievement.category

        if category == "streak":
            return await self._get_current_streak(session, user.id)
        elif category == "messages":
            return await self._get_total_messages(session, user.id)
        elif category == "stars":
            return await self._get_total_stars(session, user.id)
        elif category == "vocabulary":
            return await self._get_saved_words_count(session, user.id)
        elif category == "review":
            return await self._get_mastered_words_count(session, user.id)
        elif category == "thematic":
            # Для тематических достижений используем код для определения темы
            topic = achievement.code.replace("_master", "").replace("_buff", "").replace("_lover", "")
            return await self._get_topic_count(session, user.id, topic)
        elif category == "time":
            # Временные достижения проверяются отдельно
            return await self._get_time_achievement_count(session, user.id, achievement.code)
        elif category == "quality":
            return await self._get_quality_value(session, user.id, achievement.code)
        elif category == "challenge":
            return await self._get_completed_challenges_count(session, user.id)

        return 0

    async def _get_current_streak(self, session: AsyncSession, user_id: int) -> int:
        """Получить текущий streak пользователя."""
        result = await session.execute(
            select(DailyStats.streak_day)
            .where(DailyStats.user_id == user_id)
            .order_by(DailyStats.date.desc())
            .limit(1)
        )
        streak = result.scalar_one_or_none()
        return streak or 0

    async def _get_total_messages(self, session: AsyncSession, user_id: int) -> int:
        """Получить общее количество сообщений пользователя."""
        result = await session.execute(
            select(func.count(Message.id))
            .where(and_(Message.user_id == user_id, Message.role == "user"))
        )
        return result.scalar() or 0

    async def _get_total_stars(self, session: AsyncSession, user_id: int) -> int:
        """Получить общее количество звёзд пользователя."""
        result = await session.execute(
            select(Stars.lifetime).where(Stars.user_id == user_id)
        )
        return result.scalar() or 0

    async def _get_saved_words_count(self, session: AsyncSession, user_id: int) -> int:
        """Получить количество сохранённых слов."""
        result = await session.execute(
            select(func.count(SavedWord.id)).where(SavedWord.user_id == user_id)
        )
        return result.scalar() or 0

    async def _get_mastered_words_count(self, session: AsyncSession, user_id: int) -> int:
        """Получить количество освоенных слов (interval >= 90 дней)."""
        result = await session.execute(
            select(func.count(SavedWord.id))
            .where(
                and_(
                    SavedWord.user_id == user_id,
                    SavedWord.interval_days >= 90
                )
            )
        )
        return result.scalar() or 0

    async def _get_topic_count(
        self, session: AsyncSession, user_id: int, topic: str
    ) -> int:
        """Получить количество сообщений по теме."""
        result = await session.execute(
            select(TopicMessageCount.count)
            .where(
                and_(
                    TopicMessageCount.user_id == user_id,
                    TopicMessageCount.topic == topic
                )
            )
        )
        return result.scalar() or 0

    async def _get_time_achievement_count(
        self, session: AsyncSession, user_id: int, achievement_code: str
    ) -> int:
        """Получить количество для временных достижений."""
        # early_bird, night_owl, weekend_warrior, early_bird_10, night_owl_10
        # Эти достижения обновляются при обработке сообщений
        # Здесь возвращаем прогресс из user_achievements если есть

        # Для временных достижений используем отдельный механизм
        # Возвращаем 0, так как check выполняется отдельно
        return 0

    async def _get_quality_value(
        self, session: AsyncSession, user_id: int, achievement_code: str
    ) -> int:
        """Получить значение для качественных достижений."""
        if "perfectionist" in achievement_code:
            # Получить количество последовательных сообщений с >90%
            return await self._get_consecutive_high_accuracy(session, user_id)
        elif "no_mistakes" in achievement_code:
            # Получить количество сообщений без ошибок
            return await self._get_no_mistakes_count(session, user_id)
        elif "improver" in achievement_code:
            # Улучшение за неделю (проверяется отдельно)
            return 0
        return 0

    async def _get_consecutive_high_accuracy(
        self, session: AsyncSession, user_id: int
    ) -> int:
        """Получить количество последовательных сообщений с >90% точностью."""
        result = await session.execute(
            select(Message.correctness_score)
            .where(
                and_(
                    Message.user_id == user_id,
                    Message.role == "user",
                    Message.correctness_score.isnot(None)
                )
            )
            .order_by(Message.created_at.desc())
            .limit(20)  # Проверяем последние 20 сообщений
        )
        scores = list(result.scalars().all())

        consecutive = 0
        for score in scores:
            if score >= 90:
                consecutive += 1
            else:
                break

        return consecutive

    async def _get_no_mistakes_count(self, session: AsyncSession, user_id: int) -> int:
        """Получить количество сообщений без ошибок (100%)."""
        result = await session.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.user_id == user_id,
                    Message.role == "user",
                    Message.correctness_score == 100
                )
            )
        )
        return result.scalar() or 0

    async def _get_completed_challenges_count(
        self, session: AsyncSession, user_id: int
    ) -> int:
        """Получить количество выполненных челленджей."""
        result = await session.execute(
            select(func.count(UserChallenge.id))
            .where(
                and_(
                    UserChallenge.user_id == user_id,
                    UserChallenge.completed
                )
            )
        )
        return result.scalar() or 0

    async def _award_stars(
        self, session: AsyncSession, user_id: int, amount: int
    ) -> None:
        """Начислить звёзды пользователю."""
        result = await session.execute(
            select(Stars).where(Stars.user_id == user_id)
        )
        stars = result.scalar_one_or_none()

        if stars:
            stars.total += amount
            stars.available += amount
            stars.lifetime += amount
            stars.updated_at = datetime.utcnow()
        else:
            # Создаём запись если нет
            stars = Stars(
                user_id=user_id,
                total=amount,
                available=amount,
                lifetime=amount
            )
            session.add(stars)

    async def check_thematic_achievements(
        self,
        session: AsyncSession,
        user: User,
        message_text: str,
    ) -> list[dict[str, Any]]:
        """
        Проверить тематические достижения на основе содержания сообщения.

        Args:
            session: Сессия БД
            user: Пользователь
            message_text: Текст сообщения

        Returns:
            Список новых разблокированных достижений
        """
        newly_unlocked = []
        detected_topics = self._detect_topics(message_text)

        for topic in detected_topics:
            # Увеличиваем счётчик темы
            await self._increment_topic_count(session, user.id, topic)

            # Проверяем достижения для этой темы
            achievements = await self.check_achievements(
                session=session,
                user=user,
                category=AchievementCategory.THEMATIC,
            )
            newly_unlocked.extend(achievements)

        return newly_unlocked

    def _detect_topics(self, text: str) -> list[str]:
        """Определить темы в тексте."""
        text_lower = text.lower()
        topics = []

        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)

        return topics

    async def _increment_topic_count(
        self, session: AsyncSession, user_id: int, topic: str
    ) -> int:
        """Увеличить счётчик сообщений по теме."""
        result = await session.execute(
            select(TopicMessageCount)
            .where(
                and_(
                    TopicMessageCount.user_id == user_id,
                    TopicMessageCount.topic == topic
                )
            )
        )
        topic_count = result.scalar_one_or_none()

        if topic_count:
            topic_count.count += 1
            topic_count.updated_at = datetime.utcnow()
        else:
            topic_count = TopicMessageCount(
                user_id=user_id,
                topic=topic,
                count=1
            )
            session.add(topic_count)

        await session.flush()
        return topic_count.count

    async def check_time_based_achievements(
        self,
        session: AsyncSession,
        user: User,
        message_time: datetime,
        timezone_str: str = "Europe/Prague",
    ) -> list[dict[str, Any]]:
        """
        Проверить достижения, связанные со временем.

        Args:
            session: Сессия БД
            user: Пользователь
            message_time: Время сообщения
            timezone_str: Timezone пользователя

        Returns:
            Список новых разблокированных достижений
        """
        newly_unlocked = []

        try:
            tz = ZoneInfo(timezone_str)
        except Exception:
            tz = ZoneInfo("Europe/Prague")

        local_time = message_time.astimezone(tz)
        hour = local_time.hour
        weekday = local_time.weekday()  # 0 = Monday, 6 = Sunday

        # Early Bird: до 7 утра
        if hour < 7:
            achievement = await self._unlock_time_achievement(
                session, user, "early_bird"
            )
            if achievement:
                newly_unlocked.append(achievement)

            # Проверяем early_bird_10
            count = await self._get_early_bird_count(session, user.id)
            if count >= 10:
                achievement = await self._unlock_time_achievement(
                    session, user, "early_bird_10"
                )
                if achievement:
                    newly_unlocked.append(achievement)

        # Night Owl: после 23:00
        if hour >= 23:
            achievement = await self._unlock_time_achievement(
                session, user, "night_owl"
            )
            if achievement:
                newly_unlocked.append(achievement)

            # Проверяем night_owl_10
            count = await self._get_night_owl_count(session, user.id)
            if count >= 10:
                achievement = await self._unlock_time_achievement(
                    session, user, "night_owl_10"
                )
                if achievement:
                    newly_unlocked.append(achievement)

        # Weekend Warrior: оба выходных
        if weekday in (5, 6):  # Saturday or Sunday
            achievement = await self._check_weekend_warrior(
                session, user, local_time.date()
            )
            if achievement:
                newly_unlocked.append(achievement)

        return newly_unlocked

    async def _unlock_time_achievement(
        self,
        session: AsyncSession,
        user: User,
        achievement_code: str,
    ) -> dict[str, Any] | None:
        """Попытаться разблокировать временное достижение."""
        # Получаем достижение по коду
        result = await session.execute(
            select(Achievement).where(Achievement.code == achievement_code)
        )
        achievement = result.scalar_one_or_none()

        if not achievement:
            return None

        # Проверяем, не разблокировано ли уже
        existing = await session.execute(
            select(UserAchievement)
            .where(
                and_(
                    UserAchievement.user_id == user.id,
                    UserAchievement.achievement_id == achievement.id
                )
            )
        )
        if existing.scalar_one_or_none():
            return None

        # Разблокируем
        user_achievement = UserAchievement(
            user_id=user.id,
            achievement_id=achievement.id,
            progress=1,
        )
        session.add(user_achievement)

        # Начисляем звёзды
        if achievement.stars_reward > 0:
            await self._award_stars(session, user.id, achievement.stars_reward)

        await session.flush()

        logger.info(
            "time_achievement_unlocked",
            user_id=user.id,
            achievement_code=achievement_code,
        )

        return {
            "id": achievement.id,
            "code": achievement.code,
            "name": achievement.name,
            "description": achievement.description,
            "icon": achievement.icon,
            "category": achievement.category,
            "stars_reward": achievement.stars_reward,
        }

    async def _get_early_bird_count(self, session: AsyncSession, user_id: int) -> int:
        """Получить количество сообщений до 7 утра."""
        result = await session.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.user_id == user_id,
                    Message.role == "user",
                    func.extract('hour', Message.created_at) < 7
                )
            )
        )
        return result.scalar() or 0

    async def _get_night_owl_count(self, session: AsyncSession, user_id: int) -> int:
        """Получить количество сообщений после 23:00."""
        result = await session.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.user_id == user_id,
                    Message.role == "user",
                    func.extract('hour', Message.created_at) >= 23
                )
            )
        )
        return result.scalar() or 0

    async def _check_weekend_warrior(
        self,
        session: AsyncSession,
        user: User,
        current_date: date,
    ) -> dict[str, Any] | None:
        """Проверить достижение Weekend Warrior."""
        # Определяем субботу и воскресенье текущей недели
        weekday = current_date.weekday()
        if weekday == 5:  # Saturday
            saturday = current_date
            sunday = current_date + timedelta(days=1)
        else:  # Sunday
            saturday = current_date - timedelta(days=1)
            sunday = current_date

        # Проверяем, есть ли сообщения в оба дня
        sat_result = await session.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.user_id == user.id,
                    Message.role == "user",
                    func.date(Message.created_at) == saturday
                )
            )
        )
        sat_count = sat_result.scalar() or 0

        sun_result = await session.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.user_id == user.id,
                    Message.role == "user",
                    func.date(Message.created_at) == sunday
                )
            )
        )
        sun_count = sun_result.scalar() or 0

        if sat_count > 0 and sun_count > 0:
            return await self._unlock_time_achievement(
                session, user, "weekend_warrior"
            )

        return None

    async def check_quality_achievements(
        self,
        session: AsyncSession,
        user: User,
        correctness_score: int,
    ) -> list[dict[str, Any]]:
        """
        Проверить качественные достижения.

        Args:
            session: Сессия БД
            user: Пользователь
            correctness_score: Оценка правильности

        Returns:
            Список новых разблокированных достижений
        """
        return await self.check_achievements(
            session=session,
            user=user,
            category=AchievementCategory.QUALITY,
        )

    async def get_user_achievements(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[dict[str, Any]]:
        """
        Получить все достижения пользователя со статусом разблокировки.

        Args:
            session: Сессия БД
            user_id: ID пользователя

        Returns:
            Список достижений со статусом
        """
        # Получаем все достижения
        all_query = select(Achievement).order_by(Achievement.category, Achievement.threshold)
        all_result = await session.execute(all_query)
        all_achievements = all_result.scalars().all()

        # Получаем разблокированные достижения пользователя
        unlocked_query = (
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
        )
        unlocked_result = await session.execute(unlocked_query)
        unlocked_map = {ua.achievement_id: ua for ua in unlocked_result.scalars().all()}

        achievements = []
        for achievement in all_achievements:
            unlocked = unlocked_map.get(achievement.id)

            # Пропускаем скрытые незаблокированные достижения
            if achievement.is_hidden and not unlocked:
                continue

            achievements.append({
                "id": achievement.id,
                "code": achievement.code,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "category": achievement.category,
                "threshold": achievement.threshold,
                "stars_reward": achievement.stars_reward,
                "is_unlocked": unlocked is not None,
                "unlocked_at": unlocked.unlocked_at.isoformat() if unlocked else None,
                "progress": unlocked.progress if unlocked else 0,
            })

        return achievements

    async def get_achievement_progress(
        self,
        session: AsyncSession,
        user: User,
    ) -> dict[str, Any]:
        """
        Получить сводку прогресса достижений пользователя.

        Args:
            session: Сессия БД
            user: Пользователь

        Returns:
            Сводка прогресса по категориям
        """
        # Получаем количество достижений
        total_query = select(Achievement).where(not Achievement.is_hidden)
        total_result = await session.execute(total_query)
        total_count = len(list(total_result.scalars().all()))

        unlocked_query = select(UserAchievement).where(UserAchievement.user_id == user.id)
        unlocked_result = await session.execute(unlocked_query)
        unlocked_count = len(list(unlocked_result.scalars().all()))

        # Получаем значения категорий
        categories = {
            "streak": await self._get_current_streak(session, user.id),
            "messages": await self._get_total_messages(session, user.id),
            "stars": await self._get_total_stars(session, user.id),
            "vocabulary": await self._get_saved_words_count(session, user.id),
            "review": await self._get_mastered_words_count(session, user.id),
            "challenges": await self._get_completed_challenges_count(session, user.id),
        }

        # Получаем счётчики по темам
        topic_result = await session.execute(
            select(TopicMessageCount)
            .where(TopicMessageCount.user_id == user.id)
        )
        topic_counts = {tc.topic: tc.count for tc in topic_result.scalars().all()}

        return {
            "total_achievements": total_count,
            "unlocked_achievements": unlocked_count,
            "completion_percent": round((unlocked_count / total_count) * 100) if total_count > 0 else 0,
            "category_progress": categories,
            "topic_progress": topic_counts,
        }


# Singleton instance
achievement_service = AchievementService()
