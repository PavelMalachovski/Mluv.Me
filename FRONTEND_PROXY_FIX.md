# Frontend Proxy Fix

**Дата**: 8 декабря 2025
**Статус**: ✅ ГОТОВО К ДЕПЛОЮ

## Проблема

Frontend (Next.js) запускается на порту 3000, но Railway проксирует только порт 8000 (backend).
Пользователи не могут получить доступ к Web UI.

## Решение

Добавлен reverse proxy в FastAPI backend, который проксирует все non-API запросы на Next.js.

### Как это работает

```
User Request → Railway (port 8000) → FastAPI Backend
                                           ↓
                                    /api/* → Backend API
                                    /* → Next.js Frontend (port 3000)
```

### Изменения

#### 1. `backend/main.py`

Добавлен catch-all route:

```python
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_to_frontend(request: Request, path: str):
    """
    Proxy all non-API requests to Next.js frontend.
    """
    # Skip API routes
    if path.startswith("api/") or path == "health" or path.startswith("docs"):
        return 404

    # Proxy to Next.js on localhost:3000
    frontend_url = f"http://localhost:{settings.frontend_port}/{path}"

    # Forward request and return response
    async with httpx.AsyncClient() as client:
        response = await client.request(...)
        return StreamingResponse(...)
```

#### 2. `backend/config.py`

Добавлена настройка:

```python
frontend_port: int = Field(
    default=3000,
    description="Port for Next.js frontend"
)
```

### Что проксируется

✅ **Проксируется на Next.js (port 3000)**:
- `/` - главная страница
- `/login` - авторизация
- `/dashboard/*` - дашборд
- `/_next/*` - Next.js assets (JS, CSS)
- `/favicon.ico`, `/robots.txt`, etc.

❌ **Остается в Backend (port 8000)**:
- `/api/*` - все API endpoints
- `/health` - healthcheck
- `/docs` - Swagger docs
- `/redoc` - ReDoc docs

### Fallback

Если Next.js еще не запустился, показывается красивая страница загрузки с автообновлением.

## Деплой

```bash
git add .
git commit -m "fix: add reverse proxy for frontend"
git push
```

Railway автоматически задеплоит.

## Проверка

После деплоя проверьте:

1. **Root URL**: `https://your-app.railway.app` → должен показать Next.js
2. **API**: `https://your-app.railway.app/api/health` → должен показать API response
3. **Docs**: `https://your-app.railway.app/docs` → Swagger UI

## Логи

Правильные логи:

```
Starting backend server...
INFO: Uvicorn running on http://0.0.0.0:8000

Starting frontend (Next.js)...
▲ Next.js 14.2.33
- Network: http://0.0.0.0:3000
✓ Ready in 492ms

All services started.
```

Proxy работает:

```
INFO: 127.0.0.1:xxxx - "GET / HTTP/1.1" 200 OK
INFO: frontend_proxy: GET / → http://localhost:3000/
```

## Технические детали

### Почему не nginx?

Railway предоставляет только один порт наружу. Варианты:
1. ❌ Запустить nginx в контейнере - сложно, избыточно
2. ✅ Прокси в FastAPI - просто, работает из коробки
3. ❌ Два отдельных сервиса - дороже, сложнее

### Performance

- httpx async client - без блокировки
- StreamingResponse для binary content
- Follow redirects автоматически

### Ограничения

- WebSocket proxy не реализован (пока не нужен)
- Upload файлов через прокси может быть медленнее

## Альтернативные решения

Если нужна большая производительность:

### Вариант 1: Separate Services

Запустить 2 сервиса в Railway:
- `backend` - FastAPI (api.mluv.me)
- `frontend` - Next.js (mluv.me)

### Вариант 2: Static Export

Next.js static export → serve через FastAPI StaticFiles:

```python
app.mount("/", StaticFiles(directory="frontend/out", html=True))
```

Но теряем SSR и API routes.

---

**Готово к деплою!** 🚀

**Result**: Теперь один URL Railway → Backend + Frontend через proxy.
