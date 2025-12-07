@echo off
REM Start Celery worker for Mluv.Me (Windows)

echo Starting Celery Worker...

REM Переходим в корневую директорию проекта
cd /d "%~dp0\.."

REM Устанавливаем PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Запускаем worker
celery -A backend.tasks.celery_app worker ^
    --loglevel=info ^
    --concurrency=4 ^
    --max-tasks-per-child=1000 ^
    --pool=solo ^
    --task-events

echo Celery Worker stopped
pause
