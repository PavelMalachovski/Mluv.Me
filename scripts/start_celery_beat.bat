@echo off
REM Start Celery Beat scheduler for Mluv.Me (Windows)

echo Starting Celery Beat Scheduler...

REM Переходим в корневую директорию проекта
cd /d "%~dp0\.."

REM Устанавливаем PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Удаляем старый schedule файл
if exist celerybeat-schedule.db del celerybeat-schedule.db

REM Запускаем beat scheduler
celery -A backend.tasks.celery_app beat ^
    --loglevel=info ^
    --scheduler celery.beat:PersistentScheduler

echo Celery Beat stopped
pause
