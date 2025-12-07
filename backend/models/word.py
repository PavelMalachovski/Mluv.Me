"""
SavedWord model.
Хранит сохраненные пользователем слова для повторения.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.db.database import Base

if TYPE_CHECKING:
    from backend.models.user import User


class SavedWord(Base):
    """
    Модель сохраненного слова.

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        word_czech: Чешское слово
        translation: Перевод на родной язык
        context_sentence: Предложение-контекст
        phonetics: Фонетическая транскрипция
        times_reviewed: Сколько раз повторялось
        created_at: Дата добавления
        last_reviewed_at: Дата последнего повторения
    """

    __tablename__ = "saved_words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID"
    )

    word_czech: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Чешское слово"
    )

    translation: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Перевод на родной язык"
    )

    context_sentence: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Предложение-контекст"
    )

    phonetics: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Фонетическая транскрипция"
    )

    times_reviewed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Сколько раз повторялось"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Дата добавления"
    )

    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата последнего повторения"
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="saved_words")

    def __repr__(self) -> str:
        return (
            f"<SavedWord(id={self.id}, user_id={self.user_id}, "
            f"word={self.word_czech}, translation={self.translation})>"
        )



