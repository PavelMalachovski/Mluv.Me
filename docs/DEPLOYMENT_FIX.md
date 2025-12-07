# 🔧 Исправление проблем с деплоем

**Дата**: December 7, 2025

---

## ✅ Проблема 1: ImportError - ИСПРАВЛЕНО

### Ошибка:
```
ImportError: cannot import name 'settings' from 'backend.config'
```

### Решение:
Обновлён файл `backend/routers/web_auth.py`:
- ✅ Изменён импорт: `from backend.config import get_settings`
- ✅ Добавлен вызов `settings = get_settings()` в функции

**Статус**: ✅ ИСПРАВЛЕНО

---

## ⚠️ Проблема 2: Telegram Conflict

### Ошибка:
```
TelegramConflictError: Conflict: terminated by other getUpdates request;
make sure that only one bot instance is running
```

### Причина:
У вас запущено **ДВА экземпляра бота одновременно**:
- 🤖 Локальная разработка (`python bot/main.py`)
- 🚂 Railway production

### Решение:

#### Вариант 1: Остановить локальный бот (рекомендуется)
```bash
# Найти процесс
ps aux | grep "bot/main.py"

# Остановить
kill <PID>

# Или в Windows Task Manager найти python процесс
```

#### Вариант 2: Использовать разные боты для dev/prod

**Для локальной разработки:**
1. Создайте тестовый бот через @BotFather
2. В локальном `.env` файле:
   ```env
   TELEGRAM_BOT_TOKEN=<токен_тестового_бота>
   ```

**Для production (Railway):**
- Используйте основной бот: `7471812936:AAFoji4k74oAo347ahNaa1K1WAPtiSQ_ox8`

---

## 🚀 Правильный деплой на Railway

### Шаг 1: Закоммитить изменения

```bash
cd c:\Git\Mluv.Me

# Проверить изменения
git status

# Добавить изменения
git add backend/routers/web_auth.py
git add backend/routers/web_lessons.py
git add backend/main.py
git add frontend/

# Закоммитить
git commit -m "feat: add web UI implementation - Phase 1 complete

- Add web authentication endpoints
- Add web lessons endpoints
- Add Next.js frontend with dashboard and practice pages
- Fix settings import in web_auth router
"

# Запушить на Railway
git push origin master
```

### Шаг 2: Railway автоматически задеплоит

Railway увидит новый коммит и:
1. ✅ Запустит миграции
2. ✅ Перезапустит backend с новыми роутерами
3. ✅ Запустит bot

### Шаг 3: Проверить деплой

```bash
# Проверить логи Railway
railway logs

# Или в Railway Dashboard → Deployments → View Logs
```

### Шаг 4: Получить Railway URL

```bash
# В Railway Dashboard найти:
# Settings → Networking → Public Domain

# Формат URL:
https://mluv-me-production-XXXX.up.railway.app
```

---

## 🌐 Деплой Frontend на Vercel

После того как backend задеплоен на Railway:

### Шаг 1: Получить Railway URL

Из Railway Dashboard скопировать Public URL вашего backend.

### Шаг 2: Создать .env.local для тестирования

```bash
cd frontend

# Создать файл
echo "NEXT_PUBLIC_API_URL=https://ваш-railway-url.up.railway.app" > .env.local
echo "NEXT_PUBLIC_TELEGRAM_BOT_ID=7471812936" >> .env.local

# Проверить работу локально
npm run dev
```

### Шаг 3: Деплой на Vercel

**Option A: Vercel Dashboard**
1. Зайти на https://vercel.com
2. New Project → Import Git Repository
3. Выбрать Mluv.Me репозиторий
4. Root Directory: `frontend`
5. Environment Variables:
   ```
   NEXT_PUBLIC_API_URL = https://ваш-railway-url.up.railway.app
   NEXT_PUBLIC_TELEGRAM_BOT_ID = 7471812936
   ```
6. Deploy

**Option B: Vercel CLI**
```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

### Шаг 4: Обновить CORS в backend

В `backend/main.py` добавить Vercel URL в CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ваш-проект.vercel.app",
        "https://*.vercel.app",  # Для preview deployments
        "http://localhost:3000",  # Для локальной разработки
        "*"  # ИЛИ оставить "*" для упрощения (не рекомендуется для production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Закоммитить и запушить изменения.

---

## ✅ Проверка после деплоя

### Backend (Railway)

1. **Health Check**
   ```bash
   curl https://ваш-railway-url.up.railway.app/health
   ```
   Должен вернуть:
   ```json
   {
     "status": "healthy",
     "service": "mluv-me",
     "version": "1.0.0"
   }
   ```

2. **Swagger Docs**
   ```
   https://ваш-railway-url.up.railway.app/docs
   ```
   Должны увидеть новые endpoints:
   - `/api/v1/web/auth/telegram`
   - `/api/v1/web/lessons/text`

3. **Telegram Bot**
   - Написать боту в Telegram
   - Должен отвечать

### Frontend (Vercel)

1. **Открыть URL**
   ```
   https://ваш-проект.vercel.app
   ```

2. **Тест логина**
   - Кликнуть "Login with Telegram"
   - Авторизоваться
   - Должен редиректить на `/dashboard`

3. **Тест практики**
   - Кликнуть "Start Practicing"
   - Написать что-то на чешском
   - Должен прийти ответ от Honzík

---

## 🐛 Troubleshooting

### Если backend не стартует:

```bash
# Проверить логи Railway
railway logs --tail 100

# Типичные проблемы:
# 1. Миграции не применились → railway run alembic upgrade head
# 2. Переменные окружения не установлены → проверить Railway Variables
# 3. Синтаксические ошибки → проверить логи
```

### Если frontend не работает:

```bash
# Проверить логи Vercel
vercel logs

# Типичные проблемы:
# 1. CORS ошибка → обновить backend CORS
# 2. API URL неправильный → проверить env variables в Vercel
# 3. Build failed → проверить package.json dependencies
```

### Если Telegram Bot конфликтует:

```bash
# Остановить ВСЕ локальные боты
pkill -f "bot/main.py"

# В Windows:
# Task Manager → найти python → End Task

# Подождать 1 минуту, Railway бот перезапустится
```

---

## 📊 Текущий статус

### ✅ Готово:
- [x] Web authentication endpoints
- [x] Web lessons endpoints
- [x] Next.js frontend полностью
- [x] Dashboard с графиками
- [x] Practice интерфейс
- [x] Исправлен ImportError

### 🔄 В процессе:
- [ ] Деплой на Railway (ждём пуш коммита)
- [ ] Деплой на Vercel (после Railway)

### 📝 Следующие шаги:
1. Закоммитить изменения
2. Запушить на Railway
3. Получить Railway URL
4. Задеплоить frontend на Vercel
5. Протестировать всё вместе

---

**Готово к деплою! 🚀**
