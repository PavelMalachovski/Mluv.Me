"""
Repository pattern для работы с базой данных.
Абстрагирует SQL запросы от бизнес-логики.
"""

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
import structlog

from backend.models import (
    User,
    UserSettings,
    Message,
    SavedWord,
    DailyStats,
    Stars,
)
from backend.cache.redis_client import redis_client
from backend.cache.cache_keys import CacheKeys
from backend.config import get_settings

logger = structlog.get_logger(__name__)


class UserRepository:
    """Repository для работы с пользователями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Получить пользователя по ID.

        Args:
            user_id: ID пользователя

        Returns:
            User | None: Пользователь или None
        """
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.settings))
        )
        return result.scalar_one_or_none()

    async def get_by_telegram_id(
        self, telegram_id: int, use_cache: bool = True
    ) -> User | None:
        """
        Получить пользователя по Telegram ID с кешированием.

        Args:
            telegram_id: Telegram user ID
            use_cache: Использовать кеш (default: True)

        Returns:
            User | None: Пользователь или None
        """
        # Try cache first
        if use_cache and redis_client.is_enabled:
            cache_key = CacheKeys.user_profile(telegram_id)
            cached = await redis_client.get(cache_key)
            if cached:
                logger.debug("user_cache_hit", telegram_id=telegram_id)
                # Reconstruct User object from cached dict
                user = User(**{k: v for k, v in cached.items() if k != "settings"})
                if "settings" in cached and cached["settings"]:
                    user.settings = UserSettings(**cached["settings"])
                return user

        # Database query
        result = await self.session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.settings))
        )
        user = result.scalar_one_or_none()

        # Cache result
        if user and use_cache and redis_client.is_enabled:
            cache_key = CacheKeys.user_profile(telegram_id)
            settings = get_settings()
            user_dict = user.to_dict()
            if user.settings:
                user_dict["settings"] = user.settings.to_dict()
            await redis_client.set(
                cache_key, user_dict, ttl=settings.redis_cache_ttl_user
            )
            logger.debug("user_cached", telegram_id=telegram_id)

        return user

    async def create(self, **kwargs: Any) -> User:
        """
        Создать нового пользователя.

        Args:
            **kwargs: Параметры пользователя

        Returns:
            User: Созданный пользователь
        """
        user = User(**kwargs)
        self.session.add(user)
        await self.session.flush()

        # Create default settings
        settings = UserSettings(user_id=user.id)
        self.session.add(settings)

        # Create stars record
        stars = Stars(user_id=user.id)
        self.session.add(stars)

        await self.session.flush()
        await self.session.refresh(user, ["settings"])

        return user

    async def update(self, user_id: int, **kwargs: Any) -> User | None:
        """
        Обновить пользователя и инвалидировать кеш.

        Args:
            user_id: ID пользователя
            **kwargs: Обновляемые поля

        Returns:
            User | None: Обновленный пользователь или None
        """
        # Get user to find telegram_id for cache invalidation
        user = await self.get_by_id(user_id)
        if not user:
            return None

        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**kwargs, updated_at=datetime.now(timezone.utc))
        )
        await self.session.commit()

        # Invalidate cache
        if redis_client.is_enabled:
            cache_key = CacheKeys.user_profile(user.telegram_id)
            await redis_client.delete(cache_key)
            logger.debug("user_cache_invalidated", telegram_id=user.telegram_id)

        return await self.get_by_id(user_id)

    async def delete(self, user_id: int) -> bool:
        """
        Удалить пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если удален, False если не найден
        """
        result = await self.session.execute(
            delete(User).where(User.id == user_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_telegram_id_with_relations(
        self,
        telegram_id: int,
        include: list[str] | None = None,
    ) -> User | None:
        """
        Получить пользователя с связанными данными одним запросом (eager loading).

        Эта функция использует eager loading для получения пользователя
        и его связанных данных в одном SQL запросе, устраняя проблему N+1.

        Args:
            telegram_id: Telegram user ID
            include: Список связей для загрузки. Допустимые значения:
                - 'settings': Настройки пользователя
                - 'recent_messages': Последние 10 сообщений
                - 'daily_stats': Последние 30 дней статистики
                - 'saved_words': Сохраненные слова
                - 'stars': Звезды пользователя

        Returns:
            User | None: Пользователь со связанными данными или None

        Example:
            ```python
            # Загрузить пользователя с настройками и последними сообщениями
            user = await user_repo.get_by_telegram_id_with_relations(
                123456,
                include=['settings', 'recent_messages']
            )
            # Теперь user.settings и user.messages доступны без дополнительных запросов
            ```
        """
        query = select(User).where(User.telegram_id == telegram_id)

        if include:
            # Settings - используем joinedload так как это 1:1 связь
            if 'settings' in include:
                query = query.options(joinedload(User.settings))

            # Recent messages - используем selectinload и limit
            if 'recent_messages' in include:
                query = query.options(
                    selectinload(User.messages)
                    .options(selectinload(Message.user))
                    .limit(10)
                )

            # Daily stats - последние 30 дней
            if 'daily_stats' in include:
                query = query.options(
                    selectinload(User.daily_stats).limit(30)
                )

            # Saved words
            if 'saved_words' in include:
                query = query.options(
                    selectinload(User.saved_words)
                )

            # Stars - 1:1 связь
            if 'stars' in include:
                query = query.options(joinedload(User.stars))

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()


class UserSettingsRepository:
    """Repository для работы с настройками пользователей."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> UserSettings | None:
        """
        Получить настройки пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            UserSettings | None: Настройки или None
        """
        result = await self.session.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(self, user_id: int, **kwargs: Any) -> UserSettings | None:
        """
        Обновить настройки пользователя и инвалидировать кеш.

        Args:
            user_id: ID пользователя
            **kwargs: Обновляемые поля

        Returns:
            UserSettings | None: Обновленные настройки или None
        """
        await self.session.execute(
            update(UserSettings)
            .where(UserSettings.user_id == user_id)
            .values(**kwargs)
        )
        await self.session.commit()

        # Invalidate user cache (settings are part of user cache)
        if redis_client.is_enabled:
            from backend.models import User
            result = await self.session.execute(
                select(User.telegram_id).where(User.id == user_id)
            )
            telegram_id = result.scalar_one_or_none()
            if telegram_id:
                cache_key = CacheKeys.user_profile(telegram_id)
                await redis_client.delete(cache_key)
                logger.debug("user_settings_cache_invalidated", telegram_id=telegram_id)

        return await self.get_by_user_id(user_id)


class MessageRepository:
    """Repository для работы с сообщениями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs: Any) -> Message:
        """
        Создать сообщение.

        Args:
            **kwargs: Параметры сообщения

        Returns:
            Message: Созданное сообщение
        """
        message = Message(**kwargs)
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_user_messages(
        self,
        user_id: int,
        limit: int = 10,
    ) -> list[Message]:
        """
        Получить последние сообщения пользователя (user и assistant).

        Args:
            user_id: ID пользователя
            limit: Максимальное количество сообщений

        Returns:
            list[Message]: Сообщения, отсортированные от новых к старым
        """
        return await self.get_recent_by_user(user_id=user_id, limit=limit)

    async def get_recent_by_user(
        self,
        user_id: int,
        limit: int = 10
    ) -> list[Message]:
        """
        Получить последние сообщения пользователя.

        Args:
            user_id: ID пользователя
            limit: Количество сообщений

        Returns:
            list[Message]: Список сообщений
        """
        result = await self.session.execute(
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_messages_by_date(
        self,
        user_id: int,
        start_date: date,
        end_date: date | None = None
    ) -> list[Message]:
        """
        Получить сообщения пользователя за период.

        Args:
            user_id: ID пользователя
            start_date: Начальная дата
            end_date: Конечная дата (если None, то только start_date)

        Returns:
            list[Message]: Список сообщений
        """
        from sqlalchemy import func

        if end_date is None:
            end_date = start_date

        result = await self.session.execute(
            select(Message)
            .where(
                and_(
                    Message.user_id == user_id,
                    func.date(Message.created_at) >= start_date,
                    func.date(Message.created_at) <= end_date
                )
            )
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_recent_with_user(
        self,
        user_id: int,
        limit: int = 10
    ) -> list[Message]:
        """
        Получить последние сообщения с предзагруженными данными пользователя.

        Использует eager loading для устранения N+1 запросов.

        Args:
            user_id: ID пользователя
            limit: Количество сообщений

        Returns:
            list[Message]: Список сообщений с предзагруженным user
        """
        result = await self.session.execute(
            select(Message)
            .where(Message.user_id == user_id)
            .options(joinedload(Message.user))
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        return list(result.unique().scalars().all())


class SavedWordRepository:
    """Repository для работы с сохраненными словами."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs: Any) -> SavedWord:
        """
        Сохранить слово.

        Args:
            **kwargs: Параметры слова

        Returns:
            SavedWord: Сохраненное слово
        """
        word = SavedWord(**kwargs)
        self.session.add(word)
        await self.session.flush()
        await self.session.refresh(word)
        return word

    async def get_by_user(
        self,
        user_id: int,
        limit: int | None = None
    ) -> list[SavedWord]:
        """
        Получить сохраненные слова пользователя.

        Args:
            user_id: ID пользователя
            limit: Ограничение количества

        Returns:
            list[SavedWord]: Список слов
        """
        query = (
            select(SavedWord)
            .where(SavedWord.user_id == user_id)
            .order_by(SavedWord.created_at.desc())
        )

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete(self, word_id: int) -> bool:
        """
        Удалить сохраненное слово.

        Args:
            word_id: ID слова

        Returns:
            bool: True если удалено
        """
        result = await self.session.execute(
            delete(SavedWord).where(SavedWord.id == word_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_user_id(
        self,
        user_id: int,
        limit: int | None = None
    ) -> list[SavedWord]:
        """
        Alias для get_by_user чтобы сохранить обратную совместимость.

        Args:
            user_id: ID пользователя
            limit: Ограничение количества

        Returns:
            list[SavedWord]: Список слов
        """
        return await self.get_by_user(user_id=user_id, limit=limit)

    async def get_by_id(self, word_id: int) -> SavedWord | None:
        """
        Получить сохраненное слово по ID.

        Args:
            word_id: ID слова

        Returns:
            SavedWord | None: Найденное слово или None
        """
        result = await self.session.execute(
            select(SavedWord).where(SavedWord.id == word_id)
        )
        return result.scalar_one_or_none()

    async def increment_review(self, word_id: int) -> SavedWord | None:
        """
        Увеличить счетчик повторений и обновить дату последнего повторения.

        Args:
            word_id: ID слова

        Returns:
            SavedWord | None: Обновленное слово или None если не найдено
        """
        word = await self.get_by_id(word_id)
        if not word:
            return None

        word.times_reviewed = (word.times_reviewed or 0) + 1
        word.last_reviewed_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(word)

        return word


class StatsRepository:
    """Repository для работы со статистикой."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_daily(
        self,
        user_id: int,
        date_value: date
    ) -> DailyStats:
        """
        Получить или создать статистику за день.

        Args:
            user_id: ID пользователя
            date_value: Дата

        Returns:
            DailyStats: Статистика за день
        """
        result = await self.session.execute(
            select(DailyStats)
            .where(
                and_(
                    DailyStats.user_id == user_id,
                    DailyStats.date == date_value
                )
            )
        )
        stats = result.scalar_one_or_none()

        if stats is None:
            stats = DailyStats(user_id=user_id, date=date_value)
            self.session.add(stats)
            await self.session.flush()
            await self.session.refresh(stats)

        return stats

    async def update_daily(
        self,
        user_id: int,
        date_value: date,
        **kwargs: Any
    ) -> DailyStats:
        """
        Обновить статистику за день и инвалидировать кеш.

        Args:
            user_id: ID пользователя
            date_value: Дата
            **kwargs: Обновляемые поля

        Returns:
            DailyStats: Обновленная статистика
        """
        stats = await self.get_or_create_daily(user_id, date_value)

        for key, value in kwargs.items():
            setattr(stats, key, value)

        await self.session.flush()
        await self.session.refresh(stats)

        # Invalidate stats cache
        if redis_client.is_enabled:
            from backend.models import User
            result = await self.session.execute(
                select(User.telegram_id).where(User.id == user_id)
            )
            telegram_id = result.scalar_one_or_none()
            if telegram_id:
                cache_key = CacheKeys.daily_stats(telegram_id, str(date_value))
                await redis_client.delete(cache_key)
                logger.debug("stats_cache_invalidated", telegram_id=telegram_id)

        return stats

    async def get_user_stars(self, user_id: int) -> Stars | None:
        """
        Получить звезды пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Stars | None: Звезды или None
        """
        result = await self.session.execute(
            select(Stars).where(Stars.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_stars(
        self,
        user_id: int,
        total: int,
        available: int,
        lifetime: int
    ) -> Stars | None:
        """
        Обновить звезды пользователя.

        Args:
            user_id: ID пользователя
            total: Всего звезд
            available: Доступно
            lifetime: За все время

        Returns:
            Stars | None: Обновленные звезды
        """
        await self.session.execute(
            update(Stars)
            .where(Stars.user_id == user_id)
            .values(
                total=total,
                available=available,
                lifetime=lifetime,
                updated_at=datetime.now(timezone.utc)
            )
        )
        await self.session.commit()
        return await self.get_user_stars(user_id)

    async def get_daily_stats(
        self, user_id: int, date_value: date
    ) -> dict[str, Any] | None:
        """
        Получить статистику за конкретный день.

        Args:
            user_id: ID пользователя
            date_value: Дата

        Returns:
            dict | None: Словарь со статистикой или None
        """
        result = await self.session.execute(
            select(DailyStats).where(
                and_(
                    DailyStats.user_id == user_id,
                    DailyStats.date == date_value
                )
            )
        )
        stats = result.scalar_one_or_none()

        if stats is None:
            return None

        return {
            "messages_count": stats.messages_count,
            "words_said": stats.words_said,
            "correct_percent": stats.correct_percent,
            "streak_day": stats.streak_day,
        }

    async def get_user_summary(self, user_id: int) -> dict[str, Any]:
        """
        Получить общую статистику пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            dict: Словарь со статистикой
        """
        # Получаем все записи daily_stats для пользователя
        result = await self.session.execute(
            select(DailyStats)
            .where(DailyStats.user_id == user_id)
            .order_by(DailyStats.date.desc())
        )
        all_stats = list(result.scalars().all())

        if not all_stats:
            return {
                "total_messages": 0,
                "total_words": 0,
                "average_correctness": 0,
                "current_streak": 0,
                "max_streak": 0,
            }

        # Рассчитываем общую статистику
        total_messages = sum(s.messages_count for s in all_stats)
        total_words = sum(s.words_said for s in all_stats)

        # Средняя правильность (взвешенная по количеству слов)
        total_weighted = sum(
            s.correct_percent * s.words_said for s in all_stats if s.words_said > 0
        )
        average_correctness = (
            total_weighted / total_words if total_words > 0 else 0
        )

        # Текущий и максимальный streak
        current_streak = all_stats[0].streak_day if all_stats else 0
        max_streak = max((s.streak_day for s in all_stats), default=0)

        return {
            "total_messages": total_messages,
            "total_words": total_words,
            "average_correctness": round(average_correctness, 1),
            "current_streak": current_streak,
            "max_streak": max_streak,
        }

    async def update_user_stars(
        self,
        user_id: int,
        total: int | None = None,
        available: int | None = None,
        lifetime: int | None = None,
    ) -> None:
        """
        Обновить звезды пользователя (гибкая версия).

        Args:
            user_id: ID пользователя
            total: Всего звезд (если None, не обновляется)
            available: Доступно (если None, не обновляется)
            lifetime: За все время (если None, не обновляется)
        """
        values = {"updated_at": datetime.now(timezone.utc)}
        if total is not None:
            values["total"] = total
        if available is not None:
            values["available"] = available
        if lifetime is not None:
            values["lifetime"] = lifetime

        await self.session.execute(
            update(Stars).where(Stars.user_id == user_id).values(**values)
        )
        await self.session.flush()

    async def get_stats_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> list[dict[str, Any]]:
        """
        Получить статистику за период.

        Args:
            user_id: ID пользователя
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            list[dict]: Список статистики по дням
        """
        result = await self.session.execute(
            select(DailyStats)
            .where(
                and_(
                    DailyStats.user_id == user_id,
                    DailyStats.date >= start_date,
                    DailyStats.date <= end_date
                )
            )
            .order_by(DailyStats.date.asc())
        )
        stats_list = list(result.scalars().all())

        return [
            {
                "date": stats.date.isoformat(),
                "messages_count": stats.messages_count,
                "words_said": stats.words_said,
                "correct_percent": stats.correct_percent,
                "streak_day": stats.streak_day,
            }
            for stats in stats_list
        ]

    async def get_stats_range_with_user(
        self,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> list[DailyStats]:
        """
        Получить статистику за период с предзагруженными данными пользователя.

        Использует eager loading для устранения N+1 запросов.

        Args:
            user_id: ID пользователя
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            list[DailyStats]: Список статистики с предзагруженным user
        """
        result = await self.session.execute(
            select(DailyStats)
            .where(
                and_(
                    DailyStats.user_id == user_id,
                    DailyStats.date >= start_date,
                    DailyStats.date <= end_date
                )
            )
            .options(joinedload(DailyStats.user))
            .order_by(DailyStats.date.asc())
        )
        return list(result.unique().scalars().all())


class MaterializedViewRepository:
    """Repository для работы с материализованными представлениями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_stats_summary(
        self,
        telegram_id: int | None = None,
        limit: int | None = None,
        order_by: str = "total_messages"
    ) -> list[dict[str, Any]]:
        """
        Получить агрегированную статистику пользователей из материализованного представления.

        Это намного быстрее чем вычислять статистику на лету,
        так как данные предварительно агрегированы.

        Args:
            telegram_id: ID конкретного пользователя (опционально)
            limit: Ограничение количества результатов
            order_by: Поле для сортировки (total_messages, total_stars, max_streak)

        Returns:
            list[dict]: Список статистики пользователей
        """
        from sqlalchemy import text

        # Build query dynamically
        query_parts = ["SELECT * FROM user_stats_summary"]
        params = {}

        if telegram_id is not None:
            query_parts.append("WHERE telegram_id = :telegram_id")
            params["telegram_id"] = telegram_id

        # Order by
        valid_order_fields = [
            "total_messages", "total_stars", "max_streak",
            "avg_correctness", "last_activity", "total_words_said"
        ]
        if order_by in valid_order_fields:
            query_parts.append(f"ORDER BY {order_by} DESC")

        if limit is not None:
            query_parts.append("LIMIT :limit")
            params["limit"] = limit

        query = " ".join(query_parts)
        result = await self.session.execute(text(query), params)

        # Convert to list of dicts
        columns = result.keys()
        rows = result.fetchall()

        return [
            {col: val for col, val in zip(columns, row)}
            for row in rows
        ]

    async def get_leaderboard(
        self,
        metric: str = "total_stars",
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Получить таблицу лидеров по выбранной метрике.

        Args:
            metric: Метрика для рейтинга (total_stars, max_streak, total_messages)
            limit: Количество пользователей

        Returns:
            list[dict]: Топ пользователей
        """
        from sqlalchemy import text

        valid_metrics = ["total_stars", "max_streak", "total_messages", "avg_correctness"]
        if metric not in valid_metrics:
            metric = "total_stars"

        query = f"""
            SELECT
                telegram_id,
                first_name,
                username,
                level,
                {metric} as score,
                total_messages,
                total_stars,
                max_streak,
                avg_correctness
            FROM user_stats_summary
            WHERE {metric} > 0
            ORDER BY {metric} DESC
            LIMIT :limit
        """

        result = await self.session.execute(text(query), {"limit": limit})
        columns = result.keys()
        rows = result.fetchall()

        return [
            {col: val for col, val in zip(columns, row)}
            for row in rows
        ]

    async def get_active_users(
        self,
        days: int = 7,
        limit: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Получить активных пользователей за последние N дней.

        Args:
            days: Количество дней для проверки активности
            limit: Ограничение количества результатов

        Returns:
            list[dict]: Список активных пользователей
        """
        from sqlalchemy import text

        query = f"""
            SELECT
                telegram_id,
                first_name,
                username,
                level,
                total_messages,
                messages_last_{days}_days,
                avg_correctness,
                last_activity
            FROM user_stats_summary
            WHERE messages_last_{days}_days > 0
            ORDER BY messages_last_{days}_days DESC
        """

        if limit is not None:
            query += " LIMIT :limit"
            result = await self.session.execute(text(query), {"limit": limit})
        else:
            result = await self.session.execute(text(query))

        columns = result.keys()
        rows = result.fetchall()

        return [
            {col: val for col, val in zip(columns, row)}
            for row in rows
        ]


