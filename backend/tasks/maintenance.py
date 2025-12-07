"""
Maintenance background tasks for Mluv.Me.

Содержит задачи для:
- Очистки старых данных
- Обновления материализованных представлений
- Оптимизации базы данных
"""

from datetime import datetime, timedelta
from typing import Dict, Any

from celery import Task
from sqlalchemy import text, select, delete

from backend.tasks.celery_app import celery_app
from backend.db.database import AsyncSessionLocal
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
async def cleanup_old_data(self) -> Dict[str, Any]:
    """
    Очистка старых данных из базы.

    Вызывается каждый понедельник в 02:00 UTC.

    Удаляет:
    - Сообщения старше 90 дней (опционально, для GDPR)
    - Устаревшие кеш записи
    - Неиспользуемые временные данные

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

            # Удаляем старые daily_stats (старше 1 года)
            # Оставляем только за последний год для производительности
            year_ago = datetime.now() - timedelta(days=365)

            from backend.models.stats import DailyStats

            delete_stats_query = delete(DailyStats).where(
                DailyStats.date < year_ago.date()
            )

            result = await db.execute(delete_stats_query)
            stats["old_stats_deleted"] = result.rowcount

            await db.commit()

            logger.info(
                "cleanup_completed",
                **stats
            )

            return stats

    except Exception as exc:
        logger.error(
            "cleanup_failed",
            error=str(exc)
        )
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
            await db.execute(text(
                "REFRESH MATERIALIZED VIEW CONCURRENTLY user_stats_summary"
            ))
            await db.commit()

            duration = (datetime.now() - start_time).total_seconds()

            logger.info(
                "materialized_views_refreshed",
                duration_seconds=duration,
                views=["user_stats_summary"]
            )

            return {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "views_refreshed": ["user_stats_summary"]
            }

    except Exception as exc:
        logger.error(
            "refresh_materialized_views_failed",
            error=str(exc)
        )
        # Retry on failure with exponential backoff
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
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
                "operations": ["ANALYZE"]
            }

    except Exception as exc:
        logger.error(
            "database_optimization_failed",
            error=str(exc)
        )
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
            "note": "Will be implemented when cloud storage is configured"
        }

    except Exception as exc:
        logger.error(
            "statistics_backup_failed",
            error=str(exc)
        )
        raise
