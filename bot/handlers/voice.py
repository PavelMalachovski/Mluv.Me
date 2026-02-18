"""
Обработчик голосовых сообщений.

Language Immersion: Все сообщения бота на чешском.
Объяснения ошибок на простом чешском + перевод на родной язык.
"""

import base64
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

    # Показываем что Хонзик записывает голосовой ответ
    await message.bot.send_chat_action(chat_id=message.chat.id, action="record_voice")

    try:
        # Скачиваем аудио файл
        file = await message.bot.get_file(message.voice.file_id)
        audio_bytes = await message.bot.download_file(file.file_path)

        # Отправляем в backend для обработки
        logger.info(
            "processing_voice",
            telegram_id=telegram_id,
            duration=message.voice.duration,
        )

        response = await api_client.process_voice(
            user_id=telegram_id,
            audio_bytes=audio_bytes.read(),
            filename="voice.ogg",
        )

        if not response:
            await message.answer(get_text("error_backend"))
            return

        # Получаем данные из ответа
        audio_response = response.get("honzik_response_audio") or response.get(
            "audio_response"
        )
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

        # Отправляем голосовой ответ Хонзика
        if audio_response is not None:
            audio_bytes_response = None
            if isinstance(audio_response, str):
                audio_bytes_response = base64.b64decode(audio_response)
            elif isinstance(audio_response, bytes):
                audio_bytes_response = audio_response

            if audio_bytes_response:
                voice_file = BufferedInputFile(
                    audio_bytes_response, filename="honzik.ogg"
                )

                # Caption: Správnost + stars + praise if perfect
                caption = f"{get_text('voice_correctness', score=correctness_score)}"
                if stars_earned > 0:
                    caption += f"\n{get_text('voice_stars_earned', stars=stars_earned)}"
                if not mistakes:
                    caption += f"\n{get_text('no_corrections')}"

                # Создаём кнопки для голосового сообщения
                buttons = []

                # WebApp кнопка "Text" для открытия страницы с текстом ответа
                if honzik_text:
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

                # Создаём клавиатуру только если есть кнопки
                keyboard = None
                if buttons:
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[buttons]
                    )

                # Отправляем голосовое сообщение с кнопкой
                await message.answer_voice(
                    voice=voice_file, caption=caption, reply_markup=keyboard
                )

        logger.info(
            "voice_processed",
            telegram_id=telegram_id,
            score=correctness_score,
            streak=streak,
            stars=stars_earned,
        )

    except Exception as e:
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
