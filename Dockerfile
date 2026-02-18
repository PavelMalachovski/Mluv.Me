# ==========================================
# Stage 1: Build Frontend (Next.js)
# ==========================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files (including package-lock.json)
COPY frontend/package*.json ./

# Install dependencies (npm ci is faster and more reliable for CI/CD)
RUN npm ci || npm install --legacy-peer-deps

# Copy frontend source
COPY frontend/ ./

# Build Next.js app
RUN npm run build

# ==========================================
# Stage 2: Python Backend + Bot
# ==========================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js for Next.js
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application code
COPY backend/ ./backend/
COPY bot/ ./bot/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/node_modules ./frontend/node_modules
COPY --from=frontend-builder /app/frontend/package.json ./frontend/package.json
COPY --from=frontend-builder /app/frontend/next.config.js ./frontend/next.config.js
COPY --from=frontend-builder /app/frontend/public ./frontend/public

# Expose port (Railway will set PORT env var)
EXPOSE ${PORT:-8000}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/health')" || exit 1

# Create startup script that runs all services
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Function to handle graceful shutdown\n\
cleanup() {\n\
    echo "Shutting down services..."\n\
    kill $BACKEND_PID $BOT_PID $FRONTEND_PID $WORKER_PID $BEAT_PID 2>/dev/null\n\
    wait $BACKEND_PID $BOT_PID $FRONTEND_PID $WORKER_PID $BEAT_PID 2>/dev/null\n\
    exit 0\n\
}\n\
\n\
trap cleanup SIGTERM SIGINT\n\
\n\
echo "Running database migrations..."\n\
alembic upgrade head\n\
\n\
echo "Starting backend server..."\n\
uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} &\n\
BACKEND_PID=$!\n\
\n\
echo "Starting frontend (Next.js)..."\n\
cd /app/frontend && npm start -- --port ${FRONTEND_PORT:-3000} --hostname 0.0.0.0 &\n\
FRONTEND_PID=$!\n\
cd /app\n\
\n\
# Wait a bit for backend to be ready\n\
sleep 5\n\
\n\
echo "Starting Telegram bot..."\n\
python -m bot.main &\n\
BOT_PID=$!\n\
\n\
echo "Starting Celery worker..."\n\
celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=2 --max-tasks-per-child=1000 &\n\
WORKER_PID=$!\n\
\n\
echo "Starting Celery beat (scheduler)..."\n\
celery -A backend.tasks.celery_app beat --loglevel=info &\n\
BEAT_PID=$!\n\
\n\
echo "All services started."\n\
echo "Backend PID: $BACKEND_PID"\n\
echo "Frontend PID: $FRONTEND_PID"\n\
echo "Bot PID: $BOT_PID"\n\
echo "Celery Worker PID: $WORKER_PID"\n\
echo "Celery Beat PID: $BEAT_PID"\n\
\n\
# Wait for all processes\n\
wait $BACKEND_PID $BOT_PID $FRONTEND_PID $WORKER_PID $BEAT_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run startup script
CMD ["/bin/bash", "/app/start.sh"]

