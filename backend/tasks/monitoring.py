"""
Monitoring and metrics for Celery tasks.

Интеграция с Sentry и логирование метрик.
"""

from typing import Dict, Any
from datetime import datetime

from celery.signals import (
    task_failure,
    task_success,
    task_retry,
    task_prerun,
    task_postrun,
)

from backend.utils.logger import get_logger

logger = get_logger(__name__)


# Task execution metrics
task_metrics: Dict[str, Dict[str, Any]] = {
    "total_executed": 0,
    "total_failed": 0,
    "total_retried": 0,
    "by_task": {},
}


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """
    Handler вызывается перед запуском задачи.

    Логирует начало выполнения задачи.
    """
    logger.info(
        "task_started",
        task_id=task_id,
        task_name=sender.name if sender else "unknown",
    )


@task_postrun.connect
def task_postrun_handler(
    sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **extra
):
    """
    Handler вызывается после завершения задачи.

    Логирует завершение и обновляет метрики.
    """
    task_name = sender.name if sender else "unknown"

    logger.info(
        "task_completed",
        task_id=task_id,
        task_name=task_name,
        state=state,
    )

    # Обновляем метрики
    task_metrics["total_executed"] += 1

    if task_name not in task_metrics["by_task"]:
        task_metrics["by_task"][task_name] = {
            "executed": 0,
            "failed": 0,
            "retried": 0,
            "last_execution": None,
        }

    task_metrics["by_task"][task_name]["executed"] += 1
    task_metrics["by_task"][task_name]["last_execution"] = datetime.now().isoformat()


@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **extra
):
    """
    Handler вызывается при ошибке задачи.

    Логирует ошибку и отправляет в Sentry.
    """
    task_name = sender.name if sender else "unknown"

    logger.error(
        "task_failed",
        task_id=task_id,
        task_name=task_name,
        exception=str(exception),
        args=args,
        kwargs=kwargs,
    )

    # Обновляем метрики
    task_metrics["total_failed"] += 1

    if task_name in task_metrics["by_task"]:
        task_metrics["by_task"][task_name]["failed"] += 1

    # Отправляем в Sentry (если настроен)
    try:
        import sentry_sdk
        sentry_sdk.capture_exception(exception)
    except ImportError:
        # Sentry не установлен
        pass


@task_success.connect
def task_success_handler(sender=None, result=None, **extra):
    """
    Handler вызывается при успешном завершении задачи.

    Логирует успех.
    """
    task_name = sender.name if sender else "unknown"

    logger.debug(
        "task_succeeded",
        task_name=task_name,
    )


@task_retry.connect
def task_retry_handler(
    sender=None, task_id=None, reason=None, einfo=None, **extra
):
    """
    Handler вызывается при повторной попытке выполнения задачи.

    Логирует retry.
    """
    task_name = sender.name if sender else "unknown"

    logger.warning(
        "task_retrying",
        task_id=task_id,
        task_name=task_name,
        reason=str(reason),
    )

    # Обновляем метрики
    task_metrics["total_retried"] += 1

    if task_name in task_metrics["by_task"]:
        task_metrics["by_task"][task_name]["retried"] += 1


def get_task_metrics() -> Dict[str, Any]:
    """
    Получить текущие метрики задач.

    Returns:
        dict: Метрики выполнения задач
    """
    return {
        **task_metrics,
        "timestamp": datetime.now().isoformat(),
    }


def reset_task_metrics() -> None:
    """Сбросить метрики задач."""
    global task_metrics
    task_metrics = {
        "total_executed": 0,
        "total_failed": 0,
        "total_retried": 0,
        "by_task": {},
    }
    logger.info("task_metrics_reset")
