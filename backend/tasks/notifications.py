"""
Notification background tasks for Mluv.Me.

Evening grammar notifications (19:00 CET = 18:00 UTC):
- Grammar rule of the day
- Practice reminder with streak info
- Czech-only content (immersion)

Daily slang notification (19:00 CET = 18:00 UTC):
- Random slang/idiom of the day
- Sent to users with notifications_enabled
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Any

from celery import Task
from sqlalchemy import select, func

from backend.tasks.celery_app import celery_app
from backend.db.database import AsyncSessionLocal
from backend.db.repositories import StatsRepository, UserRepository
from backend.db.grammar_repository import GrammarRepository
from backend.services.grammar_service import GrammarService
from backend.data.slang_data import SLANG_ITEMS
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AsyncTask(Task):
    """Base task class with async support."""

    def __call__(self, *args, **kwargs):
        """Run async task in a fresh event loop to avoid cross-loop asyncpg errors."""
        return asyncio.run(self.run_async(*args, **kwargs))

    async def run_async(self, *args, **kwargs):
        raise NotImplementedError


# ────────────────────────────────────────────────────────
#  send_grammar_reminder
# ────────────────────────────────────────────────────────


class _SendGrammarReminderTask(AsyncTask):
    name = "backend.tasks.notifications.send_grammar_reminder"
    max_retries = 5

    async def run_async(self, user_id: int) -> Dict[str, Any]:
        try:
            async with AsyncSessionLocal() as db:
                user_repo = UserRepository(db)
                stats_repo = StatsRepository(db)
                grammar_repo = GrammarRepository(db)
                grammar_service = GrammarService(grammar_repo)

                user = await user_repo.get_by_id(user_id)
                if not user:
                    logger.warning("user_not_found_for_reminder", user_id=user_id)
                    return {
                        "user_id": user_id,
                        "sent": False,
                        "reason": "user_not_found",
                    }

                if user.settings and not user.settings.notifications_enabled:
                    return {
                        "user_id": user_id,
                        "sent": False,
                        "reason": "notifications_disabled",
                    }

                user_stats = await stats_repo.get_user_summary(user_id)
                current_streak = user_stats.get("current_streak", 0)
                total_stars = user_stats.get("total_stars", 0)

                message = await grammar_service.get_notification_message(
                    user_id=user_id,
                    streak=current_streak,
                    stars=total_stars,
                )

                if not message:
                    return {
                        "user_id": user_id,
                        "sent": False,
                        "reason": "no_grammar_rule",
                    }

                # get_notification_message returns {"message": str, "rule_id": int}
                message_text = message["message"]

                try:
                    from aiogram import Bot
                    from backend.config import get_settings

                    settings = get_settings()
                    bot = Bot(token=settings.telegram_bot_token)
                    await bot.send_message(user.telegram_id, message_text, parse_mode="HTML")
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
                        "telegram_send_failed", user_id=user_id, error=str(bot_exc)
                    )
                    raise self.retry(exc=bot_exc, countdown=300)

        except Exception as exc:
            logger.error("grammar_reminder_failed", user_id=user_id, error=str(exc))
            raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


send_grammar_reminder = celery_app.register_task(_SendGrammarReminderTask())


# ────────────────────────────────────────────────────────
#  send_evening_grammar_notifications
# ────────────────────────────────────────────────────────


class _SendEveningNotificationsTask(AsyncTask):
    name = "backend.tasks.notifications.send_evening_grammar_notifications"

    async def run_async(self) -> Dict[str, Any]:
        """
        Send evening grammar notifications to all active users.
        Triggered daily at 18:00 UTC (= 19:00 CET).
        """
        try:
            async with AsyncSessionLocal() as db:
                from backend.models.message import Message
                from backend.models.user import UserSettings

                two_weeks_ago = datetime.now() - timedelta(days=14)

                query = (
                    select(func.distinct(Message.user_id))
                    .join(UserSettings, Message.user_id == UserSettings.user_id)
                    .where(
                        Message.created_at >= two_weeks_ago,
                        UserSettings.notifications_enabled == True,  # noqa: E712
                    )
                )

                result = await db.execute(query)
                active_user_ids = [row[0] for row in result.all()]

                logger.info(
                    "sending_evening_grammar_notifications",
                    user_count=len(active_user_ids),
                )

                scheduled = 0
                failed = 0

                for uid in active_user_ids:
                    try:
                        send_grammar_reminder.apply_async(
                            args=[uid],
                            countdown=scheduled * 2,
                        )
                        scheduled += 1
                    except Exception as e:
                        logger.error(
                            "failed_to_schedule_grammar_reminder",
                            user_id=uid,
                            error=str(e),
                        )
                        failed += 1

                stats = {
                    "total_users": len(active_user_ids),
                    "scheduled": scheduled,
                    "failed": failed,
                    "timestamp": datetime.now().isoformat(),
                }
                logger.info("evening_grammar_notifications_completed", **stats)
                return stats

        except Exception as exc:
            logger.error("evening_grammar_notifications_failed", error=str(exc))
            raise


send_evening_grammar_notifications = celery_app.register_task(
    _SendEveningNotificationsTask()
)


# ────────────────────────────────────────────────────────
#  send_weekly_report_notification
# ────────────────────────────────────────────────────────


class _SendWeeklyReportTask(AsyncTask):
    name = "backend.tasks.notifications.send_weekly_report_notification"

    async def run_async(self, user_id: int) -> Dict[str, Any]:
        try:
            async with AsyncSessionLocal() as db:
                user_repo = UserRepository(db)
                grammar_repo = GrammarRepository(db)
                grammar_service = GrammarService(grammar_repo)

                user = await user_repo.get_by_id(user_id)
                if not user or (
                    user.settings and not user.settings.notifications_enabled
                ):
                    return {
                        "user_id": user_id,
                        "sent": False,
                        "reason": "notifications_disabled",
                    }

                summary = await grammar_service.get_progress_summary(user_id)
                message = "📊 <b>Týdenní přehled</b>\n\n"

                if summary.get("total_practiced", 0) > 0:
                    message += (
                        f"📝 Procvičená pravidla: {summary['total_practiced']}\n"
                        f"✅ Celková přesnost: {summary['average_accuracy']}%\n"
                        f"🏆 Zvládnutá pravidla: {summary['mastered_count']}\n"
                        f"📚 Celkem pravidel: {summary['total_rules']}\n\n"
                    )
                    if summary.get("weak_count", 0) > 0:
                        message += (
                            f"💪 K procvičení: {summary['weak_count']} pravidel\n\n"
                        )
                    message += "Pokračuj dál — každý den se zlepšuješ! 🚀"
                else:
                    message += (
                        "Tento týden jsi ještě neprocvičoval(a) gramatiku.\n\n"
                        "Začni dnes — stačí jedna minihra denně! 🎮\n"
                        "Učení je cesta, ne cíl. 💪"
                    )

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


send_weekly_report_notification = celery_app.register_task(_SendWeeklyReportTask())


# ────────────────────────────────────────────────────────
#  send_slang_reminder  (per-user)
# ────────────────────────────────────────────────────────


def _get_daily_slang() -> tuple[str, str, str]:
    """Pick a deterministic-random slang item based on the current date."""
    day_seed = int(datetime.utcnow().strftime("%Y%m%d"))
    rng = random.Random(day_seed)
    return rng.choice(SLANG_ITEMS)


class _SendSlangReminderTask(AsyncTask):
    name = "backend.tasks.notifications.send_slang_reminder"
    max_retries = 3

    async def run_async(self, user_id: int) -> Dict[str, Any]:
        try:
            async with AsyncSessionLocal() as db:
                user_repo = UserRepository(db)
                user = await user_repo.get_by_id(user_id)

                if not user:
                    return {"user_id": user_id, "sent": False, "reason": "user_not_found"}

                if user.settings is not None and not user.settings.notifications_enabled:
                    return {"user_id": user_id, "sent": False, "reason": "notifications_disabled"}

                phrase, meaning, example = _get_daily_slang()

                message = (
                    f"🗣️ <b>Slovo dne</b>\n\n"
                    f"Ahoj! Věděl(a) jsi, že <b>{phrase}</b> znamená "
                    f"<i>{meaning}</i>?\n\n"
                    f"📝 <b>Příklad:</b> {example}\n\n"
                    f"A to je tvoje denní připomínka procvičovat češtinu! 💪\n"
                    f"👉 Otevři sekci <b>Slang</b> v Procvičování a uč se další."
                )

                try:
                    from aiogram import Bot
                    from backend.config import get_settings

                    settings = get_settings()
                    bot = Bot(token=settings.telegram_bot_token)
                    await bot.send_message(user.telegram_id, message, parse_mode="HTML")
                    await bot.session.close()

                    logger.info(
                        "slang_reminder_sent",
                        user_id=user_id,
                        telegram_id=user.telegram_id,
                        phrase=phrase,
                    )
                    return {"user_id": user_id, "sent": True, "phrase": phrase}

                except Exception as bot_exc:
                    logger.error("slang_telegram_send_failed", user_id=user_id, error=str(bot_exc))
                    raise self.retry(exc=bot_exc, countdown=300)

        except Exception as exc:
            logger.error("slang_reminder_failed", user_id=user_id, error=str(exc))
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


send_slang_reminder = celery_app.register_task(_SendSlangReminderTask())


# ────────────────────────────────────────────────────────
#  send_evening_slang_notifications  (dispatcher)
# ────────────────────────────────────────────────────────


class _SendEveningSlangNotificationsTask(AsyncTask):
    name = "backend.tasks.notifications.send_evening_slang_notifications"

    async def run_async(self) -> Dict[str, Any]:
        """
        Send evening slang notifications to all users with notifications enabled.
        Triggered daily at 18:00 UTC (= 19:00 CET), same window as grammar.
        """
        try:
            async with AsyncSessionLocal() as db:
                from backend.models.user import User, UserSettings
                from sqlalchemy.orm import selectinload

                # LEFT OUTER JOIN — users without a settings row
                # are treated as notifications_enabled=True (default)
                query = (
                    select(User.id)
                    .outerjoin(UserSettings, User.id == UserSettings.user_id)
                    .where(
                        (UserSettings.notifications_enabled == True)  # noqa: E712
                        | (UserSettings.id == None)  # noqa: E711  — no settings row
                    )
                )

                result = await db.execute(query)
                user_ids = [row[0] for row in result.all()]

                logger.info(
                    "sending_evening_slang_notifications",
                    user_count=len(user_ids),
                )

                scheduled = 0
                failed = 0

                for uid in user_ids:
                    try:
                        send_slang_reminder.apply_async(
                            args=[uid],
                            countdown=scheduled * 2,  # stagger 2s apart
                        )
                        scheduled += 1
                    except Exception as e:
                        logger.error(
                            "failed_to_schedule_slang_reminder",
                            user_id=uid,
                            error=str(e),
                        )
                        failed += 1

                stats = {
                    "total_users": len(user_ids),
                    "scheduled": scheduled,
                    "failed": failed,
                    "phrase": _get_daily_slang()[0],
                    "timestamp": datetime.now().isoformat(),
                }
                logger.info("evening_slang_notifications_completed", **stats)
                return stats

        except Exception as exc:
            logger.error("evening_slang_notifications_failed", error=str(exc))
            raise


send_evening_slang_notifications = celery_app.register_task(
    _SendEveningSlangNotificationsTask()
)