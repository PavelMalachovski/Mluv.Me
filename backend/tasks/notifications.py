"""
Notification background tasks for Mluv.Me.

Содержит задачи для:
- Напоминаний о streak
- Daily challenge уведомлений
- Еженедельных отчетов
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any

from celery import Task
from sqlalchemy import select, func

from backend.tasks.celery_app import celery_app
from backend.db.database import AsyncSessionLocal
from backend.db.repositories import StatsRepository, UserRepository
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
async def send_streak_reminder(self, user_id: int) -> Dict[str, Any]:
    """
    Отправить напоминание о streak пользователю.

    Проверяет, практиковался ли пользователь сегодня.
    Если нет - отправляет уведомление в Telegram.

    Args:
        user_id: ID пользователя

    Returns:
        dict: Результат отправки

    Raises:
        Exception: При ошибке отправки (с retry)
    """
    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            stats_repo = StatsRepository(db)

            # Получаем пользователя
            user = await user_repo.get_by_id(user_id)
            if not user:
                logger.warning("user_not_found_for_reminder", user_id=user_id)
                return {
                    "user_id": user_id,
                    "sent": False,
                    "reason": "user_not_found"
                }

            # Проверяем настройки уведомлений
            if user.settings and not user.settings.notifications_enabled:
                logger.debug(
                    "notifications_disabled",
                    user_id=user_id,
                    telegram_id=user.telegram_id
                )
                return {
                    "user_id": user_id,
                    "sent": False,
                    "reason": "notifications_disabled"
                }

            # Получаем текущий streak
            user_stats = await stats_repo.get_user_summary(user_id)
            current_streak = user_stats.get("current_streak", 0)

            # Проверяем активность сегодня
            from backend.services.gamification import GamificationService
            gamification = GamificationService(stats_repo, user_repo)

            user_date = gamification.get_user_date(
                user.settings.timezone if user.settings else None
            )

            today_stats = await stats_repo.get_daily_stats(user_id, user_date)
            messages_today = today_stats.get("messages_count", 0) if today_stats else 0

            # Если сегодня уже практиковался - не отправляем
            if messages_today > 0:
                logger.debug(
                    "user_already_practiced_today",
                    user_id=user_id,
                    messages_today=messages_today
                )
                return {
                    "user_id": user_id,
                    "sent": False,
                    "reason": "already_practiced"
                }

            # Отправляем уведомление через Telegram Bot API
            try:
                from aiogram import Bot
                from backend.config import get_settings

                settings = get_settings()
                bot = Bot(token=settings.telegram_bot_token)

                # Формируем сообщение в зависимости от языка и streak
                ui_lang = user.ui_language or "ru"

                if current_streak > 0:
                    # Есть активный streak - мотивируем его сохранить
                    if ui_lang == "uk":
                        message = (
                            f"🔥 Не втрати свій streak {current_streak} днів!\n\n"
                            "Попрактикуй чеську мову сьогодні, щоб продовжити. "
                            "Хонзік чекає на твоє повідомлення! 🇨🇿"
                        )
                    else:  # ru
                        message = (
                            f"🔥 Не потеряй свой streak {current_streak} дней!\n\n"
                            "Попрактикуй чешский сегодня, чтобы продолжить. "
                            "Хонзик ждет твоего сообщения! 🇨🇿"
                        )
                else:
                    # Нет streak - общая мотивация
                    if ui_lang == "uk":
                        message = (
                            "👋 Привіт! Сьогодні ще не практикувався?\n\n"
                            "Відправ голосове повідомлення Хонзіку і заробляй зірки! ⭐\n"
                            "Регулярна практика - ключ до успіху! 🎯"
                        )
                    else:  # ru
                        message = (
                            "👋 Привет! Сегодня еще не практиковался?\n\n"
                            "Отправь голосовое Хонзику и зарабатывай звезды! ⭐\n"
                            "Регулярная практика - ключ к успеху! 🎯"
                        )

                await bot.send_message(user.telegram_id, message)
                await bot.session.close()

                logger.info(
                    "streak_reminder_sent",
                    user_id=user_id,
                    telegram_id=user.telegram_id,
                    current_streak=current_streak
                )

                return {
                    "user_id": user_id,
                    "sent": True,
                    "telegram_id": user.telegram_id,
                    "current_streak": current_streak
                }

            except Exception as bot_exc:
                logger.error(
                    "telegram_send_failed",
                    user_id=user_id,
                    error=str(bot_exc)
                )
                raise self.retry(exc=bot_exc, countdown=300)  # Retry после 5 минут

    except Exception as exc:
        logger.error(
            "streak_reminder_failed",
            user_id=user_id,
            error=str(exc)
        )
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, base=AsyncTask)
async def send_daily_reminders(self) -> Dict[str, Any]:
    """
    Отправить ежедневные напоминания всем активным пользователям.

    Вызывается автоматически в 18:00 UTC каждый день.
    Обрабатывает только пользователей с включенными уведомлениями,
    которые были активны в последние 7 дней и еще не практиковались сегодня.

    Returns:
        dict: Статистика отправки
    """
    try:
        async with AsyncSessionLocal() as db:
            from backend.models.message import Message
            from backend.models.user_settings import UserSettings

            # Находим активных пользователей за последние 7 дней
            week_ago = datetime.now() - timedelta(days=7)

            query = (
                select(func.distinct(Message.user_id))
                .join(UserSettings, Message.user_id == UserSettings.user_id)
                .where(
                    Message.created_at >= week_ago,
                    UserSettings.notifications_enabled == True
                )
            )

            result = await db.execute(query)
            active_user_ids = [row[0] for row in result.all()]

            logger.info(
                "sending_daily_reminders",
                user_count=len(active_user_ids)
            )

            # Запускаем задачи отправки для каждого пользователя
            sent = 0
            failed = 0
            skipped = 0

            for user_id in active_user_ids:
                try:
                    # Запускаем задачу асинхронно с небольшой задержкой
                    # чтобы не перегрузить Telegram API
                    send_streak_reminder.apply_async(
                        args=[user_id],
                        countdown=sent * 2  # 2 секунды между отправками
                    )
                    sent += 1
                except Exception as e:
                    logger.error(
                        "failed_to_schedule_reminder",
                        user_id=user_id,
                        error=str(e)
                    )
                    failed += 1

            result = {
                "total_users": len(active_user_ids),
                "scheduled": sent,
                "failed": failed,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(
                "daily_reminders_completed",
                **result
            )

            return result

    except Exception as exc:
        logger.error(
            "daily_reminders_failed",
            error=str(exc)
        )
        raise


@celery_app.task(bind=True, base=AsyncTask)
async def send_daily_challenge_notification(self, user_id: int) -> Dict[str, Any]:
    """
    Отправить уведомление о Daily Challenge.

    Вызывается когда пользователь близок к выполнению daily challenge
    (например, отправил 3 или 4 сообщения из 5).

    Args:
        user_id: ID пользователя

    Returns:
        dict: Результат отправки
    """
    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)
            stats_repo = StatsRepository(db)

            # Получаем пользователя
            user = await user_repo.get_by_id(user_id)
            if not user or (user.settings and not user.settings.notifications_enabled):
                return {
                    "user_id": user_id,
                    "sent": False,
                    "reason": "notifications_disabled"
                }

            # Проверяем прогресс challenge
            from backend.services.gamification import GamificationService
            gamification = GamificationService(stats_repo, user_repo)

            user_date = gamification.get_user_date(
                user.settings.timezone if user.settings else None
            )

            today_stats = await stats_repo.get_daily_stats(user_id, user_date)
            messages_today = today_stats.get("messages_count", 0) if today_stats else 0

            # Отправляем уведомление если 3 или 4 сообщения
            if messages_today not in [3, 4]:
                return {
                    "user_id": user_id,
                    "sent": False,
                    "reason": "not_applicable",
                    "messages_today": messages_today
                }

            needed = 5 - messages_today

            # Формируем сообщение
            ui_lang = user.ui_language or "ru"

            if ui_lang == "uk":
                message = (
                    f"🎯 Daily Challenge майже виконано!\n\n"
                    f"Відправ ще {needed} повідомлень і отримай +5 зірок! ⭐\n"
                    f"Прогрес: {messages_today}/5"
                )
            else:  # ru
                message = (
                    f"🎯 Daily Challenge почти выполнен!\n\n"
                    f"Отправь еще {needed} сообщений и получи +5 звезд! ⭐\n"
                    f"Прогресс: {messages_today}/5"
                )

            # Отправляем через Telegram
            from aiogram import Bot
            from backend.config import get_settings

            settings = get_settings()
            bot = Bot(token=settings.telegram_bot_token)

            await bot.send_message(user.telegram_id, message)
            await bot.session.close()

            logger.info(
                "daily_challenge_notification_sent",
                user_id=user_id,
                messages_today=messages_today
            )

            return {
                "user_id": user_id,
                "sent": True,
                "messages_today": messages_today,
                "needed": needed
            }

    except Exception as exc:
        logger.error(
            "daily_challenge_notification_failed",
            user_id=user_id,
            error=str(exc)
        )
        return {
            "user_id": user_id,
            "sent": False,
            "error": str(exc)
        }


@celery_app.task(bind=True, base=AsyncTask)
async def send_weekly_report_notification(self, user_id: int) -> Dict[str, Any]:
    """
    Отправить еженедельный отчет пользователю.

    Вызывается каждый понедельник для всех активных пользователей.
    Генерирует отчет и отправляет его в Telegram.

    Args:
        user_id: ID пользователя

    Returns:
        dict: Результат отправки
    """
    try:
        async with AsyncSessionLocal() as db:
            user_repo = UserRepository(db)

            # Получаем пользователя
            user = await user_repo.get_by_id(user_id)
            if not user or (user.settings and not user.settings.notifications_enabled):
                return {
                    "user_id": user_id,
                    "sent": False,
                    "reason": "notifications_disabled"
                }

            # Генерируем отчет (используем задачу из analytics)
            from backend.tasks.analytics import generate_weekly_report

            report_result = await generate_weekly_report.apply_async(args=[user_id])
            report = await report_result.get()

            if not report.get("active"):
                return {
                    "user_id": user_id,
                    "sent": False,
                    "reason": "no_activity"
                }

            # Формируем сообщение
            ui_lang = user.ui_language or "ru"

            if ui_lang == "uk":
                message = (
                    "📊 Твій тижневий звіт\n\n"
                    f"📝 Повідомлень: {report['total_messages']}\n"
                    f"💬 Слів: {report['total_words']}\n"
                    f"✅ Правильність: {report['avg_correctness']}%\n"
                    f"📅 Активних днів: {report['active_days']}/7\n"
                    f"🔥 Поточний streak: {report['current_streak']}\n"
                    f"🏆 Максимальний streak: {report['max_streak']}\n\n"
                )

                if report.get("recommendations"):
                    message += "💡 Рекомендації:\n"
                    for rec in report["recommendations"]:
                        message += f"• {rec}\n"
            else:  # ru
                message = (
                    "📊 Твой недельный отчет\n\n"
                    f"📝 Сообщений: {report['total_messages']}\n"
                    f"💬 Слов: {report['total_words']}\n"
                    f"✅ Правильность: {report['avg_correctness']}%\n"
                    f"📅 Активных дней: {report['active_days']}/7\n"
                    f"🔥 Текущий streak: {report['current_streak']}\n"
                    f"🏆 Максимальный streak: {report['max_streak']}\n\n"
                )

                if report.get("recommendations"):
                    message += "💡 Рекомендации:\n"
                    for rec in report["recommendations"]:
                        message += f"• {rec}\n"

            message += "\nПродолжай в том же духе! 🚀"

            # Отправляем через Telegram
            from aiogram import Bot
            from backend.config import get_settings

            settings = get_settings()
            bot = Bot(token=settings.telegram_bot_token)

            await bot.send_message(user.telegram_id, message)
            await bot.session.close()

            logger.info(
                "weekly_report_notification_sent",
                user_id=user_id,
                total_messages=report["total_messages"]
            )

            return {
                "user_id": user_id,
                "sent": True,
                "report": report
            }

    except Exception as exc:
        logger.error(
            "weekly_report_notification_failed",
            user_id=user_id,
            error=str(exc)
        )
        return {
            "user_id": user_id,
            "sent": False,
            "error": str(exc)
        }
