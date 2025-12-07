"""
High-level caching service for OpenAI responses and other cached data.
"""

import hashlib
import json
from typing import Any

import structlog

from backend.cache.redis_client import redis_client
from backend.cache.cache_keys import CacheKeys
from backend.config import get_settings

logger = structlog.get_logger(__name__)


class CacheService:
    """High-level caching logic for OpenAI responses."""

    def create_openai_cache_key(
        self, user_text: str, settings: dict[str, Any], model: str
    ) -> str:
        """
        Create deterministic cache key for OpenAI responses.

        Args:
            user_text: User text input
            settings: Relevant settings that affect response
            model: Model name

        Returns:
            str: Cache key
        """
        # Include relevant settings that affect response
        cache_input = {
            "text": user_text.lower().strip(),
            "level": settings.get("czech_level"),
            "correction_level": settings.get("correction_level"),
            "conversation_style": settings.get("conversation_style"),
            "model": model,
        }

        # Create hash
        content = json.dumps(cache_input, sort_keys=True)
        hash_key = hashlib.sha256(content.encode()).hexdigest()[:16]

        return CacheKeys.HONZIK_RESPONSE.format(hash=hash_key)

    async def get_cached_honzik_response(
        self, user_text: str, settings: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Get cached Honzik response if available.

        Args:
            user_text: User text
            settings: User settings

        Returns:
            Cached response or None
        """
        if not redis_client.is_enabled:
            return None

        cache_key = self.create_openai_cache_key(user_text, settings, "gpt-4o")
        cached = await redis_client.get(cache_key)

        if cached:
            logger.info("honzik_cache_hit", text_length=len(user_text))
            return cached

        return None

    async def cache_honzik_response(
        self, user_text: str, settings: dict[str, Any], response: dict[str, Any]
    ) -> None:
        """
        Cache Honzik response.

        Args:
            user_text: User text
            settings: User settings
            response: Honzik response to cache
        """
        if not redis_client.is_enabled:
            return

        cache_key = self.create_openai_cache_key(user_text, settings, "gpt-4o")
        app_settings = get_settings()

        await redis_client.set(
            cache_key, response, ttl=app_settings.redis_cache_ttl_openai
        )
        logger.info("honzik_response_cached", text_length=len(user_text))


cache_service = CacheService()
