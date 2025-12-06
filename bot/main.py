"""
Главный модуль Telegram бота Mluv.Me.
"""

import asyncio
import sys

import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import config
from bot.handlers import get_main_router
from bot.services.api_client import APIClient

# Настройка логирования
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()


async def main() -> None:
    """Главная функция запуска бота."""
    logger.info(
        "bot_starting",
        environment=config.environment,
        backend_url=config.backend_api_url,
    )

    # Создаем бота
    bot = Bot(
        token=config.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Создаем диспетчер
    dp = Dispatcher()

    # Создаем API клиент
    api_client = APIClient(config.backend_api_url)

    # Регистрируем роутеры
    main_router = get_main_router()
    dp.include_router(main_router)

    # Middleware для передачи api_client в handlers
    @dp.update.outer_middleware()
    async def api_client_middleware(handler, event, data):
        """Middleware для добавления api_client в данные."""
        data["api_client"] = api_client
        return await handler(event, data)

    try:
        # Удаляем webhook если был установлен
        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("bot_started", mode="polling")

        # Запускаем polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as e:
        logger.error("bot_error", error=str(e))
        raise
    finally:
        await api_client.close()
        await bot.session.close()
        logger.info("bot_stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("bot_stopped_by_user")
        sys.exit(0)
    except Exception as e:
        logger.error("bot_fatal_error", error=str(e))
        sys.exit(1)
