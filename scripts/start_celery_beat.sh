#!/bin/bash
# Start Celery Beat scheduler for Mluv.Me

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Celery Beat Scheduler...${NC}"

# Переходим в корневую директорию проекта
cd "$(dirname "$0")/.."

# Устанавливаем переменные окружения
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Удаляем старый schedule файл при необходимости
rm -f celerybeat-schedule.db

# Запускаем beat scheduler
celery -A backend.tasks.celery_app beat \
    --loglevel=info \
    --scheduler celery.beat:PersistentScheduler

echo -e "${YELLOW}Celery Beat stopped${NC}"
