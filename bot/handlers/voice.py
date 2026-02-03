"""
Обработчик голосовых сообщений.

Language Immersion: Все сообщения бота на чешском.
Объяснения ошибок на простом чешском + перевод на родной язык.
"""

import base64

from aiogram import F, Router
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
import structlog

from bot.localization import get_text
from bot.services.api_client import APIClient

router = Router()
logger = structlog.get_logger()

# Временное хранилище текстовых ответов Хонзика (telegram_id -> text)
# Используется для показа текста через callback кнопку
honzik_text_storage: dict[int, str] = {}



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

                # Создаем caption с результатами (на чешском)
                caption = f"{get_text('voice_correctness', score=correctness_score)}\n"
                caption += get_text("voice_streak", streak=streak)

                # Сохраняем текстовый ответ Хонзика для этого пользователя
                if honzik_text:
                    honzik_text_storage[telegram_id] = honzik_text

                # Callback кнопка "Text" для показа текста
                text_button = InlineKeyboardButton(
                    text=get_text("btn_show_text"),
                    callback_data=f"show_text:{telegram_id}"
                )
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[[text_button]]
                )

                # Отправляем голосовое сообщение с кнопкой
                await message.answer_voice(
                    voice=voice_file, caption=caption, reply_markup=keyboard
                )

        # Показываем исправления если есть (новый формат с двуязычными объяснениями)
        mistakes = corrections.get("mistakes", [])
        if mistakes:
            corrections_text = get_text("corrections_header")

            for mistake in mistakes[:3]:  # Показываем только первые 3 ошибки
                original = mistake.get("original", "")
                corrected = mistake.get("corrected", "")

                # Новый формат с explanation_cs и explanation_native
                explanation_cs = mistake.get("explanation_cs", "")
                explanation_native = mistake.get("explanation_native", "")

                # Fallback на старый формат
                if not explanation_cs and "explanation" in mistake:
                    explanation_cs = mistake.get("explanation", "")

                corrections_text += f"❌ <i>{original}</i>\n"
                corrections_text += f"✅ <b>{corrected}</b>\n"
                if explanation_cs:
                    corrections_text += f"💡 {explanation_cs}\n"
                if explanation_native:
                    corrections_text += f"🌐 {explanation_native}\n"
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
            "voice_processed",
            telegram_id=telegram_id,
            score=correctness_score,
            streak=streak,
            stars=stars_earned,
        )

    except Exception as e:
        logger.error("voice_processing_error", telegram_id=telegram_id, error=str(e))
        await message.answer(get_text("error_general"))


@router.callback_query(F.data.startswith("show_text:"))
async def show_honzik_text(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Callback handler для кнопки "Text".

    Показывает текстовый ответ Хонзика прямо в Telegram без открытия WebApp.
    Language Immersion: Сообщение на чешском.

    Args:
        callback: Callback query от кнопки
        api_client: API клиент
    """
    telegram_id = callback.from_user.id

    # Получаем сохранённый текст
    honzik_text = honzik_text_storage.get(telegram_id)

    if honzik_text:
        # Отправляем текст как reply на голосовое сообщение (на чешском)
        await callback.message.reply(
            get_text("honzik_text_response", text=honzik_text),
            parse_mode="HTML",
        )

        logger.info(
            "text_shown_via_callback",
            telegram_id=telegram_id,
            text_length=len(honzik_text),
        )
    else:
        # Текст не найден - сообщение на чешском
        await callback.answer(
            "Text není k dispozici. Pošli novou zprávu!",
            show_alert=True
        )

    # Закрываем callback (убираем loading)
    await callback.answer()
