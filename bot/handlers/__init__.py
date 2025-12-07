"""
Модуль обработчиков для Telegram бота.
"""

from aiogram import Router

from . import commands, start, voice


def get_main_router() -> Router:
    """
    Получить главный роутер со всеми обработчиками.

    Returns:
        Router с подключенными обработчиками
    """
    main_router = Router()

    # Порядок важен! start должен быть первым
    main_router.include_router(start.router)
    main_router.include_router(commands.router)
    main_router.include_router(voice.router)

    return main_router


__all__ = ["get_main_router"]


