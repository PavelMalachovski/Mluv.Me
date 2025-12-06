"""
Statistics endpoints.
Статистика пользователя, streak, прогресс.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_session
from backend.db.repositories import StatsRepository, UserRepository

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get(
    "/{telegram_id}/summary",
    summary="Получить общую статистику",
    description="Получить общую статистику пользователя (streak, слова, процент правильных, и т.д.)",
)
async def get_stats_summary(
    telegram_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Получить общую статистику пользователя.

    Args:
        telegram_id: Telegram ID пользователя
        session: Database session

    Returns:
        Статистика пользователя

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

    # Собираем агрегированную статистику пользователя
    stats_repo = StatsRepository(session)
    summary = await stats_repo.get_user_summary(user.id)
    stars = await stats_repo.get_user_stars(user.id)

    return {
        "streak": summary.get("current_streak", 0),
        "words_said": summary.get("total_words", 0),
        "correct_percent": summary.get("average_correctness", 0),
        "messages_count": summary.get("total_messages", 0),
        "stars": stars.total if stars else 0,
    }

