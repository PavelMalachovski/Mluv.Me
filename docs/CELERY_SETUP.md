# Celery Task Queue Setup - Mluv.Me

## 📋 Overview

Celery интегрирован в Mluv.Me для асинхронной обработки задач в фоне. Это позволяет:

- **Снизить latency**: Пользователи не ждут завершения тяжелых операций
- **Улучшить масштабируемость**: Задачи распределяются между worker'ами
- **Повысить надежность**: Retry механизм для неудачных задач
- **Автоматизировать**: Периодические задачи (streak checks, notifications)

## 🏗️ Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   FastAPI   │────────▶│   Redis     │◀────────│   Celery    │
│   Backend   │         │   Broker    │         │   Workers   │
└─────────────┘         └─────────────┘         └─────────────┘
                             │
                             ▼
                        ┌─────────────┐
                        │   Redis     │
                        │   Results   │
                        └─────────────┘
```

### Components

1. **Redis Database 1**: Celery message broker (очередь задач)
2. **Redis Database 2**: Celery result backend (результаты задач)
3. **Celery Workers**: Выполняют задачи асинхронно
4. **Celery Beat**: Планировщик периодических задач
5. **Flower**: Web dashboard для мониторинга

## 📦 Installation

Зависимости уже добавлены в `requirements.txt`:

```bash
pip install -r requirements.txt
```

Включает:
- `celery[redis]==5.4.0` - Celery с поддержкой Redis
- `flower==2.0.1` - Мониторинг dashboard

## 🚀 Running Celery

### Development (Windows)

Откройте **3 терминала**:

**Terminal 1 - Celery Worker:**
```bash
cd C:\Git\Mluv.Me
scripts\start_celery_worker.bat
```

**Terminal 2 - Celery Beat (scheduler):**
```bash
cd C:\Git\Mluv.Me
scripts\start_celery_beat.bat
```

**Terminal 3 - Flower (monitoring):**
```bash
cd C:\Git\Mluv.Me
scripts\start_celery_flower.bat
```

Flower dashboard: http://localhost:5555 (admin/admin123)

### Development (Linux/Mac)

```bash
# Terminal 1 - Worker
./scripts/start_celery_worker.sh

# Terminal 2 - Beat
./scripts/start_celery_beat.sh

# Terminal 3 - Flower
./scripts/start_celery_flower.sh
```

### Production (Railway.com)

Railway автоматически запускает worker через `Procfile`:

```yaml
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
worker: celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4
beat: celery -A backend.tasks.celery_app beat --loglevel=info
```

## 📊 Task Types

### Analytics Tasks (`backend/tasks/analytics.py`)

**1. `calculate_daily_statistics(user_id: int)`**
- Рассчитывает ежедневную статистику пользователя
- Кеширует результаты
- Retry: 3 попытки

**2. `aggregate_platform_metrics()`**
- Агрегирует метрики платформы
- Rate limited: 10/minute
- Выполняется каждые 30 минут

**3. `generate_weekly_report(user_id: int)`**
- Генерирует еженедельный отчет
- Вызывается каждый понедельник

**4. `calculate_all_users_daily_stats()`**
- Запускает расчет статистики для всех активных пользователей
- Выполняется в 00:05 UTC ежедневно

### Notification Tasks (`backend/tasks/notifications.py`)

**1. `send_streak_reminder(user_id: int)`**
- Напоминание о streak
- Проверяет активность пользователя
- Retry: 5 попыток

**2. `send_daily_reminders()`**
- Отправка напоминаний всем активным пользователям
- Выполняется в 18:00 UTC
- Throttling: 2 секунды между сообщениями

**3. `send_daily_challenge_notification(user_id: int)`**
- Уведомление о прогрессе Daily Challenge
- Отправляется при 3 или 4 сообщениях

**4. `send_weekly_report_notification(user_id: int)`**
- Отправка еженедельного отчета
- Вызывается каждый понедельник

### Gamification Tasks (`backend/tasks/gamification.py`)

**1. `check_and_reset_streaks()`**
- Проверка и сброс неактивных streaks
- Выполняется в 00:05 UTC ежедневно

**2. `award_streak_milestone_bonus(user_id: int, streak_days: int)`**
- Начисление бонуса за milestone (7, 30, 100, 365 дней)

### Maintenance Tasks (`backend/tasks/maintenance.py`)

**1. `cleanup_old_data()`**
- Удаление старых данных (>1 года)
- Выполняется каждый понедельник в 02:00 UTC

**2. `refresh_materialized_views()`**
- Обновление материализованных представлений
- Выполняется каждый час
- (Будет реализовано в Phase 3)

**3. `optimize_database()`**
- ANALYZE и оптимизация PostgreSQL
- Раз в неделю

## ⏰ Scheduled Tasks (Celery Beat)

| Task | Schedule | Description |
|------|----------|-------------|
| `check_and_reset_streaks` | Daily 00:05 UTC | Проверка streaks |
| `send_daily_reminders` | Daily 18:00 UTC | Напоминания |
| `aggregate_platform_metrics` | Every 30 min | Метрики платформы |
| `cleanup_old_data` | Monday 02:00 UTC | Очистка БД |
| `refresh_materialized_views` | Hourly | Обновление views |

## 📈 Monitoring

### Flower Dashboard

Доступ: http://localhost:5555 (dev) или Railway URL (prod)

**Features:**
- Real-time task monitoring
- Worker status
- Task history and stats
- Retry/revoke tasks
- Performance metrics

**Default credentials:**
- Username: `admin`
- Password: `admin123`

### Logs

Все задачи логируются через `structlog`:

```python
from backend.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("task_completed", user_id=123, duration=1.5)
```

### Metrics

Task metrics доступны через:

```python
from backend.tasks.monitoring import get_task_metrics

metrics = get_task_metrics()
# {
#   "total_executed": 1234,
#   "total_failed": 12,
#   "total_retried": 5,
#   "by_task": {...}
# }
```

## 🔧 Configuration

### Celery App (`backend/tasks/celery_app.py`)

```python
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
)
```

### Task Queues

```python
task_routes={
    'backend.tasks.analytics.*': {'queue': 'analytics'},
    'backend.tasks.notifications.*': {'queue': 'notifications'},
    'backend.tasks.maintenance.*': {'queue': 'maintenance'},
}
```

Запуск worker для конкретной очереди:

```bash
celery -A backend.tasks.celery_app worker -Q analytics
```

## 🧪 Testing Tasks

### Manual Task Execution

```python
from backend.tasks.analytics import calculate_daily_statistics

# Синхронно (для тестов)
result = calculate_daily_statistics.apply(args=[user_id]).get()

# Асинхронно (реальное использование)
task = calculate_daily_statistics.apply_async(args=[user_id])
result = task.get(timeout=10)
```

### Testing with Pytest

```python
import pytest
from backend.tasks.analytics import calculate_daily_statistics

@pytest.mark.asyncio
async def test_daily_stats_calculation():
    """Test daily statistics calculation."""
    result = await calculate_daily_statistics.apply_async(args=[123]).get()

    assert result["user_id"] == 123
    assert "messages_count" in result
    assert result["messages_count"] >= 0
```

## 🚨 Error Handling

### Retry Mechanism

```python
@celery_app.task(bind=True, max_retries=3)
async def my_task(self, user_id: int):
    try:
        # Task logic
        pass
    except Exception as exc:
        # Exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### Failure Handling

Все ошибки логируются и отправляются в Sentry (если настроен):

```python
@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    logger.error("task_failed", task_id=task_id, exception=str(exception))
    sentry_sdk.capture_exception(exception)
```

## 📝 Best Practices

### 1. Keep Tasks Idempotent

Задачи должны быть идемпотентными (можно запускать многократно):

```python
@celery_app.task
async def update_user_stats(user_id: int):
    # ✅ Good: Overwrites, not increments
    stats = calculate_stats(user_id)
    await save_stats(user_id, stats)

    # ❌ Bad: Multiple executions = wrong result
    # await increment_counter(user_id)
```

### 2. Use Appropriate Timeouts

```python
@celery_app.task(
    time_limit=300,  # Hard limit
    soft_time_limit=240  # Warning
)
async def long_running_task():
    pass
```

### 3. Rate Limiting

```python
@celery_app.task(rate_limit='10/m')  # 10 per minute
async def api_call_task():
    pass
```

### 4. Avoid Circular Imports

```python
# ❌ Bad: Import at module level
from backend.services.gamification import GamificationService

# ✅ Good: Import inside task
@celery_app.task
async def my_task():
    from backend.services.gamification import GamificationService
    service = GamificationService()
```

## 🐛 Troubleshooting

### Worker не запускается

**Problem:** `ModuleNotFoundError: No module named 'backend'`

**Solution:**
```bash
# Убедитесь что PYTHONPATH установлен
set PYTHONPATH=%CD%  # Windows
export PYTHONPATH=$(pwd)  # Linux/Mac
```

### Задачи не выполняются

**Problem:** Tasks stuck in queue

**Solution:**
1. Проверьте что worker запущен: `celery -A backend.tasks.celery_app inspect active`
2. Проверьте Redis: `redis-cli ping`
3. Проверьте логи worker

### Flower не доступен

**Problem:** Can't access http://localhost:5555

**Solution:**
```bash
# Проверьте что Flower запущен
celery -A backend.tasks.celery_app flower --port=5555
```

### Task fails immediately

**Problem:** Task fails without retry

**Solution:**
- Проверьте что `bind=True` и `max_retries` указаны
- Убедитесь что используете `self.retry()`

## 📚 Resources

- [Celery Documentation](https://docs.celeryq.dev/)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices)
- [Flower Documentation](https://flower.readthedocs.io/)
- [Redis Documentation](https://redis.io/docs/)

## 🎯 Next Steps

После внедрения Task Queue System:

1. ✅ Phase 1: Redis Caching - Completed
2. ✅ Phase 2: Task Queue System - **Current**
3. ⏳ Phase 3: Database Optimization - Next
4. ⏳ Phase 4: Code-Level Optimizations
5. ⏳ Phase 5: Load Testing

---

**Last Updated:** December 7, 2025
**Status:** ✅ Implemented
