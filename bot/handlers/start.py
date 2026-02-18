"""
Обработчик команды /start и онбординга.

Language Immersion: UI на чешском, выбираем только родной язык для объяснений.
"""

import time

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
import structlog

from bot.keyboards import get_native_language_keyboard, get_level_keyboard
from bot.localization import get_text
from bot.services.api_client import APIClient

router = Router()
logger = structlog.get_logger()

# Временное хранилище данных онбординга (telegram_id -> data)
onboarding_data: dict[int, dict] = {}
_ONBOARDING_MAX_SIZE = 500
_ONBOARDING_TTL = 3600  # 1 hour — abandon timeout


def _cleanup_onboarding():
    """Remove stale onboarding entries and enforce max size."""
    now = time.time()
    expired = [k for k, v in onboarding_data.items() if now - v.get("_ts", 0) > _ONBOARDING_TTL]
    for k in expired:
        del onboarding_data[k]
    # If still over cap, drop oldest
    while len(onboarding_data) > _ONBOARDING_MAX_SIZE:
        oldest = min(onboarding_data, key=lambda k: onboarding_data[k].get("_ts", 0))
        del onboarding_data[oldest]


@router.message(CommandStart())
async def command_start_handler(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /start.

    Language Immersion: Приветствие на чешском.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент для общения с backend
    """
    telegram_id = message.from_user.id

    # Проверяем существует ли пользователь
    user = await api_client.get_user(telegram_id)

    if user:
        # Пользователь уже зарегистрирован (сообщение на чешском)
        await message.answer(get_text("already_registered"))
        return

    # Начинаем онбординг
    _cleanup_onboarding()
    onboarding_data[telegram_id] = {
        "username": message.from_user.username,
        "first_name": message.from_user.first_name or "User",
        "_ts": time.time(),
    }

    # Приветствие на чешском + выбор родного языка
    await message.answer(
        get_text("welcome"),
        reply_markup=get_native_language_keyboard(),
    )

    logger.info("onboarding_started", telegram_id=telegram_id)


@router.callback_query(F.data.startswith("native:"))
async def native_language_selected_handler(
    callback: CallbackQuery, api_client: APIClient
) -> None:
    """
    Обработчик выбора родного языка (для объяснений).

    Language Immersion: UI остается на чешском.

    Args:
        callback: Callback query от кнопки
        api_client: API клиент
    """
    telegram_id = callback.from_user.id
    native_language = callback.data.split(":")[1]  # ru, uk, pl, sk

    # Сохраняем родной язык в данные онбординга
    if telegram_id not in onboarding_data:
        onboarding_data[telegram_id] = {}

    onboarding_data[telegram_id]["native_language"] = native_language

    # Обновляем сообщение - переходим к выбору уровня (на чешском)
    await callback.message.edit_text(
        get_text("language_selected"),  # Чешский текст
        reply_markup=get_level_keyboard(),  # Уровни на чешском
    )

    await callback.answer()

    logger.info("native_language_selected", telegram_id=telegram_id, native_language=native_language)


# Backward compatibility: обработка старого формата lang:
@router.callback_query(F.data.startswith("lang:"))
async def language_selected_handler_legacy(
    callback: CallbackQuery, api_client: APIClient
) -> None:
    """
    Legacy обработчик для обратной совместимости.
    Перенаправляет на новый native: формат.
    """
    telegram_id = callback.from_user.id
    language = callback.data.split(":")[1]

    # Сохраняем как native_language
    if telegram_id not in onboarding_data:
        onboarding_data[telegram_id] = {}

    onboarding_data[telegram_id]["native_language"] = language

    await callback.message.edit_text(
        get_text("language_selected"),
        reply_markup=get_level_keyboard(),
    )

    await callback.answer()


@router.callback_query(F.data.startswith("level:"))
async def level_selected_handler(
    callback: CallbackQuery, api_client: APIClient
) -> None:
    """
    Обработчик выбора уровня чешского.

    Args:
        callback: Callback query от кнопки
        api_client: API клиент
    """
    telegram_id = callback.from_user.id
    level = callback.data.split(":")[1]  # beginner, intermediate, advanced, native

    # Получаем данные онбординга
    data = onboarding_data.get(telegram_id, {})
    native_language = data.get("native_language", "ru")

    # Создаем пользователя в backend
    user = await api_client.create_user(
        telegram_id=telegram_id,
        username=data.get("username"),
        first_name=data.get("first_name", "User"),
        native_language=native_language,
        level=level,
    )

    if user:
        # Удаляем данные онбординга
        onboarding_data.pop(telegram_id, None)

        # Приветственное сообщение на чешском
        await callback.message.edit_text(get_text("onboarding_complete"))

        await callback.answer()

        logger.info(
            "user_registered",
            telegram_id=telegram_id,
            native_language=native_language,
            level=level,
        )
    else:
        # Ошибка создания пользователя (на чешском)
        await callback.message.edit_text(get_text("error_general"))
        await callback.answer()

        logger.error("user_registration_failed", telegram_id=telegram_id)


