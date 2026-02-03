"""
Challenge models.
Модели для системы ежедневных и еженедельных челленджей.
"""

from datetime import datetime, date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Date, DateTime, ForeignKey, Integer, String, Boolean, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.db.database import Base

if TYPE_CHECKING:
    from backend.models.user import User


class Challenge(Base):
    """
    Модель челленджа.

    Attributes:
        id: Primary key
        code: Уникальный код челленджа
        type: Тип (daily/weekly/special)
        title_cs: Название на чешском
        description_cs: Описание на чешском
        goal_type: Тип цели (messages, high_accuracy_messages, saved_words, topic_message, streak_days)
        goal_topic: Тема для topic_message
        goal_value: Целевое значение
        reward_stars: Награда в звездах
        is_active: Активен ли челлендж
    """

    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Unique challenge code"
    )

    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="daily/weekly/special"
    )

    title_cs: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Czech title"
    )

    description_cs: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Czech description"
    )

    goal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="messages/high_accuracy_messages/saved_words/topic_message/streak_days"
    )

    goal_topic: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Topic for topic_message goal type"
    )

    goal_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Target value"
    )

    reward_stars: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        comment="Stars reward"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Is challenge active"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Relationships
    user_challenges: Mapped[List["UserChallenge"]] = relationship(
        "UserChallenge",
        back_populates="challenge",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Challenge(code={self.code}, type={self.type})>"


class UserChallenge(Base):
    """
    Модель связи пользователя с челленджем.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        challenge_id: Foreign key to Challenge
        date: Дата челленджа (для daily/weekly)
        progress: Текущий прогресс
        completed: Завершён ли челлендж
        completed_at: Время завершения
        reward_claimed: Получена ли награда
    """

    __tablename__ = "user_challenges"

    __table_args__ = (
        UniqueConstraint('user_id', 'challenge_id', 'date', name='uq_user_challenge_date'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    challenge_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("challenges.id", ondelete="CASCADE"),
        nullable=False
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Challenge date (for daily/weekly)"
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Current progress towards challenge"
    )

    completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Challenge completed"
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Completion timestamp"
    )

    reward_claimed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Reward claimed"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="challenges")
    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="user_challenges")

    def __repr__(self) -> str:
        return f"<UserChallenge(user_id={self.user_id}, challenge_id={self.challenge_id}, date={self.date})>"


class TopicMessageCount(Base):
    """
    Модель счётчика сообщений по темам.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        topic: Тема (beer, food, history, travel, etc.)
        count: Количество сообщений по теме
    """

    __tablename__ = "topic_message_counts"

    __table_args__ = (
        UniqueConstraint('user_id', 'topic', name='uq_user_topic'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    topic: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Topic: beer, food, history, travel, etc."
    )

    count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of messages on this topic"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="topic_counts")

    def __repr__(self) -> str:
        return f"<TopicMessageCount(user_id={self.user_id}, topic={self.topic}, count={self.count})>"
