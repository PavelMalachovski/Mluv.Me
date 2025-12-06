"""
User management endpoints.
CRUD операции для пользователей и их настроек.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_session
from backend.db.repositories import UserRepository, UserSettingsRepository
from backend.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserSettingsResponse,
    UserSettingsUpdate,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
    description="Создать нового пользователя при первом запуске /start",
)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """
    Создать нового пользователя.

    Args:
        user_data: Данные пользователя
        session: Database session

    Returns:
        UserResponse: Созданный пользователь

    Raises:
        HTTPException: Если пользователь с таким telegram_id уже существует
    """
    repo = UserRepository(session)

    # Check if user already exists
    existing_user = await repo.get_by_telegram_id(user_data.telegram_id)
    if existing_user:
        logger.warning(
            "user_already_exists",
            telegram_id=user_data.telegram_id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with telegram_id {user_data.telegram_id} already exists"
        )

    # Create user
    user = await repo.create(**user_data.model_dump())
    await session.commit()

    logger.info(
        "user_created",
        user_id=user.id,
        telegram_id=user.telegram_id,
        ui_language=user.ui_language,
        level=user.level
    )

    return UserResponse.model_validate(user)


@router.get(
    "/telegram/{telegram_id}",
    response_model=UserResponse,
    summary="Получить пользователя по Telegram ID",
    description="Получить пользователя по его Telegram ID",
)
async def get_user_by_telegram_id(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """
    Получить пользователя по Telegram ID.

    Args:
        telegram_id: Telegram user ID
        session: Database session

    Returns:
        UserResponse: Пользователь

    Raises:
        HTTPException: Если пользователь не найден
    """
    repo = UserRepository(session)
    user = await repo.get_by_telegram_id(telegram_id)

    if not user:
        logger.warning("user_not_found", telegram_id=telegram_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found"
        )

    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Получить пользователя по ID",
    description="Получить пользователя по его внутреннему ID",
)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """
    Получить пользователя по ID.

    Args:
        user_id: User ID
        session: Database session

    Returns:
        UserResponse: Пользователь

    Raises:
        HTTPException: Если пользователь не найден
    """
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)

    if not user:
        logger.warning("user_not_found", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Обновить пользователя",
    description="Обновить профиль пользователя",
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """
    Обновить пользователя.

    Args:
        user_id: User ID
        user_data: Обновляемые данные
        session: Database session

    Returns:
        UserResponse: Обновленный пользователь

    Raises:
        HTTPException: Если пользователь не найден
    """
    repo = UserRepository(session)

    # Only update fields that are provided
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data:
        # No fields to update
        user = await repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return UserResponse.model_validate(user)

    user = await repo.update(user_id, **update_data)

    if not user:
        logger.warning("user_not_found", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    logger.info(
        "user_updated",
        user_id=user_id,
        updated_fields=list(update_data.keys())
    )

    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}/settings",
    response_model=UserSettingsResponse,
    summary="Получить настройки пользователя",
    description="Получить настройки пользователя",
)
async def get_user_settings(
    user_id: int,
    session: AsyncSession = Depends(get_session),
) -> UserSettingsResponse:
    """
    Получить настройки пользователя.

    Args:
        user_id: User ID
        session: Database session

    Returns:
        UserSettingsResponse: Настройки

    Raises:
        HTTPException: Если настройки не найдены
    """
    repo = UserSettingsRepository(session)
    settings = await repo.get_by_user_id(user_id)

    if not settings:
        logger.warning("settings_not_found", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settings for user {user_id} not found"
        )

    return UserSettingsResponse.model_validate(settings)


@router.patch(
    "/{user_id}/settings",
    response_model=UserSettingsResponse,
    summary="Обновить настройки пользователя",
    description="Обновить настройки пользователя (стиль Хонзика, скорость голоса, и т.д.)",
)
async def update_user_settings(
    user_id: int,
    settings_data: UserSettingsUpdate,
    session: AsyncSession = Depends(get_session),
) -> UserSettingsResponse:
    """
    Обновить настройки пользователя.

    Args:
        user_id: User ID
        settings_data: Обновляемые настройки
        session: Database session

    Returns:
        UserSettingsResponse: Обновленные настройки

    Raises:
        HTTPException: Если настройки не найдены
    """
    repo = UserSettingsRepository(session)

    # Only update fields that are provided
    update_data = settings_data.model_dump(exclude_unset=True)
    if not update_data:
        # No fields to update
        settings = await repo.get_by_user_id(user_id)
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Settings for user {user_id} not found"
            )
        return UserSettingsResponse.model_validate(settings)

    settings = await repo.update(user_id, **update_data)

    if not settings:
        logger.warning("settings_not_found", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Settings for user {user_id} not found"
        )

    logger.info(
        "settings_updated",
        user_id=user_id,
        updated_fields=list(update_data.keys())
    )

    return UserSettingsResponse.model_validate(settings)


