"""
Repository pattern для работы с базой данных.
Абстрагирует SQL запросы от бизнес-логики.
"""

from datetime import date, datetime
from typing import Any

from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models import (
    User,
    UserSettings,
    Message,
    SavedWord,
    DailyStats,
    Stars,
)


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

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """
        Получить пользователя по Telegram ID.

        Args:
            telegram_id: Telegram user ID

        Returns:
            User | None: Пользователь или None
        """
        result = await self.session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.settings))
        )
        return result.scalar_one_or_none()

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
        Обновить пользователя.

        Args:
            user_id: ID пользователя
            **kwargs: Обновляемые поля

        Returns:
            User | None: Обновленный пользователь или None
        """
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**kwargs, updated_at=datetime.utcnow())
        )
        await self.session.commit()
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
        Обновить настройки пользователя.

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
        Обновить статистику за день.

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
                updated_at=datetime.utcnow()
            )
        )
        await self.session.commit()
        return await self.get_user_stars(user_id)


