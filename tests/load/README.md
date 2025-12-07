# Load Testing с Locust

Этот каталог содержит load tests для Mluv.Me API используя [Locust](https://locust.io/).

## 📋 Содержание

- `locustfile.py` - Основной файл с load tests
- `test_data.py` - Тестовые данные (чешские фразы)
- `README.md` - Этот файл

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install locust
```

Или используйте requirements.txt проекта:

```bash
pip install -r requirements.txt
```

### 2. Запуск локально

```bash
# Базовый запуск с Web UI
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Откройте http://localhost:8089 в браузере
```

### 3. Запуск без UI (headless)

```bash
# 100 пользователей, по 10 в секунду, 5 минут
locust -f tests/load/locustfile.py \
    --host=http://localhost:8000 \
    --users=100 \
    --spawn-rate=10 \
    --run-time=5m \
    --headless \
    --html=reports/load_test_local.html
```

## 🎯 Тестовые сценарии

### MluvMeUser

Симулирует реального пользователя с следующими задачами:

| Задача | Вес | Описание |
|--------|-----|----------|
| `process_voice_message` | 10 | Отправка голосового сообщения (основной flow) |
| `get_user_stats` | 3 | Получение статистики пользователя |
| `get_user_profile` | 2 | Получение профиля пользователя |
| `get_saved_words` | 2 | Получение сохраненных слов |
| `get_streak_calendar` | 1 | Получение streak календаря |

**Вес** определяет относительную частоту выполнения задачи.

## 📊 Сценарии тестирования

### Scenario 1: Базовая нагрузка (Development)

Проверка основной функциональности под легкой нагрузкой.

```bash
locust -f tests/load/locustfile.py \
    --host=http://localhost:8000 \
    --users=10 \
    --spawn-rate=2 \
    --run-time=2m \
    --headless
```

**Ожидаемые результаты:**
- Все запросы успешны (0% failures)
- p95 response time < 500ms
- p99 response time < 1000ms

### Scenario 2: Средняя нагрузка (Staging)

Проверка производительности под нормальной нагрузкой.

```bash
locust -f tests/load/locustfile.py \
    --host=https://staging.mluv.me \
    --users=100 \
    --spawn-rate=10 \
    --run-time=10m \
    --headless \
    --html=reports/load_test_staging.html
```

**Ожидаемые результаты:**
- Failures < 1%
- p95 response time < 500ms
- p99 response time < 1000ms
- Database connections stable

### Scenario 3: Пиковая нагрузка (Production)

Проверка максимальной нагрузки и выявление bottlenecks.

```bash
locust -f tests/load/locustfile.py \
    --host=https://api.mluv.me \
    --users=1000 \
    --spawn-rate=50 \
    --run-time=30m \
    --headless \
    --html=reports/load_test_production.html
```

**Ожидаемые результаты:**
- Failures < 1%
- p95 response time < 1000ms
- p99 response time < 2000ms
- No memory leaks
- Database connections < 50

### Scenario 4: Stress Test

Тест до полного отказа для определения пределов системы.

```bash
locust -f tests/load/locustfile.py \
    --host=https://api.mluv.me \
    --users=2000 \
    --spawn-rate=100 \
    --run-time=15m \
    --headless \
    --html=reports/stress_test.html
```

**Цель:** Определить максимальное количество concurrent пользователей.

## 📈 Метрики производительности

### Целевые показатели (Phase 5 roadmap)

| Метрика | Baseline (до оптимизации) | Target (после Phase 4) |
|---------|---------------------------|------------------------|
| API Response (p50) | 200ms | <50ms |
| API Response (p95) | 450ms | <150ms |
| DB Query Time (avg) | 80ms | <10ms |
| Cache Hit Rate | 0% | >85% |
| OpenAI Cost/User | $0.15 | <$0.12 |
| Concurrent Users | 250 | 1000+ |

### Как измерять

1. **Response Time**: Locust автоматически измеряет
2. **DB Query Time**: Смотреть логи PostgreSQL
3. **Cache Hit Rate**: Redis INFO stats
4. **Cost**: OpenAI dashboard
5. **Concurrent Users**: Постепенно увеличивать до появления ошибок

## 🔍 Анализ результатов

### 1. Web UI (в реальном времени)

Откройте `http://localhost:8089` для мониторинга в реальном времени:
- Количество пользователей
- Requests per second (RPS)
- Response times (p50, p95, p99)
- Failures

### 2. HTML Report

После завершения теста откройте `reports/load_test_*.html`:
- Детальная статистика по endpoints
- Графики response time
- Failures breakdown

### 3. Анализ bottlenecks

```bash
# Проверить загрузку CPU/Memory
htop

# Проверить PostgreSQL
psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Проверить Redis
redis-cli INFO stats

# Проверить Celery workers
celery -A backend.tasks.celery_app inspect active
```

## ⚠️ Важные замечания

### Перед запуском load tests:

1. **Не тестировать на production без предупреждения**
2. Убедиться, что база данных настроена для тестов
3. Использовать отдельный OpenAI API key с лимитом
4. Мониторить расходы OpenAI API
5. Иметь план rollback

### Тестовые данные

- Используются fake аудио файлы (минимальный размер)
- Генерируются уникальные telegram_id для каждого пользователя
- Случайные настройки пользователей

### Известные ограничения

- OpenAI API имеет rate limits (особенно для Whisper/TTS)
- Railway.com может иметь network limits
- PostgreSQL connection pool limit (default: 20)

## 📝 Checklist перед деплоем

После успешных load tests:

- [ ] Все тесты прошли с failures < 1%
- [ ] p95 response time соответствует целям
- [ ] База данных стабильна под нагрузкой
- [ ] Redis cache hit rate > 85%
- [ ] Нет memory leaks
- [ ] Celery workers обрабатывают задачи
- [ ] Логи не содержат критических ошибок
- [ ] Мониторинг настроен (Sentry, Prometheus)
- [ ] Alerts настроены
- [ ] Rollback plan документирован

## 🆘 Troubleshooting

### Проблема: High failure rate

**Решение:**
- Проверить логи backend
- Увеличить connection pool
- Проверить Redis connectivity
- Проверить OpenAI API limits

### Проблема: Slow response times

**Решение:**
- Проверить cache hit rate
- Оптимизировать database queries
- Добавить indexes
- Увеличить Celery workers

### Проблема: Memory leaks

**Решение:**
- Проверить connection pool closing
- Проверить Celery task cleanup
- Мониторить с `memory_profiler`

## 📚 Дополнительные ресурсы

- [Locust Documentation](https://docs.locust.io/)
- [Performance Testing Best Practices](https://locust.io/best-practices)
- [FastAPI Performance](https://fastapi.tiangolo.com/advanced/performance/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

**Последнее обновление:** December 7, 2025
**Версия:** 1.0.0
