"""
Обработчик текстовых сообщений.

Language Immersion: Все сообщения бота на чешском.
Пользователь может писать Хонзику текстом на чешском,
а не только голосовыми сообщениями.
"""

import base64

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

    # Показываем что Хонзик печатает
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        # Отправляем текст в backend
        logger.info(
            "processing_text",
            telegram_id=telegram_id,
            text_length=len(text),
        )

        response = await api_client.process_text(
            user_id=telegram_id,
            text=text,
            include_audio=True,  # Хонзик отвечает голосом
        )

        if not response:
            await message.answer(get_text("error_backend"))
            return

        # Получаем данные из ответа
        audio_response = response.get("honzik_response_audio")
        honzik_text = response.get("honzik_response_text") or response.get(
            "honzik_response_transcript", ""
        )
        corrections = response.get("corrections", {}) or {}
        correctness_score = corrections.get("correctness_score", 0)
        streak = response.get("current_streak", 0)
        stars_earned = response.get("stars_earned", 0)

        # Отправляем ответ Хонзика
        if audio_response:
            # Если есть аудио - отправляем голосовое
            audio_bytes = base64.b64decode(audio_response)
            voice_file = BufferedInputFile(audio_bytes, filename="honzik.ogg")

            # Caption с результатами (на чешском)
            caption = f"{get_text('voice_correctness', score=correctness_score)}"

            # Создаём кнопки
            buttons = []

            # WebApp кнопка "Text" для открытия страницы с текстом ответа
            if honzik_text:
                # Кодируем текст для URL
                encoded_text = urllib.parse.quote(honzik_text, safe="")
                webui_url = f"{config.webui_url}/response?text={encoded_text}"

                text_button = InlineKeyboardButton(
                    text=get_text("btn_show_text"),
                    web_app=WebAppInfo(url=webui_url)
                )
                buttons.append(text_button)

            # Создаём клавиатуру только если есть кнопки
            keyboard = None
            if buttons:
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[buttons]
                )

            await message.answer_voice(
                voice=voice_file,
                caption=caption,
                reply_markup=keyboard
            )
        else:
            # Если нет аудио - просто текст
            response_text = f"🗣️ <b>Honzík:</b>\n{honzik_text}\n\n"
            response_text += f"{get_text('voice_correctness', score=correctness_score)}"

            await message.answer(response_text, parse_mode="HTML")

        # Показываем исправления если есть
        mistakes = corrections.get("mistakes", [])
        if mistakes:
            corrections_text = get_text("corrections_header")

            for mistake in mistakes[:3]:  # Показываем только первые 3 ошибки
                original = mistake.get("original", "")
                corrected = mistake.get("corrected", "")

                # Новый формат с explanation_cs
                explanation_cs = mistake.get("explanation_cs", "")

                # Fallback на старый формат
                if not explanation_cs and "explanation" in mistake:
                    explanation_cs = mistake.get("explanation", "")

                corrections_text += f"❌ <i>{original}</i>\n"
                corrections_text += f"✅ <b>{corrected}</b>\n"
                if explanation_cs:
                    corrections_text += f"💡 {explanation_cs}\n"
                corrections_text += "\n"

            await message.answer(corrections_text, parse_mode="HTML")
        else:
            await message.answer(get_text("no_corrections"))

        # Показываем совет если есть
        suggestion = corrections.get("suggestion")
        if suggestion:
            await message.answer(
                get_text("suggestion", suggestion=suggestion),
                parse_mode="HTML",
            )

        # Если заработали звезды - показываем
        if stars_earned > 0:
            await message.answer(
                get_text("voice_stars_earned", stars=stars_earned)
            )

        logger.info(
            "text_processed",
            telegram_id=telegram_id,
            score=correctness_score,
            streak=streak,
            stars=stars_earned,
        )

    except Exception as e:
        logger.error("text_processing_error", telegram_id=telegram_id, error=str(e))
        await message.answer(get_text("error_general"))
