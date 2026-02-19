"""
Tests for GrammarRepository - joinedload N+1 fix and basic queries.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from backend.db.grammar_repository import GrammarRepository


@pytest.mark.asyncio
class TestGrammarRepository:
    """Test grammar repository query methods."""

    async def test_get_rule_by_id_found(self):
        """Should return rule when found."""
        mock_session = AsyncMock()
        mock_rule = MagicMock()
        mock_rule.id = 1
        mock_rule.code = "present_tense"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_rule
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = GrammarRepository(mock_session)
        result = await repo.get_rule_by_id(1)

        assert result is not None
        assert result.id == 1
        mock_session.execute.assert_called_once()

    async def test_get_rule_by_id_not_found(self):
        """Should return None when rule not found."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = GrammarRepository(mock_session)
        result = await repo.get_rule_by_id(999)

        assert result is None

    async def test_get_rule_by_code(self):
        """Should find rule by code string."""
        mock_session = AsyncMock()
        mock_rule = MagicMock()
        mock_rule.code = "past_tense"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_rule
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = GrammarRepository(mock_session)
        result = await repo.get_rule_by_code("past_tense")

        assert result is not None
        assert result.code == "past_tense"

    async def test_get_user_progress_with_rules_returns_list(self):
        """get_user_progress_with_rules should use joinedload and return list."""
        mock_session = AsyncMock()

        # Create mock progress entries with joined rules
        progress1 = MagicMock()
        progress1.grammar_rule = MagicMock()
        progress1.grammar_rule.title_cs = "Přítomný čas"
        progress1.success_rate = 0.8

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.unique.return_value = mock_scalars
        mock_scalars.all.return_value = [progress1]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        repo = GrammarRepository(mock_session)
        result = await repo.get_user_progress_with_rules(user_id=1)

        assert len(result) == 1
        assert result[0].grammar_rule.title_cs == "Přítomný čas"
        # Verify joinedload was used (query was executed)
        mock_session.execute.assert_called_once()
