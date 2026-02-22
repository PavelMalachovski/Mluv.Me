"""
Модуль обработчиков для Telegram бота.
"""

from aiogram import Router

from . import commands, start, text, voice, payments


def get_main_router() -> Router:
    """
    Получить главный роутер со всеми обработчиками.

    Returns:
        Router с подключенными обработчиками
    """
    main_router = Router()

    # Порядок важен!
    # 1. start - регистрация и онбординг
    # 2. commands - команды /help, /stats и т.д.
    # 3. payments - Telegram Stars (pre_checkout, successful_payment, buy: callbacks)
    # 4. voice - голосовые сообщения
    # 5. text - текстовые сообщения (должен быть последним, т.к. ловит все текстовые)
    main_router.include_router(start.router)
    main_router.include_router(commands.router)
    main_router.include_router(payments.router)
    main_router.include_router(voice.router)
    main_router.include_router(text.router)

    return main_router


__all__ = ["get_main_router"]


