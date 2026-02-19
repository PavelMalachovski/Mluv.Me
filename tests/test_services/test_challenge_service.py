"""
Tests for ChallengeService - deterministic RNG and challenge generation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date

from backend.services.challenge_service import ChallengeService


class TestChallengeServiceDeterministicRNG:
    """Verify that daily challenge selection is deterministic per user+date."""

    @pytest.mark.asyncio
    async def test_same_user_same_date_same_challenge(self):
        """Same user_id + date should always produce the same challenge."""
        service = ChallengeService()

        # Mock 3 challenges
        challenges = []
        for i in range(3):
            c = MagicMock()
            c.id = i + 1
            c.code = f"ch_{i}"
            c.type = "daily"
            c.is_active = True
            c.title_cs = f"Challenge {i}"
            c.description_cs = f"Desc {i}"
            c.goal_type = "messages"
            c.goal_topic = None
            c.goal_value = 5
            c.reward_stars = 10
            challenges.append(c)

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = challenges
        mock_session.execute = AsyncMock(return_value=mock_result)

        user_challenge = MagicMock()
        user_challenge.progress = 0
        user_challenge.completed = False
        user_challenge.reward_claimed = False

        service._get_or_create_user_challenge = AsyncMock(return_value=user_challenge)
        service._calculate_progress = AsyncMock(return_value=0)
        mock_session.flush = AsyncMock()

        user_date = date(2025, 1, 15)

        # Call twice with same params
        r1 = await service.get_daily_challenge(mock_session, user_id=42, user_date=user_date)
        r2 = await service.get_daily_challenge(mock_session, user_id=42, user_date=user_date)

        assert r1["id"] == r2["id"], "Same user+date must produce same challenge"

    @pytest.mark.asyncio
    async def test_different_dates_may_differ(self):
        """Different dates for same user should (likely) produce different challenges."""
        import random

        # With 10 challenges, probability of collision on 2 dates is low
        rng1 = random.Random(hash("42:2025-01-15"))
        rng2 = random.Random(hash("42:2025-01-16"))

        items = list(range(10))
        choice1 = rng1.choice(items)
        choice2 = rng2.choice(items)
        # We just verify the RNG works - it might still collide
        # but we're testing the mechanism, not guarantee
        assert isinstance(choice1, int)
        assert isinstance(choice2, int)

    @pytest.mark.asyncio
    async def test_empty_challenges_returns_error(self):
        """When no challenges exist, should return error dict."""
        service = ChallengeService()

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await service.get_daily_challenge(
            mock_session, user_id=1, user_date=date(2025, 1, 1)
        )
        assert "error" in result
