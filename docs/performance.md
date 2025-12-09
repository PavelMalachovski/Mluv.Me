# 🚀 Performance Improvements - Mluv.Me Code Review

> **Дата ревью:** декабрь 2024
> **Версия:** 1.0.0

---

## 📊 Текущее состояние

Проект в целом хорошо спроектирован с точки зрения производительности:
- ✅ Async/await повсеместно
- ✅ Connection pooling для PostgreSQL
- ✅ Redis кеширование
- ✅ Exponential backoff для OpenAI API
- ✅ lru_cache для настроек

---

## 🔥 Критические улучшения (Высокий приоритет)

### 1. OpenAI Client - Singleton Pattern

**Проблема:** `OpenAIClient` создается для каждого запроса через `Depends(get_openai_client)`.

**Файл:** `backend/routers/lesson.py:68-70`
```python
def get_openai_client(settings: Settings = Depends(get_settings)) -> OpenAIClient:
    return OpenAIClient(settings)  # Новый экземпляр каждый раз!
```

**Решение:**
```python
from functools import lru_cache

@lru_cache
def get_openai_client(settings: Settings = Depends(get_settings)) -> OpenAIClient:
    return OpenAIClient(settings)
```

**Эффект:** Избежание создания нового AsyncOpenAI клиента и tiktoken энкодера на каждый запрос.

---

### 2. Двойной запрос к daily_stats

**Проблема:** В `lesson.py` вызывается `get_or_create_daily` дважды подряд.

**Файл:** `backend/routers/lesson.py:257-269`
```python
await stats_repo.update_daily(
    messages_count=(
        await stats_repo.get_or_create_daily(user.id, user_date)  # Запрос 1
    ).messages_count + 1,
    words_said=(
        await stats_repo.get_or_create_daily(user.id, user_date)  # Запрос 2
    ).words_said + processed["words_total"],
)
```

**Решение:**
```python
daily_stats = await stats_repo.get_or_create_daily(user.id, user_date)
await stats_repo.update_daily(
    user_id=user.id,
    date_value=user_date,
    messages_count=daily_stats.messages_count + 1,
    words_said=daily_stats.words_said + processed["words_total"],
)
```

**Эффект:** -50% запросов к БД в этом месте.

---

### 3. CORS Wildcard в Production

**Проблема:** CORS разрешает все origins даже в production.

**Файл:** `backend/main.py:77-83`
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ОПАСНО для production!
)
```

**Решение:**
```python
settings = get_settings()
allowed_origins = (
    ["*"] if settings.is_development
    else ["https://mluv.me", "https://t.me"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
)
```

---

## ⚡ Средний приоритет

### 4. HTTP клиент в прокси без повторного использования

**Проблема:** Новый `httpx.AsyncClient` создается на каждый запрос.

**Файл:** `backend/main.py:211`
```python
async with httpx.AsyncClient(...) as client:  # Каждый раз новый!
```

**Решение:**
```python
# В lifespan
app.state.http_client = httpx.AsyncClient()

# В прокси
response = await request.app.state.http_client.request(...)

# В shutdown
await app.state.http_client.aclose()
```

---

### 5. Отсутствие кеширования переводов слов

**Проблема:** Каждый перевод слова вызывает OpenAI API.

**Файл:** `backend/services/translation_service.py`

**Решение:**
```python
async def translate_word(self, word: str, target: str) -> str:
    cache_key = f"translation:{word}:{target}"
    cached = await redis_client.get(cache_key)
    if cached:
        return cached

    translation = await self._call_openai(word, target)
    await redis_client.set(cache_key, translation, ttl=86400*7)  # 7 дней
    return translation
```

**Эффект:** Значительная экономия токенов OpenAI.

---

### 6. Frontend - React Query staleTime

**Проблема:** Данные считаются устаревшими сразу после получения.

**Файл:** `frontend/app/providers.tsx`

**Решение:**
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 минут
      gcTime: 1000 * 60 * 30,   // 30 минут
      refetchOnWindowFocus: false,
    },
  },
})
```

---

### 7. База данных - отсутствуют индексы

**Проблема:** Нет индекса на `messages.created_at` для сортировки.

**Решение (Alembic миграция):**
```python
op.create_index(
    'idx_messages_user_created',
    'messages',
    ['user_id', 'created_at'],
    postgresql_using='btree'
)

op.create_index(
    'idx_saved_words_user_word',
    'saved_words',
    ['user_id', 'word_czech']
)
```

---

## 🔧 Низкий приоритет

### 8. Lazy loading для tiktoken

**Проблема:** Tiktoken энкодер загружается при инициализации.

**Файл:** `backend/services/openai_client.py:60-64`

**Решение:**
```python
@property
def encoding(self):
    if self._encoding is None:
        self._encoding = tiktoken.encoding_for_model(self.settings.openai_model)
    return self._encoding
```

---

### 9. Session autoflush отключен

**Проблема:** `autoflush=False` может вызвать неожиданное поведение.

**Файл:** `backend/db/database.py:147`

**Рекомендация:** Включить `autoflush=True` и явно контролировать flush в транзакциях.

---

### 10. Next.js Image Optimization

**Текущее состояние (хорошо):**
```javascript
images: {
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 60 * 60 * 24 * 30,
}
```

**Дополнительно:**
```javascript
experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react'],
}
```

---

## 📈 Метрики для мониторинга

| Метрика | Текущее | Цель |
|---------|---------|------|
| Время ответа API | ~500ms | <300ms |
| OpenAI запросов/мин | N/A | <100 |
| Cache hit ratio | N/A | >80% |
| DB connections | 20 | Оптимально |

---

## ✅ Что уже сделано хорошо

1. **Connection Pooling** - `pool_size=20`, `pool_pre_ping=True`
2. **Token Optimization** - `optimize_conversation_history()` метод
3. **Adaptive Model Selection** - GPT-3.5 для beginners
4. **Structured Logging** - structlog с JSON
5. **Redis Caching** - Базовая инфраструктура готова

---

## 🎯 План действий

1. **Неделя 1:** Пункты 1-3 (критические)
2. **Неделя 2:** Пункты 4-6 (средние)
3. **Неделя 3:** Пункты 7-10 (низкие)
4. **Постоянно:** Мониторинг метрик
