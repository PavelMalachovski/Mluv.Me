"""
Grammar Rule models.
Модели для хранения грамматических правил из příručky ÚJČ
и отслеживания прогресса пользователей.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    DateTime, ForeignKey, Integer, String, Boolean, Text,
    UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.db.database import Base

if TYPE_CHECKING:
    from backend.models.user import User


class GrammarRule(Base):
    """
    Грамматическое правило из Internetové jazykové příručky.

    Контент переработан и адаптирован для изучающих чешский (A1–B2).
    Все тексты на чешском языке (Czech immersion).

    Attributes:
        id: Primary key
        code: Уникальный slug (vyjmenovana_slova_b, velka_pismena_obecne)
        category: Грамматическая категория
        subcategory: Подкатегория (nullable)
        level: Уровень сложности (A1/A2/B1/B2)
        title_cs: Заголовок правила на чешском
        rule_cs: Правило на чешском (упрощённое)
        explanation_cs: Подробное пояснение на чешском
        examples: JSON массив примеров
        mnemonic: Мнемоническое правило
        common_mistakes: JSON массив частых ошибок
        exercise_data: JSON массив упражнений для игр
        source_ref: Ссылка на оригинал в příručce
        is_active: Активно ли правило
        sort_order: Порядок внутри категории
    """

    __tablename__ = "grammar_rules"

    __table_args__ = (
        Index("ix_grammar_rules_category_level", "category", "level"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Unique rule slug, e.g. vyjmenovana_slova_b"
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="vyslovnost, pravopis_hlasky, pravopis_interpunkce, pravopis_velka_pismena, "
                "morfematika, slovotvorba, tvaroslovi_podstatna, tvaroslovi_pridavna, "
                "tvaroslovi_zajmena, tvaroslovi_slovesa, tvaroslovi_cislovky, skladba, stylistika"
    )

    subcategory: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Subcategory within the main category"
    )

    level: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        comment="CEFR level: A1, A2, B1, B2"
    )

    title_cs: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        comment="Rule title in Czech"
    )

    rule_cs: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Rule explanation in Czech (simplified for learners)"
    )

    explanation_cs: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Detailed explanation in Czech"
    )

    examples: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
        comment='JSON: [{"correct": "...", "incorrect": "...", "note_cs": "..."}]'
    )

    mnemonic: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Mnemonic tip in Czech"
    )

    common_mistakes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment='JSON: [{"wrong": "...", "right": "...", "why_cs": "..."}]'
    )

    exercise_data: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
        comment='JSON: [{"type": "fill_gap|choose|transform|order", '
                '"question": "...", "answer": "...", "options": [...]}]'
    )

    source_ref: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Reference to original příručka article, e.g. prirucka.ujc.cas.cz/?id=100"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        comment="Is the rule active"
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Sort order within category"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now()
    )

    # Relationships
    user_progress: Mapped[List["UserGrammarProgress"]] = relationship(
        "UserGrammarProgress",
        back_populates="grammar_rule",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<GrammarRule(code={self.code}, category={self.category}, level={self.level})>"


class UserGrammarProgress(Base):
    """
    Прогресс пользователя по грамматическому правилу.

    Отслеживает: сколько раз показано в уведомлениях,
    сколько раз тренировано в играх, правильные/неправильные ответы.

    Attributes:
        id: Primary key
        user_id: FK → users.id
        grammar_rule_id: FK → grammar_rules.id
        times_shown: Сколько раз показано в нотификациях
        times_practiced: Сколько раз тренировано в играх
        last_shown_at: Последний показ в уведомлении
        last_practiced_at: Последняя тренировка
        mastery_level: Уровень владения (new → mastered)
        correct_count: Правильных ответов
        incorrect_count: Неправильных ответов
    """

    __tablename__ = "user_grammar_progress"

    __table_args__ = (
        UniqueConstraint(
            "user_id", "grammar_rule_id",
            name="uq_user_grammar_rule"
        ),
        Index("ix_user_grammar_progress_user_rule", "user_id", "grammar_rule_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID"
    )

    grammar_rule_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("grammar_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Grammar rule ID"
    )

    times_shown: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Times shown in notifications"
    )

    times_practiced: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Times practiced in games"
    )

    last_shown_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last notification show"
    )

    last_practiced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last game practice"
    )

    mastery_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="new",
        comment="new, seen, practiced, known, mastered"
    )

    correct_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Correct answers count"
    )

    incorrect_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Incorrect answers count"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="grammar_progress")
    grammar_rule: Mapped["GrammarRule"] = relationship("GrammarRule", back_populates="user_progress")

    def __repr__(self) -> str:
        return (
            f"<UserGrammarProgress(user_id={self.user_id}, "
            f"rule_id={self.grammar_rule_id}, mastery={self.mastery_level})>"
        )

    @property
    def accuracy(self) -> float:
        """Процент правильных ответов."""
        total = self.correct_count + self.incorrect_count
        if total == 0:
            return 0.0
        return round(self.correct_count / total * 100, 1)
