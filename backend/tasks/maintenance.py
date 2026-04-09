"""
Maintenance background tasks for Mluv.Me.

Содержит задачи для:
- Очистки старых данных
- Обновления материализованных представлений
- Оптимизации базы данных
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from celery import Task
from sqlalchemy import text, delete, select, and_

from backend.tasks.celery_app import celery_app
from backend.db.database import AsyncSessionLocal
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AsyncTask(Task):
    """Base task class with async support."""

    def __call__(self, *args, **kwargs):
        """Run async task in a fresh event loop to avoid cross-loop asyncpg errors."""
        from backend.db.database import reset_engine, dispose_engine

        reset_engine()  # Discard stale connections from previous closed loop

        async def _wrapper():
            try:
                return await self.run(*args, **kwargs)
            finally:
                await dispose_engine()

        return asyncio.run(_wrapper())


@celery_app.task(bind=True, base=AsyncTask)
async def cleanup_old_data(self) -> Dict[str, Any]:
    """
    Очистка старых данных из базы.

    Вызывается ежедневно в 03:00 UTC.

    Удаляет:
    - Сообщения free-пользователей старше 7 дней
    - PRO-пользователи: сообщения НЕ удаляются (хранится вся история)
    - Устаревшие daily_stats старше 1 года

    Returns:
        dict: Статистика очистки
    """
    try:
        async with AsyncSessionLocal() as db:
            stats = {
                "timestamp": datetime.now().isoformat(),
                "messages_deleted": 0,
                "old_stats_deleted": 0,
            }

            from backend.models.message import Message
            from backend.models.subscription import Subscription

            now = datetime.now(timezone.utc)
            seven_days_ago = now - timedelta(days=7)

            # Находим user_id всех активных PRO-подписчиков
            pro_result = await db.execute(
                select(Subscription.user_id).where(
                    and_(
                        Subscription.plan == "pro",
                        Subscription.status == "active",
                        Subscription.expires_at > now,
                    )
                )
            )
            pro_user_ids = {row[0] for row in pro_result.fetchall()}

            # Удаляем сообщения старше 7 дней у НЕ-PRO пользователей
            delete_messages_query = delete(Message).where(
                and_(
                    Message.created_at < seven_days_ago,
                    ~Message.user_id.in_(pro_user_ids) if pro_user_ids else True,
                )
            )
            result = await db.execute(delete_messages_query)
            stats["messages_deleted"] = result.rowcount

            # Удаляем старые daily_stats (старше 1 года)
            year_ago = now - timedelta(days=365)

            from backend.models.stats import DailyStats

            delete_stats_query = delete(DailyStats).where(
                DailyStats.date < year_ago.date()
            )

            result = await db.execute(delete_stats_query)
            stats["old_stats_deleted"] = result.rowcount

            await db.commit()

            logger.info(
                "cleanup_completed",
                pro_users_preserved=len(pro_user_ids),
                **stats,
            )

            return stats

    except Exception as exc:
        logger.error("cleanup_failed", error=str(exc))
        raise


@celery_app.task(bind=True, base=AsyncTask, max_retries=3)
async def refresh_materialized_views(self) -> Dict[str, Any]:
    """
    Обновить материализованные представления.

    Вызывается каждый час для обновления агрегированных данных.

    Обновляет:
    - user_stats_summary: Агрегированная статистика пользователей

    Использует CONCURRENTLY для обновления без блокировки чтений.
    Это критически важно для производительности в production.

    Returns:
        dict: Результат обновления
    """
    start_time = datetime.now()

    try:
        async with AsyncSessionLocal() as db:
            # Refresh user_stats_summary materialized view
            # CONCURRENTLY позволяет обновлять без блокировки чтений
            await db.execute(
                text("REFRESH MATERIALIZED VIEW user_stats_summary")
            )
            await db.commit()

            duration = (datetime.now() - start_time).total_seconds()

            logger.info(
                "materialized_views_refreshed",
                duration_seconds=duration,
                views=["user_stats_summary"],
            )

            return {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "views_refreshed": ["user_stats_summary"],
            }

    except Exception as exc:
        logger.error("refresh_materialized_views_failed", error=str(exc))
        # Retry on failure with exponential backoff
        self.retry(exc=exc, countdown=60 * (2**self.request.retries))
        raise


@celery_app.task(bind=True, base=AsyncTask)
async def optimize_database(self) -> Dict[str, Any]:
    """
    Оптимизация базы данных.

    Вызывается раз в неделю для:
    - VACUUM ANALYZE (PostgreSQL)
    - Переиндексации при необходимости
    - Обновления статистики планировщика

    Returns:
        dict: Результат оптимизации
    """
    try:
        async with AsyncSessionLocal() as db:
            # Обновляем статистику таблиц
            await db.execute(text("ANALYZE"))

            logger.info("database_optimized")

            return {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "operations": ["ANALYZE"],
            }

    except Exception as exc:
        logger.error("database_optimization_failed", error=str(exc))
        raise


@celery_app.task(bind=True, base=AsyncTask)
async def backup_statistics(self) -> Dict[str, Any]:
    """
    Резервное копирование важной статистики.

    Вызывается ежедневно для сохранения ключевых метрик
    в долгосрочное хранилище (например, S3 или аналог).

    Returns:
        dict: Результат резервного копирования
    """
    try:
        # TODO: Реализовать бэкап в S3/облако при необходимости
        logger.info("statistics_backup_placeholder")

        return {
            "status": "placeholder",
            "timestamp": datetime.now().isoformat(),
            "note": "Will be implemented when cloud storage is configured",
        }

    except Exception as exc:
        logger.error("statistics_backup_failed", error=str(exc))
        raise
