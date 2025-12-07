"""
Stats models (DailyStats and Stars).
Хранит статистику пользователей и звезды для геймификации.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.db.database import Base

if TYPE_CHECKING:
    from backend.models.user import User


class DailyStats(Base):
    """
    Модель ежедневной статистики пользователя.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        date: Дата
        messages_count: Количество сообщений
        words_said: Слов сказано
        correct_percent: Процент правильных
        streak_day: День streak подряд
        created_at: Дата создания записи
    """

    __tablename__ = "daily_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID"
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Дата статистики"
    )

    messages_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Количество сообщений за день"
    )

    words_said: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Слов сказано за день"
    )

    correct_percent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Средний процент правильных за день"
    )

    streak_day: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="День streak подряд"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Дата создания записи"
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="daily_stats")

    def __repr__(self) -> str:
        return (
            f"<DailyStats(id={self.id}, user_id={self.user_id}, "
            f"date={self.date}, streak={self.streak_day})>"
        )


class Stars(Base):
    """
    Модель звезд пользователя для геймификации.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        total: Всего заработано звезд
        available: Доступно для обмена
        lifetime: За все время (не может уменьшаться)
        updated_at: Дата последнего обновления
    """

    __tablename__ = "stars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="User ID"
    )

    total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Всего заработано звезд (текущий баланс)"
    )

    available: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Доступно для обмена"
    )

    lifetime: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="За все время (не может уменьшаться)"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата последнего обновления"
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="stars")

    def __repr__(self) -> str:
        return (
            f"<Stars(id={self.id}, user_id={self.user_id}, "
            f"total={self.total}, lifetime={self.lifetime})>"
        )



