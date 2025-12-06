"""
Обработчики команд бота.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
import structlog

from bot.keyboards import (
    get_corrections_keyboard,
    get_level_keyboard,
    get_reset_confirm_keyboard,
    get_style_keyboard,
    get_voice_speed_keyboard,
)
from bot.localization import get_days_word, get_text
from bot.services.api_client import APIClient

router = Router()
logger = structlog.get_logger()


@router.message(Command("help"))
async def command_help(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /help.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general", "ru"))
        return

    language = user.get("ui_language", "ru")

    help_text = get_text("help_header", language)
    help_text += get_text("help_commands", language)
    help_text += get_text("help_tips", language)

    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("stats"))
async def command_stats(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /stats.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general", "ru"))
        return

    language = user.get("ui_language", "ru")

    # Получаем статистику
    stats = await api_client.get_stats(telegram_id)

    if not stats:
        await message.answer(get_text("error_backend", language))
        return

    # Формируем сообщение со статистикой
    streak = stats.get("streak", 0)
    words = stats.get("words_said", 0)
    correct = stats.get("correct_percent", 0)
    messages_count = stats.get("messages_count", 0)
    stars = stats.get("stars", 0)

    stats_text = get_text("stats_header", language)
    stats_text += get_text(
        "stats_streak",
        language,
        streak=streak,
        days=get_days_word(streak, language),
    )
    stats_text += get_text("stats_words", language, words=words)
    stats_text += get_text("stats_correct", language, correct=correct)
    stats_text += get_text("stats_messages", language, messages=messages_count)
    stats_text += get_text("stats_stars", language, stars=stars)

    # TODO: Добавить календарь последних 7 дней
    # calendar = format_calendar(stats.get("calendar", []))
    # stats_text += get_text("stats_calendar", language, calendar=calendar)

    await message.answer(stats_text, parse_mode="HTML")


@router.message(Command("saved"))
async def command_saved(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /saved.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general", "ru"))
        return

    language = user.get("ui_language", "ru")

    # Получаем сохраненные слова
    words = await api_client.get_saved_words(telegram_id, limit=10)

    if not words:
        await message.answer(get_text("saved_empty", language))
        return

    # Формируем список слов
    saved_text = get_text("saved_header", language)

    for word_data in words:
        word = word_data.get("word_czech", "")
        translation = word_data.get("translation", "")
        saved_text += get_text("saved_word", language, word=word, translation=translation)

    await message.answer(saved_text, parse_mode="HTML")


@router.message(Command("reset"))
async def command_reset(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /reset.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general", "ru"))
        return

    language = user.get("ui_language", "ru")

    # Запрашиваем подтверждение
    await message.answer(
        get_text("reset_confirm", language),
        reply_markup=get_reset_confirm_keyboard(language),
    )


@router.callback_query(F.data == "reset:yes")
async def reset_confirmed(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Подтверждение сброса разговора.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    telegram_id = callback.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await callback.answer()
        return

    language = user.get("ui_language", "ru")

    # Сбрасываем контекст разговора
    success = await api_client.reset_conversation(telegram_id)

    if success:
        await callback.message.edit_text(get_text("reset_done", language))
        logger.info("conversation_reset", telegram_id=telegram_id)
    else:
        await callback.message.edit_text(get_text("error_backend", language))

    await callback.answer()


@router.callback_query(F.data == "reset:no")
async def reset_cancelled(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Отмена сброса разговора.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    telegram_id = callback.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await callback.answer()
        return

    language = user.get("ui_language", "ru")

    await callback.message.delete()
    await callback.answer()


# === НАСТРОЙКИ ===


@router.message(Command("level"))
async def command_level(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /level.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general", "ru"))
        return

    language = user.get("ui_language", "ru")
    current_level = user.get("level", "beginner")

    await message.answer(
        get_text("settings_level", language, current=current_level),
        reply_markup=get_level_keyboard(language),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("level:"))
async def level_changed(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Изменение уровня чешского.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    telegram_id = callback.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await callback.answer()
        return

    language = user.get("ui_language", "ru")
    level = callback.data.split(":")[1]

    # Обновляем настройки
    await api_client.update_user_settings(telegram_id, level=level)

    await callback.message.edit_text(
        get_text("settings_level_changed", language, level=level), parse_mode="HTML"
    )
    await callback.answer()

    logger.info("level_changed", telegram_id=telegram_id, level=level)


@router.message(Command("voice_speed"))
async def command_voice_speed(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /voice_speed.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general", "ru"))
        return

    language = user.get("ui_language", "ru")
    settings = user.get("settings", {})
    current_speed = settings.get("voice_speed", "normal")

    await message.answer(
        get_text("settings_voice_speed", language, current=current_speed),
        reply_markup=get_voice_speed_keyboard(language),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("voice_speed:"))
async def voice_speed_changed(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Изменение скорости голоса.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    telegram_id = callback.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await callback.answer()
        return

    language = user.get("ui_language", "ru")
    speed = callback.data.split(":")[1]

    # Обновляем настройки
    await api_client.update_user_settings(telegram_id, voice_speed=speed)

    await callback.message.edit_text(
        get_text("settings_voice_speed_changed", language, speed=speed),
        parse_mode="HTML",
    )
    await callback.answer()

    logger.info("voice_speed_changed", telegram_id=telegram_id, speed=speed)


@router.message(Command("corrections"))
async def command_corrections(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /corrections.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general", "ru"))
        return

    language = user.get("ui_language", "ru")
    settings = user.get("settings", {})
    current_corrections = settings.get("corrections_level", "balanced")

    await message.answer(
        get_text("settings_corrections", language, current=current_corrections),
        reply_markup=get_corrections_keyboard(language),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("corrections:"))
async def corrections_changed(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Изменение уровня исправлений.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    telegram_id = callback.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await callback.answer()
        return

    language = user.get("ui_language", "ru")
    corrections_level = callback.data.split(":")[1]

    # Обновляем настройки
    await api_client.update_user_settings(telegram_id, corrections_level=corrections_level)

    await callback.message.edit_text(
        get_text("settings_corrections_changed", language, level=corrections_level),
        parse_mode="HTML",
    )
    await callback.answer()

    logger.info(
        "corrections_changed", telegram_id=telegram_id, level=corrections_level
    )


@router.message(Command("style"))
async def command_style(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /style.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general", "ru"))
        return

    language = user.get("ui_language", "ru")
    settings = user.get("settings", {})
    current_style = settings.get("conversation_style", "friendly")

    await message.answer(
        get_text("settings_style", language, current=current_style),
        reply_markup=get_style_keyboard(language),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("style:"))
async def style_changed(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Изменение стиля общения.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    telegram_id = callback.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await callback.answer()
        return

    language = user.get("ui_language", "ru")
    style = callback.data.split(":")[1]

    # Обновляем настройки
    await api_client.update_user_settings(telegram_id, conversation_style=style)

    await callback.message.edit_text(
        get_text("settings_style_changed", language, style=style), parse_mode="HTML"
    )
    await callback.answer()

    logger.info("style_changed", telegram_id=telegram_id, style=style)

