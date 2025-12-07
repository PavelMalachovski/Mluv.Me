# Task Queue Usage Guide

## 🎯 Когда использовать Task Queue

Используйте Celery задачи для:

### ✅ Хорошие кандидаты

1. **Тяжелые вычисления** (>1 секунды)
   - Расчет статистики
   - Агрегация данных
   - Генерация отчетов

2. **Внешние API вызовы**
   - Отправка уведомлений (Telegram)
   - Email рассылки
   - Webhook'и

3. **Фоновая обработка**
   - Очистка БД
   - Обновление кешей
   - Бэкапы

4. **Периодические задачи**
   - Daily reminders
   - Streak checks
   - Метрики

### ❌ Плохие кандидаты

1. **Быстрые операции** (<100ms)
   - Простые SELECT запросы
   - Кеш lookup
   - Валидация

2. **Критичные для UX**
   - Авторизация
   - Первичная загрузка данных
   - Real-time updates

3. **Требуют немедленного ответа**
   - API endpoints с синхронным ответом
   - WebSocket сообщения

## 🚀 Quick Start

### 1. Создание простой задачи

```python
# backend/tasks/my_tasks.py

from backend.tasks.celery_app import celery_app
from backend.utils.logger import get_logger

logger = get_logger(__name__)

@celery_app.task
def simple_task(user_id: int) -> dict:
    """Простая синхронная задача."""
    logger.info("processing_user", user_id=user_id)

    # Your logic here
    result = {"user_id": user_id, "status": "processed"}

    return result
```

### 2. Создание async задачи

```python
from celery import Task

class AsyncTask(Task):
    """Base task class with async support."""

    def __call__(self, *args, **kwargs):
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self.run_async(*args, **kwargs)
        )

    async def run_async(self, *args, **kwargs):
        raise NotImplementedError


@celery_app.task(bind=True, base=AsyncTask)
async def async_task(self, user_id: int) -> dict:
    """Async задача с доступом к БД."""
    from backend.db.database import AsyncSessionLocal
    from backend.db.repositories import UserRepository

    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)

        return {"user_id": user_id, "username": user.username}
```

### 3. Вызов задачи из кода

```python
# backend/routers/users.py

from fastapi import APIRouter
from backend.tasks.my_tasks import simple_task, async_task

router = APIRouter()

@router.post("/process-user/{user_id}")
async def process_user(user_id: int):
    """
    Endpoint для запуска обработки пользователя в фоне.
    """
    # Запускаем задачу асинхронно
    task = simple_task.apply_async(args=[user_id])

    # Возвращаем task_id для отслеживания
    return {
        "message": "Processing started",
        "task_id": task.id,
        "status_url": f"/tasks/{task.id}"
    }


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Проверка статуса задачи.
    """
    from celery.result import AsyncResult

    task = AsyncResult(task_id)

    if task.ready():
        return {
            "status": "completed",
            "result": task.result
        }
    else:
        return {
            "status": "pending" if task.state == "PENDING" else task.state,
            "progress": task.info if task.info else {}
        }
```

## 🔄 Retry & Error Handling

### Автоматический retry

```python
@celery_app.task(
    bind=True,
    max_retries=3,  # Максимум 3 попытки
    default_retry_delay=60  # 60 секунд между попытками
)
async def task_with_retry(self, user_id: int):
    try:
        # Risky operation
        result = await some_external_api_call(user_id)
        return result
    except Exception as exc:
        # Retry с экспоненциальной задержкой
        raise self.retry(
            exc=exc,
            countdown=60 * (2 ** self.request.retries)
        )
```

### Custom error handling

```python
@celery_app.task(bind=True, max_retries=5)
async def task_with_custom_handling(self, user_id: int):
    try:
        result = await process_something(user_id)
        return result
    except TemporaryError as exc:
        # Повторяем для временных ошибок
        raise self.retry(exc=exc, countdown=300)
    except PermanentError as exc:
        # Не повторяем для постоянных ошибок
        logger.error("permanent_error", user_id=user_id, error=str(exc))
        return {"error": str(exc), "user_id": user_id}
```

## ⏱️ Scheduling Tasks

### Delayed execution

```python
# Запустить через 5 минут
task.apply_async(args=[user_id], countdown=300)

# Запустить в конкретное время
from datetime import datetime, timedelta

eta = datetime.now() + timedelta(hours=1)
task.apply_async(args=[user_id], eta=eta)
```

### Периодические задачи (Celery Beat)

Добавьте в `backend/tasks/celery_app.py`:

```python
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'my-periodic-task': {
        'task': 'backend.tasks.my_tasks.my_periodic_task',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9:00
    },
}
```

**Примеры schedule:**

```python
# Каждые 30 минут
'schedule': crontab(minute='*/30')

# Каждый понедельник в 8:00
'schedule': crontab(day_of_week=1, hour=8, minute=0)

# Каждый день в полночь
'schedule': crontab(hour=0, minute=0)

# Каждые 10 секунд (для тестирования)
'schedule': 10.0
```

## 📊 Task Priority & Routing

### Priority

```python
# High priority task
task.apply_async(args=[user_id], priority=9)

# Low priority task
task.apply_async(args=[user_id], priority=0)
```

### Routing to specific queues

```python
# Отправить в конкретную очередь
task.apply_async(args=[user_id], queue='high_priority')

# В celery_app.py настройте routes:
celery_app.conf.task_routes = {
    'backend.tasks.notifications.*': {
        'queue': 'notifications',
        'priority': 8
    },
    'backend.tasks.analytics.*': {
        'queue': 'analytics',
        'priority': 5
    }
}
```

## 🎭 Patterns

### Pattern 1: Fire and Forget

Для задач где результат не нужен:

```python
@router.post("/send-notification/{user_id}")
async def send_notification(user_id: int):
    # Запускаем и забываем
    send_notification_task.apply_async(args=[user_id])

    return {"message": "Notification scheduled"}
```

### Pattern 2: Wait for Result

Для задач где нужен результат:

```python
@router.post("/calculate-stats/{user_id}")
async def calculate_stats(user_id: int):
    # Запускаем и ждем
    task = calculate_stats_task.apply_async(args=[user_id])

    try:
        result = task.get(timeout=30)  # Ждем максимум 30 секунд
        return result
    except TimeoutError:
        return {"status": "processing", "task_id": task.id}
```

### Pattern 3: Chain Tasks

Для последовательного выполнения:

```python
from celery import chain

# task1 -> task2 -> task3
workflow = chain(
    task1.s(user_id),
    task2.s(),  # Получает результат task1
    task3.s()   # Получает результат task2
)

workflow.apply_async()
```

### Pattern 4: Group Tasks

Для параллельного выполнения:

```python
from celery import group

# Обработать несколько пользователей параллельно
job = group(
    process_user_task.s(user_id)
    for user_id in user_ids
)

result = job.apply_async()
result.get()  # Ждем завершения всех задач
```

### Pattern 5: Chord (Group + Callback)

Параллельная обработка с финальным callback:

```python
from celery import chord

# Обработать всех пользователей, затем агрегировать
callback = aggregate_results.s()

workflow = chord(
    process_user_task.s(user_id)
    for user_id in user_ids
)(callback)

workflow.get()
```

## 🧪 Testing

### Unit testing tasks

```python
import pytest
from backend.tasks.my_tasks import simple_task

def test_simple_task():
    """Test task logic without Celery."""
    # Вызываем функцию напрямую
    result = simple_task(user_id=123)

    assert result["user_id"] == 123
    assert result["status"] == "processed"
```

### Integration testing with Celery

```python
import pytest
from celery.contrib.testing.worker import start_worker

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://'
    }

@pytest.fixture(scope='session')
def celery_worker(celery_app):
    with start_worker(celery_app, perform_ping_check=False):
        yield

def test_task_execution(celery_worker):
    """Test task with Celery worker."""
    result = simple_task.apply_async(args=[123])
    assert result.get(timeout=10)["user_id"] == 123
```

## 📝 Best Practices

### 1. Задачи должны быть идемпотентными

```python
# ✅ Good: Can run multiple times safely
@celery_app.task
async def update_stats(user_id: int):
    stats = await calculate_stats(user_id)
    await save_stats(user_id, stats)  # Overwrites

# ❌ Bad: Multiple runs = wrong result
@celery_app.task
async def bad_update_stats(user_id: int):
    await increment_counter(user_id)  # Increments each time
```

### 2. Используйте логирование

```python
from backend.utils.logger import get_logger

logger = get_logger(__name__)

@celery_app.task
async def my_task(user_id: int):
    logger.info("task_started", user_id=user_id)

    try:
        result = await process(user_id)
        logger.info("task_completed", user_id=user_id, result=result)
        return result
    except Exception as e:
        logger.error("task_failed", user_id=user_id, error=str(e))
        raise
```

### 3. Избегайте circular imports

```python
# ❌ Bad: Import at top
from backend.services.gamification import GamificationService

@celery_app.task
async def my_task():
    service = GamificationService()

# ✅ Good: Import inside function
@celery_app.task
async def my_task():
    from backend.services.gamification import GamificationService
    service = GamificationService()
```

### 4. Timeouts

```python
@celery_app.task(
    time_limit=300,  # Hard limit: kill after 5 min
    soft_time_limit=240  # Soft limit: raise exception after 4 min
)
async def long_task():
    try:
        # Long operation
        pass
    except SoftTimeLimitExceeded:
        # Cleanup before hard kill
        logger.warning("task_timeout_approaching")
        raise
```

### 5. Rate limiting

```python
@celery_app.task(rate_limit='10/m')  # Max 10 per minute
async def api_call_task():
    # Calls external API
    pass
```

## 🔍 Debugging

### Enable verbose logging

```bash
celery -A backend.tasks.celery_app worker --loglevel=debug
```

### Inspect active tasks

```bash
celery -A backend.tasks.celery_app inspect active
```

### Check registered tasks

```bash
celery -A backend.tasks.celery_app inspect registered
```

### Purge all tasks

```bash
celery -A backend.tasks.celery_app purge
```

---

**Last Updated:** December 7, 2025
