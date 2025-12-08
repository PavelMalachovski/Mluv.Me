"""
Обработчик голосовых сообщений.
"""

import base64
import io
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

# Временное хранилище текстовых ответов Хонзика (telegram_id -> text)
# Используется для передачи текста в WebUI через URL
honzik_text_storage: dict[int, str] = {}



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
        await message.answer(get_text("error_general", "ru"))
        return

    language = user.get("ui_language", "ru")

    # Проверяем длительность голосового (максимум 60 секунд)
    if message.voice.duration > 60:
        await message.answer(get_text("error_voice_too_long", language))
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
            await message.answer(get_text("error_backend", language))
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

                # Создаем caption с результатами
                caption = (
                    f"{get_text('voice_correctness', language, score=correctness_score)}\n"
                )
                caption += f"{get_text('voice_streak', language, streak=streak)}"

                # Сохраняем текстовый ответ Хонзика для этого пользователя
                if honzik_text:
                    honzik_text_storage[telegram_id] = honzik_text

                # Создаем кнопку "Текст" которая открывает WebUI
                encoded_text = urllib.parse.quote(honzik_text)
                webui_url_with_text = f"{config.webui_url}/response?text={encoded_text}"

                text_button = InlineKeyboardButton(
                    text=get_text("btn_show_text", language),
                    web_app=WebAppInfo(url=webui_url_with_text)
                )
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[[text_button]]
                )

                # Отправляем голосовое сообщение с кнопкой
                await message.answer_voice(
                    voice=voice_file, caption=caption, reply_markup=keyboard
                )

        # Показываем исправления если есть
        mistakes = corrections.get("mistakes", [])
        if mistakes:
            corrections_text = get_text("corrections_header", language)

            for mistake in mistakes[:3]:  # Показываем только первые 3 ошибки
                corrections_text += get_text(
                    "correction_item",
                    language,
                    original=mistake.get("original", ""),
                    corrected=mistake.get("corrected", ""),
                    explanation=mistake.get("explanation", ""),
                )

            await message.answer(corrections_text, parse_mode="HTML")
        else:
            await message.answer(get_text("no_corrections", language))

        # Показываем совет если есть
        suggestion = corrections.get("suggestion")
        if suggestion:
            await message.answer(
                get_text("suggestion", language, suggestion=suggestion),
                parse_mode="HTML",
            )

        # Если заработали звезды - показываем
        if stars_earned > 0:
            await message.answer(
                get_text("voice_stars_earned", language, stars=stars_earned)
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
        await message.answer(get_text("error_general", language))


