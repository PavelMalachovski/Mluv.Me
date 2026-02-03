# 🔧 Рефакторинг и улучшения Mluv.Me

> **Дата анализа:** Февраль 2026
> **Версия проекта:** 1.0.0
> **Автор:** AI Code Analysis

---

## 📊 Обзор текущего состояния

### Архитектура
```
mluv-me/
├── backend/          # FastAPI + SQLAlchemy
├── bot/             # aiogram 3.x Telegram Bot
├── frontend/        # Next.js PWA
├── tests/           # Pytest
└── alembic/         # Миграции БД
```

### Сильные стороны ✅
1. **Clean Architecture** — Чёткое разделение на слои (routers → services → repositories → models)
2. **Async/Await** — Полностью асинхронный backend
3. **Redis Caching** — Кеширование частых запросов
4. **Repository Pattern** — Абстракция доступа к данным
5. **Type Hints** — Все функции типизированы
6. **Structured Logging** — structlog с JSON форматом
7. **Параллельная обработка** — TTS генерируется параллельно с DB операциями

### Слабые места ⚠️
1. **Frontend не оптимизирован** — Нет Server Components в критических местах
2. **Нет очереди задач** — Celery tasks не используются активно
3. **Rate limiting неполный** — Только базовая защита
4. **Монетизация не реализована** — Нет подписок и ограничений
5. **Нет A/B тестирования** — Промпты Хонзика фиксированы

---

## 🚀 УЛУЧШЕНИЯ ПРОИЗВОДИТЕЛЬНОСТИ

### 1. Backend Performance

#### 1.1 Оптимизация обработки голосовых (Критично!)

**Текущее состояние:**
```python
# backend/routers/lesson.py - линейный pipeline
# STT → LLM → TTS (последовательно по частям)
```

**Рекомендация:** Полная параллелизация с streaming

```python
# backend/routers/lesson_optimized.py
import asyncio
from fastapi import BackgroundTasks

@router.post("/process/v2")
async def process_voice_optimized(
    user_id: int = Form(...),
    audio: UploadFile = File(...),
    background_tasks: BackgroundTasks,
):
    """
    Оптимизированный pipeline:
    1. STT (обязательно первый)
    2. ПАРАЛЛЕЛЬНО: LLM анализ + начало TTS потока
    3. Background: сохранение в БД, статистика
    """
    # Шаг 1: STT
    transcript_result = await openai_client.transcribe_audio_with_detection(audio)

    # Шаг 2: Параллельный запуск
    llm_task = asyncio.create_task(
        honzik.generate_response_streaming(transcript_result["text"], ...)
    )

    # Подготовка кеша для быстрого ответа
    cached_response = await cache_service.get_cached_response(
        transcript_result["text"], user.level
    )

    if cached_response:
        # Мгновенный ответ из кеша!
        background_tasks.add_task(update_stats_and_save, user_id, ...)
        return cached_response

    # Ждём LLM
    llm_response = await llm_task

    # TTS запускаем СРАЗУ как получили текст ответа
    tts_task = asyncio.create_task(
        openai_client.generate_speech(llm_response["honzik_response"])
    )

    # Background задачи (не блокируют ответ!)
    background_tasks.add_task(save_message_and_stats, user_id, llm_response)
    background_tasks.add_task(check_achievements, user_id)
    background_tasks.add_task(cache_response_if_common, transcript_result["text"], llm_response)

    audio_response = await tts_task

    return LessonProcessResponse(...)
```

**Ожидаемое ускорение:** 1.5-2x (с 4-6 сек до 2-4 сек)

---

#### 1.2 Добавить Streaming TTS Response

**Текущее состояние:** Ожидание полной генерации TTS перед отправкой

**Рекомендация:** Streaming response для ощущения мгновенного ответа

```python
# backend/routers/lesson.py
from fastapi.responses import StreamingResponse

@router.post("/process/stream")
async def process_voice_stream(
    user_id: int = Form(...),
    audio: UploadFile = File(...),
):
    """Streaming endpoint для низкой latency."""

    async def generate_stream():
        # 1. Сразу отправляем статус
        yield json.dumps({"status": "transcribing"}).encode() + b"\n"

        transcript = await openai_client.transcribe_audio(audio)
        yield json.dumps({"status": "analyzing", "transcript": transcript}).encode() + b"\n"

        # 2. LLM ответ
        response = await honzik.generate_response(transcript, ...)
        yield json.dumps({
            "status": "speaking",
            "text": response["honzik_response"],
            "corrections": response["mistakes"]
        }).encode() + b"\n"

        # 3. TTS (можно отправлять чанками)
        audio_bytes = await openai_client.generate_speech(response["honzik_response"])
        yield json.dumps({
            "status": "complete",
            "audio": base64.b64encode(audio_bytes).decode()
        }).encode() + b"\n"

    return StreamingResponse(generate_stream(), media_type="application/x-ndjson")
```

---

#### 1.3 Умный выбор модели GPT

**Текущее состояние:**
```python
# Выбор модели только по уровню пользователя
if czech_level in ["beginner", "intermediate"]:
    return "gpt-4o-mini"  # 2x быстрее
```

**Рекомендация:** Адаптивный выбор по сложности запроса

```python
# backend/services/model_selector.py
class AdaptiveModelSelector:
    """Умный выбор модели для баланса цена/качество/скорость."""

    # Паттерны для быстрого ответа (gpt-4o-mini)
    SIMPLE_PATTERNS = [
        r"^(ahoj|nazdar|čau|dobr[ýé])",  # Приветствия
        r"^(ano|ne|možná|nevím)$",        # Простые ответы
        r"^(děkuj|díky|prosím)",          # Вежливость
    ]

    # Паттерны для полного анализа (gpt-4o)
    COMPLEX_PATTERNS = [
        r"\?.*\?",                          # Много вопросов
        r"\b(proč|jak|kdy|kde|kdo)\b.*\b(proč|jak|kdy|kde|kdo)\b",  # Сложные вопросы
    ]

    def select_model(
        self,
        user_text: str,
        czech_level: str,
        corrections_level: str,
        history_length: int,
    ) -> tuple[str, str]:
        """
        Возвращает (model_name, reasoning).

        Стратегия:
        1. Приветствия/простые фразы → gpt-4o-mini (50ms экономия)
        2. detailed corrections → gpt-4o (лучший анализ)
        3. native level → gpt-4o (сложнее ошибки)
        4. Длинный текст (>100 слов) → gpt-4o
        5. По умолчанию → gpt-4o-mini
        """
        text_lower = user_text.lower().strip()
        word_count = len(text_lower.split())

        # Простые фразы - всегда mini
        for pattern in self.SIMPLE_PATTERNS:
            if re.match(pattern, text_lower):
                return "gpt-4o-mini", "simple_greeting"

        # Сложные случаи - полная модель
        if corrections_level == "detailed":
            return "gpt-4o", "detailed_corrections"

        if czech_level == "native":
            return "gpt-4o", "native_level"

        if word_count > 100:
            return "gpt-4o", "long_text"

        for pattern in self.COMPLEX_PATTERNS:
            if re.search(pattern, text_lower):
                return "gpt-4o", "complex_question"

        # По умолчанию - быстрая модель
        return "gpt-4o-mini", "default_fast"

# Использование
model, reason = model_selector.select_model(transcript, user.level, ...)
logger.info("model_selected", model=model, reason=reason)
response = await openai_client.generate_chat_completion(..., model=model)
```

**Ожидаемая экономия:** 30-40% стоимости OpenAI API

---

#### 1.4 Connection Pooling для PostgreSQL

**Текущее состояние:**
```python
# backend/db/database.py - базовый async engine
engine = create_async_engine(DATABASE_URL)
```

**Рекомендация:** Настроить pool с оптимальными параметрами

```python
# backend/db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import AsyncAdaptedQueuePool

def create_optimized_engine(database_url: str):
    """Создать engine с оптимизированным пулом соединений."""
    return create_async_engine(
        database_url,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=10,              # Базовое количество соединений
        max_overflow=20,           # Дополнительные при пиковой нагрузке
        pool_timeout=30,           # Таймаут ожидания соединения
        pool_recycle=1800,         # Пересоздание соединений каждые 30 мин
        pool_pre_ping=True,        # Проверка соединения перед использованием
        echo=settings.is_development,  # SQL логи в dev режиме
        connect_args={
            "server_settings": {
                "application_name": "mluv-me-api",
                "statement_timeout": "30000",  # 30 сек таймаут запросов
            }
        }
    )
```

---

#### 1.5 Расширенное кеширование

**Текущее состояние:** Кешируются только common phrases и первые приветствия

**Рекомендация:** Многоуровневое кеширование

```python
# backend/services/cache_service_v2.py
class EnhancedCacheService:
    """Многоуровневое кеширование для максимальной производительности."""

    # Уровни кеша с разным TTL
    CACHE_TIERS = {
        "common_phrases": 604800,      # 7 дней - приветствия
        "frequent_errors": 86400,       # 1 день - частые ошибки
        "user_preferences": 3600,       # 1 час - настройки
        "tts_audio": 2592000,           # 30 дней - аудио фразы
        "translation": 604800,          # 7 дней - переводы слов
    }

    # Добавить кеширование TTS для частых фраз
    async def get_or_generate_tts(
        self,
        text: str,
        voice: str,
        speed: float,
    ) -> bytes:
        """Кешировать TTS для популярных фраз Хонзика."""
        cache_key = f"tts:{hashlib.md5(text.encode()).hexdigest()[:16]}:{voice}:{speed}"

        cached_audio = await redis_client.get_bytes(cache_key)
        if cached_audio:
            logger.info("tts_cache_hit", text_preview=text[:30])
            return cached_audio

        # Генерируем и кешируем
        audio = await openai_client.generate_speech(text, voice, speed)

        if len(text) < 200:  # Кешируем только короткие фразы
            await redis_client.set_bytes(
                cache_key,
                audio,
                ttl=self.CACHE_TIERS["tts_audio"]
            )
            logger.info("tts_cached", text_preview=text[:30])

        return audio

    # Кеширование переводов слов
    async def get_or_translate_word(
        self,
        word: str,
        target_lang: str,
    ) -> dict:
        """Кешировать переводы часто запрашиваемых слов."""
        cache_key = f"translate:{word.lower()}:{target_lang}"

        cached = await redis_client.get(cache_key)
        if cached:
            return cached

        translation = await translation_service.translate(word, target_lang)

        await redis_client.set(
            cache_key,
            translation,
            ttl=self.CACHE_TIERS["translation"]
        )

        return translation
```

**Ожидаемое ускорение повторных запросов:** 10-100x

---

### 2. Frontend Performance

#### 2.1 Server Components для Dashboard

**Текущее состояние:**
```tsx
// frontend/app/dashboard/page.tsx - Client Component
"use client"
// Всё загружается на клиенте
```

**Рекомендация:** Использовать React Server Components

```tsx
// frontend/app/dashboard/page.tsx - Server Component (NEW)
import { Suspense } from 'react'
import { cookies } from 'next/headers'
import { StatsSection } from './components/StatsSection'
import { QuickActions } from './components/QuickActions'
import { AchievementsPreview } from './components/AchievementsPreview'

// Серверный компонент - данные загружаются на сервере
export default async function DashboardPage() {
  const token = cookies().get('auth_token')?.value

  // Предзагрузка данных на сервере (без waterfalls!)
  const [user, stats] = await Promise.all([
    fetch(`${API_URL}/api/v1/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
      next: { revalidate: 60 }  // ISR - обновление каждую минуту
    }).then(r => r.json()),

    fetch(`${API_URL}/api/v1/stats/summary`, {
      headers: { Authorization: `Bearer ${token}` },
      next: { revalidate: 30 }  // Статистика обновляется чаще
    }).then(r => r.json()),
  ])

  return (
    <div className="min-h-screen cream-bg landscape-bg pb-24">
      {/* Статика - рендерится сразу */}
      <IllustratedHeader title="Dashboard" />

      <div className="mx-auto max-w-2xl px-4 pt-6">
        <WelcomeMessage userName={user.first_name} />

        {/* Streamed component - появляется по мере загрузки */}
        <Suspense fallback={<StatsSkeletons />}>
          <StatsSection userId={user.id} initialStats={stats} />
        </Suspense>

        <QuickActions />

        <Suspense fallback={<AchievementsSkeleton />}>
          <AchievementsPreview userId={user.id} />
        </Suspense>
      </div>
    </div>
  )
}
```

**Ожидаемое улучшение:**
- First Contentful Paint: -40%
- Time to Interactive: -30%

---

#### 2.2 Optimistic Updates для UI

**Текущее состояние:** Ожидание ответа сервера перед обновлением UI

**Рекомендация:** Optimistic updates с react-query

```tsx
// frontend/lib/hooks/useVoiceMutation.ts
import { useMutation, useQueryClient } from '@tanstack/react-query'

export function useVoiceMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (audioBlob: Blob) => apiClient.processVoice(userId, audioBlob),

    // Optimistic update - мгновенно показываем что сообщение отправлено
    onMutate: async (audioBlob) => {
      // Отменяем исходящие запросы
      await queryClient.cancelQueries({ queryKey: ['conversation'] })

      // Сохраняем текущее состояние для отката
      const previousConversation = queryClient.getQueryData(['conversation'])

      // Optimistic: добавляем сообщение с пометкой "sending"
      queryClient.setQueryData(['conversation'], (old: Message[]) => [
        ...old,
        {
          id: `temp-${Date.now()}`,
          role: 'user',
          status: 'sending',
          text: '🎤 Обрабатывается...',
        }
      ])

      return { previousConversation }
    },

    onSuccess: (data, _variables, context) => {
      // Заменяем temp сообщение на реальное
      queryClient.setQueryData(['conversation'], (old: Message[]) => [
        ...old.filter(m => !m.id.startsWith('temp-')),
        {
          id: data.message_id,
          role: 'user',
          text: data.transcript,
          response: data,
          status: 'sent',
        },
        {
          id: `assistant-${data.message_id}`,
          role: 'assistant',
          text: data.honzik_response_text,
          status: 'sent',
        }
      ])

      // Обновляем статистику
      queryClient.invalidateQueries({ queryKey: ['user-stats'] })
    },

    onError: (_error, _variables, context) => {
      // Откатываем при ошибке
      if (context?.previousConversation) {
        queryClient.setQueryData(['conversation'], context.previousConversation)
      }
    },
  })
}
```

---

#### 2.3 Prefetching и Code Splitting

**Рекомендация:** Prefetch популярных маршрутов

```tsx
// frontend/app/dashboard/layout.tsx
import { prefetch } from 'next/navigation'

export default function DashboardLayout({ children }) {
  return (
    <>
      {/* Prefetch популярных страниц при загрузке dashboard */}
      <PrefetchLinks />
      <Navigation />
      {children}
    </>
  )
}

function PrefetchLinks() {
  // Prefetch при hover
  return (
    <>
      <link rel="prefetch" href="/dashboard/practice" />
      <link rel="prefetch" href="/dashboard/review" />
      <link rel="prefetch" href="/dashboard/saved" />
    </>
  )
}

// Динамический импорт тяжёлых компонентов
const VoiceRecorder = dynamic(
  () => import('@/components/ui/VoiceRecorder'),
  {
    ssr: false,
    loading: () => <VoiceRecorderSkeleton />
  }
)

const ProgressChart = dynamic(
  () => import('@/components/features/ProgressChart'),
  {
    ssr: false,
    loading: () => <ChartSkeleton />
  }
)
```

---

## 🎮 УЛУЧШЕНИЯ ГЕЙМИФИКАЦИИ

### 1. Расширенная система достижений

**Текущее состояние:**
```python
# backend/services/achievement_service.py
# Только базовые категории: streak, messages, vocabulary, accuracy, stars, review
```

**Рекомендация:** Добавить тематические и социальные достижения

```python
# backend/services/achievement_service_v2.py
from enum import Enum

class AchievementType(str, Enum):
    """Типы достижений."""
    # Прогресс
    STREAK = "streak"
    MESSAGES = "messages"
    VOCABULARY = "vocabulary"

    # Тематические
    BEER_MASTER = "beer_master"        # 10 разговоров о пиве 🍺
    CZECH_HISTORY = "czech_history"    # 5 разговоров об истории 🏰
    FOODIE = "foodie"                  # 10 разговоров о еде 🥟
    TRAVELER = "traveler"              # 5 разговоров о путешествиях ✈️

    # Качество
    PERFECTIONIST = "perfectionist"    # 5 сообщений подряд >90%
    IMPROVER = "improver"              # Улучшение score на 20% за неделю

    # Время
    EARLY_BIRD = "early_bird"          # Практика до 7 утра
    NIGHT_OWL = "night_owl"            # Практика после 23:00
    WEEKEND_WARRIOR = "weekend_warrior" # Оба дня выходных

    # Социальные
    REFERRAL = "referral"              # Пригласил друга
    HELPER = "helper"                  # Помог 3 новичкам

# Новые достижения для добавления в миграцию
NEW_ACHIEVEMENTS = [
    {
        "code": "beer_master",
        "name": "🍺 Pivař",
        "description": "Обсудил пиво с Хонзиком 10 раз",
        "icon": "🍺",
        "category": "thematic",
        "threshold": 10,
        "stars_reward": 25,
        "is_hidden": False,
    },
    {
        "code": "perfectionist_5",
        "name": "✨ Perfekcionista",
        "description": "5 сообщений подряд с оценкой >90%",
        "icon": "✨",
        "category": "quality",
        "threshold": 5,
        "stars_reward": 50,
        "is_hidden": True,  # Скрытое достижение!
    },
    {
        "code": "early_bird",
        "name": "🌅 Ranní ptáče",
        "description": "Практиковался до 7 утра",
        "icon": "🌅",
        "category": "time",
        "threshold": 1,
        "stars_reward": 10,
        "is_hidden": True,
    },
    {
        "code": "night_owl",
        "name": "🦉 Noční sova",
        "description": "Практиковался после 23:00",
        "icon": "🦉",
        "category": "time",
        "threshold": 1,
        "stars_reward": 10,
        "is_hidden": True,
    },
]

class EnhancedAchievementService:
    """Расширенный сервис достижений."""

    async def check_thematic_achievements(
        self,
        session: AsyncSession,
        user: User,
        message_text: str,
    ) -> list[dict]:
        """Проверить тематические достижения на основе содержания сообщения."""
        newly_unlocked = []

        # Определяем тему сообщения
        topics = self._detect_topics(message_text)

        for topic in topics:
            # Увеличиваем счётчик темы
            topic_key = f"topic_count:{user.id}:{topic}"
            count = await redis_client.incr(topic_key)

            # Проверяем порог
            achievement_code = f"{topic}_master"
            achievement = await self._get_achievement_by_code(session, achievement_code)

            if achievement and count == achievement.threshold:
                unlocked = await self._unlock_achievement(session, user, achievement)
                if unlocked:
                    newly_unlocked.append(unlocked)

        return newly_unlocked

    def _detect_topics(self, text: str) -> list[str]:
        """Определить темы в тексте."""
        text_lower = text.lower()
        topics = []

        TOPIC_KEYWORDS = {
            "beer": ["pivo", "plzeň", "hospoda", "pijte", "čepované"],
            "food": ["jídlo", "knedlík", "svíčková", "guláš", "restaurace"],
            "history": ["praha", "hrad", "karel", "historie", "středověk"],
            "travel": ["letadlo", "vlak", "cestování", "dovolená", "turista"],
        }

        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                topics.append(topic)

        return topics

    async def check_time_based_achievements(
        self,
        session: AsyncSession,
        user: User,
        message_time: datetime,
    ) -> list[dict]:
        """Проверить достижения, связанные со временем."""
        tz = ZoneInfo(user.settings.timezone or "Europe/Prague")
        local_time = message_time.astimezone(tz)
        hour = local_time.hour

        newly_unlocked = []

        # Early Bird: до 7 утра
        if hour < 7:
            achievement = await self._unlock_if_not_exists(
                session, user, "early_bird"
            )
            if achievement:
                newly_unlocked.append(achievement)

        # Night Owl: после 23:00
        if hour >= 23:
            achievement = await self._unlock_if_not_exists(
                session, user, "night_owl"
            )
            if achievement:
                newly_unlocked.append(achievement)

        return newly_unlocked
```

---

### 2. Ежедневные и еженедельные челленджи

**Рекомендация:** Добавить систему динамических челленджей

```python
# backend/services/challenge_service.py
from enum import Enum
from datetime import date, timedelta
import random

class ChallengeType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    SPECIAL = "special"

class ChallengeService:
    """Сервис для генерации и отслеживания челленджей."""

    # Шаблоны ежедневных челленджей
    DAILY_CHALLENGES = [
        {
            "id": "messages_5",
            "title_ru": "Поговори с Хонзиком",
            "title_uk": "Поговори з Хонзіком",
            "description_ru": "Отправь 5 голосовых сообщений",
            "description_uk": "Надішли 5 голосових повідомлень",
            "goal_type": "messages",
            "goal_value": 5,
            "reward_stars": 5,
        },
        {
            "id": "accuracy_80",
            "title_ru": "Говори правильно",
            "title_uk": "Говори правильно",
            "description_ru": "Получи оценку >80% в 3 сообщениях",
            "description_uk": "Отримай оцінку >80% у 3 повідомленнях",
            "goal_type": "high_accuracy_messages",
            "goal_value": 3,
            "reward_stars": 10,
        },
        {
            "id": "new_words_3",
            "title_ru": "Расширяй словарь",
            "title_uk": "Розширюй словник",
            "description_ru": "Сохрани 3 новых слова",
            "description_uk": "Збережи 3 нових слова",
            "goal_type": "saved_words",
            "goal_value": 3,
            "reward_stars": 8,
        },
        {
            "id": "topic_beer",
            "title_ru": "🍺 Поговори о пиве",
            "title_uk": "🍺 Поговори про пиво",
            "description_ru": "Обсуди пиво или чешские пабы",
            "description_uk": "Обговори пиво або чеські паби",
            "goal_type": "topic_message",
            "goal_topic": "beer",
            "goal_value": 1,
            "reward_stars": 5,
        },
    ]

    # Еженедельные челленджи (сложнее)
    WEEKLY_CHALLENGES = [
        {
            "id": "week_streak",
            "title_ru": "Неделя без пропусков",
            "title_uk": "Тиждень без пропусків",
            "description_ru": "Практикуйся 7 дней подряд",
            "description_uk": "Практикуйся 7 днів поспіль",
            "goal_type": "streak_days",
            "goal_value": 7,
            "reward_stars": 25,
        },
        {
            "id": "week_30_messages",
            "title_ru": "Активный ученик",
            "title_uk": "Активний учень",
            "description_ru": "Отправь 30 сообщений за неделю",
            "description_uk": "Надішли 30 повідомлень за тиждень",
            "goal_type": "weekly_messages",
            "goal_value": 30,
            "reward_stars": 30,
        },
    ]

    async def get_daily_challenge(
        self,
        user_id: int,
        user_date: date
    ) -> dict:
        """
        Получить ежедневный челлендж для пользователя.

        Челлендж генерируется детерминистически на основе user_id и даты,
        чтобы у одного пользователя был один челлендж в день.
        """
        # Детерминистический выбор челленджа
        seed = hash(f"{user_id}:{user_date}")
        random.seed(seed)
        challenge_template = random.choice(self.DAILY_CHALLENGES)

        # Получаем текущий прогресс
        progress = await self._get_challenge_progress(
            user_id,
            challenge_template["id"],
            user_date
        )

        return {
            **challenge_template,
            "progress": progress,
            "completed": progress >= challenge_template["goal_value"],
            "expires_at": (user_date + timedelta(days=1)).isoformat(),
        }

    async def update_challenge_progress(
        self,
        user_id: int,
        event_type: str,
        event_data: dict,
    ) -> dict | None:
        """
        Обновить прогресс челленджа.

        Возвращает информацию о награде если челлендж завершён.
        """
        today = date.today()
        challenge = await self.get_daily_challenge(user_id, today)

        if challenge["completed"]:
            return None  # Уже завершён

        # Проверяем соответствие события
        if not self._event_matches_challenge(event_type, event_data, challenge):
            return None

        # Увеличиваем прогресс
        new_progress = await self._increment_progress(
            user_id,
            challenge["id"],
            today
        )

        # Проверяем завершение
        if new_progress >= challenge["goal_value"]:
            # Начисляем награду
            await self._award_challenge_reward(user_id, challenge)
            return {
                "challenge_completed": True,
                "challenge_title": challenge[f"title_{user.ui_language}"],
                "stars_earned": challenge["reward_stars"],
            }

        return {
            "challenge_completed": False,
            "progress": new_progress,
            "goal": challenge["goal_value"],
        }
```

---

### 3. Лидерборд и социальные функции

```python
# backend/routers/leaderboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/leaderboard", tags=["leaderboard"])

@router.get("/weekly")
async def get_weekly_leaderboard(
    metric: str = "stars",  # stars, streak, messages
    limit: int = 10,
    db: AsyncSession = Depends(get_session),
):
    """
    Еженедельный лидерборд.

    Пользователи могут отключить отображение в настройках.
    """
    materialized_view_repo = MaterializedViewRepository(db)

    leaderboard = await materialized_view_repo.get_leaderboard(
        metric=metric,
        limit=limit,
    )

    # Анонимизируем имена для пользователей с privacy=True
    for entry in leaderboard:
        if entry.get("privacy_enabled"):
            entry["first_name"] = f"User {entry['id'] % 1000}"
            entry["username"] = None

    return {
        "metric": metric,
        "period": "weekly",
        "leaderboard": leaderboard,
    }

@router.get("/friends")
async def get_friends_leaderboard(
    user_id: int,
    metric: str = "stars",
    db: AsyncSession = Depends(get_session),
):
    """
    Лидерборд среди друзей (приглашённых рефералов).
    """
    # Получаем друзей пользователя
    friends = await referral_repo.get_user_referrals(user_id)
    friend_ids = [f.referred_id for f in friends] + [user_id]

    leaderboard = await materialized_view_repo.get_leaderboard_for_users(
        user_ids=friend_ids,
        metric=metric,
    )

    return {
        "metric": metric,
        "friends_count": len(friend_ids) - 1,
        "leaderboard": leaderboard,
    }
```

---

## 💰 РЕАЛИЗАЦИЯ МОНЕТИЗАЦИИ

### 1. Система подписок

**Рекомендация:** Реализовать модель из `docs/money.md`

```python
# backend/models/subscription.py
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PROFI = "profi"

class Subscription(Base):
    """Модель подписки пользователя."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # NULL = не истекает (free)
    payment_provider = Column(String(50))  # telegram_stars, stripe
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    # Отношения
    user = relationship("User", back_populates="subscription")

# backend/services/usage_limiter.py
class UsageLimiter:
    """Лимиты использования по тарифам."""

    LIMITS = {
        SubscriptionTier.FREE: {
            "daily_messages": 5,
            "saved_words": 50,
            "tts_per_word": 0,  # Нет озвучки слов
            "history_days": 7,
            "topics": ["general"],  # Только общие темы
        },
        SubscriptionTier.PREMIUM: {
            "daily_messages": float("inf"),
            "saved_words": float("inf"),
            "tts_per_word": float("inf"),
            "history_days": 365,
            "topics": ["all"],
        },
        SubscriptionTier.PROFI: {
            "daily_messages": float("inf"),
            "saved_words": float("inf"),
            "tts_per_word": float("inf"),
            "history_days": float("inf"),
            "topics": ["all"],
            "exam_prep": True,
            "document_check": True,
        },
    }

    async def check_and_decrement(
        self,
        user_id: int,
        action: str,
        amount: int = 1,
    ) -> tuple[bool, dict]:
        """
        Проверить лимит и уменьшить счётчик.

        Returns:
            (allowed, info) - разрешено ли действие и информация
        """
        user = await self.get_user_with_subscription(user_id)
        tier = user.subscription.tier if user.subscription else SubscriptionTier.FREE
        limits = self.LIMITS[tier]

        if action == "daily_messages":
            today = date.today()
            cache_key = f"usage:{user_id}:{action}:{today}"

            current = await redis_client.get(cache_key) or 0
            limit = limits[action]

            if current >= limit:
                return False, {
                    "error": "daily_limit_reached",
                    "current": current,
                    "limit": limit,
                    "resets_at": (today + timedelta(days=1)).isoformat(),
                    "upgrade_url": "/dashboard/settings?upgrade=true",
                }

            # Инкрементируем
            await redis_client.incr(cache_key)
            await redis_client.expire(cache_key, 86400)  # TTL 24 часа

            return True, {
                "remaining": limit - current - 1,
                "limit": limit,
            }

        # ... другие типы лимитов

        return True, {}
```

---

### 2. Интеграция Telegram Stars

```python
# bot/handlers/payments.py
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    LabeledPrice, PreCheckoutQuery,
    SuccessfulPayment
)

router = Router()

# Продукты для покупки
PRODUCTS = {
    "premium_month": {
        "title": "💫 Premium на месяц",
        "description": "Безлимитные сообщения, все темы, TTS для слов",
        "stars": 299,
        "duration_days": 30,
        "tier": "premium",
    },
    "premium_year": {
        "title": "💫 Premium на год",
        "description": "Скидка 20%! Всё из Premium на целый год",
        "stars": 2399,
        "duration_days": 365,
        "tier": "premium",
    },
    "messages_10": {
        "title": "🎤 +10 сообщений",
        "description": "Дополнительные голосовые на сегодня",
        "stars": 50,
        "type": "consumable",
        "amount": 10,
    },
    "topic_pack_restaurant": {
        "title": "🍽️ Пакет 'В ресторане'",
        "description": "Диалоги для заказа еды и общения с официантом",
        "stars": 100,
        "type": "topic_pack",
        "topic": "restaurant",
    },
}

@router.callback_query(F.data.startswith("buy:"))
async def process_buy(callback: CallbackQuery):
    """Обработка нажатия кнопки покупки."""
    product_id = callback.data.split(":")[1]
    product = PRODUCTS.get(product_id)

    if not product:
        await callback.answer("Продукт не найден", show_alert=True)
        return

    # Создаём инвойс для Telegram Stars
    await callback.message.answer_invoice(
        title=product["title"],
        description=product["description"],
        payload=product_id,
        provider_token="",  # Пустой для Stars
        currency="XTR",     # Telegram Stars
        prices=[LabeledPrice(
            label=product["title"],
            amount=product["stars"]
        )],
    )

    await callback.answer()

@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout: PreCheckoutQuery):
    """Проверка перед оплатой."""
    product_id = pre_checkout.invoice_payload
    product = PRODUCTS.get(product_id)

    if not product:
        await pre_checkout.answer(ok=False, error_message="Продукт не найден")
        return

    # Можно добавить дополнительные проверки
    await pre_checkout.answer(ok=True)

@router.message(F.successful_payment)
async def process_successful_payment(message: Message, api_client: APIClient):
    """Обработка успешной оплаты."""
    payment = message.successful_payment
    product_id = payment.invoice_payload
    product = PRODUCTS[product_id]
    user_id = message.from_user.id

    logger.info(
        "payment_successful",
        user_id=user_id,
        product_id=product_id,
        stars=payment.total_amount,
    )

    # Активируем покупку
    if product.get("tier"):
        # Подписка
        await api_client.activate_subscription(
            user_id=user_id,
            tier=product["tier"],
            duration_days=product["duration_days"],
            payment_provider="telegram_stars",
            transaction_id=payment.telegram_payment_charge_id,
        )

        await message.answer(
            f"🎉 {product['title']} активирован!\n\n"
            f"Теперь тебе доступны все Premium функции.\n"
            f"Спасибо за поддержку проекта! ❤️"
        )

    elif product.get("type") == "consumable":
        # Расходуемый товар (сообщения)
        await api_client.add_bonus_messages(
            user_id=user_id,
            amount=product["amount"],
        )

        await message.answer(
            f"✅ +{product['amount']} сообщений добавлено!\n"
            f"Можешь продолжать практику."
        )

    elif product.get("type") == "topic_pack":
        # Тематический пакет
        await api_client.unlock_topic(
            user_id=user_id,
            topic=product["topic"],
        )

        await message.answer(
            f"🎉 Пакет '{product['title']}' разблокирован!\n"
            f"Теперь можешь практиковать эту тему с Хонзиком."
        )

# Команда /premium для показа тарифов
@router.message(F.text == "/premium")
async def show_premium_options(message: Message):
    """Показать варианты Premium."""
    user = await api_client.get_user(message.from_user.id)
    language = user.get("ui_language", "ru")

    text = PREMIUM_TEXTS[language]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💫 Premium (299⭐/мес)",
            callback_data="buy:premium_month"
        )],
        [InlineKeyboardButton(
            text="🌟 Premium год (-20%)",
            callback_data="buy:premium_year"
        )],
        [InlineKeyboardButton(
            text="🎤 +10 сообщений (50⭐)",
            callback_data="buy:messages_10"
        )],
    ])

    await message.answer(text, reply_markup=keyboard)
```

---

### 3. Paywall в Web UI

```tsx
// frontend/components/features/Paywall.tsx
"use client"

import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { Button } from "@/components/ui/button"
import { Lock, Sparkles } from "lucide-react"

interface PaywallProps {
  feature: string
  requiredTier: "premium" | "profi"
  children: React.ReactNode
}

export function Paywall({ feature, requiredTier, children }: PaywallProps) {
  const user = useAuthStore((state) => state.user)
  const router = useRouter()

  // Проверяем подписку
  const userTier = user?.subscription?.tier || "free"
  const hasAccess =
    userTier === "profi" ||
    (userTier === "premium" && requiredTier !== "profi")

  if (hasAccess) {
    return <>{children}</>
  }

  return (
    <div className="relative">
      {/* Размытый контент */}
      <div className="blur-sm pointer-events-none opacity-50">
        {children}
      </div>

      {/* Overlay с призывом к действию */}
      <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/80 dark:bg-gray-900/80 rounded-lg">
        <Lock className="h-12 w-12 text-gray-400 mb-4" />

        <h3 className="text-lg font-semibold mb-2">
          {feature} — Premium функция
        </h3>

        <p className="text-sm text-gray-600 dark:text-gray-400 text-center mb-4 px-4">
          Разблокируй {feature} и другие возможности с Premium подпиской
        </p>

        <Button
          onClick={() => router.push("/dashboard/settings?tab=subscription")}
          className="gap-2"
        >
          <Sparkles className="h-4 w-4" />
          Получить Premium
        </Button>

        <p className="text-xs text-gray-500 mt-2">
          От 299 CZK/месяц
        </p>
      </div>
    </div>
  )
}

// Использование
export function AdvancedAnalytics() {
  return (
    <Paywall feature="Расширенная аналитика" requiredTier="premium">
      <AnalyticsChart />
    </Paywall>
  )
}
```

---

## 🎨 УЛУЧШЕНИЯ ДИЗАЙНА

### 1. Новые UI компоненты

#### 1.1 Анимированный прогресс-бар

```tsx
// frontend/components/ui/AnimatedProgress.tsx
"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface AnimatedProgressProps {
  value: number
  max: number
  label?: string
  showPercentage?: boolean
  color?: "primary" | "success" | "warning" | "danger"
  animated?: boolean
}

const colorVariants = {
  primary: "from-primary to-purple-600",
  success: "from-green-400 to-green-500",
  warning: "from-yellow-400 to-orange-500",
  danger: "from-red-400 to-red-500",
}

export function AnimatedProgress({
  value,
  max,
  label,
  showPercentage = true,
  color = "primary",
  animated = true,
}: AnimatedProgressProps) {
  const percentage = Math.min(100, (value / max) * 100)

  return (
    <div className="space-y-2">
      {(label || showPercentage) && (
        <div className="flex justify-between text-sm">
          {label && <span className="text-gray-600 dark:text-gray-400">{label}</span>}
          {showPercentage && (
            <motion.span
              key={percentage}
              initial={{ scale: 1.2, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="font-medium"
            >
              {Math.round(percentage)}%
            </motion.span>
          )}
        </div>
      )}

      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          className={cn(
            "h-full bg-gradient-to-r rounded-full",
            colorVariants[color]
          )}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{
            duration: animated ? 0.8 : 0,
            ease: "easeOut",
          }}
        >
          {/* Shimmer effect */}
          {animated && (
            <motion.div
              className="h-full w-1/3 bg-gradient-to-r from-transparent via-white/30 to-transparent"
              animate={{
                x: ["-100%", "400%"],
              }}
              transition={{
                repeat: Infinity,
                duration: 2,
                ease: "linear",
              }}
            />
          )}
        </motion.div>
      </div>
    </div>
  )
}
```

---

#### 1.2 Карточка достижения с анимацией

```tsx
// frontend/components/features/AchievementCard.tsx
"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import { Lock, Star } from "lucide-react"

interface AchievementCardProps {
  achievement: {
    id: number
    code: string
    name: string
    description: string
    icon: string
    category: string
    threshold: number
    stars_reward: number
    is_unlocked: boolean
    unlocked_at?: string
    progress?: number
  }
  showProgress?: boolean
}

export function AchievementCard({ achievement, showProgress = true }: AchievementCardProps) {
  const progress = achievement.progress || 0
  const progressPercent = Math.min(100, (progress / achievement.threshold) * 100)

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(
        "relative p-4 rounded-xl border transition-all duration-300",
        achievement.is_unlocked
          ? "bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-200 dark:from-yellow-900/20 dark:to-orange-900/20 dark:border-yellow-800"
          : "bg-gray-50 border-gray-200 dark:bg-gray-800 dark:border-gray-700 opacity-75"
      )}
    >
      {/* Иконка достижения */}
      <div className="flex items-start gap-3">
        <div className={cn(
          "text-4xl transition-all duration-300",
          achievement.is_unlocked ? "grayscale-0" : "grayscale opacity-50"
        )}>
          {achievement.icon}
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className={cn(
              "font-semibold",
              achievement.is_unlocked
                ? "text-gray-900 dark:text-gray-100"
                : "text-gray-500 dark:text-gray-400"
            )}>
              {achievement.name}
            </h3>

            {!achievement.is_unlocked && (
              <Lock className="h-4 w-4 text-gray-400" />
            )}
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {achievement.description}
          </p>

          {/* Прогресс для незаблокированных */}
          {showProgress && !achievement.is_unlocked && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>{progress} / {achievement.threshold}</span>
                <span>{Math.round(progressPercent)}%</span>
              </div>
              <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-400 to-purple-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${progressPercent}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>
          )}

          {/* Награда */}
          <div className="flex items-center gap-1 mt-2 text-xs">
            <Star className="h-3 w-3 text-yellow-500" />
            <span className="text-yellow-600 dark:text-yellow-400">
              +{achievement.stars_reward} звёзд
            </span>
          </div>
        </div>
      </div>

      {/* Дата получения */}
      {achievement.is_unlocked && achievement.unlocked_at && (
        <div className="absolute top-2 right-2 text-xs text-gray-500">
          {new Date(achievement.unlocked_at).toLocaleDateString()}
        </div>
      )}

      {/* Shine effect для полученных */}
      {achievement.is_unlocked && (
        <motion.div
          className="absolute inset-0 rounded-xl pointer-events-none"
          animate={{
            background: [
              "linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.1) 50%, transparent 60%)",
              "linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.1) 50%, transparent 60%)",
            ],
            backgroundPosition: ["-200% 0", "200% 0"],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            repeatDelay: 5,
          }}
        />
      )}
    </motion.div>
  )
}
```

---

### 2. Улучшенный Onboarding

```tsx
// frontend/app/(auth)/onboarding/page.tsx
"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useRouter } from "next/navigation"
import Image from "next/image"

const STEPS = [
  {
    id: "welcome",
    image: "/images/mascot/honzik-waving.png",
    title: "Ahoj! 🇨🇿",
    description: "Я Хонзік — твій веселий чеський друг!\nДопоможу тобі заговорити чеською.",
  },
  {
    id: "language",
    title: "Мова інтерфейсу",
    description: "Якою мовою показувати підказки?",
    options: [
      { value: "ru", label: "🇷🇺 Русский", flag: "🇷🇺" },
      { value: "uk", label: "🇺🇦 Українська", flag: "🇺🇦" },
    ],
  },
  {
    id: "level",
    title: "Твій рівень чеської",
    description: "Обери, щоб я міг підлаштуватися",
    options: [
      { value: "beginner", label: "🌱 Začátečník", desc: "Тільки починаю" },
      { value: "intermediate", label: "📚 Středně pokročilý", desc: "Знаю основи" },
      { value: "advanced", label: "🎓 Pokročilý", desc: "Говорю вільно" },
      { value: "native", label: "🏆 Rodilý", desc: "Хочу ідеальну мову" },
    ],
  },
  {
    id: "style",
    title: "Як зі мною спілкуватися?",
    description: "Можеш змінити пізніше в налаштуваннях",
    options: [
      { value: "friendly", label: "😊 Дружелюбно", desc: "Більше підтримки, менше виправлень" },
      { value: "tutor", label: "📖 Як вчитель", desc: "Детальні пояснення помилок" },
      { value: "casual", label: "🍺 Як друг", desc: "Невимушена розмова" },
    ],
  },
  {
    id: "ready",
    image: "/images/mascot/honzik-thumbs-up.png",
    title: "Готово! 🎉",
    description: "Тепер надішли мені голосове повідомлення чеською.\nНе бійся помилок — так вчаться!",
  },
]

export default function OnboardingPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [selections, setSelections] = useState<Record<string, string>>({})

  const step = STEPS[currentStep]

  const handleSelect = (value: string) => {
    setSelections(prev => ({ ...prev, [step.id]: value }))

    // Автоматически переходим дальше через 300ms
    setTimeout(() => {
      if (currentStep < STEPS.length - 1) {
        setCurrentStep(prev => prev + 1)
      }
    }, 300)
  }

  const handleFinish = async () => {
    // Создаём пользователя с выбранными настройками
    await apiClient.createUser({
      ...telegramUser,
      ui_language: selections.language,
      level: selections.level,
      conversation_style: selections.style,
    })

    router.push("/dashboard")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-purple-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Progress dots */}
        <div className="flex justify-center gap-2 mb-8">
          {STEPS.map((_, index) => (
            <motion.div
              key={index}
              className={cn(
                "w-2 h-2 rounded-full transition-colors",
                index === currentStep
                  ? "bg-primary w-8"
                  : index < currentStep
                    ? "bg-primary/50"
                    : "bg-gray-300 dark:bg-gray-600"
              )}
              layoutId={index === currentStep ? "active-dot" : undefined}
            />
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={step.id}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6"
          >
            {/* Image */}
            {step.image && (
              <div className="flex justify-center mb-6">
                <motion.div
                  initial={{ scale: 0.8, rotate: -10 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ type: "spring", bounce: 0.4 }}
                >
                  <Image
                    src={step.image}
                    alt="Honzík"
                    width={150}
                    height={150}
                    className="drop-shadow-lg"
                  />
                </motion.div>
              </div>
            )}

            {/* Title */}
            <h1 className="text-2xl font-bold text-center mb-2 text-gray-900 dark:text-gray-100">
              {step.title}
            </h1>

            {/* Description */}
            <p className="text-center text-gray-600 dark:text-gray-400 mb-6 whitespace-pre-line">
              {step.description}
            </p>

            {/* Options */}
            {step.options && (
              <div className="space-y-3">
                {step.options.map((option) => (
                  <motion.button
                    key={option.value}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSelect(option.value)}
                    className={cn(
                      "w-full p-4 rounded-xl border-2 transition-all text-left",
                      selections[step.id] === option.value
                        ? "border-primary bg-primary/10"
                        : "border-gray-200 dark:border-gray-700 hover:border-primary/50"
                    )}
                  >
                    <div className="font-medium">{option.label}</div>
                    {option.desc && (
                      <div className="text-sm text-gray-500 mt-1">{option.desc}</div>
                    )}
                  </motion.button>
                ))}
              </div>
            )}

            {/* Finish button */}
            {step.id === "ready" && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleFinish}
                className="w-full py-4 bg-gradient-to-r from-primary to-purple-600 text-white rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transition-shadow"
              >
                Почати практику! 🚀
              </motion.button>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Back button */}
        {currentStep > 0 && currentStep < STEPS.length - 1 && (
          <button
            onClick={() => setCurrentStep(prev => prev - 1)}
            className="mt-4 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 text-sm mx-auto block"
          >
            ← Назад
          </button>
        )}
      </div>
    </div>
  )
}
```

---

## 📋 ПЛАН ВНЕДРЕНИЯ

### Фаза 1: Критические улучшения (1-2 недели)

| Задача | Приоритет | Оценка |
|--------|-----------|--------|
| Параллельная обработка голосовых | 🔴 Критично | 3 дня |
| Умный выбор модели GPT | 🔴 Критично | 1 день |
| Кеширование TTS | 🟠 Высокий | 2 дня |
| Connection pooling | 🟠 Высокий | 1 день |
| Background tasks для DB | 🟠 Высокий | 2 дня |

### Фаза 2: Монетизация (2-3 недели)

| Задача | Приоритет | Оценка |
|--------|-----------|--------|
| Модель подписок в БД | 🔴 Критично | 2 дня |
| Telegram Stars интеграция | 🔴 Критично | 3 дня |
| Usage limiter | 🔴 Критично | 2 дня |
| Paywall UI | 🟠 Высокий | 2 дня |
| Premium функции | 🟠 Высокий | 5 дней |

### Фаза 3: Геймификация (2-3 недели)

| Задача | Приоритет | Оценка |
|--------|-----------|--------|
| Новые достижения | 🟠 Высокий | 3 дня |
| Ежедневные челленджи | 🟠 Высокий | 3 дня |
| Лидерборд | 🟡 Средний | 2 дня |
| Реферальная программа | 🟡 Средний | 3 дня |

### Фаза 4: Frontend (1-2 недели)

| Задача | Приоритет | Оценка |
|--------|-----------|--------|
| Server Components | 🟠 Высокий | 3 дня |
| Optimistic updates | 🟠 Высокий | 2 дня |
| Новый Onboarding | 🟡 Средний | 2 дня |
| Анимации достижений | 🟡 Средний | 2 дня |

---

## 📊 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

### Performance
| Метрика | До | После |
|---------|-----|-------|
| Время ответа (P95) | 5-6 сек | 2-4 сек |
| OpenAI cost/user/day | $0.08 | $0.05 |
| Cache hit rate | 15% | 50%+ |
| FCP (Frontend) | 2.5s | 1.5s |

### Business
| Метрика | Цель (6 мес) |
|---------|-------------|
| MAU | 5000+ |
| Premium конверсия | 7% |
| MRR | 100,000 CZK |
| NPS | >50 |

### Engagement
| Метрика | Цель |
|---------|------|
| DAU/MAU | >30% |
| Avg. messages/user/day | 5+ |
| 7-day retention | >40% |
| 30-day retention | >20% |

---

## 🔗 ПОЛЕЗНЫЕ ССЫЛКИ

- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Next.js Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Telegram Stars Payments](https://core.telegram.org/bots/payments)
- [React Query Optimistic Updates](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates)

---

*Документ создан: Февраль 2026*
*Версия: 1.0*
*Автор: AI Code Analyst*

**Na zdraví! 🍺 Pojďme zlepšit Mluv.Me! 🇨🇿**
