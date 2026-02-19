"""
Tests for ScenarioService (Redis-backed active scenarios).
"""

import pytest
from unittest.mock import AsyncMock, patch

from backend.services.scenario_service import ScenarioService, SCENARIOS


class TestScenarioServiceSync:
    """Synchronous tests for scenario helpers."""

    def test_scenarios_defined(self):
        """SCENARIOS dict should contain expected scenario IDs."""
        assert "v_hospode" in SCENARIOS
        assert "u_lekare" in SCENARIOS
        assert "na_cizinecke_policii" in SCENARIOS
        assert len(SCENARIOS) >= 8

    def test_scenario_has_required_fields(self):
        """Each scenario definition should have required fields."""
        for sid, s in SCENARIOS.items():
            assert "name_cs" in s, f"{sid} missing name_cs"
            assert "steps" in s, f"{sid} missing steps"
            assert "min_level" in s, f"{sid} missing min_level"
            assert "vocabulary" in s, f"{sid} missing vocabulary"
            assert "hints" in s, f"{sid} missing hints"
            assert s["steps"] > 0, f"{sid} steps must be > 0"


@pytest.mark.asyncio
class TestScenarioServiceAsync:
    """Async tests for Redis-backed scenario operations."""

    async def test_get_active_scenario_none(self):
        """When no scenario active, should return None."""
        from backend.cache.redis_client import redis_client

        service = ScenarioService.__new__(ScenarioService)
        with patch.object(redis_client, "get", new_callable=AsyncMock, return_value=None):
            result = await service.get_active_scenario(user_id=42)
        assert result is None

    async def test_cancel_scenario_active(self):
        """cancel_scenario should delete state from Redis and return True."""
        from backend.cache.redis_client import redis_client

        service = ScenarioService.__new__(ScenarioService)
        state = {"scenario_id": "v_hospode", "current_step": 2}

        with patch.object(redis_client, "get", new_callable=AsyncMock, return_value=state), \
             patch.object(redis_client, "delete", new_callable=AsyncMock, return_value=True):
            result = await service.cancel_scenario(user_id=42)
        assert result is True

    async def test_cancel_scenario_no_active(self):
        """cancel_scenario when none active should return False."""
        from backend.cache.redis_client import redis_client

        service = ScenarioService.__new__(ScenarioService)
        with patch.object(redis_client, "get", new_callable=AsyncMock, return_value=None):
            result = await service.cancel_scenario(user_id=42)
        assert result is False
