"""
Messages router.
Управление сообщениями пользователя.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from backend.db.database import get_session
from backend.db.repositories import UserRepository
from backend.models.message import Message

router = APIRouter(prefix="/api/v1/messages", tags=["messages"])
log = structlog.get_logger()


@router.delete("/{telegram_id}/history", status_code=status.HTTP_200_OK)
async def delete_conversation_history(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Удалить всю историю переписки пользователя с Хонзиком.

    **ВАЖНО:** Это действие необратимо!
    - Удаляются все сообщения пользователя и ответы Хонзика
    - Статистика и сохранённые слова остаются

    Args:
        telegram_id: Telegram ID пользователя
        session: Database session

    Returns:
        Сообщение об успешном удалении

    Raises:
        404: Пользователь не найден
    """
    log.info("delete_conversation_history_requested", telegram_id=telegram_id)

    # Проверяем существование пользователя
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(telegram_id)

    if not user:
        log.warning("user_not_found_for_history_deletion", telegram_id=telegram_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found"
        )

    # Удаляем все сообщения пользователя
    stmt = delete(Message).where(Message.user_id == user.id)
    result = await session.execute(stmt)
    await session.commit()

    deleted_count = result.rowcount

    log.info(
        "conversation_history_deleted",
        telegram_id=telegram_id,
        user_id=user.id,
        deleted_messages=deleted_count
    )

    return {
        "status": "success",
        "message": "Conversation history deleted successfully",
        "deleted_messages": deleted_count,
        "telegram_id": telegram_id
    }
