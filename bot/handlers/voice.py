"""
Обработчик голосовых сообщений.

Language Immersion: Все сообщения бота на чешском.
Объяснения ошибок на простом чешском + перевод на родной язык.
"""

import asyncio
import time
import urllib.parse

from aiogram import F, Router
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
import structlog

from bot.config import config
from bot.localization import get_text
from bot.services.api_client import APIClient

router = Router()
logger = structlog.get_logger()

# Temporary storage for corrections (sent only on Opravy button press)
# Key: "chat_id:message_id", Value: {"mistakes": [...], "suggestion": str, "timestamp": float}
_corrections_cache: dict[str, dict] = {}
_CACHE_TTL = 3600  # 1 hour
_CACHE_MAX_SIZE = 1000


def _cleanup_old_corrections():
    """Remove corrections older than TTL and enforce max size."""
    now = time.time()
    expired = [k for k, v in _corrections_cache.items() if now - v["timestamp"] > _CACHE_TTL]
    for k in expired:
        del _corrections_cache[k]
    # If still over cap, drop oldest entries
    while len(_corrections_cache) > _CACHE_MAX_SIZE:
        oldest = min(_corrections_cache, key=lambda k: _corrections_cache[k]["timestamp"])
        del _corrections_cache[oldest]


async def _keep_chat_action(bot, chat_id: int, action: str, stop: asyncio.Event):
    """Refresh chat_action every 4s so the typing/recording indicator stays visible."""
    while not stop.is_set():
        try:
            await bot.send_chat_action(chat_id=chat_id, action=action)
        except Exception:
            break
        try:
            await asyncio.wait_for(stop.wait(), timeout=4.0)
        except asyncio.TimeoutError:
            pass


@router.message(F.voice)
async def handle_voice(message: Message, api_client: APIClient) -> None:
    """
    Обработчик голосовых сообщений.

    Language Immersion: Все сообщения на чешском.

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
    from bot.handlers.payments import get_subscription_keyboard, get_limit_reached_text
    quota = await api_client.check_quota(telegram_id, "voice")
    if quota and not quota.get("allowed", True):
        await message.answer(
            get_limit_reached_text("voice"),
            parse_mode="HTML",
            reply_markup=get_subscription_keyboard(),
        )
        return

    # Keep "recording" indicator alive during the entire backend round-trip
    action_stop = asyncio.Event()
    _action_task = asyncio.create_task(  # noqa: F841 – prevent GC
        _keep_chat_action(message.bot, message.chat.id, "record_voice", action_stop)
    )

    try:
        # Скачиваем аудио файл
        file = await message.bot.get_file(message.voice.file_id)
        audio_bytes = await message.bot.download_file(file.file_path)

        # ========================================
        # STEP 1: Анализ БЕЗ TTS (быстро: STT + GPT ≈ 3-6с)
        # ========================================
        logger.info(
            "processing_voice",
            telegram_id=telegram_id,
            duration=message.voice.duration,
        )

        response = await api_client.process_voice(
            user_id=telegram_id,
            audio_bytes=audio_bytes.read(),
            filename="voice.ogg",
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
        streak = response.get("current_streak", response.get("streak", 0))
        stars_earned = response.get("stars_earned", 0)

        # Получаем информацию о языке
        language_notice = response.get("language_notice")
        detected_language = response.get("detected_language", "cs")

        # Если пользователь говорил не на чешском - показываем уведомление (на чешском)
        if language_notice:
            await message.answer(language_notice)
            logger.info(
                "language_notice_shown",
                telegram_id=telegram_id,
                detected_language=detected_language,
            )

        # Extract corrections data for deferred sending via Opravy button
        mistakes = corrections.get("mistakes", [])
        suggestion = corrections.get("suggestion")

        # ⚡ Stop the "recording" indicator — analysis is ready
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
                voice_file = BufferedInputFile(
                    audio_bytes_response, filename="honzik.ogg"
                )

                # Создаём кнопки для голосового сообщения
                buttons = []

                # WebApp кнопка "Text" для открытия страницы с текстом ответа
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

                # Отправляем голосовое сообщение с кнопками
                await message.answer_voice(
                    voice=voice_file, reply_markup=keyboard
                )

        logger.info(
            "voice_processed",
            telegram_id=telegram_id,
            score=correctness_score,
            streak=streak,
            stars=stars_earned,
        )

    except Exception as e:
        action_stop.set()
        logger.error("voice_processing_error", telegram_id=telegram_id, error=str(e))
        await message.answer(get_text("error_general"))


@router.callback_query(F.data.startswith("opravy:"))
async def handle_opravy_callback(callback: CallbackQuery) -> None:
    """
    Send corrections and tips when Opravy button is pressed.

    Retrieves cached corrections data and sends it as messages.
    """
    msg_id = callback.data.split(":", 1)[1]
    cache_key = f"{callback.message.chat.id}:{msg_id}"
    data = _corrections_cache.get(cache_key)

    if not data:
        await callback.answer("⏰ Opravy již nejsou k dispozici", show_alert=True)
        return

    mistakes = data.get("mistakes", [])
    suggestion = data.get("suggestion")

    # Send corrections if any
    if mistakes:
        corrections_text = get_text("corrections_header")

        for mistake in mistakes[:3]:
            original = mistake.get("original", "")
            corrected = mistake.get("corrected", "")
            explanation_cs = mistake.get("explanation_cs", "")
            if not explanation_cs and "explanation" in mistake:
                explanation_cs = mistake.get("explanation", "")

            corrections_text += f"❌ <i>{original}</i>\n"
            corrections_text += f"✅ <b>{corrected}</b>\n"
            if explanation_cs:
                corrections_text += f"💡 {explanation_cs}\n"
            corrections_text += "\n"

        await callback.message.answer(corrections_text, parse_mode="HTML")

    # Send suggestion/tip if any
    if suggestion:
        await callback.message.answer(
            get_text("suggestion", suggestion=suggestion),
            parse_mode="HTML",
        )

    # Remove from cache after showing
    _corrections_cache.pop(cache_key, None)
    await callback.answer()
