"""
Repository for grammar rules and user grammar progress.
Abstrahuje SQL dotazy pro gramatická pravidla.
"""

import json
import random
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update, func, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from backend.models.grammar import GrammarRule, UserGrammarProgress

logger = structlog.get_logger(__name__)


class GrammarRepository:
    """Repository pro práci s gramatickými pravidly."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ─── Rule queries ──────────────────────────────────────────────

    async def get_rule_by_id(self, rule_id: int) -> GrammarRule | None:
        """Получить правило по ID."""
        result = await self.session.execute(
            select(GrammarRule).where(GrammarRule.id == rule_id)
        )
        return result.scalar_one_or_none()

    async def get_rule_by_code(self, code: str) -> GrammarRule | None:
        """Получить правило по уникальному коду."""
        result = await self.session.execute(
            select(GrammarRule).where(GrammarRule.code == code)
        )
        return result.scalar_one_or_none()

    async def get_rules_by_category(
        self,
        category: str | None = None,
        level: str | None = None,
        active_only: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> list[GrammarRule]:
        """
        Получить правила по категории.

        Args:
            category: Грамматическая категория (None = все)
            level: CEFR уровень (A1, A2, B1, B2) — optional фильтр
            active_only: Только активные правила
            limit: Макс. количество записей
            offset: Смещение для пагинации

        Returns:
            list[GrammarRule]: Список правил, отсортированных по sort_order
        """
        query = select(GrammarRule)

        if category:
            query = query.where(GrammarRule.category == category)
        if level:
            query = query.where(GrammarRule.level == level)
        if active_only:
            query = query.where(GrammarRule.is_active.is_(True))

        query = query.order_by(GrammarRule.sort_order, GrammarRule.id)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_all_categories(self) -> list[dict[str, Any]]:
        """
        Получить список всех категорий с количеством правил.

        Returns:
            list[dict]: [{"category": "...", "count": N, "levels": ["A1", ...]}]
        """
        query = (
            select(
                GrammarRule.category,
                func.count(GrammarRule.id).label("count"),
                func.array_agg(func.distinct(GrammarRule.level)).label("levels"),
            )
            .where(GrammarRule.is_active.is_(True))
            .group_by(GrammarRule.category)
            .order_by(GrammarRule.category)
        )
        result = await self.session.execute(query)
        rows = result.all()
        return [
            {"category": row.category, "count": row.count, "levels": sorted(row.levels)}
            for row in rows
        ]

    async def get_random_rule(
        self,
        level: str | None = None,
        exclude_ids: list[int] | None = None,
    ) -> GrammarRule | None:
        """
        Получить случайное активное правило.

        Args:
            level: Фильтр по уровню
            exclude_ids: ID правил для исключения

        Returns:
            GrammarRule | None
        """
        query = select(GrammarRule).where(GrammarRule.is_active.is_(True))

        if level:
            query = query.where(GrammarRule.level == level)
        if exclude_ids:
            query = query.where(not_(GrammarRule.id.in_(exclude_ids)))

        query = query.order_by(func.random()).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_rules_for_game(
        self,
        category: str | None = None,
        level: str | None = None,
        exercise_type: str | None = None,
        limit: int = 10,
    ) -> list[GrammarRule]:
        """
        Получить правила с exercise_data для игр.

        Args:
            category: Фильтр по категории
            level: Фильтр по уровню
            exercise_type: Фильтр по типу упражнения (fill_gap, choose, transform, order)
            limit: Максимум правил

        Returns:
            list[GrammarRule]: Правила с непустым exercise_data
        """
        query = (
            select(GrammarRule)
            .where(
                GrammarRule.is_active.is_(True),
                GrammarRule.exercise_data != "[]",
            )
        )

        if category:
            query = query.where(GrammarRule.category == category)
        if level:
            query = query.where(GrammarRule.level == level)
        if exercise_type:
            # Filter rules that contain the specific exercise type in JSON
            query = query.where(
                GrammarRule.exercise_data.contains(f'"type": "{exercise_type}"')
            )

        query = query.order_by(func.random()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_rules(
        self,
        category: str | None = None,
        level: str | None = None,
    ) -> int:
        """Подсчитать количество активных правил."""
        query = select(func.count(GrammarRule.id)).where(GrammarRule.is_active.is_(True))

        if category:
            query = query.where(GrammarRule.category == category)
        if level:
            query = query.where(GrammarRule.level == level)

        result = await self.session.execute(query)
        return result.scalar() or 0

    # ─── User progress queries ─────────────────────────────────────

    async def get_user_progress(
        self,
        user_id: int,
        rule_id: int | None = None,
    ) -> list[UserGrammarProgress] | UserGrammarProgress | None:
        """
        Получить прогресс пользователя.

        Args:
            user_id: ID пользователя
            rule_id: ID правила (если None — все правила)

        Returns:
            Список прогрессов или один прогресс
        """
        if rule_id is not None:
            result = await self.session.execute(
                select(UserGrammarProgress).where(
                    UserGrammarProgress.user_id == user_id,
                    UserGrammarProgress.grammar_rule_id == rule_id,
                )
            )
            return result.scalar_one_or_none()

        result = await self.session.execute(
            select(UserGrammarProgress).where(
                UserGrammarProgress.user_id == user_id
            )
        )
        return list(result.scalars().all())

    async def get_or_create_progress(
        self,
        user_id: int,
        rule_id: int,
    ) -> UserGrammarProgress:
        """Получить или создать запись прогресса."""
        progress = await self.get_user_progress(user_id, rule_id)
        if progress is None:
            progress = UserGrammarProgress(
                user_id=user_id,
                grammar_rule_id=rule_id,
                mastery_level="new",
            )
            self.session.add(progress)
            await self.session.flush()
        return progress

    async def update_progress_shown(
        self,
        user_id: int,
        rule_id: int,
    ) -> UserGrammarProgress:
        """Обновить прогресс: правило показано в уведомлении."""
        progress = await self.get_or_create_progress(user_id, rule_id)
        progress.times_shown += 1
        progress.last_shown_at = datetime.now(timezone.utc)

        if progress.mastery_level == "new":
            progress.mastery_level = "seen"

        await self.session.flush()
        return progress

    async def update_progress_practiced(
        self,
        user_id: int,
        rule_id: int,
        correct: bool,
    ) -> UserGrammarProgress:
        """
        Обновить прогресс: правило тренировано в игре.

        Args:
            user_id: ID пользователя
            rule_id: ID правила
            correct: Правильный ли был ответ
        """
        progress = await self.get_or_create_progress(user_id, rule_id)
        progress.times_practiced += 1
        progress.last_practiced_at = datetime.now(timezone.utc)

        if correct:
            progress.correct_count += 1
        else:
            progress.incorrect_count += 1

        # Update mastery level based on practice results
        total = progress.correct_count + progress.incorrect_count
        accuracy = progress.correct_count / total if total > 0 else 0

        if total >= 10 and accuracy >= 0.9:
            progress.mastery_level = "mastered"
        elif total >= 5 and accuracy >= 0.8:
            progress.mastery_level = "known"
        elif total >= 3:
            progress.mastery_level = "practiced"
        elif progress.mastery_level == "new":
            progress.mastery_level = "seen"

        await self.session.flush()
        return progress

    async def get_unseen_rules(
        self,
        user_id: int,
        level: str | None = None,
        limit: int = 5,
    ) -> list[GrammarRule]:
        """
        Получить правила, которые пользователь ещё не видел.

        Приоритет для уведомлений — показать новое.
        """
        # Get IDs of rules user has already seen
        seen_query = (
            select(UserGrammarProgress.grammar_rule_id)
            .where(UserGrammarProgress.user_id == user_id)
        )
        seen_result = await self.session.execute(seen_query)
        seen_ids = [row[0] for row in seen_result.all()]

        # Get unseen rules
        query = select(GrammarRule).where(GrammarRule.is_active.is_(True))
        
        if seen_ids:
            query = query.where(not_(GrammarRule.id.in_(seen_ids)))

        if level:
            query = query.where(GrammarRule.level == level)

        query = query.order_by(GrammarRule.sort_order, GrammarRule.id).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_weak_rules(
        self,
        user_id: int,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Получить правила с высоким процентом ошибок.

        Returns:
            list[dict]: [{"rule": GrammarRule, "accuracy": float, "total": int}]
        """
        # Get progress records with errors
        query = (
            select(UserGrammarProgress)
            .where(
                UserGrammarProgress.user_id == user_id,
                (UserGrammarProgress.correct_count + UserGrammarProgress.incorrect_count) >= 2,
                UserGrammarProgress.mastery_level.notin_(["mastered"]),
            )
            .order_by(
                # Sort by accuracy ascending (worst first)
                (
                    UserGrammarProgress.correct_count * 1.0
                    / (UserGrammarProgress.correct_count + UserGrammarProgress.incorrect_count)
                ).asc()
            )
            .limit(limit)
        )
        result = await self.session.execute(query)
        progress_list = list(result.scalars().all())

        # Load associated rules
        weak_rules = []
        for progress in progress_list:
            rule = await self.get_rule_by_id(progress.grammar_rule_id)
            if rule:
                total = progress.correct_count + progress.incorrect_count
                accuracy = progress.correct_count / total if total > 0 else 0
                weak_rules.append({
                    "rule": rule,
                    "accuracy": round(accuracy * 100, 1),
                    "total": total,
                    "progress": progress,
                })

        return weak_rules

    async def get_user_grammar_summary(
        self,
        user_id: int,
    ) -> dict[str, Any]:
        """
        Получить сводку прогресса пользователя по грамматике.

        Returns:
            dict с total_rules, seen, practiced, known, mastered, avg_accuracy
        """
        total_rules = await self.count_rules()

        # Count by mastery level
        query = (
            select(
                UserGrammarProgress.mastery_level,
                func.count(UserGrammarProgress.id).label("count"),
            )
            .where(UserGrammarProgress.user_id == user_id)
            .group_by(UserGrammarProgress.mastery_level)
        )
        result = await self.session.execute(query)
        levels = {row.mastery_level: row.count for row in result.all()}

        # Calculate average accuracy
        acc_query = (
            select(
                func.sum(UserGrammarProgress.correct_count).label("correct"),
                func.sum(UserGrammarProgress.incorrect_count).label("incorrect"),
            )
            .where(UserGrammarProgress.user_id == user_id)
        )
        acc_result = await self.session.execute(acc_query)
        acc_row = acc_result.one()
        correct = acc_row.correct or 0
        incorrect = acc_row.incorrect or 0
        total_answers = correct + incorrect

        return {
            "total_rules": total_rules,
            "practiced_rules": sum(levels.values()),
            "mastered_rules": levels.get("mastered", 0) + levels.get("known", 0),
            "weak_rules": levels.get("seen", 0) + levels.get("practiced", 0),
            "average_accuracy": round(correct / total_answers * 100, 1) if total_answers > 0 else 0,
        }
