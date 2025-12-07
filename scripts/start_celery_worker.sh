#!/bin/bash
# Start Celery worker for Mluv.Me

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Celery Worker...${NC}"

# Переходим в корневую директорию проекта
cd "$(dirname "$0")/.."

# Устанавливаем переменные окружения
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Запускаем worker
celery -A backend.tasks.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --task-events \
    --without-gossip \
    --without-mingle \
    --without-heartbeat

echo -e "${YELLOW}Celery Worker stopped${NC}"
