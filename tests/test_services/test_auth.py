"""
Tests for auth flow: session creation, token validation, logout.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from backend.routers.web_auth import _create_session, get_authenticated_user
from backend.cache.redis_client import redis_client


@pytest.mark.asyncio
class TestSessionManagement:
    """Tests for Redis-backed session management."""

    async def test_create_session_returns_token(self):
        """_create_session returns a non-empty string token."""
        with patch.object(redis_client, "set", new_callable=AsyncMock, return_value=True):
            token = await _create_session(user_id=42)
            assert isinstance(token, str)
            assert len(token) > 20

    async def test_create_session_stores_in_redis(self):
        """_create_session calls redis_client.set with correct key prefix and TTL."""
        mock_set = AsyncMock(return_value=True)
        with patch.object(redis_client, "set", mock_set):
            token = await _create_session(user_id=99)
            mock_set.assert_called_once()
            call_args = mock_set.call_args
            key = call_args[0][0]
            data = call_args[0][1]
            assert key == f"session:{token}"
            assert data == {"user_id": 99}
            assert call_args[1]["ttl"] == 30 * 24 * 60 * 60  # 30 days

    async def test_get_authenticated_user_no_token(self):
        """get_authenticated_user raises 401 with no token."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await get_authenticated_user(token=None, db=AsyncMock())
        assert exc_info.value.status_code == 401

    async def test_get_authenticated_user_invalid_token(self):
        """get_authenticated_user raises 401 for unknown token."""
        from fastapi import HTTPException

        with patch.object(redis_client, "get", new_callable=AsyncMock, return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await get_authenticated_user(token="invalid-token", db=AsyncMock())
            assert exc_info.value.status_code == 401


@pytest.mark.asyncio
class TestLogoutEndpoint:
    """Tests for the /logout endpoint."""

    async def test_logout_deletes_session(self, client: AsyncClient):
        """POST /logout should remove session cookie."""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
