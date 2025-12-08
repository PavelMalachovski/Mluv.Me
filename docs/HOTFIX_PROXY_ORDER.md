# Hotfix: Proxy Route Order

**Дата**: 8 декабря 2025
**Проблема**: Web UI не работал из-за неправильного порядка роутов

## Проблема

Catch-all route `/{path:path}` был зарегистрирован **до** всех API роутов, поэтому перехватывал все запросы, включая API endpoints.

FastAPI обрабатывает роуты в порядке регистрации - первый подходящий роут выполняется.

### Было (неправильно):

```python
app.include_router(users.router)  # /api/v1/users/*
app.include_router(lesson.router)  # /api/v1/lessons/*
...

@app.api_route("/{path:path}")  # ← перехватывает ВСЕ
async def proxy_to_frontend(...):
    ...

@app.exception_handler(Exception)  # никогда не достигается
async def global_exception_handler(...):
    ...
```

## Решение

Переместили catch-all route в **самый конец**, после всех роутов и error handlers:

```python
app.include_router(users.router)
app.include_router(lesson.router)
...

@app.get("/health")
async def health_check():
    ...

@app.exception_handler(Exception)
async def global_exception_handler(...):
    ...

# MUST BE LAST!
@app.api_route("/{path:path}")
async def proxy_to_frontend(...):
    ...
```

## Результат

Теперь порядок обработки правильный:

1. `/api/v1/*` → API routers
2. `/health` → healthcheck
3. `/docs`, `/redoc` → documentation
4. `/*` → proxy to Next.js (catch-all)

## Деплой

```bash
git add .
git commit -m "fix: move catch-all proxy route to end"
git push
```

---

**Исправлено!** Теперь Web UI должен работать! 🚀
