"""
Grammar Service for Czech grammar rules from příručka ÚJČ.

Provides:
- Daily grammar rule selection for notifications
- Notification message formatting (Czech only)
- Exercise retrieval for grammar games
- Answer checking and progress tracking
"""

import json
import random
from datetime import datetime
from typing import Any

import structlog

from backend.db.grammar_repository import GrammarRepository
from backend.db.repositories import UserRepository, StatsRepository

logger = structlog.get_logger(__name__)

# Mapping user levels to CEFR levels for rule selection
LEVEL_TO_CEFR = {
    "beginner": ["A1"],
    "intermediate": ["A1", "A2"],
    "advanced": ["A1", "A2", "B1"],
    "native": ["A1", "A2", "B1", "B2"],
}

# Motivational phrases in Czech (rotated daily)
MOTIVATIONAL_PHRASES = [
    "Pojď si procvičit češtinu! 🇨🇿",
    "Každý den trochu lepší! 💪",
    "Honzík na tebe čeká! 🎓",
    "Praxí k dokonalosti! ✨",
    "Dnes je skvělý den na učení! 📚",
    "Malý krok každý den = velký pokrok! 🚀",
    "Nevzdávej se, jde ti to skvěle! 🌟",
    "Čeština je krásný jazyk! ❤️",
    "Zkus to dnes, bude to stát za to! 🎯",
    "Tvůj streak je důležitý! 🔥",
]


class GrammarService:
    """
    Servis pro gramatická pravidla.

    Manages rule selection, notification formatting,
    game exercises, and progress tracking.
    """

    def __init__(
        self,
        grammar_repo: GrammarRepository,
        user_repo: UserRepository | None = None,
        stats_repo: StatsRepository | None = None,
    ):
        self.grammar_repo = grammar_repo
        self.user_repo = user_repo
        self.stats_repo = stats_repo
        self.logger = logger.bind(service="grammar_service")

    async def get_daily_rule(self, user_id: int) -> dict[str, Any] | None:
        """
        Выбрать правило дня для пользователя.

        Приоритет:
        1. Непросмотренные правила подходящего уровня
        2. Слабые правила (высокий % ошибок)
        3. Случайное правило

        Args:
            user_id: ID пользователя

        Returns:
            dict с данными правила или None
        """
        # Determine user level and applicable CEFR levels
        user = None
        cefr_levels = ["A1", "A2"]  # default

        if self.user_repo:
            user = await self.user_repo.get_by_id(user_id)
            if user:
                cefr_levels = LEVEL_TO_CEFR.get(user.level, ["A1", "A2"])

        # Priority 1: Unseen rules
        for level in reversed(cefr_levels):  # Start from highest applicable level
            unseen = await self.grammar_repo.get_unseen_rules(
                user_id, level=level, limit=1
            )
            if unseen:
                return self._rule_to_dict(unseen[0])

        # Priority 2: Weak rules (high error rate)
        weak = await self.grammar_repo.get_weak_rules(user_id, limit=1)
        if weak:
            return self._rule_to_dict(weak[0]["rule"])

        # Priority 3: Random rule matching user level
        random_level = random.choice(cefr_levels)
        rule = await self.grammar_repo.get_random_rule(level=random_level)
        if rule:
            return self._rule_to_dict(rule)

        # Fallback: any random rule
        rule = await self.grammar_repo.get_random_rule()
        return self._rule_to_dict(rule) if rule else None

    async def get_notification_message(
        self,
        user_id: int,
        streak: int = 0,
        stars: int = 0,
    ) -> dict[str, Any] | None:
        """
        Сгенерировать текст вечернего уведомления с правилом.

        Всё на чешском языке.

        Args:
            user_id: ID пользователя
            streak: Текущий streak
            stars: Текущие звёзды

        Returns:
            dict: {"message": str, "rule_id": int} или None
        """
        rule_data = await self.get_daily_rule(user_id)
        if not rule_data:
            return None

        # Parse examples
        examples = rule_data.get("examples", [])
        correct_example = ""
        incorrect_example = ""

        if examples:
            ex = examples[0]
            correct_example = ex.get("correct", "")
            incorrect_example = ex.get("incorrect", "")

        # Build message
        parts = [
            "👋 Čau! Tady Honzík.",
            "Čas na trochu češtiny! 🇨🇿",
            "",
            f"📖 <b>Pravidlo dne:</b> {rule_data['title_cs']}",
            "",
            rule_data["rule_cs"],
        ]

        if correct_example:
            parts.append("")
            parts.append(f"✅ Správně: {correct_example}")
        if incorrect_example:
            parts.append(f"❌ Chyba: {incorrect_example}")

        # Add mnemonic if available
        mnemonic = rule_data.get("mnemonic")
        if mnemonic:
            parts.append("")
            parts.append(f"💡 {mnemonic}")

        # Add streak/stars and motivation
        parts.append("")

        stats_line = []
        if streak > 0:
            stats_line.append(f"🔥 Streak: {streak} dní")
        if stars > 0:
            stats_line.append(f"⭐ {stars}")

        if stats_line:
            parts.append(" | ".join(stats_line))

        # Motivational phrase
        phrase = random.choice(MOTIVATIONAL_PHRASES)
        parts.append(phrase)

        message = "\n".join(parts)

        # Mark rule as shown
        await self.grammar_repo.update_progress_shown(user_id, rule_data["id"])

        return {
            "message": message,
            "rule_id": rule_data["id"],
            "rule_code": rule_data["code"],
        }

    async def get_game_exercises(
        self,
        exercise_type: str,
        level: str | None = None,
        category: str | None = None,
        count: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Получить упражнения для мини-игр из exercise_data правил.

        Args:
            exercise_type: Тип упражнения (fill_gap, choose, transform, order)
            level: CEFR уровень
            category: Грамматическая категория
            count: Количество упражнений

        Returns:
            list[dict]: Список упражнений с rule_id
        """
        rules = await self.grammar_repo.get_rules_for_game(
            category=category,
            level=level,
            exercise_type=exercise_type,
            limit=count * 3,  # Fetch more rules to get enough exercises
        )

        exercises = []
        for rule in rules:
            try:
                rule_exercises = json.loads(rule.exercise_data)
            except (json.JSONDecodeError, TypeError):
                continue

            for ex in rule_exercises:
                if ex.get("type") == exercise_type:
                    exercises.append({
                        "rule_id": rule.id,
                        "rule_code": rule.code,
                        "category": rule.category,
                        "level": rule.level,
                        **ex,
                    })

        # Shuffle and limit
        random.shuffle(exercises)
        return exercises[:count]

    def check_exercise_answer(
        self,
        exercise: dict[str, Any],
        user_answer: str,
    ) -> dict[str, Any]:
        """
        Проверить ответ пользователя на упражнение.

        Args:
            exercise: Данные упражнения (from get_game_exercises)
            user_answer: Ответ пользователя

        Returns:
            dict: {"is_correct": bool, "correct_answer": str, "explanation": str}
        """
        correct = exercise.get("answer", "").strip()
        user = user_answer.strip()
        exercise_type = exercise.get("type", "")

        # Normalize for comparison
        user_norm = user.lower()
        correct_norm = correct.lower()

        is_correct = False

        if exercise_type == "choose":
            # Exact match (case-insensitive)
            is_correct = user_norm == correct_norm

        elif exercise_type == "fill_gap":
            # Exact match for the filled part
            is_correct = user_norm == correct_norm

        elif exercise_type == "transform":
            # For punctuation/transform — exact match
            is_correct = user_norm == correct_norm

        elif exercise_type == "order":
            # Word order — exact match of the sentence
            is_correct = user_norm == correct_norm

        else:
            is_correct = user_norm == correct_norm

        # Also accept multiple valid answers separated by |
        if not is_correct and "|" in correct:
            alternatives = [a.strip().lower() for a in correct.split("|")]
            is_correct = user_norm in alternatives

        return {
            "is_correct": is_correct,
            "correct_answer": correct,
            "user_answer": user,
            "explanation": exercise.get("explanation_cs", ""),
        }

    async def record_practice(
        self,
        user_id: int,
        rule_id: int,
        correct: bool,
    ) -> dict[str, Any]:
        """
        Записать результат практики правила.

        Args:
            user_id: ID пользователя
            rule_id: ID правила
            correct: Правильный ли ответ

        Returns:
            dict с обновлённым прогрессом
        """
        progress = await self.grammar_repo.update_progress_practiced(
            user_id, rule_id, correct
        )

        self.logger.info(
            "grammar_practice_recorded",
            user_id=user_id,
            rule_id=rule_id,
            correct=correct,
            mastery=progress.mastery_level,
            accuracy=progress.accuracy,
        )

        return {
            "mastery_level": progress.mastery_level,
            "correct_count": progress.correct_count,
            "incorrect_count": progress.incorrect_count,
            "accuracy": progress.accuracy,
            "times_practiced": progress.times_practiced,
        }

    async def get_progress_summary(
        self,
        user_id: int,
    ) -> dict[str, Any]:
        """Получить сводку прогресса пользователя по грамматике."""
        return await self.grammar_repo.get_user_grammar_summary(user_id)

    # ─── Private helpers ───────────────────────────────────────────

    def _rule_to_dict(self, rule: Any) -> dict[str, Any]:
        """Конвертировать GrammarRule в словарь."""
        examples = []
        common_mistakes = []
        exercise_data = []

        try:
            examples = json.loads(rule.examples) if rule.examples else []
        except (json.JSONDecodeError, TypeError):
            pass

        try:
            common_mistakes = json.loads(rule.common_mistakes) if rule.common_mistakes else []
        except (json.JSONDecodeError, TypeError):
            pass

        try:
            exercise_data = json.loads(rule.exercise_data) if rule.exercise_data else []
        except (json.JSONDecodeError, TypeError):
            pass

        return {
            "id": rule.id,
            "code": rule.code,
            "category": rule.category,
            "subcategory": rule.subcategory,
            "level": rule.level,
            "title_cs": rule.title_cs,
            "rule_cs": rule.rule_cs,
            "explanation_cs": rule.explanation_cs,
            "examples": examples,
            "mnemonic": rule.mnemonic,
            "common_mistakes": common_mistakes,
            "exercise_data": exercise_data,
            "source_ref": rule.source_ref,
        }
