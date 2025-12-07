"""
Tests for Redis caching functionality.
"""

import pytest
from datetime import date

from backend.cache.redis_client import redis_client
from backend.cache.cache_keys import CacheKeys
from backend.db.repositories import UserRepository, StatsRepository
from backend.services.cache_service import cache_service


@pytest.mark.asyncio
class TestRedisClient:
    """Tests for RedisClient."""

    async def test_redis_connect_disconnect(self):
        """Test Redis connection and disconnection."""
        if not redis_client.is_enabled:
            pytest.skip("Redis caching is disabled")

        await redis_client.connect()
        assert redis_client.is_connected
        assert await redis_client.ping()

        await redis_client.disconnect()
        assert not redis_client.is_connected

    async def test_set_and_get(self):
        """Test setting and getting values."""
        if not redis_client.is_enabled:
            pytest.skip("Redis caching is disabled")

        await redis_client.connect()

        try:
            # Set value
            result = await redis_client.set("test_key", {"foo": "bar"}, ttl=60)
            assert result is True

            # Get value
            value = await redis_client.get("test_key")
            assert value == {"foo": "bar"}

            # Delete value
            deleted = await redis_client.delete("test_key")
            assert deleted is True

            # Verify deleted
            value = await redis_client.get("test_key")
            assert value is None
        finally:
            await redis_client.disconnect()

    async def test_exists(self):
        """Test checking if key exists."""
        if not redis_client.is_enabled:
            pytest.skip("Redis caching is disabled")

        await redis_client.connect()

        try:
            await redis_client.set("test_exists", "value", ttl=60)
            assert await redis_client.exists("test_exists")

            await redis_client.delete("test_exists")
            assert not await redis_client.exists("test_exists")
        finally:
            await redis_client.disconnect()


@pytest.mark.asyncio
class TestCacheKeys:
    """Tests for cache key patterns."""

    def test_user_profile_key(self):
        """Test user profile key generation."""
        key = CacheKeys.user_profile(123456)
        assert key == "user:123456:profile"

    def test_user_settings_key(self):
        """Test user settings key generation."""
        key = CacheKeys.user_settings(123456)
        assert key == "user:123456:settings"

    def test_daily_stats_key(self):
        """Test daily stats key generation."""
        key = CacheKeys.daily_stats(1, "2024-01-01")
        assert key == "stats:1:daily:2024-01-01"

    def test_honzik_response_key(self):
        """Test Honzik response key generation."""
        key1 = CacheKeys.honzik_response("Ahoj, jak se máš?", "beginner:balanced")
        key2 = CacheKeys.honzik_response("Ahoj, jak se máš?", "beginner:balanced")
        # Should be deterministic
        assert key1 == key2
        assert "honzik:response:" in key1


@pytest.mark.asyncio
class TestUserRepositoryCaching:
    """Tests for UserRepository caching."""

    async def test_cache_hit_rate(self, session, user_data):
        """Test cache hit rate for user lookups."""
        if not redis_client.is_enabled:
            pytest.skip("Redis caching is disabled")

        await redis_client.connect()

        try:
            repo = UserRepository(session)

            # Create user
            user = await repo.create(**user_data)
            await session.commit()

            # First lookup (cache miss, should cache)
            user1 = await repo.get_by_telegram_id(user.telegram_id, use_cache=True)
            assert user1 is not None

            # Second lookup (cache hit)
            user2 = await repo.get_by_telegram_id(user.telegram_id, use_cache=True)
            assert user2 is not None
            assert user2.telegram_id == user.telegram_id

            # Verify cache exists
            cache_key = CacheKeys.user_profile(user.telegram_id)
            assert await redis_client.exists(cache_key)
        finally:
            await redis_client.disconnect()

    async def test_cache_invalidation_on_update(self, session, user_data):
        """Test cache is invalidated on user update."""
        if not redis_client.is_enabled:
            pytest.skip("Redis caching is disabled")

        await redis_client.connect()

        try:
            repo = UserRepository(session)

            # Create user and cache it
            user = await repo.create(**user_data)
            await session.commit()
            await repo.get_by_telegram_id(user.telegram_id, use_cache=True)

            # Verify cached
            cache_key = CacheKeys.user_profile(user.telegram_id)
            assert await redis_client.exists(cache_key)

            # Update user
            await repo.update(user.id, level="advanced")

            # Verify cache invalidated
            assert not await redis_client.exists(cache_key)
        finally:
            await redis_client.disconnect()

    async def test_cache_bypass(self, session, user_data):
        """Test cache bypass when use_cache=False."""
        if not redis_client.is_enabled:
            pytest.skip("Redis caching is disabled")

        await redis_client.connect()

        try:
            repo = UserRepository(session)

            # Create user
            user = await repo.create(**user_data)
            await session.commit()

            # Lookup with cache bypass
            user1 = await repo.get_by_telegram_id(user.telegram_id, use_cache=False)
            assert user1 is not None

            # Verify no cache entry
            cache_key = CacheKeys.user_profile(user.telegram_id)
            assert not await redis_client.exists(cache_key)
        finally:
            await redis_client.disconnect()


@pytest.mark.asyncio
class TestCacheService:
    """Tests for CacheService."""

    async def test_openai_cache_key_deterministic(self):
        """Test OpenAI cache key is deterministic."""
        settings1 = {
            "czech_level": "beginner",
            "correction_level": "balanced",
            "conversation_style": "friendly",
        }
        settings2 = {
            "czech_level": "beginner",
            "correction_level": "balanced",
            "conversation_style": "friendly",
        }

        key1 = cache_service.create_openai_cache_key(
            "Ahoj, jak se máš?", settings1, "gpt-4o"
        )
        key2 = cache_service.create_openai_cache_key(
            "Ahoj, jak se máš?", settings2, "gpt-4o"
        )

        assert key1 == key2

    async def test_cache_honzik_response(self):
        """Test caching Honzik response."""
        if not redis_client.is_enabled:
            pytest.skip("Redis caching is disabled")

        await redis_client.connect()

        try:
            settings = {
                "czech_level": "beginner",
                "correction_level": "balanced",
                "conversation_style": "friendly",
            }
            response = {
                "honzik_response": "Ahoj! Jak se máš?",
                "corrected_text": "Ahoj, jak se máš?",
                "mistakes": [],
                "correctness_score": 100,
                "suggestion": "Perfect!",
            }

            # Cache response
            await cache_service.cache_honzik_response(
                "Ahoj, jak se máš?", settings, response
            )

            # Retrieve cached response
            cached = await cache_service.get_cached_honzik_response(
                "Ahoj, jak se máš?", settings
            )
            assert cached is not None
            assert cached["honzik_response"] == "Ahoj! Jak se máš?"
            assert cached["correctness_score"] == 100
        finally:
            await redis_client.disconnect()


@pytest.mark.asyncio
class TestStatsRepositoryCaching:
    """Tests for StatsRepository caching."""

    async def test_stats_cache_invalidation(self, session, user_data):
        """Test stats cache is invalidated on update."""
        if not redis_client.is_enabled:
            pytest.skip("Redis caching is disabled")

        await redis_client.connect()

        try:
            user_repo = UserRepository(session)
            stats_repo = StatsRepository(session)

            # Create user
            user = await user_repo.create(**user_data)
            await session.commit()

            today = date.today()

            # Create stats and manually cache
            stats = await stats_repo.get_or_create_daily(user.id, today)
            await session.commit()

            cache_key = CacheKeys.daily_stats(user.telegram_id, str(today))
            await redis_client.set(cache_key, {"test": "data"}, ttl=3600)
            assert await redis_client.exists(cache_key)

            # Update stats
            await stats_repo.update_daily(
                user.id, today, messages_count=5, words_said=50
            )
            await session.commit()

            # Verify cache invalidated
            assert not await redis_client.exists(cache_key)
        finally:
            await redis_client.disconnect()
