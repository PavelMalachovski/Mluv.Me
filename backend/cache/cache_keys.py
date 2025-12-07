"""
Centralized cache key patterns for Redis.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CacheKeys:
    """Centralized cache key patterns."""

    # User data
    USER_PROFILE: str = "user:{telegram_id}:profile"
    USER_SETTINGS: str = "user:{telegram_id}:settings"
    USER_HISTORY: str = "user:{telegram_id}:history:{limit}"

    # Statistics
    DAILY_STATS: str = "stats:{user_id}:daily:{date}"
    USER_PROGRESS: str = "stats:{user_id}:progress"
    LEADERBOARD: str = "leaderboard:{period}:{limit}"

    # OpenAI responses
    HONZIK_RESPONSE: str = "honzik:response:{hash}"
    WHISPER_TRANSCRIPTION: str = "whisper:{audio_hash}"
    TTS_AUDIO: str = "tts:{text_hash}:{voice}"

    # Vocabulary
    SAVED_WORDS: str = "words:{user_id}:all"
    WORD_DUE_REVIEW: str = "words:{user_id}:due"

    @staticmethod
    def user_profile(telegram_id: int) -> str:
        """Build cache key for user profile."""
        return CacheKeys.USER_PROFILE.format(telegram_id=telegram_id)

    @staticmethod
    def user_settings(telegram_id: int) -> str:
        """Build cache key for user settings."""
        return CacheKeys.USER_SETTINGS.format(telegram_id=telegram_id)

    @staticmethod
    def user_history(telegram_id: int, limit: int = 10) -> str:
        """Build cache key for user history."""
        return CacheKeys.USER_HISTORY.format(telegram_id=telegram_id, limit=limit)

    @staticmethod
    def honzik_response(user_text: str, settings_hash: str) -> str:
        """Create cache key for Honzik response."""
        import hashlib

        content = f"{user_text}:{settings_hash}"
        hash_key = hashlib.sha256(content.encode()).hexdigest()[:16]
        return CacheKeys.HONZIK_RESPONSE.format(hash=hash_key)

    @staticmethod
    def daily_stats(user_id: int, date: str) -> str:
        """Build cache key for daily stats."""
        return CacheKeys.DAILY_STATS.format(user_id=user_id, date=date)

