#!/bin/bash
# Start Celery Flower monitoring dashboard for Mluv.Me

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Celery Flower...${NC}"
echo -e "${BLUE}Dashboard will be available at: http://localhost:5555${NC}"

# Переходим в корневую директорию проекта
cd "$(dirname "$0")/.."

# Устанавливаем переменные окружения
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Запускаем Flower
celery -A backend.tasks.celery_app flower \
    --port=5555 \
    --basic_auth="${FLOWER_USER:-admin}:${FLOWER_PASSWORD:-admin123}" \
    --persistent=True \
    --db=flower.db

echo -e "${BLUE}Celery Flower stopped${NC}"
