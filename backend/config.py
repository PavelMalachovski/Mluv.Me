"""
Application configuration using Pydantic Settings.
Загружает переменные окружения для Railway.com и локальной разработки.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
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


@lru_cache
def get_settings() -> Settings:
    """
    Получить настройки приложения (с кешированием).

    Returns:
        Settings: Настройки приложения
    """
    return Settings()

