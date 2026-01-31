"""
Application configuration using Pydantic Settings.
Загружает переменные окружения для Railway.com и локальной разработки.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки приложения с автоматической загрузкой из переменных окружения.

    Railway.com автоматически предоставляет DATABASE_URL для PostgreSQL.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./temp.db",
        description="Database connection string (PostgreSQL or SQLite for testing)"
    )

    # OpenAI
    openai_api_key: str = Field(
        description="OpenAI API key for GPT-4o, Whisper, and TTS"
    )

    # Telegram
    telegram_bot_token: str = Field(
        default="7471812936:AAFoji4k74oAo347ahNaa1K1WAPtiSQ_ox8",
        description="Telegram Bot API token"
    )

    # Application
    environment: Literal["development", "production", "testing"] = Field(
        default="development",
        description="Application environment"
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )

    port: int = Field(
        default=8000,
        description="Port for FastAPI server (Railway sets this automatically)"
    )

    frontend_port: int = Field(
        default=3000,
        description="Port for Next.js frontend"
    )

    # Redis Cache
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )

    redis_max_connections: int = Field(
        default=50,
        description="Maximum connections in Redis pool"
    )

    cache_enabled: bool = Field(
        default=True,
        description="Enable Redis caching"
    )

    redis_cache_ttl_default: int = Field(
        default=3600,
        description="Default cache TTL in seconds (1 hour)"
    )

    redis_cache_ttl_user: int = Field(
        default=3600,
        description="User data cache TTL in seconds (1 hour)"
    )

    redis_cache_ttl_stats: int = Field(
        default=900,
        description="Stats cache TTL in seconds (15 minutes)"
    )

    redis_cache_ttl_openai: int = Field(
        default=86400,
        description="OpenAI response cache TTL in seconds (24 hours)"
    )

    # API Configuration
    max_voice_duration: int = Field(
        default=60,
        description="Maximum voice message duration in seconds"
    )

    rate_limit_per_minute: int = Field(
        default=20,
        description="Maximum API requests per user per minute"
    )

    # OpenAI Configuration
    openai_model: str = Field(
        default="gpt-4o",
        description="OpenAI model for Honzik personality"
    )

    openai_model_simple: str = Field(
        default="gpt-3.5-turbo",
        description="Simpler/cheaper model for beginners"
    )

    openai_model_fast: str = Field(
        default="gpt-4o-mini",
        description="Fast model for quick responses (2x faster than gpt-4o)"
    )

    use_adaptive_model_selection: bool = Field(
        default=True,
        description="Use cheaper models for beginners (A1, A2 levels)"
    )

    openai_temperature: float = Field(
        default=0.8,
        description="Temperature for GPT responses (higher = more creative)"
    )

    whisper_model: str = Field(
        default="whisper-1",
        description="Whisper model for speech-to-text"
    )

    tts_model: str = Field(
        default="tts-1",
        description="TTS model for text-to-speech"
    )

    tts_voice: str = Field(
        default="alloy",
        description="Voice for Honzik (alloy or onyx)"
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing."""
        return self.environment == "testing"

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_environment(cls, value: str) -> str:
        """
        Normalize environment value to lowercase and validate allowed options.

        Railway may pass values with different casing (e.g., "Production").
        This ensures they are accepted while preserving strict choices.
        """
        if not isinstance(value, str):
            raise ValueError("environment must be a string")
        value_normalized = value.lower()
        allowed = {"development", "production", "testing"}
        if value_normalized not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return value_normalized


@lru_cache
def get_settings() -> Settings:
    """
    Получить настройки приложения (с кешированием).

    Returns:
        Settings: Настройки приложения
    """
    return Settings()

