"""
Обработчик команды /start и онбординга.
"""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
import structlog

from bot.keyboards import get_language_keyboard, get_level_keyboard
from bot.localization import get_text
from bot.services.api_client import APIClient

router = Router()
logger = structlog.get_logger()

# Временное хранилище данных онбординга (telegram_id -> data)
onboarding_data: dict[int, dict] = {}


@router.message(CommandStart())
async def command_start_handler(message: Message, api_client: APIClient) -> None:
    """
    Обработчик команды /start.

    Args:
        message: Сообщение от пользователя
        api_client: API клиент для общения с backend
    """
    telegram_id = message.from_user.id

    # Проверяем существует ли пользователь
    user = await api_client.get_user(telegram_id)

    if user:
        # Пользователь уже зарегистрирован
        language = user.get("ui_language", "ru")
        await message.answer(get_text("already_registered", language))
        return

    # Начинаем онбординг
    onboarding_data[telegram_id] = {
        "username": message.from_user.username,
        "first_name": message.from_user.first_name or "User",
    }

    await message.answer(
        get_text("welcome", "ru"),
        reply_markup=get_language_keyboard(),
    )

    logger.info("onboarding_started", telegram_id=telegram_id)


@router.callback_query(F.data.startswith("lang:"))
async def language_selected_handler(
    callback: CallbackQuery, api_client: APIClient
) -> None:
    """
    Обработчик выбора языка интерфейса.

    Args:
        callback: Callback query от кнопки
        api_client: API клиент
    """
    telegram_id = callback.from_user.id
    language = callback.data.split(":")[1]  # ru или uk

    # Сохраняем язык в данные онбординга
    if telegram_id not in onboarding_data:
        onboarding_data[telegram_id] = {}

    onboarding_data[telegram_id]["ui_language"] = language

    # Обновляем сообщение
    await callback.message.edit_text(
        get_text("language_selected", language),
        reply_markup=get_level_keyboard(language),
    )

    await callback.answer()

    logger.info("language_selected", telegram_id=telegram_id, language=language)


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
    language = data.get("ui_language", "ru")

    # Создаем пользователя в backend
    user = await api_client.create_user(
        telegram_id=telegram_id,
        username=data.get("username"),
        first_name=data.get("first_name", "User"),
        ui_language=language,
        level=level,
    )

    if user:
        # Удаляем данные онбординга
        onboarding_data.pop(telegram_id, None)

        # Отправляем приветственное сообщение
        await callback.message.edit_text(get_text("onboarding_complete", language))

        # TODO: В будущем здесь можно отправить приветственное аудио от Хонзика
        # через OpenAI TTS

        await callback.answer()

        logger.info(
            "user_registered",
            telegram_id=telegram_id,
            language=language,
            level=level,
        )
    else:
        # Ошибка создания пользователя
        await callback.message.edit_text(get_text("error_general", language))
        await callback.answer()

        logger.error("user_registration_failed", telegram_id=telegram_id)

