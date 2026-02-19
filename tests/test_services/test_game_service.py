"""
Tests for GameService (Redis-backed active games).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.services.game_service import GameService, GAMES


@pytest.mark.asyncio
class TestGameService:
    """Tests for game service logic."""

    def test_get_available_games_returns_all(self):
        """get_available_games returns exactly 5 games."""
        service = GameService()
        games = service.get_available_games()
        assert len(games) == 5
        game_ids = [g["id"] for g in games]
        assert "pravopisny_duel" in game_ids
        assert "carky_prosim" in game_ids

    def test_check_answer_exact_match(self):
        """Exact string match should return True."""
        service = GameService()
        assert service._check_answer("správný", "správný", "pravopisny_duel") is True

    def test_check_answer_case_insensitive(self):
        """Answer matching should be case-insensitive."""
        service = GameService()
        assert service._check_answer("Správný", "správný", "pravopisny_duel") is True

    def test_check_answer_wrong(self):
        """Wrong answer should return False."""
        service = GameService()
        assert service._check_answer("špatný", "správný", "pravopisny_duel") is False

    async def test_start_game_stores_in_redis(self):
        """start_game should store game data in Redis."""
        from backend.cache.redis_client import redis_client

        mock_set = AsyncMock(return_value=True)
        mock_grammar = AsyncMock()
        mock_grammar.get_exercises_for_game = AsyncMock(return_value=[{
            "question": {"sentence": "Test?", "options": ["a", "b"]},
            "correct_answer": "a",
            "rule_id": 1,
        }])

        service = GameService(grammar_service=mock_grammar)

        with patch.object(redis_client, "set", mock_set):
            result = await service.start_game(
                user_id=1, game_type="pravopisny_duel", level="beginner"
            )

        assert result["game_type"] == "pravopisny_duel"
        assert "question" in result
        mock_set.assert_called_once()
        key = mock_set.call_args[0][0]
        assert key.startswith("game:active:")

    async def test_submit_answer_correct(self):
        """Submitting a correct answer should award stars."""
        from backend.cache.redis_client import redis_client
        from datetime import datetime, timezone

        game_data = {
            "game_id": "1_pravopisny_duel_123",
            "game_type": "pravopisny_duel",
            "user_id": 1,
            "question": {"sentence": "test"},
            "correct_answer": "správný",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "level": "beginner",
            "rule_id": None,
        }

        service = GameService()

        with patch.object(redis_client, "get", new_callable=AsyncMock, return_value=game_data), \
             patch.object(redis_client, "delete", new_callable=AsyncMock, return_value=True):
            result = await service.submit_answer(user_id=1, answer="správný")

        assert result["is_correct"] is True
        assert result["stars_earned"] > 0

    async def test_submit_answer_no_game(self):
        """Submitting when no game active should raise ValueError."""
        from backend.cache.redis_client import redis_client

        service = GameService()
        with patch.object(redis_client, "get", new_callable=AsyncMock, return_value=None):
            with pytest.raises(ValueError, match="No active game"):
                await service.submit_answer(user_id=999, answer="anything")
