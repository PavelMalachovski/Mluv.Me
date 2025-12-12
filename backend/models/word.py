"""
SavedWord model.
Хранит сохраненные пользователем слова для повторения.
"""

from datetime import datetime, date
from typing import TYPE_CHECKING, List, Optional
import json

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Float, Date, Index
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

        # Spaced Repetition (SM-2) fields
        ease_factor: Фактор легкости (2.5 по умолчанию)
        interval_days: Интервал до следующего повторения в днях
        next_review_date: Дата следующего повторения
        sr_review_count: Количество SR-повторений
        quality_history: История оценок качества (JSON)
    """

    __tablename__ = "saved_words"

    # Performance: Composite index for efficient word lookup by user
    __table_args__ = (
        Index('idx_saved_words_user_word', 'user_id', 'word_czech'),
    )

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

    # Spaced Repetition (SM-2) fields
    ease_factor: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=2.5,
        comment="SM-2 ease factor"
    )

    interval_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Days until next review"
    )

    next_review_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="Next review date"
    )

    sr_review_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="SR review count"
    )

    quality_history: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Quality history JSON"
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="saved_words")

    def __repr__(self) -> str:
        return (
            f"<SavedWord(id={self.id}, user_id={self.user_id}, "
            f"word={self.word_czech}, translation={self.translation})>"
        )

    def get_quality_history(self) -> List[int]:
        """Get quality history as list."""
        if self.quality_history:
            try:
                return json.loads(self.quality_history)
            except json.JSONDecodeError:
                return []
        return []

    def add_quality_rating(self, quality: int) -> None:
        """Add quality rating to history (keep last 5)."""
        history = self.get_quality_history()
        history.append(quality)
        self.quality_history = json.dumps(history[-5:])

    @property
    def is_due_for_review(self) -> bool:
        """Check if word is due for review."""
        if self.next_review_date is None:
            return True
        return date.today() >= self.next_review_date

    @property
    def mastery_level(self) -> str:
        """Calculate mastery level based on SR data."""
        if self.sr_review_count == 0:
            return "new"
        elif self.interval_days < 7:
            return "learning"
        elif self.interval_days < 30:
            return "familiar"
        elif self.interval_days < 90:
            return "known"
        else:
            return "mastered"


