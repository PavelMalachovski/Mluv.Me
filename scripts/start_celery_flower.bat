@echo off
REM Start Celery Flower monitoring dashboard for Mluv.Me (Windows)

echo Starting Celery Flower...
echo Dashboard will be available at: http://localhost:5555

REM Переходим в корневую директорию проекта
cd /d "%~dp0\.."

REM Устанавливаем PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Устанавливаем дефолтные учетные данные если не заданы
if not defined FLOWER_USER set FLOWER_USER=admin
if not defined FLOWER_PASSWORD set FLOWER_PASSWORD=admin123

REM Запускаем Flower
celery -A backend.tasks.celery_app flower ^
    --port=5555 ^
    --basic_auth=%FLOWER_USER%:%FLOWER_PASSWORD% ^
    --persistent=True ^
    --db=flower.db

echo Celery Flower stopped
pause
