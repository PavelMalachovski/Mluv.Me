"""
Обработчики команд бота.

Language Immersion: Все сообщения на чешском.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
import structlog

from bot.keyboards import (
    get_clear_history_confirm_keyboard,
    get_corrections_keyboard,
    get_level_keyboard,
    get_native_language_keyboard,
    get_reset_confirm_keyboard,
    get_reset_full_confirm_keyboard,
    get_style_keyboard,
    get_voice_speed_keyboard,
)
from bot.localization import get_days_word, get_text, get_native_language_name
from bot.services.api_client import APIClient

router = Router()
logger = structlog.get_logger()


@router.message(Command("help"))
async def command_help(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /help.

    Language Immersion: Все на чешском.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general"))
        return

    # Language Immersion: UI всегда на чешском
    help_text = get_text("help_header")
    help_text += get_text("help_commands")
    help_text += get_text("help_tips")

    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("stats"))
async def command_stats(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /stats.

    Language Immersion: Все на чешском.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general"))
        return

    # Получаем статистику
    stats = await api_client.get_stats(telegram_id)

    if not stats:
        await message.answer(get_text("error_backend"))
        return

    # Формируем сообщение со статистикой (на чешском)
    streak = stats.get("streak", 0)
    words = stats.get("words_said", 0)
    correct = stats.get("correct_percent", 0)
    messages_count = stats.get("messages_count", 0)
    stars = stats.get("stars", 0)

    stats_text = get_text("stats_header")
    stats_text += get_text(
        "stats_streak",
        streak=streak,
        days=get_days_word(streak),
    )
    stats_text += get_text("stats_words", words=words)
    stats_text += get_text("stats_correct", correct=correct)
    stats_text += get_text("stats_messages", messages=messages_count)
    stats_text += get_text("stats_stars", stars=stars)

    await message.answer(stats_text, parse_mode="HTML")


@router.message(Command("saved"))
async def command_saved(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /saved.

    Language Immersion: Все на чешском.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general"))
        return

    # Получаем сохраненные слова
    words = await api_client.get_saved_words(telegram_id, limit=10)

    if not words:
        await message.answer(get_text("saved_empty"))
        return

    # Формируем список слов (на чешском)
    saved_text = get_text("saved_header")

    for word_data in words:
        word = word_data.get("word_czech", "")
        translation = word_data.get("translation", "")
        saved_text += get_text("saved_word", word=word, translation=translation)

    await message.answer(saved_text, parse_mode="HTML")


@router.message(Command("reset"))
async def command_reset(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /reset.

    Language Immersion: Все на чешском.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general"))
        return

    # Запрашиваем подтверждение (на чешском)
    await message.answer(
        get_text("reset_confirm"),
        reply_markup=get_reset_confirm_keyboard(),
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

    # Сбрасываем контекст разговора
    success = await api_client.reset_conversation(telegram_id)

    if success:
        await callback.message.edit_text(get_text("reset_done"))
        logger.info("conversation_reset", telegram_id=telegram_id)
    else:
        await callback.message.edit_text(get_text("error_backend"))

    await callback.answer()



@router.callback_query(F.data == "reset:full")
async def reset_full_requested(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Запрос на полный сброс.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    await callback.message.edit_text(
        get_text("reset_full_confirm"),
        reply_markup=get_reset_full_confirm_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "reset:full_yes")
async def reset_full_confirmed(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Подтверждение полного сброса.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    telegram_id = callback.from_user.id

    # Выполняем полный сброс
    success = await api_client.full_reset_user(telegram_id)

    if success:
        await callback.message.edit_text(get_text("reset_full_done"))
        logger.info("user_full_reset_confirmed", telegram_id=telegram_id)
    else:
        await callback.message.edit_text(get_text("error_backend"))

    await callback.answer()


@router.callback_query(F.data == "reset:no")
async def reset_cancelled(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Отмена сброса разговора.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    await callback.message.delete()
    await callback.answer()


@router.message(Command("clear_history"))
async def command_clear_history(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /clear_history - удаление всей истории переписки.

    Language Immersion: Все на чешском.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general"))
        return

    # Запрашиваем подтверждение (на чешском)
    await message.answer(
        get_text("clear_history_confirm"),
        reply_markup=get_clear_history_confirm_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "clear_history:yes")
async def clear_history_confirmed(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Подтверждение удаления истории переписки.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    telegram_id = callback.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await callback.answer()
        return

    # Удаляем всю историю сообщений через API
    success = await api_client.delete_conversation_history(telegram_id)

    if success:
        await callback.message.edit_text(
            get_text("clear_history_done"),
            parse_mode="HTML"
        )
        logger.info("conversation_history_cleared", telegram_id=telegram_id)
    else:
        await callback.message.edit_text(get_text("error_backend"))

    await callback.answer()


@router.callback_query(F.data == "clear_history:no")
async def clear_history_cancelled(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Отмена удаления истории переписки.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    await callback.message.delete()
    await callback.answer()


# === НАСТРОЙКИ ===


@router.message(Command("level"))
async def command_level(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /level.

    Language Immersion: Все на чешском.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general"))
        return

    current_level = user.get("level", "beginner")

    await message.answer(
        get_text("settings_level", current=current_level),
        reply_markup=get_level_keyboard(),
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

    level = callback.data.split(":")[1]

    # Обновляем настройки
    await api_client.update_user_settings(telegram_id, level=level)

    await callback.message.edit_text(
        get_text("settings_level_changed", level=level), parse_mode="HTML"
    )
    await callback.answer()

    logger.info("level_changed", telegram_id=telegram_id, level=level)


@router.message(Command("native"))
async def command_native(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /native - выбор родного языка для объяснений.

    Language Immersion: UI на чешском, меняем только язык объяснений.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general"))
        return

    current_native = user.get("native_language", "ru")
    current_name = get_native_language_name(current_native)

    await message.answer(
        get_text("settings_native", current=current_name),
        reply_markup=get_native_language_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("native:"))
async def native_language_changed(callback: CallbackQuery, api_client: APIClient) -> None:
    """
    Изменение родного языка для объяснений.

    Args:
        callback: Callback query
        api_client: API клиент
    """
    telegram_id = callback.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await callback.answer()
        return

    native_language = callback.data.split(":")[1]
    lang_name = get_native_language_name(native_language)

    # Обновляем настройки
    await api_client.update_user_settings(telegram_id, native_language=native_language)

    await callback.message.edit_text(
        get_text("settings_native_changed", language=lang_name), parse_mode="HTML"
    )
    await callback.answer()

    logger.info("native_language_changed", telegram_id=telegram_id, native_language=native_language)


@router.message(Command("voice_speed"))
async def command_voice_speed(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /voice_speed.

    Language Immersion: Все на чешском.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general"))
        return

    settings = user.get("settings", {})
    current_speed = settings.get("voice_speed", "normal")

    await message.answer(
        get_text("settings_voice_speed", current=current_speed),
        reply_markup=get_voice_speed_keyboard(),
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

    speed = callback.data.split(":")[1]

    # Обновляем настройки
    await api_client.update_user_settings(telegram_id, voice_speed=speed)

    await callback.message.edit_text(
        get_text("settings_voice_speed_changed", speed=speed),
        parse_mode="HTML",
    )
    await callback.answer()

    logger.info("voice_speed_changed", telegram_id=telegram_id, speed=speed)


@router.message(Command("corrections"))
async def command_corrections(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /corrections.

    Language Immersion: Все на чешском.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general"))
        return

    settings = user.get("settings", {})
    current_corrections = settings.get("corrections_level", "balanced")

    await message.answer(
        get_text("settings_corrections", current=current_corrections),
        reply_markup=get_corrections_keyboard(),
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

    corrections_level = callback.data.split(":")[1]

    # Обновляем настройки
    await api_client.update_user_settings(telegram_id, corrections_level=corrections_level)

    await callback.message.edit_text(
        get_text("settings_corrections_changed", level=corrections_level),
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

    Language Immersion: Все на чешском.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general"))
        return

    settings = user.get("settings", {})
    current_style = settings.get("conversation_style", "friendly")

    await message.answer(
        get_text("settings_style", current=current_style),
        reply_markup=get_style_keyboard(),
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

    style = callback.data.split(":")[1]

    # Обновляем настройки
    await api_client.update_user_settings(telegram_id, conversation_style=style)

    await callback.message.edit_text(
        get_text("settings_style_changed", style=style), parse_mode="HTML"
    )
    await callback.answer()

    logger.info("style_changed", telegram_id=telegram_id, style=style)


@router.message(Command("translate"))
async def command_translate(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /translate <word>.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент
    """
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if not user:
        await message.answer(get_text("error_general"))
        return

    native_language = user.get("native_language", "ru")

    # Получаем слово из команды
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        await message.answer(
            get_text("translate_usage"), parse_mode="HTML"
        )
        return

    word = command_parts[1].strip()

    # Переводим слово на родной язык пользователя
    translation_result = await api_client.translate_word(word, target_language=native_language)

    if not translation_result:
        await message.answer(get_text("translate_error"))
        return

    translation = translation_result.get("translation", "")
    phonetics = translation_result.get("phonetics")

    # Формируем ответ (на чешском)
    response_text = get_text(
        "translate_result",
        word=word,
        translation=translation,
    )

    if phonetics:
        response_text += f"\n📝 {get_text('phonetics')}: {phonetics}"

    await message.answer(response_text, parse_mode="HTML")
    logger.info("word_translated", telegram_id=telegram_id, word=word)
