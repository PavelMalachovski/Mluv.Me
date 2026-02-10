"""
Notification background tasks for Mluv.Me.

Evening grammar notifications (19:00 CET = 18:00 UTC):
- Grammar rule of the day
- Practice reminder with streak info
- Czech-only content (immersion)
"""

from datetime import datetime, timedelta
from typing import Dict, Any

from celery import Task
from sqlalchemy import select, func

from backend.tasks.celery_app import celery_app
from backend.db.database import AsyncSessionLocal
from backend.db.repositories import StatsRepository, UserRepository
from backend.db.grammar_repository import GrammarRepository
from backend.services.grammar_service import GrammarService
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


@celery_app.task(bind=True, base=AsyncTask, max_retries=5)
async def send_grammar_reminder(self, user_id: int) -> Dict[str, Any]:
    """
    Send evening grammar reminder to a user.

    Includes:
    - A grammar rule (unseen → weak → random)
    - Practice motivation with streak info
    - All in Czech (immersion approach)

    Args:
        user_id: User ID

    Returns:
        dict: Send result
    """
    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            stats_repo = StatsRepository(db)
            grammar_repo = GrammarRepository(db)
            grammar_service = GrammarService(grammar_repo)

            # Get user
            user = await user_repo.get_by_id(user_id)
            if not user:
                logger.warning("user_not_found_for_reminder", user_id=user_id)
                return {"user_id": user_id, "sent": False, "reason": "user_not_found"}

            # Check notification settings
            if user.settings and not user.settings.notifications_enabled:
                return {"user_id": user_id, "sent": False, "reason": "notifications_disabled"}

            # Get streak and stars info
            user_stats = await stats_repo.get_user_summary(user_id)
            current_streak = user_stats.get("current_streak", 0)
            total_stars = user_stats.get("total_stars", 0)

            # Generate grammar notification message (Czech only)
            message = await grammar_service.get_notification_message(
                user_id=user_id,
                streak=current_streak,
                stars=total_stars,
            )

            # Send via Telegram Bot API
            try:
                from aiogram import Bot
                from backend.config import get_settings

                settings = get_settings()
                bot = Bot(token=settings.telegram_bot_token)

                await bot.send_message(
                    user.telegram_id,
                    message,
                    parse_mode="HTML",
                )
                await bot.session.close()

                logger.info(
                    "grammar_reminder_sent",
                    user_id=user_id,
                    telegram_id=user.telegram_id,
                    streak=current_streak,
                )

                return {
                    "user_id": user_id,
                    "sent": True,
                    "telegram_id": user.telegram_id,
                    "streak": current_streak,
                }

            except Exception as bot_exc:
                logger.error(
                    "telegram_send_failed",
                    user_id=user_id,
                    error=str(bot_exc),
                )
                raise self.retry(exc=bot_exc, countdown=300)

    except Exception as exc:
        logger.error(
            "grammar_reminder_failed",
            user_id=user_id,
            error=str(exc),
        )
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, base=AsyncTask)
async def send_evening_grammar_notifications(self) -> Dict[str, Any]:
    """
    Send evening grammar notifications to all active users.

    Triggered daily at 18:00 UTC (= 19:00 CET).
    Processes users who:
    - Have notifications enabled
    - Were active in last 14 days

    Returns:
        dict: Send statistics
    """
    try:
        async with AsyncSessionLocal() as db:
            from backend.models.message import Message
            from backend.models.user_settings import UserSettings

            # Find active users from last 14 days
            two_weeks_ago = datetime.now() - timedelta(days=14)

            query = (
                select(func.distinct(Message.user_id))
                .join(UserSettings, Message.user_id == UserSettings.user_id)
                .where(
                    Message.created_at >= two_weeks_ago,
                    UserSettings.notifications_enabled,
                )
            )

            result = await db.execute(query)
            active_user_ids = [row[0] for row in result.all()]

            logger.info(
                "sending_evening_grammar_notifications",
                user_count=len(active_user_ids),
            )

            sent = 0
            failed = 0

            for user_id in active_user_ids:
                try:
                    # Stagger sends to avoid Telegram rate limits
                    send_grammar_reminder.apply_async(
                        args=[user_id],
                        countdown=sent * 2,  # 2 seconds between sends
                    )
                    sent += 1
                except Exception as e:
                    logger.error(
                        "failed_to_schedule_grammar_reminder",
                        user_id=user_id,
                        error=str(e),
                    )
                    failed += 1

            result = {
                "total_users": len(active_user_ids),
                "scheduled": sent,
                "failed": failed,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info("evening_grammar_notifications_completed", **result)
            return result

    except Exception as exc:
        logger.error("evening_grammar_notifications_failed", error=str(exc))
        raise


@celery_app.task(bind=True, base=AsyncTask)
async def send_weekly_report_notification(self, user_id: int) -> Dict[str, Any]:
    """
    Send weekly report to a user.

    Triggered every Monday for active users.
    """
    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            grammar_repo = GrammarRepository(db)
            grammar_service = GrammarService(grammar_repo)

            user = await user_repo.get_by_id(user_id)
            if not user or (user.settings and not user.settings.notifications_enabled):
                return {"user_id": user_id, "sent": False, "reason": "notifications_disabled"}

            # Get grammar progress summary
            summary = await grammar_service.get_progress_summary(user_id)

            # Build weekly report (Czech only)
            message = (
                "📊 <b>Týdenní přehled</b>\n\n"
            )

            if summary["total_practiced"] > 0:
                message += (
                    f"📝 Procvičená pravidla: {summary['total_practiced']}\n"
                    f"✅ Celková přesnost: {summary['average_accuracy']}%\n"
                    f"🏆 Zvládnutá pravidla: {summary['mastered_count']}\n"
                    f"📚 Celkem pravidel: {summary['total_rules']}\n\n"
                )

                if summary['weak_count'] > 0:
                    message += f"💪 K procvičení: {summary['weak_count']} pravidel\n\n"

                message += "Pokračuj dál — každý den se zlepšuješ! 🚀"
            else:
                message += (
                    "Tento týden jsi ještě neprocvičoval(a) gramatiku.\n\n"
                    "Začni dnes — stačí jedna minihra denně! 🎮\n"
                    "Učení je cesta, ne cíl. 💪"
                )

            # Send via Telegram
            from aiogram import Bot
            from backend.config import get_settings

            settings = get_settings()
            bot = Bot(token=settings.telegram_bot_token)

            await bot.send_message(user.telegram_id, message, parse_mode="HTML")
            await bot.session.close()

            logger.info("weekly_report_sent", user_id=user_id)
            return {"user_id": user_id, "sent": True}

    except Exception as exc:
        logger.error("weekly_report_failed", user_id=user_id, error=str(exc))
        return {"user_id": user_id, "sent": False, "error": str(exc)}
