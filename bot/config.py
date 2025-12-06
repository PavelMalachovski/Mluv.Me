"""
Конфигурация Telegram бота.
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    """Настройки Telegram бота."""

    # Telegram Bot Token
    telegram_bot_token: str = os.getenv(
        "TELEGRAM_BOT_TOKEN", "7471812936:AAFoji4k74oAo347ahNaa1K1WAPtiSQ_ox8"
    )

    # Backend API URL
    backend_api_url: str = os.getenv("BACKEND_API_URL", "http://localhost:8000")

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Webhook settings (для Railway)
    webhook_url: Optional[str] = os.getenv("WEBHOOK_URL", None)
    webhook_path: str = "/webhook/bot"

    # Polling settings
    polling_timeout: int = 30

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


# Создаем глобальный экземпляр конфига
config = BotConfig()

