"""
Game Service for grammar-based mini-games.

5 gramatických her založených na Internetové jazykové příručce:
- Pravopisný duel (📝 Vyber správnou variantu i/y, ě/je, ú/ů)
- Doplňka (🔤 Doplň správný tvar / koncovku)
- Kde je chyba? (🔍 Najdi chybu ve větě)
- Správná věta (🧩 Seřaď slova do správného pořadí)
- Čárky, prosím! (✏️ Doplň čárky do věty)
"""

import random
import json
from datetime import datetime, timezone
from typing import Literal
from dataclasses import dataclass

import structlog

from backend.services.grammar_service import GrammarService

logger = structlog.get_logger(__name__)

# Game types
GameType = Literal[
    "pravopisny_duel",
    "doplnka",
    "kde_je_chyba",
    "spravna_veta",
    "carky_prosim",
]

CzechLevel = Literal["beginner", "intermediate", "advanced", "native"]


# Game definitions
GAMES = {
    "pravopisny_duel": {
        "name_cs": "📝 Pravopisný duel",
        "description_cs": "Vyber správnou variantu: i/y, ě/je, ú/ů a další.",
        "reward_stars": 3,
        "time_limit_seconds": 30,
        "difficulty_multiplier": 1.0,
        "exercise_type": "choose",
    },
    "doplnka": {
        "name_cs": "🔤 Doplňka",
        "description_cs": "Doplň správný tvar, koncovku nebo písmeno.",
        "reward_stars": 3,
        "time_limit_seconds": 45,
        "difficulty_multiplier": 1.0,
        "exercise_type": "fill_gap",
    },
    "kde_je_chyba": {
        "name_cs": "🔍 Kde je chyba?",
        "description_cs": "Najdi a oprav chybu ve větě.",
        "reward_stars": 4,
        "time_limit_seconds": 30,
        "difficulty_multiplier": 1.2,
        "exercise_type": "choose",  # uses common_mistakes
    },
    "spravna_veta": {
        "name_cs": "🧩 Správná věta",
        "description_cs": "Seřaď slova do správného pořadí.",
        "reward_stars": 4,
        "time_limit_seconds": 45,
        "difficulty_multiplier": 1.2,
        "exercise_type": "order",
    },
    "carky_prosim": {
        "name_cs": "✏️ Čárky, prosím!",
        "description_cs": "Doplň čárky do věty na správná místa.",
        "reward_stars": 5,
        "time_limit_seconds": 45,
        "difficulty_multiplier": 1.5,
        "exercise_type": "transform",
    },
}


@dataclass
class ActiveGame:
    """Active game for a user."""
    game_id: str
    game_type: GameType
    user_id: int
    question: dict
    correct_answer: str
    started_at: datetime
    level: str
    rule_id: int | None = None  # Track which grammar rule was used


class GameService:
    """
    Grammar-based mini-games service.

    Pulls exercises from GrammarRule.exercise_data via GrammarService.
    Manages active games, scoring, and leaderboard.
    """

    # Class-level shared state — persists across request-scoped instances
    _active_games: dict[int, "ActiveGame"] = {}
    _leaderboard: dict[str, list[dict]] = {
        game_type: [] for game_type in GAMES
    }
    _MAX_ACTIVE_GAMES = 500
    _GAME_TTL_SECONDS = 1800  # 30 minutes

    @classmethod
    def _cleanup_stale_games(cls):
        """Remove games older than TTL and enforce max size."""
        now = datetime.now(timezone.utc)
        expired = [
            uid for uid, g in cls._active_games.items()
            if (now - g.started_at).total_seconds() > cls._GAME_TTL_SECONDS
        ]
        for uid in expired:
            del cls._active_games[uid]
        while len(cls._active_games) > cls._MAX_ACTIVE_GAMES:
            oldest_uid = min(cls._active_games, key=lambda k: cls._active_games[k].started_at)
            del cls._active_games[oldest_uid]

    def __init__(self, grammar_service: GrammarService | None = None):
        self.grammar_service = grammar_service
        self.logger = logger.bind(service="game_service")

    def get_available_games(self) -> list[dict]:
        """Get list of available games."""
        return [
            {
                "id": game_id,
                "name_cs": info["name_cs"],
                "description_cs": info["description_cs"],
                "reward_stars": info["reward_stars"],
                "time_limit_seconds": info["time_limit_seconds"],
            }
            for game_id, info in GAMES.items()
        ]

    async def start_game(
        self,
        user_id: int,
        game_type: GameType,
        level: CzechLevel = "beginner",
    ) -> dict:
        """
        Start a new game.

        Fetches exercises from grammar rules matching the game type and level.
        """
        if game_type not in GAMES:
            raise ValueError(f"Unknown game type: {game_type}")

        self._cleanup_stale_games()
        game_info = GAMES[game_type]
        game_id = f"{user_id}_{game_type}_{datetime.now(timezone.utc).timestamp()}"

        # Generate question from grammar rules
        question, correct_answer, rule_id = await self._generate_question(
            game_type, level
        )

        active_game = ActiveGame(
            game_id=game_id,
            game_type=game_type,
            user_id=user_id,
            question=question,
            correct_answer=correct_answer,
            started_at=datetime.now(timezone.utc),
            level=level,
            rule_id=rule_id,
        )
        self._active_games[user_id] = active_game

        self.logger.info(
            "game_started",
            user_id=user_id,
            game_type=game_type,
            level=level,
            rule_id=rule_id,
        )

        return {
            "game_id": game_id,
            "game_type": game_type,
            "name_cs": game_info["name_cs"],
            "question": question,
            "time_limit_seconds": game_info["time_limit_seconds"],
            "reward_stars": game_info["reward_stars"],
        }

    async def submit_answer(
        self,
        user_id: int,
        answer: str,
    ) -> dict:
        """Submit an answer for the active game."""
        if user_id not in self._active_games:
            raise ValueError("No active game for this user")

        active_game = self._active_games[user_id]
        game_info = GAMES[active_game.game_type]

        # Check time
        elapsed = (datetime.now(timezone.utc) - active_game.started_at).total_seconds()
        time_bonus = max(0, 1 - elapsed / game_info["time_limit_seconds"])

        # Check answer
        is_correct = self._check_answer(
            answer.strip(),
            active_game.correct_answer,
            active_game.game_type,
        )

        # Calculate reward
        base_stars = game_info["reward_stars"] if is_correct else 0
        bonus_stars = int(base_stars * time_bonus * 0.5) if is_correct else 0
        total_stars = base_stars + bonus_stars

        # Record grammar progress if we have a grammar service
        if self.grammar_service and active_game.rule_id:
            try:
                await self.grammar_service.record_practice(
                    user_id=user_id,
                    rule_id=active_game.rule_id,
                    correct=is_correct,
                )
            except Exception as e:
                self.logger.warning("progress_record_failed", error=str(e))

        # Update leaderboard
        if is_correct:
            self._update_leaderboard(
                active_game.game_type,
                user_id,
                total_stars,
                elapsed,
            )

        # Remove active game
        del self._active_games[user_id]

        self.logger.info(
            "game_completed",
            user_id=user_id,
            game_type=active_game.game_type,
            is_correct=is_correct,
            stars_earned=total_stars,
            time_seconds=elapsed,
        )

        return {
            "is_correct": is_correct,
            "correct_answer": active_game.correct_answer,
            "user_answer": answer,
            "stars_earned": total_stars,
            "base_stars": base_stars,
            "bonus_stars": bonus_stars,
            "time_seconds": round(elapsed, 1),
            "time_bonus_percent": round(time_bonus * 100),
        }

    def get_leaderboard(
        self,
        game_type: GameType,
        limit: int = 10,
    ) -> list[dict]:
        """Get leaderboard for a game type."""
        if game_type not in self._leaderboard:
            return []

        return sorted(
            self._leaderboard[game_type],
            key=lambda x: (-x["total_stars"], x["best_time"]),
        )[:limit]

    async def _generate_question(
        self,
        game_type: GameType,
        level: CzechLevel,
    ) -> tuple[dict, str, int | None]:
        """
        Generate a question from grammar rules.

        Returns:
            tuple: (question_dict, correct_answer, rule_id)
        """
        exercise_type = GAMES[game_type]["exercise_type"]
        rule_id = None

        # Try to get exercises from grammar service (DB)
        if self.grammar_service:
            try:
                exercises = await self.grammar_service.get_game_exercises(
                    exercise_type=exercise_type,
                    level=level,
                    count=5,
                )
                if exercises:
                    ex = random.choice(exercises)
                    rule_id = ex.get("rule_id")
                    return self._format_exercise(game_type, ex), ex["answer"], rule_id
            except Exception as e:
                self.logger.warning("grammar_exercises_fetch_failed", error=str(e))

        # Fallback: use hardcoded exercises
        return self._fallback_question(game_type, level)

    def _format_exercise(self, game_type: GameType, exercise: dict) -> dict:
        """Format a grammar exercise for the game UI.

        Returns dict with keys matching frontend GameQuestion.question interface:
        prompt, options, hint, word, sentence, words.
        """
        hint = exercise.get("hint", exercise.get("rule_title", ""))

        if game_type == "pravopisny_duel":
            return {
                "type": "choose",
                "prompt": exercise["question"],
                "options": exercise.get("options", []),
                "hint": hint,
            }

        elif game_type == "doplnka":
            return {
                "type": "fill_gap",
                "prompt": exercise["question"],
                "hint": hint,
            }

        elif game_type == "kde_je_chyba":
            return {
                "type": "find_error",
                "prompt": exercise["question"],
                "options": exercise.get("options", []),
                "hint": hint,
            }

        elif game_type == "spravna_veta":
            answer = exercise["answer"]
            words = answer.replace("?", " ?").replace(".", " .").replace(",", " ,").split()
            shuffled = words.copy()
            for _ in range(10):
                random.shuffle(shuffled)
                if shuffled != words:
                    break
            return {
                "type": "order",
                "prompt": exercise.get("question", "Seřaď slova do věty:"),
                "words": shuffled,
                "hint": hint,
            }

        elif game_type == "carky_prosim":
            return {
                "type": "transform",
                "prompt": exercise["question"],
                "sentence": exercise["question"],
                "hint": hint,
            }

        return {"type": "unknown", "prompt": exercise.get("question", "")}

    def _fallback_question(
        self,
        game_type: GameType,
        level: CzechLevel,
    ) -> tuple[dict, str, None]:
        """Fallback questions when DB is not available."""

        if game_type == "pravopisny_duel":
            questions = [
                {"q": "b_dlit — doplň i nebo y:", "a": "y", "opts": ["i", "y"], "h": "bydlit = to live"},
                {"q": "ch_ba — doplň i nebo y:", "a": "y", "opts": ["i", "y"], "h": "chyba = mistake"},
                {"q": "č_slo — doplň í nebo ý:", "a": "í", "opts": ["í", "ý"], "h": "číslo = number"},
                {"q": "v_běhnout — doplň i nebo y:", "a": "y", "opts": ["i", "y"], "h": "Předpona vy-"},
                {"q": "jaz_k — doplň i nebo y:", "a": "y", "opts": ["i", "y"], "h": "jazyk = language"},
                {"q": "_kol — ú nebo ů?", "a": "ú", "opts": ["ú", "ů"], "h": "Na začátku slova: ú"},
                {"q": "d_m — ú nebo ů?", "a": "ů", "opts": ["ú", "ů"], "h": "Uprostřed slova: ů"},
            ]
            q = random.choice(questions)
            return {
                "type": "choose",
                "prompt": q["q"],
                "options": q["opts"],
                "hint": q.get("h", ""),
            }, q["a"], None

        elif game_type == "doplnka":
            questions = [
                {"q": "Jdu do ___. (škola, 2. p.)", "a": "školy", "h": "Vzor žena"},
                {"q": "Vidím ___. (žena, 4. p.)", "a": "ženu", "h": "Vzor žena"},
                {"q": "Vidím ___. (student, 4. p.)", "a": "studenta", "h": "Vzor pán"},
                {"q": "Já ___ česky. (mluvit)", "a": "mluvím", "h": "1. os. sg."},
                {"q": "Oni ___ doma. (být)", "a": "jsou", "h": "3. os. pl."},
            ]
            q = random.choice(questions)
            return {
                "type": "fill_gap",
                "prompt": q["q"],
                "hint": q.get("h", ""),
            }, q["a"], None

        elif game_type == "kde_je_chyba":
            questions = [
                {"q": "Která věta je správně?", "a": "bydlím v Praze", "opts": ["bidlím v Praze", "bydlím v Praze"]},
                {"q": "Která věta je správně?", "a": "jsou doma", "opts": ["sou doma", "jsou doma"]},
                {"q": "Která věta je správně?", "a": "Myslím, že ano.", "opts": ["Myslím že ano.", "Myslím, že ano."]},
            ]
            q = random.choice(questions)
            return {
                "type": "find_error",
                "prompt": q["q"],
                "options": q["opts"],
                "hint": "",
            }, q["a"], None

        elif game_type == "spravna_veta":
            sentences = [
                {"q": "jsem / Včera / v kině / byl", "a": "Včera jsem byl v kině.", "h": "Příklonky na 2. místo"},
                {"q": "auto / Koupil / si / jsem", "a": "Koupil jsem si auto.", "h": "jsem = příklonka"},
                {"q": "česky / se / Učím", "a": "Učím se česky.", "h": "se = příklonka"},
            ]
            s = random.choice(sentences)
            words = s["q"].split(" / ")
            random.shuffle(words)
            return {
                "type": "order",
                "prompt": "Seřaď slova do věty:",
                "words": words,
                "hint": s.get("h", ""),
            }, s["a"], None

        elif game_type == "carky_prosim":
            sentences = [
                {"q": "Myslím že máš pravdu.", "a": "Myslím, že máš pravdu.", "h": "Čárka před že"},
                {"q": "Řekl že přijde zítra.", "a": "Řekl, že přijde zítra.", "h": "Čárka před že"},
                {"q": "Je hezky ale studené.", "a": "Je hezky, ale studené.", "h": "Čárka před ale"},
            ]
            s = random.choice(sentences)
            return {
                "type": "transform",
                "prompt": s["q"],
                "sentence": s["q"],
                "hint": s.get("h", ""),
            }, s["a"], None

        return {"type": "unknown", "prompt": ""}, "", None

    def _check_answer(
        self,
        user_answer: str,
        correct_answer: str,
        game_type: GameType,
    ) -> bool:
        """Check if the answer is correct."""
        user_norm = user_answer.strip()
        correct_norm = correct_answer.strip()

        if game_type in ("spravna_veta", "carky_prosim"):
            # Normalize punctuation spacing
            user_clean = (
                user_norm.replace(" ?", "?").replace(" .", ".")
                .replace(" ,", ",").replace("  ", " ").strip()
            )
            correct_clean = (
                correct_norm.replace(" ?", "?").replace(" .", ".")
                .replace(" ,", ",").replace("  ", " ").strip()
            )
            return user_clean.lower() == correct_clean.lower()

        # Support multiple correct answers separated by |
        if "|" in correct_norm:
            valid_answers = [a.strip().lower() for a in correct_norm.split("|")]
            return user_norm.lower() in valid_answers

        return user_norm.lower() == correct_norm.lower()

    def _update_leaderboard(
        self,
        game_type: GameType,
        user_id: int,
        stars: int,
        time_seconds: float,
    ):
        """Update leaderboard."""
        leaderboard = self._leaderboard[game_type]

        existing = next((x for x in leaderboard if x["user_id"] == user_id), None)

        if existing:
            existing["total_stars"] += stars
            existing["games_played"] += 1
            if time_seconds < existing["best_time"]:
                existing["best_time"] = time_seconds
        else:
            leaderboard.append({
                "user_id": user_id,
                "total_stars": stars,
                "games_played": 1,
                "best_time": time_seconds,
            })

    def cancel_game(self, user_id: int) -> bool:
        """Cancel active game."""
        if user_id in self._active_games:
            del self._active_games[user_id]
            return True
        return False
