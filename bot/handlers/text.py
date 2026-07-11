"""
Обработчик текстовых сообщений.

Language Immersion: Все сообщения бота на чешском.
Пользователь может писать Хонзику текстом на чешском,
а не только голосовыми сообщениями.
Отправка ответа (správnost → озвучка → кнопки) — в lesson_reply.py.
"""

import asyncio

from aiogram import F, Router
from aiogram.types import Message
import structlog

from bot.handlers.lesson_reply import keep_chat_action, send_lesson_reply
from bot.handlers.payments import get_subscription_keyboard, get_limit_reached_text
from bot.localization import get_text
from bot.services.api_client import APIClient

router = Router()
logger = structlog.get_logger()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message, api_client: APIClient) -> None:
    """
    Обработчик текстовых сообщений (не команд).

    Args:
        message: Текстовое сообщение
        api_client: API клиент для общения с backend
    """
    telegram_id = message.from_user.id
    text = message.text.strip()

    # Получаем пользователя
    user = await api_client.get_user(telegram_id)
    if not user:
        await message.answer(get_text("error_general"))
        return

    # Проверка минимальной длины
    if len(text) < 2:
        await message.answer(get_text("error_text_too_short"))
        return

    # Quota check
    quota = await api_client.check_quota(telegram_id, "text")
    if quota and not quota.get("allowed", True):
        await message.answer(
            get_limit_reached_text("text"),
            parse_mode="HTML",
            reply_markup=get_subscription_keyboard(),
        )
        return

    # Keep "typing" indicator alive during the backend round-trip
    action_stop = asyncio.Event()
    _action_task = asyncio.create_task(  # noqa: F841 – prevent GC
        keep_chat_action(message.bot, message.chat.id, "typing", action_stop)
    )

    try:
        # STEP 1: Анализ БЕЗ TTS (быстро: GPT ≈ 2-4с);
        # backend при этом прогревает озвучку в фоне
        logger.info(
            "processing_text",
            telegram_id=telegram_id,
            text_length=len(text),
        )

        response = await api_client.process_text(
            user_id=telegram_id,
            text=text,
            include_audio=False,  # ⚡ TTS придёт вторым запросом из кеша
        )

        action_stop.set()

        if not response:
            await message.answer(get_text("error_backend"))
            return

        await send_lesson_reply(message, api_client, response)

        logger.info(
            "text_processed",
            telegram_id=telegram_id,
            score=(response.get("corrections") or {}).get("correctness_score", 0),
            streak=response.get("current_streak", 0),
            stars=response.get("stars_earned", 0),
        )

    except Exception as e:
        action_stop.set()
        logger.error("text_processing_error", telegram_id=telegram_id, error=str(e))
        await message.answer(get_text("error_general"))
