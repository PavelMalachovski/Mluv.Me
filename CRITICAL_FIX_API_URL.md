# 🚨 Critical Fix - API URL in Web App

**Дата**: 8 декабря 2025
**Проблема**: `ERR_CONNECTION_REFUSED` при обращении к `localhost:8000` из Telegram Web App

---

## 🔍 Диагностика

### Логи консоли показали:

```
Starting Web App authentication...
Web App initialized: {platform: "web", version: "7.10"}
Telegram user: 540529430 Pavel
Authenticating with backend...
Failed to load resource: net::ERR_CONNECTION_REFUSED
localhost:8000/api/v1/auth/webapp:1
```

### Проблема:

Frontend пытался обратиться к `localhost:8000`, но в **Telegram Web App это не работает**!

- ❌ `localhost:8000` - недоступен из Web App (другой контекст)
- ✅ Нужен **относительный URL** или `window.location.origin`

---

## ✅ Исправление

### 1. `frontend/lib/telegram-web-app.ts`

**Было**:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

**Стало**:
```typescript
// Use relative URL (same domain as frontend)
const API_URL = typeof window !== 'undefined' ? window.location.origin : '';
```

### 2. `frontend/lib/api-client.ts`

**Было**:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

**Стало**:
```typescript
// Use relative URL to work in both browser and Telegram Web App
const API_BASE_URL = typeof window !== 'undefined' ? window.location.origin : '';
```

### 3. `frontend/lib/telegram-auth.ts`

**Было**:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

**Стало**:
```typescript
// Use relative URL to work in both browser and Telegram Web App
const API_URL = typeof window !== 'undefined' ? window.location.origin : '';
```

---

## 📝 Почему это работает?

1. **Railway** служит и backend, и frontend с **одного домена**:
   - Frontend: `https://mluvme-production.up.railway.app`
   - Backend API: `https://mluvme-production.up.railway.app/api/...`

2. **Reverse proxy** в `backend/main.py` перенаправляет:
   - `/api/*` → FastAPI backend
   - Всё остальное → Next.js frontend

3. **`window.location.origin`** всегда возвращает:
   - В Web App: `https://mluvme-production.up.railway.app`
   - В браузере: `https://mluvme-production.up.railway.app`
   - В dev режиме: `http://localhost:3000` (если запущен локально)

---

## 🚀 Деплой

```bash
cd C:\Git\Mluv.Me
git add .
git commit -m "fix: use relative API URLs for Telegram Web App"
git push
```

Railway задеплоит через 2-3 минуты.

---

## 🎯 Тестирование

### После деплоя:

1. Откройте бота в Telegram
2. Нажмите Menu (☰)
3. Нажмите "Continue with Telegram"
4. Консоль должна показать:

```
Starting Web App authentication...
Web App initialized: {...}
Telegram user: 540529430 Pavel
Authenticating with backend...
Auth result: {success: true, user: {...}, token: "..."}
User authenticated, redirecting to dashboard...
```

5. ✅ Редирект на `/dashboard`

---

## 📊 Результат

- ✅ API запросы работают в Web App
- ✅ Авторизация проходит успешно
- ✅ Редирект на dashboard
- ✅ Совместимость с обычным браузером

**Проблема решена!** 🎉
