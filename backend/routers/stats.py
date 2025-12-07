"""
Statistics endpoints.
Статистика пользователя, streak, прогресс.
"""

from datetime import datetime, timedelta, time

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_session
from backend.db.repositories import StatsRepository, UserRepository
from backend.cache.redis_client import redis_client
from backend.cache.cache_keys import CacheKeys
from backend.config import get_settings

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
    Получить общую статистику пользователя с кешированием.

    Args:
        telegram_id: Telegram ID пользователя
        session: Database session

    Returns:
        Статистика пользователя

    Raises:
        HTTPException: Если пользователь не найден
    """
    # Try cache first
    settings = get_settings()
    today = datetime.now().date()
    cache_key = CacheKeys.daily_stats(telegram_id, str(today))

    if redis_client.is_enabled:
        cached_stats = await redis_client.get(cache_key)
        if cached_stats:
            logger.debug("stats_cache_hit", telegram_id=telegram_id)
            return cached_stats

    # Database query
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

    result = {
        "streak": summary.get("current_streak", 0),
        "words_said": summary.get("total_words", 0),
        "correct_percent": summary.get("average_correctness", 0),
        "messages_count": summary.get("total_messages", 0),
        "stars": stars.total if stars else 0,
    }

    # Cache until end of day
    if redis_client.is_enabled:
        seconds_until_midnight = (
            datetime.combine(today + timedelta(days=1), time.min) - datetime.now()
        ).seconds

        await redis_client.set(cache_key, result, ttl=seconds_until_midnight)
        logger.debug("stats_cached", telegram_id=telegram_id, ttl=seconds_until_midnight)

    return result

