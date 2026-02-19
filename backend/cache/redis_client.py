"""
Async Redis client with connection pooling.
"""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis
import structlog

from backend.config import get_settings

logger = structlog.get_logger(__name__)


class RedisClient:
    """Async Redis client with connection pooling."""

    def __init__(self) -> None:
        self.pool: ConnectionPool | None = None
        self.redis: Redis | None = None
        self._binary_pool: ConnectionPool | None = None
        self._binary_redis: Redis | None = None

    @property
    def is_enabled(self) -> bool:
        """Return True when caching is allowed."""
        return get_settings().cache_enabled

    @property
    def is_connected(self) -> bool:
        """Return True when redis connection exists."""
        return self.redis is not None

    async def connect(self) -> None:
        """Initialize Redis connection pool."""
        settings = get_settings()

        if not settings.cache_enabled:
            logger.info("redis_cache_disabled")
            return

        if self.redis:
            return

        self.pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )
        self.redis = redis.Redis(connection_pool=self.pool)

        # Binary pool for TTS audio (no decode_responses)
        self._binary_pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=5,
            decode_responses=False,
        )
        self._binary_redis = redis.Redis(connection_pool=self._binary_pool)

        try:
            await self.redis.ping()
            logger.info("redis_connected", url=settings.redis_url)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("redis_connect_failed", error=str(exc))
            self.redis = None
            if self.pool:
                await self.pool.disconnect()
                self.pool = None
            raise

    async def disconnect(self) -> None:
        """Close Redis connections."""
        if self._binary_redis:
            await self._binary_redis.aclose()
            self._binary_redis = None
        if self._binary_pool:
            await self._binary_pool.disconnect()
            self._binary_pool = None
        if self.redis:
            await self.redis.aclose()
            self.redis = None
        if self.pool:
            await self.pool.disconnect()
            self.pool = None
        logger.info("redis_disconnected")

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if not self.is_enabled or not self.redis:
            return None
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache with TTL."""
        if not self.is_enabled or not self.redis:
            return False
        settings = get_settings()
        ttl_value = ttl or settings.redis_cache_ttl_default
        payload = json.dumps(value)
        result = await self.redis.setex(key, ttl_value, payload)
        return bool(result)

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis:
            return False
        deleted = await self.redis.delete(key)
        return deleted > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.redis:
            return False
        return bool(await self.redis.exists(key))

    async def ping(self) -> bool:
        """Ping Redis."""
        if not self.redis:
            return False
        return bool(await self.redis.ping())

    async def get_bytes(self, key: str) -> bytes | None:
        """Get binary value from cache (for TTS audio)."""
        if not self.is_enabled or not self._binary_redis:
            return None
        try:
            value = await self._binary_redis.get(key)
            return value if value else None
        except Exception as e:
            logger.warning("redis_get_bytes_error", key=key, error=str(e))
            return None

    async def set_bytes(self, key: str, value: bytes, ttl: int | None = None) -> bool:
        """Set binary value in cache with TTL (for TTS audio)."""
        if not self.is_enabled or not self._binary_redis:
            return False
        settings = get_settings()
        ttl_value = ttl or settings.redis_cache_ttl_default
        try:
            result = await self._binary_redis.setex(key, ttl_value, value)
            return bool(result)
        except Exception as e:
            logger.warning("redis_set_bytes_error", key=key, error=str(e))
            return False


redis_client = RedisClient()
