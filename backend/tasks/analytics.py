"""
Analytics background tasks for Mluv.Me.

Содержит задачи для:
- Расчета ежедневной статистики пользователей
- Агрегации метрик платформы
- Генерации еженедельных отчетов
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any

from celery import Task
from sqlalchemy import select, func

from backend.tasks.celery_app import celery_app
from backend.db.database import AsyncSessionLocal
from backend.db.repositories import StatsRepository, MessageRepository
from backend.cache.redis_client import redis_client
from backend.cache.cache_keys import CacheKeys
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


@celery_app.task(bind=True, base=AsyncTask, max_retries=3)
async def calculate_daily_statistics(self, user_id: int) -> Dict[str, Any]:
    """
    Рассчитать и закешировать ежедневную статистику пользователя.

    Вызывается:
    - Автоматически в конце дня для всех активных пользователей
    - По запросу при просмотре статистики (если еще не рассчитана)

    Args:
        user_id: ID пользователя

    Returns:
        dict: Рассчитанная статистика

    Raises:
        Exception: При ошибке расчета (с retry)
    """
    try:
        async with AsyncSessionLocal() as db:
            stats_repo = StatsRepository(db)
            message_repo = MessageRepository(db)

            # Получаем сегодняшнюю дату
            today = date.today()

            # Получаем все сообщения пользователя за сегодня
            messages = await message_repo.get_user_messages_by_date(
                user_id=user_id,
                start_date=today,
                end_date=today
            )

            if not messages:
                logger.info(
                    "no_messages_for_stats",
                    user_id=user_id,
                    date=today.isoformat()
                )
                return {
                    "user_id": user_id,
                    "date": today.isoformat(),
                    "messages_count": 0,
                    "words_said": 0,
                    "correct_percent": 0
                }

            # Рассчитываем метрики
            messages_count = len(messages)
            total_words = sum(msg.words_total or 0 for msg in messages)

            # Средний процент правильности
            scores = [msg.correctness_score for msg in messages if msg.correctness_score is not None]
            avg_correctness = int(sum(scores) / len(scores)) if scores else 0

            # Получаем текущий streak
            user_stats = await stats_repo.get_user_summary(user_id)
            current_streak = user_stats.get("current_streak", 0)

            # Формируем результат
            stats = {
                "user_id": user_id,
                "date": today.isoformat(),
                "messages_count": messages_count,
                "words_said": total_words,
                "correct_percent": avg_correctness,
                "streak_day": current_streak
            }

            # Обновляем в БД
            await stats_repo.update_daily(
                user_id=user_id,
                date_value=today,
                messages_count=messages_count,
                words_said=total_words,
                correct_percent=avg_correctness,
                streak_day=current_streak
            )

            await db.commit()

            # Кешируем результаты до конца дня
            cache_key = CacheKeys.DAILY_STATS.format(
                user_id=user_id,
                date=today.isoformat()
            )

            # TTL до конца дня
            now = datetime.now()
            midnight = datetime.combine(today + timedelta(days=1), datetime.min.time())
            ttl = int((midnight - now).total_seconds())

            await redis_client.set(cache_key, stats, ttl=ttl)

            logger.info(
                "daily_stats_calculated",
                user_id=user_id,
                date=today.isoformat(),
                messages_count=messages_count,
                words_said=total_words
            )

            return stats

    except Exception as exc:
        logger.error(
            "daily_stats_calculation_failed",
            user_id=user_id,
            error=str(exc)
        )
        # Retry с экспоненциальной задержкой
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, base=AsyncTask, rate_limit='10/m')
async def aggregate_platform_metrics(self) -> Dict[str, Any]:
    """
    Агрегировать метрики платформы (rate-limited).

    Рассчитывает:
    - Общее количество пользователей
    - Активных пользователей (за последние 7 дней)
    - Сообщений сегодня/за неделю/за месяц
    - Средний процент правильности
    - Общее количество звезд

    Returns:
        dict: Агрегированные метрики
    """
    try:
        async with AsyncSessionLocal() as db:
            from backend.models.user import User
            from backend.models.message import Message
            from backend.models.stats import Stars

            # Даты для фильтрации
            today = date.today()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)

            # Общее количество пользователей
            total_users_query = select(func.count(User.id))
            total_users = (await db.execute(total_users_query)).scalar()

            # Активные пользователи (за последние 7 дней)
            active_users_query = select(func.count(func.distinct(Message.user_id))).where(
                Message.created_at >= week_ago
            )
            active_users = (await db.execute(active_users_query)).scalar()

            # Сообщений за периоды
            messages_today_query = select(func.count(Message.id)).where(
                func.date(Message.created_at) == today
            )
            messages_today = (await db.execute(messages_today_query)).scalar()

            messages_week_query = select(func.count(Message.id)).where(
                Message.created_at >= week_ago
            )
            messages_week = (await db.execute(messages_week_query)).scalar()

            messages_month_query = select(func.count(Message.id)).where(
                Message.created_at >= month_ago
            )
            messages_month = (await db.execute(messages_month_query)).scalar()

            # Средний процент правильности
            avg_correctness_query = select(func.avg(Message.correctness_score)).where(
                Message.correctness_score.isnot(None)
            )
            avg_correctness = (await db.execute(avg_correctness_query)).scalar() or 0

            # Общее количество звезд
            total_stars_query = select(func.sum(Stars.lifetime))
            total_stars = (await db.execute(total_stars_query)).scalar() or 0

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "total_users": total_users,
                "active_users_7d": active_users,
                "messages_today": messages_today,
                "messages_week": messages_week,
                "messages_month": messages_month,
                "avg_correctness": round(avg_correctness, 2),
                "total_stars_lifetime": total_stars
            }

            # Кешируем на 30 минут
            cache_key = "platform:metrics:latest"
            await redis_client.set(cache_key, metrics, ttl=1800)

            logger.info(
                "platform_metrics_aggregated",
                total_users=total_users,
                active_users=active_users,
                messages_today=messages_today
            )

            return metrics

    except Exception as exc:
        logger.error(
            "platform_metrics_aggregation_failed",
            error=str(exc)
        )
        raise


@celery_app.task(bind=True, base=AsyncTask, max_retries=2)
async def generate_weekly_report(self, user_id: int) -> Dict[str, Any]:
    """
    Генерировать еженедельный отчет прогресса пользователя.

    Вызывается каждый понедельник для всех активных пользователей.

    Args:
        user_id: ID пользователя

    Returns:
        dict: Еженедельный отчет с метриками и рекомендациями
    """
    try:
        async with AsyncSessionLocal() as db:
            stats_repo = StatsRepository(db)
            MessageRepository(db)

            # Период: последние 7 дней
            today = date.today()
            week_ago = today - timedelta(days=7)

            # Получаем статистику за неделю
            weekly_stats = await stats_repo.get_stats_range(
                user_id=user_id,
                start_date=week_ago,
                end_date=today
            )

            if not weekly_stats:
                logger.info(
                    "no_activity_for_weekly_report",
                    user_id=user_id
                )
                return {
                    "user_id": user_id,
                    "period": f"{week_ago.isoformat()} - {today.isoformat()}",
                    "active": False
                }

            # Агрегируем метрики
            total_messages = sum(day.get("messages_count", 0) for day in weekly_stats)
            total_words = sum(day.get("words_said", 0) for day in weekly_stats)

            correctness_scores = [
                day.get("correct_percent", 0)
                for day in weekly_stats
                if day.get("correct_percent", 0) > 0
            ]
            avg_correctness = int(sum(correctness_scores) / len(correctness_scores)) if correctness_scores else 0

            # Дни активности
            active_days = len([day for day in weekly_stats if day.get("messages_count", 0) > 0])

            # Streak информация
            user_stats = await stats_repo.get_user_summary(user_id)
            current_streak = user_stats.get("current_streak", 0)
            max_streak = user_stats.get("max_streak", 0)

            # Формируем отчет
            report = {
                "user_id": user_id,
                "period": f"{week_ago.isoformat()} - {today.isoformat()}",
                "active": True,
                "total_messages": total_messages,
                "total_words": total_words,
                "avg_correctness": avg_correctness,
                "active_days": active_days,
                "current_streak": current_streak,
                "max_streak": max_streak,
                "messages_per_day": round(total_messages / 7, 1),
                "words_per_day": round(total_words / 7, 1),
            }

            # Генерируем рекомендации
            recommendations = []

            if active_days < 5:
                recommendations.append("Попробуйте практиковаться чаще - хотя бы 5 дней в неделю!")

            if avg_correctness < 70:
                recommendations.append("Обратите внимание на грамматику - попросите Хонзика объяснять больше!")

            if total_messages < 10:
                recommendations.append("Отправляйте больше сообщений - практика делает совершенным!")

            if current_streak == 0 and active_days > 0:
                recommendations.append("Начните новый streak! Занимайтесь каждый день.")

            report["recommendations"] = recommendations

            # Кешируем отчет на неделю
            cache_key = f"weekly_report:{user_id}:{today.isoformat()}"
            await redis_client.set(cache_key, report, ttl=604800)  # 7 days

            logger.info(
                "weekly_report_generated",
                user_id=user_id,
                total_messages=total_messages,
                active_days=active_days,
                avg_correctness=avg_correctness
            )

            return report

    except Exception as exc:
        logger.error(
            "weekly_report_generation_failed",
            user_id=user_id,
            error=str(exc)
        )
        raise self.retry(exc=exc, countdown=300)  # Retry после 5 минут


@celery_app.task(bind=True, base=AsyncTask)
async def calculate_all_users_daily_stats(self) -> Dict[str, Any]:
    """
    Рассчитать ежедневную статистику для всех активных пользователей.

    Вызывается автоматически в конце дня (00:05 UTC).
    Обрабатывает только пользователей, активных за последние 7 дней.

    Returns:
        dict: Результаты обработки
    """
    try:
        async with AsyncSessionLocal() as db:
            from backend.models.message import Message

            # Получаем пользователей, активных за последнюю неделю
            week_ago = datetime.now() - timedelta(days=7)

            query = select(func.distinct(Message.user_id)).where(
                Message.created_at >= week_ago
            )
            result = await db.execute(query)
            active_user_ids = [row[0] for row in result.all()]

            logger.info(
                "calculating_daily_stats_for_users",
                user_count=len(active_user_ids)
            )

            # Запускаем задачи для каждого пользователя
            successful = 0
            failed = 0

            for user_id in active_user_ids:
                try:
                    # Запускаем задачу асинхронно
                    calculate_daily_statistics.apply_async(
                        args=[user_id],
                        countdown=0
                    )
                    successful += 1
                except Exception as e:
                    logger.error(
                        "failed_to_schedule_user_stats",
                        user_id=user_id,
                        error=str(e)
                    )
                    failed += 1

            result = {
                "total_users": len(active_user_ids),
                "scheduled": successful,
                "failed": failed,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(
                "daily_stats_calculation_completed",
                **result
            )

            return result

    except Exception as exc:
        logger.error(
            "all_users_daily_stats_failed",
            error=str(exc)
        )
        raise
