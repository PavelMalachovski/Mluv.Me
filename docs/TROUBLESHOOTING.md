# Troubleshooting Guide - Mluv.Me

Руководство по решению проблем при деплое на Railway.com

## Основные проблемы и решения

### 1. Telegram Bot Conflict Error

**Проблема:**
```
TelegramConflictError: Conflict: terminated by other getUpdates request;
make sure that only one bot instance is running
```

**Причины:**
- Несколько экземпляров бота работают одновременно
- Railway auto-scaled и создал дубликаты
- Бот запущен локально И на Railway одновременно
- Предыдущий деплой еще не остановился

**Решение:**

1. **Остановите все локальные инстансы бота:**
   ```bash
   # Проверьте запущенные процессы
   ps aux | grep python

   # Остановите процессы с ботом
   pkill -f "bot.main"
   ```

2. **Настройте Railway на один инстанс:**
   - В `railway.json` добавлено `"numReplicas": 1`
   - Проверьте настройки в Railway Dashboard → Service → Settings → Scaling
   - Установите: **Min instances: 1, Max instances: 1**

3. **Перезапустите deployment:**
   - Railway Dashboard → Deployments → Restart

4. **Используйте webhook вместо polling (опционально):**
   - Для production рекомендуется webhook
   - См. раздел "Настройка Webhook" ниже

### 2. 500 Internal Server Error на /api/v1/lessons/process

**Проблема:**
```
POST /api/v1/lessons/process HTTP/1.1" 500 Internal Server Error
```

**Возможные причины:**

#### A. Отсутствует OPENAI_API_KEY
```bash
# Проверьте переменные окружения в Railway
railway variables
```

**Решение:**
```bash
# Добавьте ключ
railway variables set OPENAI_API_KEY=sk-...
```

#### B. Ошибка подключения к базе данных
**Решение:**
1. Проверьте PostgreSQL Plugin в Railway
2. Убедитесь что DATABASE_URL установлен автоматически
3. Проверьте логи миграций:
   ```
   INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
   INFO  [alembic.runtime.migration] Will assume transactional DDL.
   ```

#### C. Timeout OpenAI API
**Симптомы:** Долгий ответ, затем 500 ошибка

**Решение:**
- OpenAI клиент уже имеет retry механизм (3 попытки)
- Проверьте лимиты API на platform.openai.com
- Увеличьте timeout в Railway: Settings → Healthcheck Timeout → 200s

#### D. Ошибка парсинга JSON от GPT
**Симптомы:** В логах `json_decode_error`

**Решение:**
- Код уже обрабатывает эту ошибку
- GPT должен вернуть валидный JSON (используется json_mode=True)
- Если проблема повторяется, проверьте промпт в `honzik_personality.py`

### 3. Миграции не применяются

**Проблема:**
```
sqlalchemy.exc.ProgrammingError: relation "users" does not exist
```

**Решение:**

1. **Проверьте что миграции запускаются в Dockerfile:**
   ```bash
   alembic upgrade head
   ```

2. **Запустите миграции вручную через Railway CLI:**
   ```bash
   railway run alembic upgrade head
   ```

3. **Пересоздайте базу данных:**
   - Railway Dashboard → PostgreSQL → Data → Delete All
   - Перезапустите deployment

### 4. Health Check Failed

**Проблема:**
```
Health check failed: GET /health returned 503
```

**Решение:**

1. **Проверьте что backend запущен:**
   - Логи должны содержать: `INFO: Uvicorn running on http://0.0.0.0:8000`

2. **Увеличьте timeout:**
   - Railway Settings → Healthcheck Timeout → 100s (уже установлено)

3. **Проверьте порт:**
   - Railway автоматически устанавливает `$PORT`
   - Backend должен использовать `${PORT:-8000}`

### 5. Bot не отвечает на сообщения

**Симптомы:**
- Bot онлайн
- Сообщения не обрабатываются
- Нет ошибок в логах

**Решение:**

1. **Проверьте что bot запущен:**
   ```
   INFO:     Starting bot...
   ```

2. **Проверьте webhook:**
   - Если установлен webhook, удалите его:
   ```python
   await bot.delete_webhook(drop_pending_updates=True)
   ```

3. **Проверьте backend URL:**
   - В bot/config.py должен быть правильный URL
   - Формат: `https://your-app.railway.app`

### 6. OpenAI API Rate Limit

**Проблема:**
```
RateLimitError: You exceeded your current quota
```

**Решение:**

1. **Проверьте баланс на OpenAI:**
   - https://platform.openai.com/usage

2. **Увеличьте лимиты:**
   - https://platform.openai.com/account/billing

3. **Код уже реализует exponential backoff:**
   - 3 попытки с задержкой 1s, 2s, 4s

### 7. Slow Response Time

**Проблема:**
- Обработка голосовых занимает > 30 секунд

**Объяснение:**
Pipeline включает 3 API вызова:
1. STT (Whisper) ~ 3-5 секунд
2. GPT-4o ~ 5-10 секунд
3. TTS ~ 3-5 секунд

**Итого:** 11-20 секунд - нормально

**Оптимизация (если нужно):**
- Используйте `gpt-4o-mini` (быстрее, но менее умный)
- Используйте `tts-1-hd` вместо `tts-1` (качественнее, но медленнее)

## Проверка логов

### Railway Dashboard
```
Deployments → View Logs
```

### Railway CLI
```bash
# Все логи
railway logs

# Только backend
railway logs --service backend

# Follow mode
railway logs -f
```

### Что искать в логах:

**Успешный запуск:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
Starting backend server...
Starting bot...
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     100.64.0.2:41983 - "GET /health HTTP/1.1" 200 OK
```

**Ошибки:**
```
ERROR - processing_error
ERROR - unhandled_exception
```

## Переменные окружения

### Обязательные:
```bash
DATABASE_URL=<auto от Railway PostgreSQL>
OPENAI_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=7471812936:AAFoji4k74oAo347ahNaa1K1WAPtiSQ_ox8
```

### Опциональные:
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
PORT=<auto от Railway>
```

### Проверка:
```bash
railway variables
```

## Railway Configuration Checklist

### Service Settings:
- ✅ **Builder:** Dockerfile
- ✅ **Health Check Path:** /health
- ✅ **Health Check Timeout:** 100s
- ✅ **Restart Policy:** ON_FAILURE
- ✅ **Max Retries:** 10
- ✅ **Replicas:** 1 (важно для бота!)

### PostgreSQL Plugin:
- ✅ **Version:** 15+
- ✅ **Backups:** Enabled
- ✅ **DATABASE_URL:** Автоматически установлен

### Networking:
- ✅ **Public Domain:** Включен
- ✅ **HTTPS:** Автоматически

## Настройка Webhook (Production)

Для production рекомендуется использовать webhook вместо polling.

### 1. Получите public URL:
```bash
railway domain
# Результат: https://your-app.railway.app
```

### 2. Измените bot/main.py:

```python
async def main() -> None:
    """Главная функция запуска бота."""
    logger.info("bot_starting", environment=config.environment)

    bot = Bot(token=config.telegram_bot_token)
    dp = Dispatcher()

    # ... остальная настройка ...

    if config.environment == "production":
        # Webhook для production
        webhook_url = f"{config.webhook_url}/webhook"
        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        logger.info("bot_started", mode="webhook", url=webhook_url)

        # Запуск webhook сервера через FastAPI
        # (реализация зависит от архитектуры)
    else:
        # Polling для development
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("bot_started", mode="polling")
        await dp.start_polling(bot)
```

### 3. Добавьте переменную окружения:
```bash
railway variables set WEBHOOK_URL=https://your-app.railway.app
```

## Мониторинг

### Railway Observability:
- CPU Usage
- Memory Usage
- Network Traffic
- Response Time

### Логи для мониторинга:
```json
{
  "event": "voice_message_processed_successfully",
  "user_id": 123456,
  "stars_earned": 2,
  "streak": 5,
  "duration_seconds": 15.3
}
```

### Алерты (настроить в Railway):
- Health Check Failed
- High Error Rate
- High Response Time

## Контакты для помощи

- **OpenAI Status:** https://status.openai.com/
- **Railway Status:** https://status.railway.app/
- **Telegram Bot API Status:** https://core.telegram.org/

## Changelog исправлений

### v1.0.1 (текущая версия)
- ✅ Добавлен детальный error logging
- ✅ Фикс Telegram bot conflict (numReplicas: 1)
- ✅ Улучшена обработка ошибок в lesson endpoint
- ✅ Добавлен traceback в development mode
- ✅ Улучшен global exception handler

### Следующие улучшения:
- [ ] Webhook support для production
- [ ] Metrics dashboard
- [ ] Automated testing в CI/CD
- [ ] Redis caching для ускорения

---

**На здоровье!** 🍺 Honzík


