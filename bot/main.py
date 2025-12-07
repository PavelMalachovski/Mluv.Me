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
    """Главная функция запуска бота с обработкой конфликтов."""
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

    max_conflict_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_conflict_retries):
        try:
            # Удаляем webhook если был установлен
            await bot.delete_webhook(drop_pending_updates=True)

            logger.info("bot_started", mode="polling", attempt=attempt + 1)

            # Запускаем polling с обработкой конфликтов
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types(),
                handle_as_tasks=False,  # Обработка последовательно
            )

            # Если дошли сюда - polling завершился успешно
            break

        except KeyboardInterrupt:
            logger.info("bot_stopped_by_keyboard_interrupt")
            break

        except Exception as e:
            error_str = str(e)
            logger.error("bot_error", error=error_str, error_type=type(e).__name__, attempt=attempt + 1)

            # Обработка конфликта
            if "Conflict" in error_str or "terminated by other getUpdates" in error_str:
                if attempt < max_conflict_retries - 1:
                    logger.warning(
                        "bot_conflict_detected",
                        message="Another bot instance detected. Waiting before retry...",
                        retry_attempt=attempt + 1,
                        retry_delay=retry_delay
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(
                        "bot_conflict_permanent",
                        message="Multiple bot instances conflict. Stopping this instance."
                    )
                    break
            else:
                # Другие ошибки - прерываем
                logger.error("bot_fatal_error", error=error_str)
                raise

    # Cleanup
    try:
        await api_client.close()
        await bot.session.close()
        logger.info("bot_stopped")
    except Exception as e:
        logger.error("bot_cleanup_error", error=str(e))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("bot_stopped_by_user")
        sys.exit(0)
    except Exception as e:
        logger.error("bot_fatal_error", error=str(e))
        sys.exit(1)
