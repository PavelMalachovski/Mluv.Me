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

# Типичные чешские фразы, которые кешируются для быстрого ответа
COMMON_CZECH_PHRASES = frozenset([
    "ahoj", "čau", "nazdar", "dobrý den", "dobré ráno", "dobrý večer",
    "jak se máš", "jak se máte", "jak se daří", "co děláš", "co je nového",
    "děkuji", "děkuju", "díky", "mockrát děkuji",
    "prosím", "není zač", "rádo se stalo",
    "na shledanou", "ahoj", "měj se", "pa pa", "sbohem",
    "ano", "ne", "možná", "nevím", "rozumím", "nerozumím",
    "promiň", "promiňte", "omlouvám se", "pardon",
    "dobře", "skvěle", "výborně", "super", "fajn",
    "pomoc", "pomozte", "potřebuji pomoct",
    "kde je", "kolik stojí", "kolik to stojí",
    "co to je", "jak se to řekne", "jak se řekne",
    "mluvíte anglicky", "mluvíš anglicky",
    "jsem z", "bydlím v", "jmenuji se", "jak se jmenuješ",
])

# Максимальная длина текста для кеширования common phrases
MAX_COMMON_PHRASE_LENGTH = 50


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

    def _normalize_text(self, text: str) -> str:
        """Нормализация текста для сравнения с common phrases."""
        return text.lower().strip().rstrip("?!.,;:")

    def is_common_phrase(self, user_text: str) -> bool:
        """
        Проверить, является ли текст типичной фразой.

        Args:
            user_text: Текст пользователя

        Returns:
            bool: True если это типичная фраза
        """
        if len(user_text) > MAX_COMMON_PHRASE_LENGTH:
            return False
        normalized = self._normalize_text(user_text)
        return normalized in COMMON_CZECH_PHRASES

    def create_common_phrase_cache_key(
        self, user_text: str, level: str, style: str
    ) -> str:
        """
        Создать ключ кеша для типичной фразы.

        Args:
            user_text: Текст пользователя
            level: Уровень чешского
            style: Стиль общения

        Returns:
            str: Ключ кеша
        """
        normalized = self._normalize_text(user_text)
        return f"common_phrase:{normalized}:{level}:{style}"

    async def get_cached_common_phrase(
        self, user_text: str, level: str, style: str
    ) -> dict[str, Any] | None:
        """
        Получить кешированный ответ для типичной фразы.

        Это ускоряет ответ для частых приветствий и фраз.

        Args:
            user_text: Текст пользователя
            level: Уровень чешского
            style: Стиль общения

        Returns:
            Кешированный ответ или None
        """
        if not redis_client.is_enabled:
            return None

        if not self.is_common_phrase(user_text):
            return None

        cache_key = self.create_common_phrase_cache_key(user_text, level, style)
        cached = await redis_client.get(cache_key)

        if cached:
            logger.info(
                "common_phrase_cache_hit",
                phrase=user_text[:30],
                level=level,
            )
            return cached

        return None

    async def cache_common_phrase(
        self, user_text: str, level: str, style: str, response: dict[str, Any]
    ) -> None:
        """
        Кешировать ответ для типичной фразы.

        Кешируем на 7 дней, так как ответы на приветствия редко меняются.

        Args:
            user_text: Текст пользователя
            level: Уровень чешского
            style: Стиль общения
            response: Ответ Хонзика для кеширования
        """
        if not redis_client.is_enabled:
            return

        if not self.is_common_phrase(user_text):
            return

        cache_key = self.create_common_phrase_cache_key(user_text, level, style)
        ttl = 86400 * 7  # 7 дней

        await redis_client.set(cache_key, response, ttl=ttl)
        logger.info(
            "common_phrase_cached",
            phrase=user_text[:30],
            level=level,
            ttl_days=7,
        )

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
