"""
Message model.
Хранит сообщения пользователей и ответы Хонзика.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.db.database import Base

if TYPE_CHECKING:
    from backend.models.user import User


class Message(Base):
    """
    Модель сообщения (пользователя или Хонзика).

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        role: Роль отправителя (user или assistant)
        text: Текст сообщения
        transcript_raw: Оригинальная транскрипция STT
        transcript_normalized: Нормализованный текст
        audio_file_path: Путь к аудио файлу
        correctness_score: Оценка правильности (0-100)
        words_total: Количество слов
        words_correct: Правильных слов
        created_at: Дата создания
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID"
    )

    role: Mapped[str] = mapped_column(
        Enum("user", "assistant", name="message_role_enum"),
        nullable=False,
        comment="Роль отправителя (user или assistant/Honzík)"
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Текст сообщения"
    )

    transcript_raw: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Оригинальная транскрипция STT"
    )

    transcript_normalized: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Нормализованный/исправленный текст"
    )

    audio_file_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Путь к аудио файлу"
    )

    correctness_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Оценка правильности (0-100)"
    )

    words_total: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        comment="Количество слов"
    )

    words_correct: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        comment="Правильных слов"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Дата создания"
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="messages")

    def __repr__(self) -> str:
        return (
            f"<Message(id={self.id}, user_id={self.user_id}, "
            f"role={self.role}, score={self.correctness_score})>"
        )


