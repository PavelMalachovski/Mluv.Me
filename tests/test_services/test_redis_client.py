"""
Tests for RedisClient - binary pool reuse and session management.
"""

import pytest
from unittest.mock import AsyncMock, PropertyMock, patch

from backend.cache.redis_client import RedisClient


class TestRedisClientInit:
    """Test RedisClient initialization."""

    def test_binary_pool_attrs_exist(self):
        """RedisClient should have binary pool attributes after init."""
        client = RedisClient()
        assert hasattr(client, "_binary_pool")
        assert hasattr(client, "_binary_redis")
        assert client._binary_pool is None
        assert client._binary_redis is None

    def test_pool_attrs_exist(self):
        """RedisClient should have standard pool attributes."""
        client = RedisClient()
        assert hasattr(client, "pool")
        assert hasattr(client, "redis")
        assert client.pool is None
        assert client.redis is None


@pytest.mark.asyncio
class TestRedisClientOperations:
    """Test get/set/delete with mocked Redis."""

    async def test_get_returns_value(self):
        """get() should return deserialized value from Redis."""
        client = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value='{"key": "val"}')
        client.redis = mock_redis

        with patch.object(
            type(client), "is_enabled", new_callable=PropertyMock, return_value=True
        ):
            result = await client.get("test:key")
        assert result == {"key": "val"}

    async def test_get_returns_none_on_miss(self):
        """get() should return None when key not found."""
        client = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        client.redis = mock_redis

        with patch.object(
            type(client), "is_enabled", new_callable=PropertyMock, return_value=True
        ):
            result = await client.get("nonexistent")
        assert result is None

    async def test_set_stores_value(self):
        """set() should serialize and store value."""
        client = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(return_value=True)
        client.redis = mock_redis

        with (
            patch.object(
                type(client), "is_enabled", new_callable=PropertyMock, return_value=True
            ),
            patch("backend.cache.redis_client.get_settings") as mock_settings,
        ):
            mock_settings.return_value.redis_cache_ttl_default = 300
            result = await client.set("test:key", {"hello": "world"}, ttl=300)
        assert result is True

    async def test_delete_key(self):
        """delete() should remove key from Redis."""
        client = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=1)
        client.redis = mock_redis

        result = await client.delete("test:key")
        assert result is True

    async def test_get_bytes_uses_binary_pool(self):
        """get_bytes() should use the shared binary redis instance."""
        client = RedisClient()
        mock_binary_redis = AsyncMock()
        mock_binary_redis.get = AsyncMock(return_value=b"\x89PNG")
        client._binary_redis = mock_binary_redis

        with patch.object(
            type(client), "is_enabled", new_callable=PropertyMock, return_value=True
        ):
            result = await client.get_bytes("tts:test")
        assert result == b"\x89PNG"
        mock_binary_redis.get.assert_called_once_with("tts:test")

    async def test_set_bytes_uses_binary_pool(self):
        """set_bytes() should use the shared binary redis instance."""
        client = RedisClient()
        mock_binary_redis = AsyncMock()
        mock_binary_redis.setex = AsyncMock(return_value=True)
        client._binary_redis = mock_binary_redis

        with (
            patch.object(
                type(client), "is_enabled", new_callable=PropertyMock, return_value=True
            ),
            patch("backend.cache.redis_client.get_settings") as mock_settings,
        ):
            mock_settings.return_value.redis_cache_ttl_default = 600
            await client.set_bytes("tts:test", b"\x89PNG", ttl=600)
        mock_binary_redis.setex.assert_called_once()
