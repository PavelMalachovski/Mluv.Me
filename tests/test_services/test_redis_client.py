"""
Tests for RedisClient - binary pool reuse and session management.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

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
        assert hasattr(client, "_pool")
        assert hasattr(client, "_redis")
        assert client._pool is None
        assert client._redis is None


@pytest.mark.asyncio
class TestRedisClientOperations:
    """Test get/set/delete with mocked Redis."""

    async def test_get_returns_value(self):
        """get() should return deserialized value from Redis."""
        client = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value='{"key": "val"}')
        client._redis = mock_redis

        result = await client.get("test:key")
        assert result == {"key": "val"}

    async def test_get_returns_none_on_miss(self):
        """get() should return None when key not found."""
        client = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        client._redis = mock_redis

        result = await client.get("nonexistent")
        assert result is None

    async def test_set_stores_value(self):
        """set() should serialize and store value."""
        client = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(return_value=True)
        client._redis = mock_redis

        result = await client.set("test:key", {"hello": "world"}, ttl=300)
        assert result is True
        mock_redis.set.assert_called_once()

    async def test_delete_key(self):
        """delete() should remove key from Redis."""
        client = RedisClient()
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=1)
        client._redis = mock_redis

        result = await client.delete("test:key")
        assert result == 1

    async def test_get_bytes_uses_binary_pool(self):
        """get_bytes() should use the shared binary redis instance."""
        client = RedisClient()
        mock_binary_redis = AsyncMock()
        mock_binary_redis.get = AsyncMock(return_value=b"\x89PNG")
        client._binary_redis = mock_binary_redis

        result = await client.get_bytes("tts:test")
        assert result == b"\x89PNG"
        mock_binary_redis.get.assert_called_once_with("tts:test")

    async def test_set_bytes_uses_binary_pool(self):
        """set_bytes() should use the shared binary redis instance."""
        client = RedisClient()
        mock_binary_redis = AsyncMock()
        mock_binary_redis.set = AsyncMock(return_value=True)
        client._binary_redis = mock_binary_redis

        await client.set_bytes("tts:test", b"\x89PNG", ttl=600)
        mock_binary_redis.set.assert_called_once()
