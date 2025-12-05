# 🚂 Deployment Guide - Railway.com

Пошаговая инструкция для деплоя Mluv.Me на Railway.com

---

## 📋 Предварительные требования

### 1. Аккаунты
- ✅ GitHub аккаунт (для Railway)
- ✅ Railway.com аккаунт (бесплатный)
- ✅ OpenAI API ключ
- ✅ Telegram Bot Token

### 2. Локальная подготовка
```bash
# Установить Railway CLI
npm install -g @railway/cli

# Или через Homebrew (Mac)
brew install railway
```

---

## 🚀 Шаг 1: Создание проекта на Railway

### Через Web UI

1. Зайти на https://railway.app
2. Нажать **"New Project"**
3. Выбрать **"Deploy from GitHub repo"**
4. Выбрать репозиторий `mluv-me`
5. Railway автоматически обнаружит `Dockerfile`

### Через CLI

```bash
# Войти в Railway
railway login

# Инициализировать проект
cd mluv-me
railway init

# Связать с репозиторием
railway link
```

---

## 🗄 Шаг 2: Добавление PostgreSQL

### Через Web UI

1. В проекте нажать **"New"**
2. Выбрать **"Database"**
3. Выбрать **"Add PostgreSQL"**
4. Railway создаст PostgreSQL и `DATABASE_URL`

### Через CLI

```bash
railway add --plugin postgresql
```

### Проверка DATABASE_URL

```bash
# Посмотреть переменные окружения
railway variables

# Должна быть переменная DATABASE_URL
# postgresql://user:pass@host:port/db
```

---

## 🔐 Шаг 3: Настройка переменных окружения

### Обязательные переменные

```bash
# OpenAI API Key
railway variables set OPENAI_API_KEY=sk-your-openai-api-key-here

# Telegram Bot Token
railway variables set TELEGRAM_BOT_TOKEN=7471812936:AAFoji4k74oAo347ahNaa1K1WAPtiSQ_ox8

# Environment
railway variables set ENVIRONMENT=production

# Log Level
railway variables set LOG_LEVEL=INFO
```

### Через Web UI

1. Открыть проект
2. Перейти в **"Variables"**
3. Добавить каждую переменную:
   - `OPENAI_API_KEY` = `sk-...`
   - `TELEGRAM_BOT_TOKEN` = `...`
   - `ENVIRONMENT` = `production`
   - `LOG_LEVEL` = `INFO`

### Проверка переменных

```bash
railway variables

# Должны быть:
# - DATABASE_URL (автоматически)
# - OPENAI_API_KEY
# - TELEGRAM_BOT_TOKEN
# - ENVIRONMENT
# - LOG_LEVEL
# - PORT (автоматически)
```

---

## 📦 Шаг 4: Деплой

### Автоматический деплой (через GitHub)

1. Push код в GitHub:
```bash
git add .
git commit -m "Week 1: Infrastructure and Backend ready"
git push origin main
```

2. Railway автоматически:
   - Обнаружит изменения
   - Соберет Docker контейнер
   - Запустит миграции (через Dockerfile CMD)
   - Развернет приложение

### Ручной деплой (через CLI)

```bash
# Деплой текущего кода
railway up

# Смотреть логи
railway logs
```

---

## 🗃 Шаг 5: Применение миграций

### Первый деплой

Миграции автоматически применятся из Dockerfile:

```dockerfile
CMD alembic upgrade head && \
    uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} & \
    python bot/main.py
```

### Ручное применение (если нужно)

```bash
# Подключиться к Railway
railway run alembic upgrade head

# Проверить текущую версию
railway run alembic current

# Посмотреть историю
railway run alembic history
```

---

## ✅ Шаг 6: Проверка работоспособности

### Health Check

```bash
# Получить URL проекта
railway status

# Или открыть в браузере
railway open

# Проверить health endpoint
curl https://your-app.railway.app/health

# Ответ должен быть:
{
  "status": "healthy",
  "service": "mluv-me",
  "version": "1.0.0",
  "environment": "production"
}
```

### Проверка через Web UI

1. Открыть проект на Railway
2. Перейти в **"Deployments"**
3. Последний деплой должен быть **"Success" ✅**
4. В **"Metrics"** должна быть активность

### Проверка логов

```bash
# Через CLI
railway logs

# Или в Web UI → "Logs"
# Должны быть логи:
# - application_startup
# - database connection
# - health checks
```

---

## 📊 Шаг 7: Мониторинг

### Railway Observability

1. **Metrics** (встроенные)
   - CPU usage
   - Memory usage
   - Network traffic
   - Response time

2. **Logs**
   - Structured logs (structlog)
   - Автоматический сбор stdout/stderr
   - Поиск и фильтрация

3. **Health Checks**
   - Автоматические проверки `/health`
   - Каждые 30 секунд
   - Restart при failure

### Настройка алертов

1. Перейти в **"Settings"** → **"Notifications"**
2. Добавить email или Slack
3. Настроить алерты:
   - Deployment failed
   - High CPU usage
   - High memory usage
   - Health check failed

---

## 🔄 Обновление приложения

### Автоматическое (рекомендуется)

1. Push изменения в GitHub:
```bash
git add .
git commit -m "Update: description"
git push origin main
```

2. Railway автоматически развернет новую версию

### Ручное

```bash
railway up
```

### Откат на предыдущую версию

1. Web UI → "Deployments"
2. Найти предыдущий успешный деплой
3. Нажать **"Redeploy"**

---

## 🐛 Troubleshooting

### Проблема: DATABASE_URL не установлен

**Решение:**
```bash
# Проверить что PostgreSQL добавлен
railway plugins

# Если нет - добавить
railway add --plugin postgresql

# Проверить переменные
railway variables
```

### Проблема: Миграции не применились

**Решение:**
```bash
# Применить миграции вручную
railway run alembic upgrade head

# Проверить текущую версию
railway run alembic current
```

### Проблема: Health check fails

**Проверить:**
```bash
# Логи приложения
railway logs

# Проверить PORT
railway variables | grep PORT

# Проверить что приложение слушает правильный порт
```

### Проблема: Build fails

**Проверить:**
1. `Dockerfile` корректен
2. `requirements.txt` полный
3. Логи build в Railway UI
4. Python версия (3.11+)

---

## 💰 Стоимость

### Free Tier
- $5 в месяц бесплатно
- PostgreSQL included
- 500 часов runtime
- 8GB RAM
- 100GB bandwidth

### Для <50 активных пользователей:
- Ожидаемая стоимость: **$0-2/месяц**
- Free tier достаточно для MVP

### Starter Plan ($5/месяц)
- Unlimited hours
- Priority support
- Для >50 пользователей

---

## 📈 Масштабирование

### Вертикальное (больше ресурсов)

1. Web UI → "Settings"
2. Изменить:
   - Memory limit
   - CPU allocation
3. Restart deployment

### Горизонтальное (больше инстансов)

Railway Pro Plan:
- Multiple replicas
- Load balancing
- Auto-scaling

---

## 🔒 Безопасность

### Best Practices

✅ **Секреты**
- Все ключи в Environment Variables
- Никогда не коммитить .env
- Регулярная ротация ключей

✅ **Database**
- PostgreSQL автоматически защищен
- SSL connection
- Backups enabled

✅ **API**
- CORS настроен
- Rate limiting (добавить в Week 2)
- Input validation (Pydantic)

---

## 📝 Чеклист деплоя

### Перед деплоем
- [ ] Все тесты проходят (`pytest`)
- [ ] Код без ошибок
- [ ] README.md обновлен
- [ ] `.gitignore` настроен
- [ ] `env.example` актуален

### Деплой
- [ ] Проект создан на Railway
- [ ] PostgreSQL добавлен
- [ ] Environment variables установлены
- [ ] Код задеплоен
- [ ] Миграции применены

### После деплоя
- [ ] Health check работает
- [ ] Логи чистые (нет ошибок)
- [ ] База данных работает
- [ ] API endpoints отвечают
- [ ] Мониторинг настроен

---

## 🎉 Готово!

После выполнения всех шагов:
- ✅ Backend работает на Railway
- ✅ PostgreSQL настроен
- ✅ Health checks активны
- ✅ Логирование работает
- ✅ Готово к Week 2 development

**URL проекта:** `https://your-app.railway.app`

**API Docs:** `https://your-app.railway.app/docs` (только в dev)

---

## 📞 Поддержка

### Railway Documentation
- https://docs.railway.app

### Railway Discord
- https://discord.gg/railway

### Mluv.Me Issues
- GitHub Issues в репозитории

---

**Na zdraví! 🍺 Deployment успешен!**

*Обновлено: 05.12.2025*

