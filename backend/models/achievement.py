"""
Achievement models.
Модели для системы достижений и геймификации.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.db.database import Base

if TYPE_CHECKING:
    from backend.models.user import User


class Achievement(Base):
    """
    Модель достижения.

    Attributes:
        id: Primary key
        code: Уникальный код достижения
        name: Название достижения
        description: Описание достижения
        icon: Эмодзи иконка
        category: Категория (streak, messages, vocabulary, accuracy, stars, review)
        threshold: Порог для получения
        stars_reward: Награда в звездах
        is_hidden: Скрыто до получения
    """

    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Unique achievement code"
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Display name"
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Achievement description"
    )

    icon: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Emoji icon"
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Category: streak, messages, vocabulary, accuracy, stars, review"
    )

    threshold: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Value needed to unlock"
    )

    stars_reward: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Stars awarded"
    )

    is_hidden: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Hidden until unlocked"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Relationships
    user_achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement",
        back_populates="achievement",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Achievement(code={self.code}, name={self.name})>"


class UserAchievement(Base):
    """
    Модель связи пользователя с достижением.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        achievement_id: Foreign key to Achievement
        unlocked_at: Дата получения
        progress: Текущий прогресс
    """

    __tablename__ = "user_achievements"

    __table_args__ = (
        UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    achievement_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False
    )

    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Current progress towards achievement"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")

    def __repr__(self) -> str:
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"
