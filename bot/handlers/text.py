"""
Обработчик текстовых сообщений.

Language Immersion: Все сообщения бота на чешском.
Пользователь может писать Хонзику текстом на чешском,
а не только голосовыми сообщениями.
"""

import asyncio
import time
import urllib.parse

from aiogram import F, Router
from aiogram.types import (
    BufferedInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
import structlog

from bot.config import config
from bot.handlers.voice import _corrections_cache, _cleanup_old_corrections, _keep_chat_action
from bot.handlers.payments import get_subscription_keyboard, get_limit_reached_text
from bot.localization import get_text
from bot.services.api_client import APIClient

router = Router()
logger = structlog.get_logger()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message, api_client: APIClient) -> None:
    """
    Обработчик текстовых сообщений (не команд).

    Пользователь может писать Хонзику текстом на чешском.
    Language Immersion: Все сообщения на чешском.

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

    # Keep "typing" indicator alive during the entire backend round-trip
    action_stop = asyncio.Event()
    _action_task = asyncio.create_task(  # noqa: F841 – prevent GC
        _keep_chat_action(message.bot, message.chat.id, "typing", action_stop)
    )

    try:
        # ========================================
        # STEP 1: Анализ БЕЗ TTS (быстро: GPT ≈ 2-4с)
        # ========================================
        logger.info(
            "processing_text",
            telegram_id=telegram_id,
            text_length=len(text),
        )

        response = await api_client.process_text(
            user_id=telegram_id,
            text=text,
            include_audio=False,  # ⚡ Skip TTS — saves 2-4 seconds
        )

        if not response:
            action_stop.set()
            await message.answer(get_text("error_backend"))
            return

        # Получаем данные из ответа
        honzik_text = response.get("honzik_response_text") or response.get(
            "honzik_response_transcript", ""
        )
        corrections = response.get("corrections", {}) or {}
        correctness_score = corrections.get("correctness_score", 0)
        streak = response.get("current_streak", 0)
        stars_earned = response.get("stars_earned", 0)

        # Extract corrections data for deferred sending via Opravy button
        mistakes = corrections.get("mistakes", [])
        suggestion = corrections.get("suggestion")

        # ⚡ Stop the "typing" indicator — analysis is ready
        action_stop.set()

        # ⚡ INSTANT: Send správnost — user sees result immediately
        score_parts = [get_text('voice_correctness', score=correctness_score)]
        if stars_earned > 0:
            score_parts.append(get_text('voice_stars_earned', stars=stars_earned))
        if not mistakes:
            score_parts.append(get_text('no_corrections'))
        await message.answer("\n".join(score_parts), parse_mode="HTML")

        # ========================================
        # STEP 2: TTS в отдельном запросе (пока пользователь читает správnost)
        # ========================================
        if honzik_text:
            # Show "recording voice" while TTS generates
            action_stop2 = asyncio.Event()
            _action_task2 = asyncio.create_task(  # noqa: F841 – prevent GC
                _keep_chat_action(message.bot, message.chat.id, "record_voice", action_stop2)
            )

            try:
                audio_bytes_response = await api_client.generate_tts(
                    user_id=telegram_id,
                    text=honzik_text,
                )
            finally:
                action_stop2.set()

            if audio_bytes_response:
                voice_file = BufferedInputFile(audio_bytes_response, filename="honzik.ogg")

                # Создаём кнопки
                buttons = []

                # WebApp кнопка "Text"
                encoded_text = urllib.parse.quote(honzik_text, safe="")
                webui_url = f"{config.webui_url}/response?text={encoded_text}"
                text_button = InlineKeyboardButton(
                    text=get_text("btn_show_text"),
                    web_app=WebAppInfo(url=webui_url)
                )
                buttons.append(text_button)

                # Кнопка "Opravy" — corrections & tips sent on press
                if mistakes or suggestion:
                    _cleanup_old_corrections()
                    cache_key = f"{message.chat.id}:{message.message_id}"
                    _corrections_cache[cache_key] = {
                        "mistakes": mistakes[:3],
                        "suggestion": suggestion,
                        "timestamp": time.time(),
                    }
                    opravy_button = InlineKeyboardButton(
                        text=get_text("btn_show_opravy"),
                        callback_data=f"opravy:{message.message_id}",
                    )
                    buttons.append(opravy_button)

                keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

                await message.answer_voice(
                    voice=voice_file,
                    reply_markup=keyboard
                )
            else:
                # TTS не удался — отправляем текстом
                response_text = f"🗣️ <b>Honzík:</b>\n{honzik_text}"

                keyboard = None
                if mistakes or suggestion:
                    _cleanup_old_corrections()
                    cache_key = f"{message.chat.id}:{message.message_id}"
                    _corrections_cache[cache_key] = {
                        "mistakes": mistakes[:3],
                        "suggestion": suggestion,
                        "timestamp": time.time(),
                    }
                    opravy_button = InlineKeyboardButton(
                        text=get_text("btn_show_opravy"),
                        callback_data=f"opravy:{message.message_id}",
                    )
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[[opravy_button]]
                    )

                await message.answer(response_text, parse_mode="HTML", reply_markup=keyboard)

        logger.info(
            "text_processed",
            telegram_id=telegram_id,
            score=correctness_score,
            streak=streak,
            stars=stars_earned,
        )

    except Exception as e:
        action_stop.set()
        logger.error("text_processing_error", telegram_id=telegram_id, error=str(e))
        await message.answer(get_text("error_general"))
