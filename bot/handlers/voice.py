"""
Обработчик голосовых сообщений.

Language Immersion: Все сообщения бота на чешском.
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


@router.message(F.voice)
async def handle_voice(message: Message, api_client: APIClient) -> None:
    """
    Обработчик голосовых сообщений.

    Args:
        message: Сообщение с голосовым
        api_client: API клиент для общения с backend
    """
    telegram_id = message.from_user.id

    # Получаем пользователя
    user = await api_client.get_user(telegram_id)
    if not user:
        await message.answer(get_text("error_general"))
        return

    # Проверяем длительность голосового (максимум 60 секунд)
    if message.voice.duration > 60:
        await message.answer(get_text("error_voice_too_long"))
        return

    # Quota check (voice)
    quota = await api_client.check_quota(telegram_id, "voice")
    if quota and not quota.get("allowed", True):
        await message.answer(
            get_limit_reached_text("voice"),
            parse_mode="HTML",
            reply_markup=get_subscription_keyboard(),
        )
        return

    # Keep "recording" indicator alive during the backend round-trip
    action_stop = asyncio.Event()
    _action_task = asyncio.create_task(  # noqa: F841 – prevent GC
        keep_chat_action(message.bot, message.chat.id, "record_voice", action_stop)
    )

    try:
        # Скачиваем аудио файл
        file = await message.bot.get_file(message.voice.file_id)
        audio_bytes = await message.bot.download_file(file.file_path)

        # STEP 1: Анализ БЕЗ TTS (быстро: STT + GPT ≈ 3-6с);
        # backend при этом прогревает озвучку в фоне
        logger.info(
            "processing_voice",
            telegram_id=telegram_id,
            duration=message.voice.duration,
        )

        response = await api_client.process_voice(
            user_id=telegram_id,
            audio_bytes=audio_bytes.read(),
            filename="voice.ogg",
            include_audio=False,  # ⚡ TTS придёт вторым запросом из кеша
        )

        action_stop.set()

        if not response:
            await message.answer(get_text("error_backend"))
            return

        # Уведомление, если пользователь говорил не на чешском
        language_notice = response.get("language_notice")
        if language_notice:
            await message.answer(language_notice)
            logger.info(
                "language_notice_shown",
                telegram_id=telegram_id,
                detected_language=response.get("detected_language", "cs"),
            )

        await send_lesson_reply(message, api_client, response)

        logger.info(
            "voice_processed",
            telegram_id=telegram_id,
            score=(response.get("corrections") or {}).get("correctness_score", 0),
            streak=response.get("current_streak", 0),
            stars=response.get("stars_earned", 0),
        )

    except Exception as e:
        action_stop.set()
        logger.error("voice_processing_error", telegram_id=telegram_id, error=str(e))
        await message.answer(get_text("error_general"))
