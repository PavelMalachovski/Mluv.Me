"""
Saved words endpoints.
Сохраненные слова пользователя.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_session
from backend.db.repositories import UserRepository, SavedWordRepository

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/words", tags=["words"])


@router.get(
    "/{telegram_id}",
    summary="Получить сохраненные слова",
    description="Получить список сохраненных слов пользователя",
)
async def get_saved_words(
    telegram_id: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    """
    Получить сохраненные слова пользователя.

    Args:
        telegram_id: Telegram ID пользователя
        limit: Максимальное количество слов
        session: Database session

    Returns:
        Список сохраненных слов

    Raises:
        HTTPException: Если пользователь не найден
    """
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        logger.warning("user_not_found", telegram_id=telegram_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found",
        )

    word_repo = SavedWordRepository(session)
    words = await word_repo.get_by_user_id(user.id, limit=limit)

    return [
        {
            "id": word.id,
            "word_czech": word.word_czech,
            "translation": word.translation,
            "context_sentence": word.context_sentence,
            "phonetics": word.phonetics,
            "times_reviewed": word.times_reviewed,
            "created_at": word.created_at.isoformat() if word.created_at else None,
        }
        for word in words
    ]


@router.post(
    "/{telegram_id}/reset-context",
    summary="Сбросить контекст разговора",
    description="Очистить историю сообщений для нового разговора",
)
async def reset_conversation(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Сбросить контекст разговора пользователя.

    Args:
        telegram_id: Telegram ID пользователя
        session: Database session

    Returns:
        Статус успешности

    Raises:
        HTTPException: Если пользователь не найден
    """
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        logger.warning("user_not_found", telegram_id=telegram_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found",
        )

    # В будущем здесь можно пометить сообщения как "archived"
    # Пока просто возвращаем success
    logger.info("conversation_reset", telegram_id=telegram_id, user_id=user.id)

    return {"status": "success", "message": "Conversation context reset"}

