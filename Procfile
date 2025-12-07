# Railway Procfile for Mluv.Me
# Запускает FastAPI backend, Celery worker и Celery beat

web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
worker: celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4 --max-tasks-per-child=1000
beat: celery -A backend.tasks.celery_app beat --loglevel=info
