"""
Celery tasks package for Mluv.Me.

Содержит все background tasks для асинхронной обработки:
- Analytics (статистика)
- Notifications (уведомления)
- Maintenance (обслуживание)
"""

from backend.tasks.celery_app import celery_app

__all__ = ["celery_app"]
