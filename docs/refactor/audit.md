# Mluv.Me — Полный аудит проекта

**Дата:** 18 февраля 2026  
**Версия:** 1.0.0  
**Среда:** Railway.com (production), Redis healthy  
**Стек:** FastAPI + Next.js 14 + aiogram 3 + PostgreSQL + Redis + Celery

---

## ⚠️ НЕРЕШЁННЫЕ ПРОБЛЕМЫ — сводка (актуально на 23.02.2026)

> **Итого: 4 нерешённых (5-6 бизнес/инфра), 16 исправлено ✅**

### 🔴 Высокий приоритет

| # | Проблема | Раздел | Статус |
|---|---|---|---|
| 1 | ~~Race condition в `award_stars`~~ — заменено на атомарный `UPDATE total = total + N` | [§8](#8-производительность) | ✅ Исправлено |
| 2 | ~~Detached SQLAlchemy объект из кэша~~ — `get_by_telegram_id` всегда делает DB-запрос | [§7](#7-база-данных-и-модели) | ✅ Исправлено |
| 3 | ~~`selectinload().limit()` молча игнорируется~~ — `.limit()` убран из selectinload | [§7](#7-база-данных-и-модели) | ✅ Исправлено |
| 4 | ~~N+1 в `achievement_service.py`~~ — `_prefetch_all_category_values()` за ~7 запросов | [§8](#8-производительность) | ✅ Исправлено |
| 5 | **Premium-фичи не гейтятся** — сценарии, грамматика, pronunciation, SR доступны бесплатно всем | [§14](#14-план-действий) | ❌ Не исправлено |
| 6 | **Stripe — только стуб** — `POST /checkout` и webhook возвращают 501 | [§15](#15-стратегия-монетизации--детальный-план) | ❌ Не исправлено |

### 🟡 Средний приоритет

| # | Проблема | Раздел | Статус |
|---|---|---|---|
| 7 | ~~`daily_stats` без UNIQUE(user_id, date)~~ — добавлен UniqueConstraint + миграция | [§7](#7-база-данных-и-модели) | ✅ Исправлено |
| 8 | ~~`saved_words.next_review_date` без индекса~~ — добавлен `idx_saved_words_next_review` | [§7](#7-база-данных-и-модели) | ✅ Исправлено |
| 9 | ~~`review-stats` грузит ВСЕ слова~~ — переписано на SQL COUNT + CASE WHEN | [§8](#8-производительность) | ✅ Исправлено |
| 10 | ~~`get_my_rank` загружает 1000 пользователей~~ — переписано на SQL `RANK() OVER()` | [§8](#8-производительность) | ✅ Исправлено |
| 11 | ~~BOT-5: Конфликт callback-хэндлеров~~ — онбординг использует `onb_native:` / `onb_level:` | [§6](#6-telegram-bot) | ✅ Исправлено |
| 12 | ~~`web_lessons.py` дублирует `lesson.py`~~ — общая логика в `lesson_processing.py` | [§4](#4-backend--архитектура-и-код) | ✅ Исправлено |

### 🟢 Низкий приоритет / Бэклог

| # | Проблема | Раздел | Статус |
|---|---|---|---|
| 13 | ~~Settings update дублируется~~ — общий `_do_update_settings()` хелпер | [§4](#4-backend--архитектура-и-код) | ✅ Исправлено |
| 14 | ~~User lookup + 404 повторяется~~ — `get_user_by_telegram_id` dependency в gamification.py | [§4](#4-backend--архитектура-и-код) | ✅ Исправлено |
| 15 | ~~Frontend: `refetchOnMount: "always"`~~ — удалено, staleTime теперь работает | [§5](#5-frontend--архитектура-и-код) | ✅ Исправлено |
| 16 | ~~Frontend: `filteredWords` не в `useMemo`~~ — обёрнуто в `useMemo` | [§5](#5-frontend--архитектура-и-код) | ✅ Исправлено |
| 17 | ~~UX-5: Беседа теряется~~ — sessionStorage persistence для conversation | [§12](#12-uxui-проблемы) | ✅ Исправлено |
| 18 | ~~Нет frontend-тестов~~ — Playwright smoke tests созданы | [§11](#11-тестирование) | ✅ Исправлено |

### 🏗 Инфраструктура (ещё не реализовано)

| # | Проблема | Раздел |
|---|---|---|
| 19 | **Один контейнер** — crash любого компонента убивает всё (HIGH) | [§10](#10-инфраструктура-и-деплой) |
| 20 | **Нет staging-окружения** (MEDIUM) | [§10](#10-инфраструктура-и-деплой) |
| 21 | **Нет CDN** для статики frontend (LOW) | [§10](#10-инфраструктура-и-деплой) |
| 22 | **Масштабирование этапы 2-3** — разделение сервисов, replicas, webhook бота, PgBouncer | [§16](#16-масштабирование-при-высокой-нагрузке-100-одновременных-пользователей) |

---

---

## Содержание

1. [Резюме](#1-резюме)
2. [Критические баги](#2-критические-баги)
3. [Безопасность](#3-безопасность)
4. [Backend — архитектура и код](#4-backend--архитектура-и-код)
5. [Frontend — архитектура и код](#5-frontend--архитектура-и-код)
6. [Telegram Bot](#6-telegram-bot)
7. [База данных и модели](#7-база-данных-и-модели)
8. [Производительность](#8-производительность)
9. [OpenAI — оптимизация затрат](#9-openai--оптимизация-затрат)
15. [Стратегия монетизации — детальный план](#15-стратегия-монетизации--детальный-план)
16. [Масштабирование при высокой нагрузке](#16-масштабирование-при-высокой-нагрузке)
10. [Инфраструктура и деплой](#10-инфраструктура-и-деплой)
11. [Тестирование](#11-тестирование)
12. [UX/UI проблемы](#12-uxui-проблемы)
13. [Монетизация](#13-монетизация)
14. [План действий](#14-план-действий)

---

## 1. Резюме

### Что хорошо
- Богатый функционал: 18+ сервисов (GPT-4o, Whisper, TTS, грамматика, игры, сценарии, SR, ачивки)
- Celery beat + 5 cron-задач работают стабильно
- Redis кэширование настроено и подключено
- Структура проекта логичная и читаемая
- Модели данных нормализованы, миграции Alembic актуальны

### Что критично
| Категория | Количество проблем | Статус |
|---|---|---|
| 🔴 Критические баги | 5 | ✅ Все 5 исправлены |
| 🔴 Безопасность (critical/high) | 8 | ✅ Все 8 исправлены |
| 🟡 Безопасность (medium) | 4 | ✅ Все 4 исправлены |
| 🟡 Средние баги (frontend) | 5 | ✅ 4 исправлены, 1 не баг |
| 🟡 In-memory утечки | 5 | ✅ Все 5 исправлены (TTL+cap) |
| 🟡 Производительность | 10 | ✅ N+1 fix, prompt caching |
| 🟢 Code quality / dead code | 15+ | ✅ Исправлено |
| 🟢 Тестирование | 6 test files | ✅ ~30%+ coverage |
| 🟢 Инфраструктура | CI/CD + Sentry | ✅ GitHub Actions + Sentry SDK |
| 💰 Монетизация | Subscription + Stars + лимиты | ✅ Реализовано |
| 🚀 Масштабирование Этап 1 | uvicorn workers, pool tuning, OpenAI limiter, TTS cache | ✅ Реализовано |
| 🟣 Персонажи | Honzík + paní Nováková, выбор в настройках | ✅ Реализовано |
| 🟣 Скорость Honzíka | Компактные промпты, убран overhead | ✅ Оптимизировано |

---

## 2. Критические баги ✅ ВСЕ ИСПРАВЛЕНЫ

### BUG-1: Токен не сохраняется при логине через WebApp ✅
**Файл:** `frontend/app/(auth)/login/page.tsx` (строка ~78)  
**Проблема:** `handleWebAppLogin` вызывает `setUser(result.user)`, но **никогда не вызывает `setToken(result.token)`**. В результате все последующие API-запросы идут без авторизации.  
**Влияние:** Веб-авторизация через Telegram WebApp фактически сломана.  
**Фикс:** Добавить `setToken(result.token)` после `setUser(result.user)`.

### BUG-2: user.settings может быть None → AttributeError ✅
**Файлы:** `backend/routers/lesson.py` (~10 мест), `backend/routers/gamification.py` (3 места)  
**Проблема:** Код обращается к `user.settings.conversation_style`, `user.settings.timezone` и т.д. без проверки на `None`. Новый пользователь, у которого нет записи в `UserSettings`, получит `AttributeError: 'NoneType' object has no attribute 'conversation_style'`.  
**Влияние:** Crash при первом уроке для пользователей без настроек.  
**Фикс:** Добавить null-safe access: `getattr(user.settings, 'conversation_style', 'friendly')` или создавать настройки при создании пользователя.

### BUG-3: Кэш Honzik — неправильный ключ (native_language) ✅
**Файл:** `backend/services/honzik_personality.py` (строка ~267)  
**Проблема:** `settings_dict` для ключа кэша включает `czech_level`, `correction_level`, `conversation_style`, но **не включает `native_language`**. Два пользователя с одинаковым уровнем, но разными языками (ru/uk) могут получить чужой кэшированный ответ.  
**Влияние:** Украиноязычные пользователи видят ответы на русском и наоборот.

### BUG-4: Кэш TTS — модель hardcoded как "gpt-4o" ✅
**Файл:** `backend/services/cache_service.py` (строка ~216)  
**Проблема:** `get_cached_honzik_response` хардкодит `"gpt-4o"` в ключе кэша, но реальная модель выбирается динамически (gpt-4o-mini). Ответ от mini кэшируется под ключом gpt-4o → кросс-загрязнение кэша.

### BUG-5: web_lessons.py передаёт ui_language вместо native_language ✅
**Файл:** `backend/routers/web_lessons.py` (строка ~94)  
**Проблема:** Вызывает `honzik.generate_response()` с `ui_language=user.native_language`, но в `lesson.py` тот же сервис вызывается с `native_language=user.native_language`. Один из них передаёт неправильный kwarg → параметр игнорируется или вызывает TypeError.

---

## 3. Безопасность ✅ ВСЕ ИСПРАВЛЕНЫ

### 🔴 CRITICAL — ✅ ВСЕ ИСПРАВЛЕНЫ

| # | Проблема | Файл | Описание | Статус |
|---|---|---|---|---|
| SEC-1 | **Захардкоженный Bot Token** | `bot/config.py:17` | Токен бота лежит в исходном коде: `7471812936:AAFoji...`. Кто угодно с доступом к репо контролирует бота. **Нужно ротировать токен через BotFather немедленно.** | ✅ Дефолт удалён |
| SEC-2 | **Захардкоженный Bot Token** | `backend/config.py:44` | Тот же токен дублируется в бэкенд-конфиге как default. | ✅ Дефолт удалён |
| SEC-3 | **Нет аутентификации на API** | Все роутеры | ВСЕ 12 роутеров принимают `user_id`/`telegram_id` как параметр без проверки. Любой HTTP-клиент может читать/менять/удалять данные любого пользователя. | ✅ `get_authenticated_user` dependency |
| SEC-4 | **Захардкоженный admin secret** | `backend/routers/grammar.py:293` | `os.getenv("ADMIN_SECRET", "mluv-seed-2026")` — если переменная не задана, секрет — в коде. Плюс передаётся как query param → логируется в access logs. | ✅ Дефолт убран, перенесён в Header |

### 🟡 HIGH — ✅ ВСЕ ИСПРАВЛЕНЫ

| # | Проблема | Файл | Описание | Статус |
|---|---|---|---|---|
| SEC-5 | **Сессии в памяти** | `backend/routers/web_auth.py:60` | `sessions: dict` хранится в RAM → теряется при рестарте. Нет лимита → DoS через флуд авторизаций. | ✅ MAX_SESSIONS=5000 + TTL |
| SEC-6 | **JWT в localStorage** | `frontend/lib/auth-store.ts:36` | Токен в localStorage уязвим к XSS. Нужны httpOnly cookies. | ✅ httpOnly cookie добавлен |
| SEC-7 | **DELETE без владения** | `backend/routers/words.py:174` | `DELETE /{word_id}` удаляет любое слово по ID без проверки принадлежности. | ✅ Проверка user_id |
| SEC-8 | **Push без авторизации** | `frontend/lib/push-notifications.ts:167` | `saveSubscriptionToServer` использует `fetch` вместо `apiClient` → запросы идут без токена. | ✅ Исправлено на apiClient |

### 🟢 MEDIUM — ✅ ВСЕ ИСПРАВЛЕНЫ

| # | Проблема | Описание | Статус |
|---|---|---|---|
| SEC-9 | `datetime.utcnow()` deprecated | Python 3.12+ — использовать `datetime.now(timezone.utc)` | ✅ 21 замена в 10 файлах |
| SEC-10 | Session token в query string | `GET /me` принимает токен как query param → попадает в логи и browser history | ✅ Используется `get_authenticated_user` dependency |
| SEC-11 | Admin secret в query string | Оба admin endpoint `/admin/seed` и `/admin/send-notifications` | ✅ Перенесён в `X-Admin-Secret` Header |
| SEC-12 | Logout без проверки владения | `POST /logout` принимает любой токен без проверки | ✅ Используется `_resolve_session_token` |

---

## 4. Backend — архитектура и код

### Дублирование кода
| Проблема | Где | Статус |
|---|---|---|
| User response dict повторяется 3 раза | `web_auth.py` (строки 148, 206, 351) | ✅ Извлечён `_user_response_dict()` helper |
| Settings update логика повторяется 3 раза | `users.py` | ⬜ |
| User lookup + 404 повторяется ~25 раз | Все роутеры | ⬜ |
| `web_lessons.py POST /text` дублирует `lesson.py POST /process/text` | Две разные реализации одной логики | ⬜ |

### Рекомендации
- ✅ Создать `get_authenticated_user()` FastAPI Dependency для инъекции текущего пользователя
- ✅ Вынести user response в `_user_response_dict()` helper
- ⬜ Создать `UserSettingsSafe` helper с fallback значениями
- ⬜ Удалить или объединить `web_lessons.py` с `lesson.py`
- ✅ `OpenAIClient()` в `web_lessons.py` исправлен — теперь использует `get_settings()` singleton

### In-memory хранилища (утечки памяти) ✅ ВСЕ ПЕРЕВЕДЕНО В REDIS
| Dict | Файл | Проблема | Статус |
|---|---|---|---|
| `sessions` | `web_auth.py` | Не очищается, нет TTL | ✅ Redis `session:{token}` TTL=30d |
| `onboarding_data` | `bot/handlers/start.py` | Не очищается при незавершённом онбординге | ✅ MAX=500, TTL=3600s |
| `_corrections_cache` | `bot/handlers/voice.py` | Чистится только при новом сообщении | ✅ MAX=1000, overflow eviction |
| `_active_games` | `backend/services/game_service.py` | Не шарится между воркерами, нет TTL | ✅ Redis `game:active:{uid}` TTL=30min |
| `_active_scenarios` | `backend/services/scenario_service.py` | Не шарится между воркерами, нет TTL | ✅ Redis `scenario:active:{uid}` TTL=1hr |

**✅ Долгосрочное решение применено:** Sessions, games, scenarios полностью переведены на Redis с TTL. In-memory dict'ы убраны. Binary pool оптимизирован (shared connection pool вместо per-call).

---

## 5. Frontend — архитектура и код

### Баги ✅ ВСЕ ИСПРАВЛЕНЫ

| # | Проблема | Файл | Статус |
|---|---|---|---|
| FE-1 | **Токен не сохраняется при логине** (см. BUG-1) | `login/page.tsx` | ✅ Исправлено |
| FE-2 | `useOptimisticMutations` — `user_mistakes` маппится на `string[]` вместо `Mistake[]` | `hooks/useOptimisticMutations.ts:87` | ✅ Теперь передаёт `Mistake[]` |
| FE-3 | `telegramId=0` если user=null → запрос с несуществующим ID | `practice/page.tsx:60` | ✅ Guard `if (!user?.telegram_id) return` |
| FE-4 | 401 interceptor вызывает logout на **каждый** 401, включая login | `api-client.ts:48` | ✅ Скип для `/auth/` endpoints |
| FE-5 | `hasSeenWelcomeVideo()` вызывается при рендере (не в useEffect) → hydration mismatch | `dashboard/page.tsx:53` | ✅ Не баг — уже в useEffect |

### Dead code ✅ ВСЁ УДАЛЕНО
| Что | Файл | Статус |
|---|---|---|
| `useRequireAuth()` — никогда не используется | `auth-store.ts:78` | ✅ Удалено |
| `useAuth()` — никогда не используется | `auth-store.ts:71` | ✅ Удалено |
| `validateTelegramAuth()` — никогда не вызывается | `telegram-auth.ts:54` | ✅ Удалено |
| `initTelegramAuth()` — никогда не используется | `telegram-auth.ts:26` | ✅ Удалено |
| `applyTheme()` — никогда не используется | `theme-store.ts:36` | ✅ Удалено |
| `AnalyticsData`, `WeeklyStats`, `DailyActivity` типы | `types.ts:105` | ✅ Удалено |
| Импорты `dynamic`, `Skeleton`, `Trophy`, `Star` | layout.tsx, learn/page.tsx | ✅ Удалено |

### Производительность
| Проблема | Файл |
|---|---|
| `refetchOnMount: "always"` отменяет `staleTime` | `providers.tsx:14` |
| Telegram SDK загружается на каждой странице | `layout.tsx:36` |
| Leaderboard и Challenges используют useState + useEffect вместо React Query | `Leaderboard.tsx`, `learn/page.tsx` |
| `filteredWords` не обёрнут в `useMemo` | `SavedWordsTab.tsx:109` |
| Preload изображений на страницах, где они не нужны | `layout.tsx:33` |

---

## 6. Telegram Bot

### Баги

| # | Проблема | Файл | Статус |
|---|---|---|---|
| BOT-1 | `onboarding_data` dict растёт неограниченно | `handlers/start.py:21` | ✅ MAX=500, TTL=3600s |
| BOT-2 | `_corrections_cache` dict растёт неограниченно | `handlers/voice.py:34` | ✅ MAX=1000, overflow eviction |
| BOT-3 | `random.seed()` мутирует глобальное состояние (не thread-safe) | `services/challenge_service.py:68` | ✅ `random.Random(hash(...))` |
| BOT-4 | `aiohttp.ClientSession` без таймаута (default 300s) | `services/api_client.py:29` | ✅ `ClientTimeout(total=30, connect=10)` |
| BOT-5 | Settings-change коллбэки конфликтуют с onboarding коллбэками | `handlers/commands.py` vs `start.py` | ⬜ |

### Дублирование
- `voice.py` и `text.py` содержат >50% идентичного кода (построение ответа, кнопки, кэш коррекций)
- Каждая команда вызывает `api_client.get_user()` заново, даже в callback после команды

---

## 7. База данных и модели

### Пропущенные индексы
| Таблица | Что нужно |
|---|---|
| `daily_stats` | Composite UNIQUE на `(user_id, date)` — сейчас возможны дубликаты |
| `saved_words` | Индекс на `next_review_date` для эффективного запроса слов на повторение |

### Проблема с кэшированным пользователем
**Файл:** `backend/db/repositories.py:82`  
`get_by_telegram_id` воссоздаёт `User` из кэшированного dict через `User(**cached)`, создавая **detached SQLAlchemy объект**. Любой lazy-load relationship (`user.settings`, `user.messages`) выбросит `DetachedInstanceError`. ISO-строки `created_at`/`updated_at` не конвертируются обратно в `datetime`.

### Проблема с selectinload + limit
**Файл:** `backend/db/repositories.py:193`  
`.limit()` на `selectinload` **не поддерживается** SQLAlchemy — молча игнорируется, загружая все связанные записи.

---

## 8. Производительность

### N+1 Query проблемы
| Файл | Endpoint | Проблема | Статус |
|---|---|---|---|
| `achievement_service.py:112` | `check_achievements` | Для каждой ачивки отдельный запрос → 50+ запросов | ⬜ |
| `grammar.py:259` | `GET /progress/details` | Для каждого прогресса отдельный `get_rule_by_id()` | ✅ `joinedload` |
| `challenge_service.py` | `_calculate_progress` | Отдельные запросы для каждого типа челленджа | ⬜ |
| `gamification.py:488` | `GET /leaderboard/my-rank` | Загрузка до 1000 пользователей → можно `RANK()` window function | ⬜ |

### Неоптимальные выборки
| Файл | Проблема |
|---|---|
| `words.py:449` | `GET /review-stats` загружает ВСЕ слова пользователя в Python для подсчёта. Нужна SQL агрегация. |
| `gamification.py:342` | `GET /achievements/category` загружает все ачивки, фильтрует в Python. Нужен WHERE в SQL. |
| `lesson.py:175` | 10 сообщений загружаются и реверсируются в Python. Нужен `ORDER BY`. |

### Race conditions
| Файл | Проблема |
|---|---|
| `gamification.py:128` | `award_stars` делает read-then-write вместо `UPDATE SET total = total + N` |
| `gamification.py:276` | `check_daily_challenge` проверяет `messages_today == 5` (exactly equal). При конкуретных запросах может перепрыгнуть 5. |

---

## 9. OpenAI — оптимизация затрат

### Проблемы

| # | Проблема | Экономия |
|---|---|---|
| AI-1 | System prompt (~600-1000 токенов) пересоздаётся на каждое сообщение. Нужно кэшировать по `(level, corrections_level, native_language, style)` | ✅ `@lru_cache(maxsize=64)` на `_get_base_prompt` |
| AI-2 | `honzik_personality.py:236` — история беседы отправляется **дважды**: как текст в user prompt И как отдельные messages. Двойной расход токенов | ✅ Пустая история → блок пропускается |
| AI-3 | `MAX_TTS_CACHE_LENGTH = 200` символов → увеличено до 500 | ✅ 500, +TTS cache 30 дней |
| AI-4 | `MODEL_PRICING` dict и `TOKEN_LIMITS` dict в `openai_client.py` определены, но **никогда не используются** | ✅ Удалён dead code |
| AI-5 | `OpenAIClient.get_optimal_model()` — dead code, `model_selector.py` делает то же самое | ✅ Удалён дубликат |
| AI-6 | `web_lessons.py` создаёт новый `OpenAIClient()` на **каждый запрос** вместо singleton | ✅ Исправлено: `get_settings()` + singleton |

### Оценка затрат
При 100 активных пользователях (10 сообщений/день):
- GPT-4o: ~$0.03/msg = **$30/день**
- GPT-4o-mini: ~$0.003/msg = **$3/день** (model_selector активен, ~70% на mini)
- TTS: ~$0.015/msg = **$15/день**
- STT: ~$0.006/msg = **$6/день**
- **Итого: ~$20-30/день ≈ $600-900/месяц** при 100 активных пользователях

---

## 10. Инфраструктура и деплой

### Текущая архитектура
```
Railway.com (1 контейнер)
├── FastAPI backend (:8000)
├── Next.js frontend (:3000) — проксируется через FastAPI
├── Telegram bot (polling)
├── Celery worker (2 concurrency)
├── Celery beat (scheduler)
├── PostgreSQL (Railway plugin)
└── Redis (Railway plugin)
```

### Риски
| # | Проблема | Уровень |
|---|---|---|
| INFRA-1 | **Один контейнер = одна точка отказа**. Crash Celery → рестарт всего | HIGH |
| INFRA-2 | **Нет горизонтального масштабирования** — `numReplicas: 1` | MEDIUM |
| INFRA-3 | **Нет staging окружения** для тестирования изменений | MEDIUM |
| INFRA-4 | **Нет CI/CD** — отсутствует `.github/workflows/` | ✅ GitHub Actions (lint, test, frontend-lint) |
| INFRA-5 | **Нет CDN** для статики фронтенда | LOW |
| INFRA-6 | In-memory state теряется при рестарте (sessions, games, scenarios) | ✅ Всё в Redis с TTL |

### Рекомендации
1. ⬜ Разделить на 3 сервиса: backend, bot, celery (Railway compartments)
2. ✅ GitHub Actions: lint + test на PR (`.github/workflows/ci.yml`)
3. ✅ Сессии, игры, сценарии переведены в Redis (TTL: 30d/30min/1hr)
4. ✅ Sentry SDK интегрирован (`sentry-sdk[fastapi]` + lifespan init)

---

## 11. Тестирование

### Текущее покрытие: **~30-35%** (было ~15-20%)

| Тесты есть | Тестов нет |
|---|---|
| `test_endpoints.py` | `pronunciation_analyzer.py` |
| `test_repositories.py` | `translation_service.py` |
| `test_caching.py` | Telegram bot handlers |
| `test_correction_engine.py` | Frontend (0 тестов) |
| `test_gamification.py` | E2E pipeline |
| Load test (Locust) | |
| ✅ `test_auth.py` (сессии/Redis) | |
| ✅ `test_game_service.py` (игры/Redis) | |
| ✅ `test_scenario_service.py` (сценарии/Redis) | |
| ✅ `test_challenge_service.py` (RNG) | |
| ✅ `test_honzik_personality.py` (prompt cache) | |
| ✅ `test_grammar_repository.py` (joinedload) | |
| ✅ `test_redis_client.py` (binary pool) | |

### Рекомендации
1. Добавить тесты для бизнес-логики: gamification (race conditions), SR algorithm, grammar selection
2. Добавить integration тесты для auth flow
3. Frontend: хотя бы smoke тесты с Playwright для login → practice → response
4. Запускать тесты в CI/CD (`pytest.ini` уже настроен)

---

## 12. UX/UI проблемы

### Смешение языков
| Страница | Языки |
|---|---|
| Practice | Чешский + Английский + Русский |
| Profile | Английский |
| Settings | Чешский |
| Learn | Чешский + Английский |
| Login | Английский |

**Рекомендация:** Внедрить `next-intl` или другую i18n библиотеку. Минимум — привести к единому языку (чешский для UI, native_language для объяснений).

### Проблемы UX
| # | Проблема |
|---|---|
| UX-1 | Нет `<html lang="cs">` — зашито как `en` | ✅ Исправлено на `lang="cs"` |
| UX-2 | Нет error boundary — ошибка в компоненте крашит всё приложение | ✅ `ErrorBoundary.tsx` + обёртка dashboard |
| UX-3 | Удаление слова без подтверждения |
| UX-4 | Длинные ответы Honzik не помещаются в WebApp URL (лимит ~2048 символов) |
| UX-5 | Беседа теряется при навигации (state в useState, не persisted) |
| UX-6 | Stats не показывает ошибку загрузки — просто нули |
| UX-7 | Accessibility: ноль ARIA-атрибутов, нет keyboard navigation для карточек и кнопок | ✅ ARIA labels на nav, main, links |
| UX-8 | Нет offline-detection — при потере сети мутации молча падают |

---

## 13. Монетизация

### Текущий статус: **✅ Реализовано (22 февраля 2026)**

**Реализовано:**
- Free: 5 текстовых + 4 голосовых/день, Pro: безлимит (200 CZK/мес)
- Telegram Stars: 150⭐=7d Pro, 500⭐=30d Pro (полный флоу: invoice → pre_checkout → activation)
- Redis-based daily quotas, SubscriptionService, Subscription+Payment модели
- Frontend: QuotaBanner, QuotaIndicator, 429 error handling
- Stripe: стуб для будущей интеграции
- GPT-4o разговоры (стоят $0.03/сообщение)
- TTS озвучка ($0.015/сообщение)
- Whisper STT ($0.006/сообщение)
- 8 сценариев с AI
- 5 типов мини-игр
- Spaced repetition
- Pronunciation analyzer
- Exam prep, Story generator, Podcasts

### План монетизации (по приоритету)

#### Фаза 1 — Неделя 1-2: Начать зарабатывать ✅ РЕАЛИЗОВАНО
| Действие | Срок | Ожидание |
|---|---|---|
| **Лимит сообщений** (5 текст + 4 голос/день бесплатно) | ✅ | Конверсионное давление |
| **Telegram Stars** оплата | ✅ | 150⭐=7d Pro, 500⭐=30d Pro |
| Пакеты: +10 голосовых (50⭐), тема сценария (100⭐), 7 дней безлимит (150⭐) | | |

#### Фаза 2 — Неделя 3-6: Подписки
| Действие | Срок | Ожидание |
|---|---|---|
| Модель `Subscription` + миграция | 2 дня | |
| Stripe Checkout для веба | 5 дней | |
| **Free:** 5 сообщений/день, 1 бесплатный сценарий, базовые исправления | | |
| **Pro ($9.99/мес):** Безлимит, все сценарии, SR, подробные исправления | | $500-1500/мес |
| **Expert ($19.99/мес):** + Exam prep, Pronunciation, Podcasts, Stories | | $200-500/мес |

#### Фаза 3 — Месяц 2-3: Рост
| Действие | Ожидание |
|---|---|
| Реферальная программа (пригласи → 7 дней Pro) | +30% пользователей |
| A/B тестирование pricing | Оптимизация конверсии |
| Добавить польский/словацкий языки | Новые рынки |

### Прогноз дохода (консервативный)
| Метрика | Месяц 1 | Месяц 3 | Месяц 6 |
|---|---|---|---|
| Бесплатные пользователи | 500 | 2,000 | 5,000 |
| Конверсия | 3% | 5% | 7% |
| Платящие пользователи | 15 | 100 | 350 |
| MRR (подписки) | $150 | $1,000 | $3,500 |
| Telegram Stars | $50 | $300 | $800 |
| **Итого MRR** | **$200** | **$1,300** | **$4,300** |

### Главный вывод
> **Продукт feature-complete, но раздаёт AI-функции стоимостью $10-20/пользователь/месяц бесплатно. Приоритет #1 — лимит сообщений + оплата, а не новые фичи.**

---

## 14. План действий

### 🔴 Сейчас (1-3 дня) — ✅ ВСЁ ВЫПОЛНЕНО
1. ✅ **Ротировать Bot Token** — дефолт удалён из кода (ротация через BotFather — ручное действие)
2. ✅ **Фикс BUG-1:** сохранять token при WebApp login
3. ✅ **Фикс BUG-2:** null-safe для `user.settings`
4. ✅ **Фикс BUG-3:** добавить `native_language` в ключ кэша Honzik
5. ✅ **Фикс BUG-5:** исправить kwarg `ui_language` → `native_language` в `web_lessons.py`
6. ✅ Убрать hardcoded admin secret → в env var без fallback + перенесён в Header

### 🟡 Неделя 1-2
7. ✅ Добавить лимит сообщений (5 текст + 4 голос/день) — SubscriptionService + Redis quotas
8. ✅ Реализовать Telegram Stars payments — bot/handlers/payments.py
9. ✅ Перевести sessions → Redis (полностью мигрировано: `session:{token}` TTL=30d)
10. ✅ Добавить API authentication middleware (`get_authenticated_user` dependency)
11. ✅ Фикс `random.seed()` → `random.Random(hash(...))` (thread-safe)

### 🟢 Неделя 3-6
12. ✅ Модель `Subscription` + Alembic миграция (Stripe — stub)
13. ⬜ Gate premium features (сценарии, SR, pronunciation)
14. ✅ CI/CD: GitHub Actions (`.github/workflows/ci.yml` — lint, test, frontend-lint)
15. ⬜ Разделить контейнер на 3 сервиса
16. ✅ Error boundary во frontend (`ErrorBoundary.tsx` + обёртка dashboard)
17. ✅ `<html lang="cs">` (было `en`) + ARIA labels на навигацию

### 📋 Бэклог
18. ✅ Фикс N+1 queries (grammar progress — `joinedload`, weak_rules — `joinedload`)
19. ✅ Redis для sessions/games/scenarios (полная миграция с TTL)
20. ✅ Добавлены тесты: 7 новых test files (~30%+ coverage)
21. ✅ Accessibility: ARIA labels на nav, main, links (`aria-label`, `role`, `aria-current`)
22. ✅ Sentry monitoring (`sentry-sdk[fastapi]` + lifespan init)
23. ✅ In-memory state (games, scenarios) полностью в Redis (`game:active:{uid}`, `scenario:active:{uid}`)
24. ✅ OpenAI: `@lru_cache` на system prompt, dead code удалён (MODEL_PRICING, TOKEN_LIMITS, get_optimal_model), пустая история пропускается

### 🟣 Система персонажей + Оптимизация Honzíka (20 февраля 2026)
25. ✅ **Новый персонаж: paní Nováková** — профессиональная урёдница, выкание, spisovná čeština, помощь с документами/урядами
    - `honzik_personality.py` рефакторинг: система персонажей через параметр `character`
    - DB: столбец `character` в `user_settings` (migration `20260220_add_character`)
    - Schema: `UserSettingsUpdate` / `UserSettingsResponse` + `character` field
    - TTS: `honzik` → `alloy` (male), `novakova` → `nova` (female)
    - Frontend: выбор персонажа в Nastavení → tab Učení
26. ✅ **Расширение контекста Honzíka** — вместо только пива/колбасок теперь:
    - 🏠 Прага и чешские города, 🎭 культура и музыка, ⚽ спорт, 🌍 путешествия, 💼 работа, 🚇 транспорт, 🛝 быт
27. ✅ **Оптимизация скорости ответов:**
    - Удалён `optimize_conversation_history` (экономия ~100-200ms/запрос)
    - Компактные промпты (~350 tokens вместо ~600) → быстрее на ~0.5-1s
    - `lru_cache(maxsize=128)` (было 64) для 2 персонажей
    - `web_lessons.py`: исправлен OpenAI singleton (было `OpenAIClient()` без settings)
    - Расширена карта `native_lang_names` на 40+ языков
    - `character` добавлен в ключ кэша (нет cross-contamination между персонажами)

---

## 15. Стратегия монетизации — детальный план

> **Дата добавления:** 21 февраля 2026  
> **Контекст:** Продукт feature-complete, $0 revenue, расходы ~$20-30/день при 100 активных пользователях.

### 15.1 Почему нужно монетизировать сейчас

| Метрика | Значение |
|---|---|
| Расход OpenAI на 1 активного пользователя | ~$0.50/день ($15/мес) |
| Расход при 100 пользователях | ~$600-900/мес |
| Расход при 500 пользователях | ~$3,000-4,500/мес |
| Текущий доход | **$0** |

Каждый новый пользователь **увеличивает убытки**. Без монетизации рост = банкротство.

---

### 15.2 Модель Freemium — три уровня

#### 🆓 Free (конверсионная воронка)
| Функция | Лимит |
|---|---|
| Текстовые сообщения с Honzíkem | **5/день** |
| Голосовые сообщения (STT + TTS) | **2/день** |
| Сценарии | 1 бесплатный (ротация каждую неделю) |
| Мини-игры | 3 раунда/день |
| Spaced repetition | Только просмотр (без добавления) |
| Грамматика | Только 3 базовых правила |
| Pronunciation analyzer | ❌ |
| Exam prep | ❌ |
| Podcasts / Stories | ❌ |
| Персонаж | Только Honzík |

**Цель:** Дать попробовать ценность, но создать конверсионное давление через лимиты.

#### ⭐ Pro — $7.99/мес (или 500 Telegram Stars/мес)
| Функция | Лимит |
|---|---|
| Текстовые сообщения | **50/день** |
| Голосовые сообщения | **20/день** |
| Сценарии | Все 8 |
| Мини-игры | Безлимит |
| Spaced repetition | Полный доступ |
| Грамматика | Все правила + детальный разбор |
| Pronunciation analyzer | ❌ |
| Exam prep | ❌ |
| Персонажи | Honzík + paní Nováková |
| Приоритетная скорость ответа | ✅ (GPT-4o вместо mini) |

#### 💎 Expert — $14.99/мес (или 950 Telegram Stars/мес)
| Функция | Лимит |
|---|---|
| Все функции Pro | ✅ |
| Сообщения | **Безлимит** |
| Pronunciation analyzer | ✅ |
| Exam prep (B1/B2 тренажёр) | ✅ |
| Podcasts & Story generator | ✅ |
| Эксклюзивные сценарии | ✅ (новые каждый месяц) |
| Персональная статистика + отчёты | ✅ |
| Приоритетная поддержка | ✅ |

---

### 15.3 Микроплатежи через Telegram Stars (быстрый старт)

Telegram Stars — **самый быстрый** путь к первому доходу (без Stripe, KYC, банковских счетов).

| Пакет | Цена (Stars) | Цена (~USD) | Содержание |
|---|---|---|---|
| 🗣️ +10 голосовых | 50⭐ | ~$0.75 | 10 доп. голосовых сообщений |
| 📝 +20 текстовых | 30⭐ | ~$0.45 | 20 доп. текстовых сообщений |
| 🎭 Разблокировать сценарий | 100⭐ | ~$1.50 | Доступ к 1 сценарию навсегда |
| ⏰ 7 дней безлимит | 200⭐ | ~$3.00 | Неделя Pro-функций |
| 📅 30 дней безлимит | 500⭐ | ~$7.50 | Месяц Pro-функций |
| 💎 30 дней Expert | 950⭐ | ~$14.25 | Месяц Expert-функций |

**Реализация:**
1. Middleware `check_message_limit()` — проверяет лимит перед каждым AI-запросом
2. При достижении лимита → inline keyboard с пакетами
3. `pre_checkout_query` handler в aiogram для подтверждения
4. `successful_payment` handler → обновление лимитов в DB
5. Таблица `payments` + `user_quotas` в PostgreSQL

---

### 15.4 Подписки через Stripe (web)

| Шаг | Действие | Срок |
|---|---|---|
| 1 | Модель `Subscription` (user_id, plan, status, stripe_id, expires_at) | 1 день |
| 2 | Alembic миграция + seed | 0.5 дня |
| 3 | `POST /api/checkout` → Stripe Checkout Session | 1 день |
| 4 | Webhook `/api/stripe/webhook` (payment_intent.succeeded, subscription.deleted) | 1 день |
| 5 | Middleware `require_subscription(plan="pro")` dependency | 0.5 дня |
| 6 | Customer portal для отмены/смены плана | 0.5 дня |
| 7 | Frontend: страница Pricing + кнопки в UI при достижении лимита | 1 день |

**Итого:** ~5-6 рабочих дней для полной интеграции.

---

### 15.5 Дополнительные источники дохода

#### B2B — продажа школам и курсам чешского языка
| Предложение | Цена | Аудитория |
|---|---|---|
| Школьная лицензия (до 30 студентов) | $49/мес | Языковые школы в ЧР |
| Dashboard для учителя (прогресс студентов) | +$19/мес | Репетиторы |
| White-label бот (бренд школы) | $199/мес | Крупные школы/сети |

**Почему это работает:**
- В ЧР ~500 языковых школ для иностранцев
- Учителя могут использовать бота как домашнее задание
- Школы готовы платить за инструменты, которые удерживают студентов

#### Партнёрства
| Партнёр | Модель |
|---|---|
| Языковые школы (Glossa, Czech Courses) | Реферальная комиссия 20% |
| Миграционные агентства | Пакет "подготовка к экзамену B1" |
| Чешские bank/telco | Onboarding-бот для иностранных клиентов |

#### Контент-монетизация
| Продукт | Цена | Описание |
|---|---|---|
| PDF-пак "100 диалогов для B1" | $4.99 | Генерируется AI, cursored |
| Аудиокурс "Čeština za 30 dní" | $9.99 | TTS + scenarios |
| Набор карточек Anki (export из SR) | $2.99 | Из saved_words пользователя |

---

### 15.6 Прогноз дохода — обновлённый

| Метрика | Месяц 1 | Месяц 3 | Месяц 6 | Месяц 12 |
|---|---|---|---|---|
| Всего пользователей | 500 | 2,000 | 5,000 | 15,000 |
| Free | 475 (95%) | 1,800 (90%) | 4,250 (85%) | 12,000 (80%) |
| Pro ($7.99) | 20 (4%) | 160 (8%) | 600 (12%) | 2,250 (15%) |
| Expert ($14.99) | 5 (1%) | 40 (2%) | 150 (3%) | 750 (5%) |
| MRR подписки | $235 | $1,878 | $7,039 | $29,243 |
| Telegram Stars | $50 | $400 | $1,200 | $3,000 |
| B2B | $0 | $0 | $500 | $2,000 |
| **Итого MRR** | **$285** | **$2,278** | **$8,739** | **$34,243** |
| Расходы OpenAI | -$150 | -$1,200 | -$4,500 | -$13,500 |
| Расходы инфра | -$30 | -$50 | -$100 | -$200 |
| **Чистая прибыль** | **$105** | **$1,028** | **$4,139** | **$20,543** |

### 15.7 Ключевые метрики для отслеживания

| Метрика | Цель |
|---|---|
| **DAU / MAU ratio** | >20% (здоровый engagement) |
| **Free → Pro конверсия** | >5% к месяцу 3 |
| **Churn rate** (Pro) | <8%/мес |
| **LTV** (Pro пользователь) | >$60 (удержание >7 мес) |
| **CAC** (стоимость привлечения) | <$5 через реферальную программу |
| **ARPU** (средний доход на пользователя) | >$1.50 к месяцу 6 |
| **Payback period** | <30 дней |

---

## 16. Масштабирование при высокой нагрузке (100+ одновременных пользователей)

> **Дата добавления:** 21 февраля 2026  
> **Контекст:** Текущая архитектура — 1 контейнер Railway, все сервисы в одном процессе.

### 16.1 Текущие узкие места

```
┌─────────────────────────────────────────────┐
│           Railway (1 контейнер)              │
│  ┌─────────┐ ┌──────┐ ┌────────┐ ┌───────┐ │
│  │ FastAPI  │ │ Bot  │ │ Celery │ │ Beat  │ │
│  │ :8000   │ │ poll │ │ worker │ │ sched │ │
│  └─────────┘ └──────┘ └────────┘ └───────┘ │
│               ↕ shared RAM                   │
│             1 CPU / 512MB-1GB                │
└─────────────────────────────────────────────┘
         ↓               ↓
   ┌──────────┐    ┌──────────┐
   │ PostgreSQL│    │  Redis   │
   └──────────┘    └──────────┘
```

| Узкое место | Почему критично при 100+ пользователях |
|---|---|
| **Один контейнер** | Crash любого компонента убивает ВСЁ |
| **1 Celery worker (concurrency=2)** | Очередь задач (daily_stats, reviews) блокируется |
| **OpenAI rate limits** | 100 одновременных запросов → 429 ошибки GPT |
| **PostgreSQL connections** | По умолчанию pool_size=5 (SQLAlchemy) → connection starvation |
| **Один процесс FastAPI** | uvicorn single worker → ~50-100 req/s max |
| **Bot polling** | Один aiogram поллер → медленная обработка при всплеске |
| **Нет очередей для AI** | AI-запросы блокируют event loop на 2-5 секунд |

---

### 16.2 Этап 1 — Быстрые победы (100-300 пользователей) ✅ РЕАЛИЗОВАНО

Без изменения архитектуры, реализовано 22 февраля 2026:

#### 1. Uvicorn workers ✅
```python
# Procfile
web: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```
Вместо 1 worker → 4. Каждый worker обрабатывает ~50-100 req/s. **Итого: ~200-400 req/s.**

#### 2. PostgreSQL connection pool ✅
```python
# backend/db/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # было 5
    max_overflow=30,       # было 10
    pool_timeout=30,
    pool_recycle=1800,     # переподключение каждые 30 мин
    pool_pre_ping=True,    # проверка живых соединений
)
```

#### 3. Redis connection pooling ✅
```python
# backend/cache/redis_client.py
pool = redis.ConnectionPool(
    max_connections=50,    # было default=10
    decode_responses=True,
    socket_timeout=5,
    retry_on_timeout=True,
)
```

#### 4. OpenAI защита от перегрузки ✅

**Реализовано два механизма:**

**a) `OpenAIConcurrencyLimiter`** (`backend/utils/rate_limiter.py`) — asyncio.Semaphore:
- Chat запросы: max 10 одновременных
- TTS запросы: max 8 одновременных
- STT запросы: max 8 одновременных
- Статистика в `/health` endpoint

**b) Celery AI tasks** (`backend/tasks/ai_tasks.py`) — очередь для фоновых задач:
```python
Rate limit `30/m` = защита от 429 ошибок OpenAI.

#### 5. Кэширование ответов ✅
```python
# Кэшировать частые паттерны (приветствия, команды)
COMMON_RESPONSES_TTL = 3600  # 1 час
# Кэшировать грамматические правила
GRAMMAR_RULES_TTL = 86400    # 24 часа
# Кэшировать TTS аудио (увеличить лимит)
MAX_TTS_CACHE_LENGTH = 500   # было 200
TTS_CACHE_TTL = 604800       # 7 дней
```

---

### 16.3 Этап 2 — Разделение сервисов (300-1,000 пользователей)

Разделить монолит на 3-4 отдельных сервиса Railway:

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Backend    │  │  Telegram    │  │   Celery     │  │   Frontend   │
│   FastAPI    │  │    Bot       │  │   Workers    │  │   Next.js    │
│   4 workers  │  │  aiogram 3   │  │  concur=4    │  │   (SSR/CDN)  │
│   :8000      │  │  polling     │  │  + beat      │  │   :3000      │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────────────┘
       │                 │                 │
       ▼                 ▼                 ▼
  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │ PostgreSQL│◄───│  Redis   │────►│  Redis   │
  │ (shared) │     │ (cache)  │     │ (broker) │
  └──────────┘     └──────────┘     └──────────┘
```

| Сервис | Railway план | Ресурсы | Стоимость |
|---|---|---|---|
| Backend (FastAPI) | Pro | 1 vCPU / 1GB | ~$10/мес |
| Bot (aiogram) | Pro | 0.5 vCPU / 512MB | ~$5/мес |
| Celery workers | Pro | 1 vCPU / 1GB | ~$10/мес |
| Frontend (Next.js) | Pro или Vercel Free | — | $0-20/мес |
| PostgreSQL | Railway Plugin | 1GB | ~$5/мес |
| Redis | Railway Plugin | 256MB | ~$5/мес |
| **Итого** | | | **~$35-55/мес** |

**Преимущества:**
- Crash Celery ≠ crash API
- Независимое масштабирование (больше Celery workers для AI-задач)
- Бот работает даже при перегрузке API
- Frontend можно вынести на Vercel (бесплатный CDN, edge functions)

---

### 16.4 Этап 3 — Полное масштабирование (1,000-10,000 пользователей)

#### Архитектура

```
                    ┌─────────────┐
                    │ Cloudflare  │
                    │   CDN/WAF   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Backend  │ │ Backend  │ │ Backend  │
        │ replica 1│ │ replica 2│ │ replica 3│
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │             │             │
        ┌────▼─────────────▼─────────────▼────┐
        │         PostgreSQL (primary)         │
        │    + read replica for analytics      │
        └─────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
  ┌──────────┐      ┌──────────┐       ┌──────────┐
  │ Celery   │      │ Celery   │       │ Redis    │
  │ AI tasks │      │ cron     │       │ Cluster  │
  │ workers=8│      │ beat     │       │ 3 nodes  │
  └──────────┘      └──────────┘       └──────────┘
```

#### Ключевые решения

| Компонент | Решение | Зачем |
|---|---|---|
| **Load Balancer** | Cloudflare / Railway LB | Распределение между backend replicas |
| **DB Read Replica** | PostgreSQL streaming replication | Аналитика и leaderboard не нагружают primary |
| **AI Queue** | Celery с приоритетами (Pro > Free) | Pro-пользователи не ждут в общей очереди |
| **Redis Cluster** | 3 ноды (cache + sessions + broker) | Разделение нагрузки кэша и Celery |
| **CDN** | Cloudflare / Vercel Edge | Статика (JS, CSS, аватары) ближе к пользователю |
| **Bot sharding** | aiogram webhook (вместо polling) | Webhook масштабируется через LB, polling — нет |
| **Connection pooling** | PgBouncer | 1000+ соединений без перегрузки PostgreSQL |

#### Переход на Webhook (бот)

```python
# Вместо polling:
# dp.start_polling(bot)

# Webhook через FastAPI:
@app.post("/webhook/telegram")
async def telegram_webhook(update: dict):
    telegram_update = Update(**update)
    await dp.feed_update(bot, telegram_update)
```

**Преимущества webhook vs polling:**
- Polling: 1 процесс тянет обновления → bottleneck
- Webhook: Telegram пушит обновления на URL → масштабируется горизонтально
- Latency: webhook ~10ms vs polling ~1-2s

#### Приоритетные очереди для AI

```python
# celery_app.py
celery_app.conf.task_routes = {
    'tasks.ai_response_pro': {'queue': 'ai_priority'},
    'tasks.ai_response_free': {'queue': 'ai_default'},
    'tasks.tts_generate': {'queue': 'tts'},
    'tasks.stt_transcribe': {'queue': 'stt'},
}

# Запуск workers с разными очередями:
# celery -A tasks worker -Q ai_priority -c 4   (для Pro)
# celery -A tasks worker -Q ai_default -c 2    (для Free)
# celery -A tasks worker -Q tts,stt -c 3       (для медиа)
```

---

### 16.5 Оптимизация OpenAI при масштабе

| Проблема | Решение |
|---|---|
| **Rate limits** (Tier 1: 60 RPM) | Подать на Tier 2+ (500 RPM), или batch API |
| **Стоимость GPT-4o** | Free → 100% mini, Pro → 70% mini / 30% 4o, Expert → 100% 4o |
| **Долгие ответы** | Streaming (`stream=True`) → пользователь видит ответ сразу |
| **Одинаковые промпты** | Semantic cache: хешировать embeddings вопросов, при cosine>0.95 → кэш |
| **TTS расходы** | Кэшировать аудио в S3/R2 по hash текста (TTL=30 дней) |
| **Whisper** | Пре-валидация: отклонять тишину/шум (<1s аудио) до отправки в API |

#### Оценка расходов OpenAI при масштабе

| Пользователи (DAU) | Сообщений/день | GPT-4o-mini | GPT-4o | TTS | STT | **Итого/день** | **Итого/мес** |
|---|---|---|---|---|---|---|---|
| 100 | 1,000 | $3 | $9 | $15 | $6 | **$33** | **$990** |
| 500 | 5,000 | $15 | $45 | $75 | $30 | **$165** | **$4,950** |
| 1,000 | 10,000 | $30 | $90 | $150 | $60 | **$330** | **$9,900** |
| 5,000 | 50,000 | $150 | $450 | $750 | $300 | **$1,650** | **$49,500** |

> **Вывод:** При 1,000+ DAU обязательно: (1) агрессивное кэширование TTS, (2) Free на 100% mini, (3) semantic cache для повторяющихся вопросов.

---

### 16.6 Мониторинг и алерты при масштабе

| Что мониторить | Инструмент | Порог алерта |
|---|---|---|
| Response time (p95) | Sentry Performance | >3s |
| Error rate | Sentry | >1% |
| PostgreSQL connections | pg_stat_activity | >80% pool |
| Redis memory | Redis INFO | >80% maxmemory |
| Celery queue length | Flower / Prometheus | >100 tasks pending |
| OpenAI 429 errors | Sentry + custom counter | >5/мин |
| Bot message latency | Custom metric | >5s avg |
| CPU / RAM | Railway Metrics | >85% |
| API uptime | UptimeRobot / BetterStack | <99.5% |

---

### 16.7 Чек-лист масштабирования по этапам

| Пользователи | Действия | Приоритет |
|---|---|---|
| **50-100** | ✅ Redis для state, ✅ connection pool, ✅ uvicorn 4 workers | ✅ |
| **100-300** | ✅ OpenAI concurrency limiter, ✅ TTS cache расширен, ✅ Celery AI tasks, webhook бота | ✅ |
| **300-1,000** | Разделить на 3 сервиса, PgBouncer, Celery workers=4+, CDN | ⬜ |
| **1,000-5,000** | Replicas backend (2-3), DB read replica, Redis cluster, приоритетные очереди | ⬜ |
| **5,000-10,000** | Kubernetes / Railway Pro, auto-scaling, semantic AI cache, S3 для медиа | ⬜ |
| **10,000+** | Dedicated OpenAI tier, региональные деплои, микросервисы | ⬜ |
