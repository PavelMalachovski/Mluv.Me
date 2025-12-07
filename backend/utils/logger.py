"""
Structured logging configuration using structlog.

Обеспечивает единообразное логирование для Railway.com и локальной разработки.
"""

import logging
import sys

import structlog
from structlog.types import FilteringBoundLogger

from backend.config import get_settings

settings = get_settings()


def configure_logging() -> None:
    """
    Настройка structlog для приложения.

    Railway.com автоматически собирает stdout/stderr,
    поэтому используем JSON формат для production.
    """
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_development:
        # Красивый вывод для разработки
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer()
        ]
    else:
        # JSON для production (Railway.com)
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Настройка стандартного logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )


def get_logger(name: str) -> FilteringBoundLogger:
    """
    Получить logger для модуля.

    Args:
        name: Имя модуля (обычно __name__)

    Returns:
        Настроенный structlog logger

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_registered", user_id=123, telegram_id=456789)
    """
    return structlog.get_logger(name)


# Инициализация при импорте
configure_logging()
