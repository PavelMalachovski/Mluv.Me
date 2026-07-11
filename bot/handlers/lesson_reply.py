"""
Общая логика ответа на урок (голос и текст).

Оба хендлера (voice.py, text.py) после получения анализа от backend
делают одно и то же:
1. Мгновенно отправляют správnost (оценку и звёзды)
2. Запрашивают озвучку отдельным запросом /tts (backend её уже прогрел)
3. Отправляют голосовое сообщение с кнопками «Text» и «Opravy»
4. Если TTS не удался — отправляют ответ Хонзика текстом

Opravy не отправляются сразу: они кладутся во временный кеш и уходят
пользователю только по нажатию кнопки (callback обрабатывается здесь же).
"""

import asyncio
import time
import urllib.parse

import structlog
from aiogram import F, Router
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

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


def _cleanup_old_corrections() -> None:
    """Remove corrections older than TTL and enforce max size."""
    now = time.time()
    expired = [
        k for k, v in _corrections_cache.items() if now - v["timestamp"] > _CACHE_TTL
    ]
    for k in expired:
        del _corrections_cache[k]
    # If still over cap, drop oldest entries
    while len(_corrections_cache) > _CACHE_MAX_SIZE:
        oldest = min(
            _corrections_cache, key=lambda k: _corrections_cache[k]["timestamp"]
        )
        del _corrections_cache[oldest]


async def keep_chat_action(bot, chat_id: int, action: str, stop: asyncio.Event) -> None:
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


def _build_opravy_button(
    message: Message, mistakes: list, suggestion: str | None
) -> InlineKeyboardButton | None:
    """Закешировать opravy и вернуть кнопку для их показа (или None)."""
    if not mistakes and not suggestion:
        return None

    _cleanup_old_corrections()
    cache_key = f"{message.chat.id}:{message.message_id}"
    _corrections_cache[cache_key] = {
        "mistakes": mistakes[:3],
        "suggestion": suggestion,
        "timestamp": time.time(),
    }
    return InlineKeyboardButton(
        text=get_text("btn_show_opravy"),
        callback_data=f"opravy:{message.message_id}",
    )


async def send_lesson_reply(
    message: Message, api_client: APIClient, response: dict
) -> None:
    """
    Отправить пользователю результат урока: správnost, затем голос Хонзика.

    Args:
        message: Исходное сообщение пользователя
        api_client: API клиент backend
        response: Ответ эндпоинта /process или /process/text (без аудио)
    """
    telegram_id = message.from_user.id

    honzik_text = response.get("honzik_response_text") or response.get(
        "honzik_response_transcript", ""
    )
    corrections = response.get("corrections", {}) or {}
    correctness_score = corrections.get("correctness_score", 0)
    stars_earned = response.get("stars_earned", 0)
    mistakes = corrections.get("mistakes", [])
    suggestion = corrections.get("suggestion")

    # ⚡ INSTANT: Send správnost — user sees result immediately
    score_parts = [get_text("voice_correctness", score=correctness_score)]
    if stars_earned > 0:
        score_parts.append(get_text("voice_stars_earned", stars=stars_earned))
    if not mistakes:
        score_parts.append(get_text("no_corrections"))
    await message.answer("\n".join(score_parts), parse_mode="HTML")

    if not honzik_text:
        return

    # STEP 2: TTS отдельным запросом (пока пользователь читает správnost;
    # backend уже прогрел озвучку в фоне, поэтому обычно это cache hit)
    action_stop = asyncio.Event()
    action_task = asyncio.create_task(  # noqa: F841 – prevent GC
        keep_chat_action(message.bot, message.chat.id, "record_voice", action_stop)
    )
    try:
        audio_bytes = await api_client.generate_tts(
            user_id=telegram_id, text=honzik_text
        )
    except Exception as e:
        logger.warning("tts_request_failed", telegram_id=telegram_id, error=str(e))
        audio_bytes = None
    finally:
        action_stop.set()

    # Кнопки: «Text» (WebApp с текстом ответа) и «Opravy» (по нажатию)
    encoded_text = urllib.parse.quote(honzik_text, safe="")
    text_button = InlineKeyboardButton(
        text=get_text("btn_show_text"),
        web_app=WebAppInfo(url=f"{config.webui_url}/response?text={encoded_text}"),
    )
    buttons = [text_button]
    opravy_button = _build_opravy_button(message, mistakes, suggestion)
    if opravy_button:
        buttons.append(opravy_button)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

    if audio_bytes:
        voice_file = BufferedInputFile(audio_bytes, filename="honzik.ogg")
        await message.answer_voice(voice=voice_file, reply_markup=keyboard)
    else:
        # TTS не удался — отправляем ответ Хонзика текстом
        await message.answer(
            f"🗣️ <b>Honzík:</b>\n{honzik_text}",
            parse_mode="HTML",
            reply_markup=keyboard,
        )


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
