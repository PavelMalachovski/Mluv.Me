"""
Gamification background tasks for Mluv.Me.

Содержит задачи для:
- Проверки и сброса streaks
- Обработки достижений
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any

from celery import Task
from sqlalchemy import select

from backend.tasks.celery_app import celery_app
from backend.db.database import AsyncSessionLocal
from backend.db.repositories import StatsRepository
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AsyncTask(Task):
    """Base task class with async support."""

    def __call__(self, *args, **kwargs):
        """Override to run async functions."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(self.run_async(*args, **kwargs))

    async def run_async(self, *args, **kwargs):
        """Override this method in subclasses."""
        raise NotImplementedError


@celery_app.task(bind=True, base=AsyncTask)
async def check_and_reset_streaks(self) -> Dict[str, Any]:
    """
    Проверить и сбросить streaks для неактивных пользователей.

    Вызывается автоматически в 00:05 UTC каждый день.
    Сбрасывает streak у пользователей, которые не практиковались вчера.

    Returns:
        dict: Статистика обработки
    """
    try:
        async with AsyncSessionLocal() as db:
            from backend.models.stats import DailyStats

            # Вчерашняя дата
            yesterday = date.today() - timedelta(days=1)

            # Находим всех пользователей с активным streak
            query = (
                select(DailyStats.user_id, DailyStats.streak_day)
                .where(
                    DailyStats.date == yesterday,
                    DailyStats.streak_day > 0
                )
                .distinct()
            )

            result = await db.execute(query)
            users_with_streak = [(row[0], row[1]) for row in result.all()]

            logger.info(
                "checking_streaks",
                users_count=len(users_with_streak)
            )

            stats_repo = StatsRepository(db)
            reset_count = 0
            maintained_count = 0

            # Проверяем каждого пользователя
            for user_id, yesterday_streak in users_with_streak:
                # Проверяем есть ли активность сегодня
                today = date.today()
                today_stats = await stats_repo.get_daily_stats(user_id, today)

                if today_stats and today_stats.get("messages_count", 0) > 0:
                    # Пользователь уже практиковался сегодня - streak сохранен
                    maintained_count += 1
                    continue

                # Пользователь не практиковался - сбрасываем streak
                # (на самом деле ничего не делаем, streak просто не продолжится)
                reset_count += 1

                logger.info(
                    "streak_will_reset",
                    user_id=user_id,
                    yesterday_streak=yesterday_streak
                )

            result = {
                "total_checked": len(users_with_streak),
                "maintained": maintained_count,
                "will_reset": reset_count,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(
                "streak_check_completed",
                **result
            )

            return result

    except Exception as exc:
        logger.error(
            "streak_check_failed",
            error=str(exc)
        )
        raise


@celery_app.task(bind=True, base=AsyncTask)
async def award_streak_milestone_bonus(self, user_id: int, streak_days: int) -> Dict[str, Any]:
    """
    Начислить бонус за достижение milestone в streak.

    Milestone: 7, 30, 100, 365 дней.

    Args:
        user_id: ID пользователя
        streak_days: Количество дней streak

    Returns:
        dict: Информация о начисленном бонусе
    """
    try:
        # Определяем milestone и бонус
        milestones = {
            7: {"stars": 10, "title": "7-дневный streak"},
            30: {"stars": 50, "title": "30-дневный streak"},
            100: {"stars": 200, "title": "100-дневный streak"},
            365: {"stars": 1000, "title": "Годовой streak"},
        }

        if streak_days not in milestones:
            return {
                "user_id": user_id,
                "streak_days": streak_days,
                "bonus_awarded": False,
                "reason": "not_a_milestone"
            }

        milestone = milestones[streak_days]

        async with AsyncSessionLocal() as db:
            stats_repo = StatsRepository(db)

            # Начисляем бонусные звезды
            stars_obj = await stats_repo.get_user_stars(user_id)

            if stars_obj:
                new_total = stars_obj.total + milestone["stars"]
                new_available = stars_obj.available + milestone["stars"]
                new_lifetime = stars_obj.lifetime + milestone["stars"]

                await stats_repo.update_user_stars(
                    user_id=user_id,
                    total=new_total,
                    available=new_available,
                    lifetime=new_lifetime
                )

                await db.commit()

                logger.info(
                    "streak_milestone_bonus_awarded",
                    user_id=user_id,
                    streak_days=streak_days,
                    bonus_stars=milestone["stars"]
                )

                # Отправляем уведомление пользователю
                from backend.tasks.notifications import send_achievement_notification
                send_achievement_notification.apply_async(
                    args=[user_id, "streak_milestone", milestone],
                    countdown=5
                )

                return {
                    "user_id": user_id,
                    "streak_days": streak_days,
                    "bonus_awarded": True,
                    "bonus_stars": milestone["stars"],
                    "milestone_title": milestone["title"],
                    "new_total": new_total
                }

            return {
                "user_id": user_id,
                "streak_days": streak_days,
                "bonus_awarded": False,
                "reason": "stars_not_found"
            }

    except Exception as exc:
        logger.error(
            "milestone_bonus_failed",
            user_id=user_id,
            streak_days=streak_days,
            error=str(exc)
        )
        return {
            "user_id": user_id,
            "bonus_awarded": False,
            "error": str(exc)
        }
