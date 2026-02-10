"""
Celery application configuration for Mluv.Me.

Использует Redis как broker и backend для distributed task queue.
"""

from celery import Celery
from celery.schedules import crontab

from backend.config import get_settings

settings = get_settings()

# Создаем Celery приложение
celery_app = Celery(
    'mluv_tasks',
    broker=f'{settings.redis_url}/1',  # Database 1 для broker
    backend=f'{settings.redis_url}/2'  # Database 2 для results
)

# Конфигурация Celery
celery_app.conf.update(
    # Сериализация
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task tracking
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,  # 4 minutes warning

    # Worker settings
    worker_prefetch_multiplier=4,  # Сколько задач загружать заранее
    worker_max_tasks_per_child=1000,  # Перезапуск worker после 1000 задач

    # Result backend settings
    result_expires=3600,  # Результаты хранятся 1 час
    result_backend_transport_options={
        'master_name': 'mymaster',
    },

    # Broker settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,

    # Task routes (можно добавить позже для разных очередей)
    task_routes={
        'backend.tasks.analytics.*': {'queue': 'analytics'},
        'backend.tasks.notifications.*': {'queue': 'notifications'},
        'backend.tasks.maintenance.*': {'queue': 'maintenance'},
    },

    # Beat schedule (периодические задачи)
    beat_schedule={
        'check-streaks-daily': {
            'task': 'backend.tasks.gamification.check_and_reset_streaks',
            'schedule': crontab(hour=0, minute=5),  # 00:05 UTC daily
        },
        'send-daily-reminders': {
            'task': 'backend.tasks.notifications.send_evening_grammar_notifications',
            'schedule': crontab(hour=18, minute=0),  # 18:00 UTC = 19:00 CET
        },
        'aggregate-metrics': {
            'task': 'backend.tasks.analytics.aggregate_platform_metrics',
            'schedule': crontab(minute='*/30'),  # Every 30 minutes
        },
        'cleanup-old-data': {
            'task': 'backend.tasks.maintenance.cleanup_old_data',
            'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Monday 02:00
        },
        'refresh-materialized-views': {
            'task': 'backend.tasks.maintenance.refresh_materialized_views',
            'schedule': crontab(minute=0),  # Every hour
        },
    },
)

# Автоматическое обнаружение tasks в модулях
celery_app.autodiscover_tasks([
    'backend.tasks.analytics',
    'backend.tasks.notifications',
    'backend.tasks.gamification',
    'backend.tasks.maintenance',
])

# Сигналы для мониторинга (будет использоваться в monitoring.py)
from celery.signals import task_failure, task_success, task_retry

@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    """Логирование неудачных задач."""
    from backend.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.error(
        "task_failed",
        task_id=task_id,
        task_name=sender.name if sender else "unknown",
        exception=str(exception),
    )


@task_success.connect
def handle_task_success(sender=None, result=None, **kwargs):
    """Логирование успешных задач."""
    from backend.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info(
        "task_succeeded",
        task_name=sender.name if sender else "unknown",
    )


@task_retry.connect
def handle_task_retry(sender=None, reason=None, **kwargs):
    """Логирование повторных попыток."""
    from backend.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.warning(
        "task_retry",
        task_name=sender.name if sender else "unknown",
        reason=str(reason),
    )
