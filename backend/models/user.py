"""
User and UserSettings models.
Хранит информацию о пользователях и их настройках.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.db.database import Base

if TYPE_CHECKING:
    from backend.models.message import Message
    from backend.models.word import SavedWord
    from backend.models.stats import DailyStats, Stars
    from backend.models.achievement import UserAchievement


class User(Base):
    """
    Модель пользователя Telegram бота.

    Attributes:
        id: Primary key
        telegram_id: Telegram user ID (unique)
        username: Telegram username
        first_name: Имя пользователя
        ui_language: Язык интерфейса (ru, uk)
        level: Уровень чешского языка
        created_at: Дата регистрации
        updated_at: Дата последнего обновления
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
        comment="Telegram user ID"
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Telegram username"
    )

    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Имя пользователя"
    )

    ui_language: Mapped[str] = mapped_column(
        Enum("ru", "uk", name="ui_language_enum"),
        nullable=False,
        default="ru",
        comment="Язык интерфейса (русский или украинский)"
    )

    level: Mapped[str] = mapped_column(
        Enum("beginner", "intermediate", "advanced", "native", name="level_enum"),
        nullable=False,
        default="beginner",
        comment="Уровень чешского языка"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Дата регистрации"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата последнего обновления"
    )

    # Relationships
    settings: Mapped["UserSettings"] = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    saved_words: Mapped[list["SavedWord"]] = relationship(
        "SavedWord",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    daily_stats: Mapped[list["DailyStats"]] = relationship(
        "DailyStats",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    stars: Mapped["Stars"] = relationship(
        "Stars",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert user to dictionary for caching."""
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "ui_language": self.ui_language,
            "level": self.level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"


class UserSettings(Base):
    """
    Настройки пользователя.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        conversation_style: Стиль общения Хонзика
        voice_speed: Скорость голоса Хонзика
        corrections_level: Уровень исправлений
        timezone: Timezone пользователя
        notifications_enabled: Включены ли уведомления
    """

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="User ID"
    )

    conversation_style: Mapped[str] = mapped_column(
        Enum("friendly", "tutor", "casual", name="conversation_style_enum"),
        nullable=False,
        default="friendly",
        comment="Стиль общения Хонзика"
    )

    voice_speed: Mapped[str] = mapped_column(
        Enum("very_slow", "slow", "normal", "native", name="voice_speed_enum"),
        nullable=False,
        default="normal",
        comment="Скорость голоса Хонзика"
    )

    corrections_level: Mapped[str] = mapped_column(
        Enum("minimal", "balanced", "detailed", name="corrections_level_enum"),
        nullable=False,
        default="balanced",
        comment="Уровень исправлений"
    )

    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Europe/Prague",
        comment="Timezone пользователя"
    )

    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Включены ли уведомления"
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="settings")

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to dictionary for caching."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "conversation_style": self.conversation_style,
            "voice_speed": self.voice_speed,
            "corrections_level": self.corrections_level,
            "timezone": self.timezone,
            "notifications_enabled": self.notifications_enabled,
        }

    def __repr__(self) -> str:
        return (
            f"<UserSettings(user_id={self.user_id}, "
            f"style={self.conversation_style}, "
            f"corrections={self.corrections_level})>"
        )


