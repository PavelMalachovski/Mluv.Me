# Celery Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis

```bash
# Windows (if not running)
# Download from: https://github.com/microsoftarchive/redis/releases
redis-server

# Linux/Mac
redis-server
```

### 3. Start Celery (3 separate terminals)

**Terminal 1 - Worker:**
```bash
# Windows
scripts\start_celery_worker.bat

# Linux/Mac
./scripts/start_celery_worker.sh
```

**Terminal 2 - Beat Scheduler:**
```bash
# Windows
scripts\start_celery_beat.bat

# Linux/Mac
./scripts/start_celery_beat.sh
```

**Terminal 3 - Flower Monitoring:**
```bash
# Windows
scripts\start_celery_flower.bat

# Linux/Mac
./scripts/start_celery_flower.sh
```

### 4. Verify

✅ **Worker**: Should show "ready" in terminal
✅ **Beat**: Should show scheduled tasks
✅ **Flower**: Open http://localhost:5555 (admin/admin123)

---

## 📝 Usage Example

### Trigger a task from Python:

```python
from backend.tasks.analytics import calculate_daily_statistics

# Fire and forget
task = calculate_daily_statistics.apply_async(args=[user_id])

# Wait for result
result = task.get(timeout=10)
print(result)
```

### Trigger from API endpoint:

```python
from fastapi import APIRouter
from backend.tasks.notifications import send_streak_reminder

router = APIRouter()

@router.post("/remind/{user_id}")
async def remind_user(user_id: int):
    task = send_streak_reminder.apply_async(args=[user_id])
    return {"task_id": task.id, "status": "scheduled"}
```

---

## 📊 Monitor Tasks

**Flower Dashboard:** http://localhost:5555

- View active tasks
- See task history
- Check worker status
- Monitor queue length
- Retry/revoke tasks

---

## 🔍 Common Commands

```bash
# Check active tasks
celery -A backend.tasks.celery_app inspect active

# Check registered tasks
celery -A backend.tasks.celery_app inspect registered

# Purge all tasks
celery -A backend.tasks.celery_app purge

# Check scheduled tasks
celery -A backend.tasks.celery_app inspect scheduled
```

---

## 📚 More Info

- Full documentation: `docs/CELERY_SETUP.md`
- Usage guide: `docs/TASK_QUEUE_USAGE.md`
- Implementation summary: `docs/PHASE2_IMPLEMENTATION_SUMMARY.md`

---

**Need help?** Check the docs or logs in the terminal where Celery is running.
