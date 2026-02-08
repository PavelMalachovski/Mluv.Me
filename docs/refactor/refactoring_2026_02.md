# 🔧 Рефакторинг и улучшения Mluv.Me

> **Дата анализа:** Февраль 2026
> **Версия проекта:** 1.0.0
> **Автор:** AI Code Analysis

---

## 📝 Последние изменения

### 08.02.2026 - Удаление автоматической детекции языка ✅

**Проблема:** Whisper API автоматически определял язык голосового сообщения, что могло приводить к неправильной транскрипции, если пользователь говорил не на чешском.

**Решение:**
- Заменён метод `transcribe_audio_with_detection()` на обычный `transcribe_audio(language="cs")`
- Теперь всегда используется чешский язык для транскрипции
- Поле `detected_language` в ответе API всегда возвращает `"cs"`

**Изменённые файлы:**
- `backend/routers/lesson.py` (строки 178-193)

**Преимущества:**
- ✅ Более точная транскрипция чешской речи
- ✅ Нет ложных срабатываний на другие языки
- ✅ Упрощение логики обработки



---

## 📑 Содержание

1. [📊 Обзор текущего состояния](#-обзор-текущего-состояния)
   - [Архитектура](#архитектура)
   - [Сильные стороны](#сильные-стороны-)
   - [Слабые места](#слабые-места-️)

2. [🚀 Улучшения производительности](#-улучшения-производительности)
   - [Backend Performance](#1-backend-performance)
     - [Оптимизация обработки голосовых](#11-оптимизация-обработки-голосовых-критично)
     - [Streaming TTS Response](#12-добавить-streaming-tts-response)
     - [Умный выбор модели GPT](#13-умный-выбор-модели-gpt)
     - [Connection Pooling](#14-connection-pooling-для-postgresql)
     - [Расширенное кеширование](#15-расширенное-кеширование)
   - [Frontend Performance](#2-frontend-performance)
     - [Server Components](#21-server-components-для-dashboard)
     - [Optimistic Updates](#22-optimistic-updates-для-ui)
     - [Prefetching и Code Splitting](#23-prefetching-и-code-splitting)

3. [🎮 Улучшения геймификации](#-улучшения-геймификации)
   - [Расширенная система достижений](#1-расширенная-система-достижений)
   - [Ежедневные и еженедельные челленджи](#2-ежедневные-и-еженедельные-челленджи)
   - [Лидерборд и социальные функции](#3-лидерборд-и-социальные-функции)

4. [💰 Реализация монетизации](#-реализация-монетизации)
   - [Система подписок](#1-система-подписок)
   - [Интеграция Telegram Stars](#2-интеграция-telegram-stars)
   - [Paywall в Web UI](#3-paywall-в-web-ui)

5. [🎨 Улучшения дизайна](#-улучшения-дизайна)
   - [Новые UI компоненты](#1-новые-ui-компоненты)
     - [Анимированный прогресс-бар](#11-анимированный-прогресс-бар)
     - [Карточка достижения с анимацией](#12-карточка-достижения-с-анимацией)
   - [Улучшенный Onboarding](#2-улучшенный-onboarding)

6. [🇨🇿 Полный переход на чешский интерфейс](#-полный-переход-на-чешский-интерфейс)
   - [Концепция: Погружение в язык](#концепция-погружение-в-язык-language-immersion)
   - [Удаление мультиязычности](#1-удаление-мультиязычности)
   - [Чешские тексты для интерфейса](#2-чешские-тексты-для-интерфейса)
   - [Адаптивные объяснения ошибок](#3-адаптивные-объяснения-ошибок)
   - [UI компонент для объяснений](#4-ui-компонент-для-объяснений)
   - [Миграция существующих пользователей](#5-миграция-существующих-пользователей)
   - [Обновление Telegram бота](#6-обновление-telegram-бота)

7. [✍️ Текстовое общение с Хонзиком](#️-текстовое-общение-с-хонзиком)
   - [Текущее состояние](#текущее-состояние)
   - [Backend: Endpoint для текстовых сообщений](#1-backend-endpoint-для-текстовых-сообщений)
   - [Telegram Bot: Обработка текста](#2-telegram-bot-обработка-текстовых-сообщений)
   - [API Client: Метод для текста](#3-api-client-метод-для-текста)
   - [Frontend: Улучшенный текстовый ввод](#4-frontend-улучшенный-текстовый-ввод)

8. [💡 Идеи по улучшению и новые функции](#-идеи-по-улучшению-и-новые-функции)
   - **Краткосрочные (1-2 месяца)**
     - [Ролевые сценарии с диалогами](#1--ролевые-сценарии-с-диалогами)
     - [Детальная аналитика произношения](#2--детальная-аналитика-произношения)
     - [Интеграция с учебниками](#3--интеграция-с-учебниками)
   - **Среднесрочные (3-6 месяцев)**
     - [Мини-игры для изучения](#4--мини-игры-для-изучения)
     - [Групповые функции](#5--групповые-функции)
     - [Сезонные события](#6--сезонные-события)
   - **Долгосрочные (6+ месяцев)**
     - [Множественные AI-персонажи](#7--множественные-ai-персонажи)
     - [Мобильное приложение](#8--мобильное-приложение-pwa--native)
     - [Подготовка к экзаменам](#9--подготовка-к-экзаменам)
     - [Расширение на другие языки](#10--расширение-на-другие-славянские-языки)
   - **Экспериментальные идеи**
     - [Видео-аватар Хонзика](#11--видео-аватар-хонзика)
     - [Анализ в реальном времени](#12--анализ-в-реальном-времени)
     - [Генерация персонализированных историй](#13--генерация-персонализированных-историй)
     - [Подкаст от Хонзика](#14--подкаст-от-хонзика)

9. [📋 План внедрения](#-план-внедрения)
   - [Фаза 1: Критические улучшения](#фаза-1-критические-улучшения-1-2-недели)
   - [Фаза 2: Монетизация](#фаза-2-монетизация-2-3-недели)
   - [Фаза 3: Геймификация](#фаза-3-геймификация-2-3-недели)
   - [Фаза 4: Чешский интерфейс + Текст](#фаза-4-чешский-интерфейс--текст-2-3-недели)
   - [Фаза 5: Frontend](#фаза-5-frontend-1-2-недели)
   - [Фаза 6: Новые функции](#фаза-6-новые-функции-4-недели)

10. [📊 Ожидаемые результаты](#-ожидаемые-результаты)
    - [Performance](#performance)
    - [Business](#business)
    - [Engagement](#engagement)

11. [🔗 Полезные ссылки](#-полезные-ссылки)

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

## 🇨🇿 ПОЛНЫЙ ПЕРЕХОД НА ЧЕШСКИЙ ИНТЕРФЕЙС

### Концепция: Погружение в язык (Language Immersion)

**Текущее состояние:**
- UI на русском и украинском языках
- Объяснения ошибок на языке пользователя
- Хонзик говорит по-чешски, но подсказки на ru/uk

**Новая концепция:**
> 💡 **Полное погружение** — весь интерфейс на чешском с простыми объяснениями.
> Это самый эффективный метод изучения языка!

### 1. Удаление мультиязычности

```python
# backend/models/user.py - УДАЛИТЬ ui_language

class User(Base):
    """Модель пользователя - БЕЗ выбора языка UI."""
    __tablename__ = "users"

    # УДАЛИТЬ ЭТО ПОЛЕ:
    # ui_language: Mapped[str] = mapped_column(...)

    # Добавить поле для родного языка (для понимания ошибок)
    native_language: Mapped[str] = mapped_column(
        Enum("ru", "uk", "pl", "sk", name="native_language_enum"),
        nullable=False,
        default="ru",
        comment="Родной язык пользователя (для объяснения сложных моментов)"
    )
```

### 2. Чешские тексты для интерфейса

```typescript
// frontend/lib/localization/cs.ts
export const CS_TEXTS = {
  // Навигация
  nav: {
    dashboard: "Přehled",
    practice: "Procvičování",
    review: "Opakování",
    saved: "Uložená slova",
    profile: "Profil",
    settings: "Nastavení",
  },

  // Dashboard
  dashboard: {
    greeting: (name: string) => `Ahoj, ${name}! 👋`,
    subtitle: "Připraven/a na dnešní češtinu?",
    streak: "Série dnů",
    stars: "Hvězdy",
    practice_btn: "Procvičovat",
    review_btn: "Opakovat",
    todays_progress: "Dnešní pokrok",
    messages: "Zprávy",
    to_review: "K opakování",
    accuracy: "Přesnost",
    achievements: "Úspěchy",
    view_all: "Zobrazit vše →",
    keep_going: "Pokračuj!",
  },

  // Practice
  practice: {
    title: "Procvičuj češtinu s Honzíkem",
    subtitle: "Napiš nebo nahraj zprávu v češtině",
    topic_select: "Vyber téma",
    start_btn: "Začít procvičovat",
    topic_label: "Téma:",
    send_btn: "Odeslat",
    recording: "Nahrávání...",
    processing: "Zpracovávám...",
    show_text: "Zobrazit text",
    hide_text: "Skrýt text",
    translate_word: "Přeložit slovo",
    corrections_header: "Opravy:",
    no_corrections: "Výborně! Bez chyb! 🎉",
    stars_earned: (n: number) => `+${n} hvězd ⭐`,
    tips_title: "Tipy pro procvičování:",
    tips: [
      "✅ Piš celé věty",
      "✅ Neboj se chyb — tak se učíme!",
      "✅ Ptej se Honzíka na českou kulturu",
      "✅ Procvičuj pravidelně",
    ],
    input_placeholder: "Napiš zprávu v češtině...",
    voice_hint: "🎤 Klepni pro nahrání (max 60 sekund)",
  },

  // Review (Spaced Repetition)
  review: {
    title: "Opakování slovíček",
    cards_due: "Slovíček k opakování",
    no_cards: "Žádná slovíčka k opakování! 🎉",
    show_answer: "Zobrazit odpověď",
    again: "Znovu",
    hard: "Těžké",
    good: "Dobré",
    easy: "Snadné",
    progress: (current: number, total: number) => `${current} / ${total}`,
    completed: "Dnešní opakování hotovo! 🎉",
  },

  // Saved words
  saved: {
    title: "Uložená slova",
    search_placeholder: "Hledat slovo...",
    no_words: "Zatím nemáš žádná uložená slova",
    add_words_hint: "Klepni na slovo v konverzaci pro jeho uložení",
    delete_confirm: "Opravdu smazat toto slovo?",
    phonetics: "Výslovnost",
    example: "Příklad",
  },

  // Profile
  profile: {
    title: "Profil",
    level: "Úroveň češtiny",
    member_since: "Člen od",
    stats_title: "Statistiky",
    total_messages: "Celkem zpráv",
    total_words: "Naučených slov",
    best_streak: "Nejdelší série",
    avg_accuracy: "Průměrná přesnost",
  },

  // Settings
  settings: {
    title: "Nastavení",
    level_section: "Úroveň češtiny",
    level_beginner: "Začátečník (A1-A2)",
    level_intermediate: "Středně pokročilý (B1-B2)",
    level_advanced: "Pokročilý (B2-C1)",
    level_native: "Rodilý mluvčí (C2)",
    style_section: "Styl komunikace",
    style_friendly: "Přátelský",
    style_friendly_desc: "Více podpory, méně oprav",
    style_tutor: "Učitel",
    style_tutor_desc: "Detailní vysvětlení chyb",
    style_casual: "Kamarádský",
    style_casual_desc: "Neformální konverzace",
    corrections_section: "Úroveň oprav",
    corrections_minimal: "Minimální",
    corrections_balanced: "Vyvážená",
    corrections_detailed: "Detailní",
    voice_speed: "Rychlost hlasu Honzíka",
    voice_very_slow: "Velmi pomalu",
    voice_slow: "Pomalu",
    voice_normal: "Normálně",
    voice_native: "Rychle (rodilý)",
    save_btn: "Uložit nastavení",
    saved_toast: "Nastavení uloženo!",
  },

  // Achievements
  achievements: {
    title: "Úspěchy",
    locked: "Zamčeno",
    unlocked: "Odemčeno",
    progress: "Pokrok",
    reward: "Odměna",
  },

  // Common
  common: {
    loading: "Načítání...",
    error: "Něco se pokazilo",
    retry: "Zkusit znovu",
    back: "Zpět",
    next: "Další",
    cancel: "Zrušit",
    confirm: "Potvrdit",
    save: "Uložit",
    delete: "Smazat",
    yes: "Ano",
    no: "Ne",
  },

  // Errors
  errors: {
    network: "Problém s připojením. Zkus to znovu.",
    voice_too_long: "Zpráva je příliš dlouhá (max 60 sekund)",
    processing_failed: "Nepodařilo se zpracovat. Zkus to znovu.",
  },

  // Honzík phrases
  honzik: {
    greeting: "Ahoj! Jsem Honzík 🇨🇿",
    thinking: "Honzík přemýšlí...",
    listening: "Honzík poslouchá...",
    encouragement: [
      "Výborně! Jde ti to skvěle! 💪",
      "Super práce! Pokračuj! 🎉",
      "Skvělé! Učíš se rychle! ⭐",
      "Prima! To bylo dobré! 👍",
    ],
  },
}
```

### 3. Адаптивные объяснения ошибок

**Концепция:** Объяснения ошибок сначала на простом чешском, с возможностью увидеть перевод на родной язык.

```python
# backend/services/honzik_personality.py

def _get_correction_prompt(self, native_language: str) -> str:
    """Промпт для исправлений на чешском с переводом."""
    return f"""
DŮLEŽITÉ: Piš opravy JEDNODUŠE v češtině na úrovni A2.
Používej základní slovní zásobu.

Formát odpovědi pro každou chybu:
{{
  "original": "špatný text",
  "corrected": "správný text",
  "explanation_cs": "Jednoduché vysvětlení česky (max 15 slov)",
  "explanation_native": "Překlad vysvětlení do {native_language}"
}}

Příklad:
{{
  "original": "já jsem student",
  "corrected": "jsem student",
  "explanation_cs": "V češtině nemusíme říkat 'já' - je to jasné ze slovesa.",
  "explanation_native": "В чешском не нужно говорить 'já' - это понятно из глагола."
}}
"""
```

### 4. UI компонент для объяснений

```tsx
// frontend/components/ui/CorrectionExplanation.tsx
"use client"

import { useState } from "react"
import { ChevronDown, Languages } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

interface CorrectionProps {
  original: string
  corrected: string
  explanationCs: string
  explanationNative: string
}

export function CorrectionExplanation({
  original,
  corrected,
  explanationCs,
  explanationNative,
}: CorrectionProps) {
  const [showNative, setShowNative] = useState(false)

  return (
    <div className="rounded-lg bg-red-50 dark:bg-red-900/20 p-3 space-y-2">
      {/* Исправление */}
      <div className="flex items-center gap-2 text-sm">
        <span className="line-through text-red-600">{original}</span>
        <span>→</span>
        <span className="font-medium text-green-600">{corrected}</span>
      </div>

      {/* Объяснение на чешском */}
      <p className="text-sm text-gray-700 dark:text-gray-300">
        💡 {explanationCs}
      </p>

      {/* Кнопка перевода */}
      <button
        onClick={() => setShowNative(!showNative)}
        className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700"
      >
        <Languages className="h-3 w-3" />
        {showNative ? "Skrýt překlad" : "Zobrazit překlad"}
        <ChevronDown className={`h-3 w-3 transition-transform ${showNative ? "rotate-180" : ""}`} />
      </button>

      {/* Перевод на родной язык */}
      <AnimatePresence>
        {showNative && (
          <motion.p
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="text-xs text-gray-500 italic border-l-2 border-blue-300 pl-2"
          >
            {explanationNative}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  )
}
```

### 5. Миграция существующих пользователей

```python
# alembic/versions/20260203_czech_only_ui.py
"""Remove ui_language, add native_language for explanations."""

def upgrade():
    # Добавляем новое поле
    op.add_column(
        'users',
        sa.Column('native_language', sa.String(2), nullable=True)
    )

    # Мигрируем данные: ui_language → native_language
    op.execute("""
        UPDATE users
        SET native_language = ui_language
        WHERE ui_language IS NOT NULL
    """)

    # Делаем поле обязательным
    op.alter_column('users', 'native_language', nullable=False, server_default='ru')

    # Удаляем старое поле
    op.drop_column('users', 'ui_language')

def downgrade():
    # Обратная миграция
    op.add_column('users', sa.Column('ui_language', sa.String(2), nullable=True))
    op.execute("UPDATE users SET ui_language = native_language")
    op.drop_column('users', 'native_language')
```

### 6. Обновление Telegram бота

```python
# bot/localization/cs.py
"""Все тексты бота на чешском."""

TEXTS_CS = {
    # Приветствие
    "welcome": (
        "Ahoj! 🇨🇿 Jsem Honzík!\n\n"
        "Pomohu ti s češtinou. Pošli mi hlasovou zprávu "
        "nebo napiš text v češtině.\n\n"
        "Neboj se chyb — tak se učíme! 💪"
    ),

    # Выбор уровня
    "choose_level": "Jaká je tvoje úroveň češtiny?",
    "level_beginner": "🌱 Začátečník",
    "level_intermediate": "📚 Středně pokročilý",
    "level_advanced": "🎓 Pokročilý",
    "level_native": "🏆 Rodilý mluvčí",

    # Выбор родного языка (для объяснений)
    "choose_native": "Jaký je tvůj rodný jazyk? (pro vysvětlení)",
    "native_ru": "🇷🇺 Ruština",
    "native_uk": "🇺🇦 Ukrajinština",
    "native_pl": "🇵🇱 Polština",
    "native_sk": "🇸🇰 Slovenština",

    # Помощь
    "help": (
        "📖 **Jak používat bota:**\n\n"
        "🎤 Pošli hlasovou zprávu v češtině\n"
        "✍️ Nebo napiš text v češtině\n"
        "💡 Opravím tvoje chyby\n"
        "⭐ Získej hvězdy za praxi!\n\n"
        "**Příkazy:**\n"
        "/stats — Tvoje statistiky\n"
        "/level — Změnit úroveň\n"
        "/style — Styl komunikace\n"
        "/saved — Uložená slova\n"
        "/help — Tato nápověda"
    ),

    # Результаты
    "voice_correctness": "✅ Správnost: {score}%",
    "voice_streak": "🔥 Série: {streak} dnů",
    "voice_stars_earned": "⭐ +{stars} hvězd!",

    # Исправления
    "corrections_header": "📝 **Opravy:**\n",
    "no_corrections": "🎉 Výborně! Bez chyb!",
    "suggestion": "💡 **Tip:** {suggestion}",

    # Кнопки
    "btn_show_text": "📝 Text",
    "btn_save_word": "💾 Uložit",

    # Ошибки
    "error_general": "Něco se pokazilo. Zkus to znovu.",
    "error_voice_too_long": "Zpráva je příliš dlouhá (max 60 sekund).",
    "error_backend": "Server je momentálně nedostupný.",
}

def get_text(key: str, **kwargs) -> str:
    """Получить текст на чешском."""
    text = TEXTS_CS.get(key, key)
    return text.format(**kwargs) if kwargs else text
```

---

## ✍️ ТЕКСТОВОЕ ОБЩЕНИЕ С ХОНЗИКОМ

### Текущее состояние
- В боте только голосовые сообщения
- В Web UI есть текстовый ввод (частично)
- Нет полной поддержки текста в боте

### 1. Backend: Endpoint для текстовых сообщений

```python
# backend/routers/lesson.py

@router.post("/process/text", response_model=LessonProcessResponse)
async def process_text_message(
    user_id: int = Form(..., description="Telegram ID пользователя"),
    text: str = Form(..., description="Текст сообщения на чешском"),
    include_audio: bool = Form(True, description="Включить голосовой ответ"),
    db: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
    openai_client: OpenAIClient = Depends(get_openai_client),
    honzik: HonzikPersonality = Depends(get_honzik_personality),
    gamification: GamificationService = Depends(get_gamification_service),
):
    """
    Обработать текстовое сообщение пользователя.

    В отличие от голосового, здесь:
    1. НЕТ этапа STT (текст уже есть)
    2. Опционально TTS (можно отключить для экономии)
    3. Быстрее на 1-2 секунды

    Args:
        user_id: Telegram ID пользователя
        text: Текст на чешском
        include_audio: Генерировать ли голосовой ответ
    """
    log = logger.bind(user_id=user_id, mode="text")
    log.info("processing_text_message", text_length=len(text))

    # Валидация
    user_repo = UserRepository(db)
    user = await user_repo.get_by_telegram_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if len(text) > 2000:
        raise HTTPException(status_code=400, detail="Text too long (max 2000 chars)")

    # Получаем историю
    message_repo = MessageRepository(db)
    recent_messages = await message_repo.get_user_messages(user_id=user.id, limit=10)
    conversation_history = [
        {"role": msg.role, "text": msg.text or ""}
        for msg in reversed(recent_messages)
    ]

    # Анализ Хонзика (быстрее без STT!)
    honzik_response = await honzik.generate_response(
        user_text=text,
        level=user.level,
        style=user.settings.conversation_style,
        corrections_level=user.settings.corrections_level,
        native_language=user.native_language,  # Для объяснений
        conversation_history=conversation_history,
    )

    # TTS только если нужно
    audio_base64 = None
    if include_audio:
        voice_speed = openai_client.get_voice_speed_mapping(user.settings.voice_speed)
        audio_response = await openai_client.generate_speech(
            text=honzik_response["honzik_response"],
            speed=voice_speed,
        )
        audio_base64 = base64.b64encode(audio_response).decode('utf-8')

    # Сохранение и геймификация (в background)
    await save_message_and_stats(db, user, text, honzik_response)
    gamification_result = await gamification.process_message_gamification(
        db=db,
        user_id=user.id,
        correctness_score=honzik_response["correctness_score"],
        timezone_str=user.settings.timezone,
    )

    await db.commit()

    return LessonProcessResponse(
        transcript=text,  # Для текстового - это и есть "транскрипт"
        honzik_response_text=honzik_response["honzik_response"],
        honzik_response_audio=audio_base64,  # None если include_audio=False
        corrections=CorrectionSchema(
            corrected_text=honzik_response["corrected_text"],
            mistakes=honzik_response["mistakes"],
            correctness_score=honzik_response["correctness_score"],
            suggestion=honzik_response["suggestion"],
        ),
        stars_earned=gamification_result["stars_earned"],
        total_stars=gamification_result["total_stars"],
        current_streak=gamification_result["current_streak"],
        # ...
    )
```

### 2. Telegram Bot: Обработка текстовых сообщений

```python
# bot/handlers/text.py
"""Обработчик текстовых сообщений."""

from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import structlog

from bot.localization.cs import get_text
from bot.services.api_client import APIClient

router = Router()
logger = structlog.get_logger()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message, api_client: APIClient) -> None:
    """
    Обработчик текстовых сообщений (не команд).

    Пользователь может писать Хонзику текстом на чешском,
    а не только голосовыми.
    """
    telegram_id = message.from_user.id
    text = message.text.strip()

    # Получаем пользователя
    user = await api_client.get_user(telegram_id)
    if not user:
        await message.answer(get_text("error_general"))
        return

    # Проверка минимальной длины
    if len(text) < 2:
        await message.answer("Napiš alespoň pár slov v češtině! 📝")
        return

    # Показываем что Хонзик печатает
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        # Отправляем текст в backend
        logger.info("processing_text", telegram_id=telegram_id, text_length=len(text))

        response = await api_client.process_text(
            user_id=telegram_id,
            text=text,
            include_audio=True,  # Хонзик отвечает голосом
        )

        if not response:
            await message.answer(get_text("error_backend"))
            return

        # Ответ Хонзика
        honzik_text = response.get("honzik_response_text", "")
        audio_response = response.get("honzik_response_audio")
        corrections = response.get("corrections", {})
        correctness_score = corrections.get("correctness_score", 0)
        streak = response.get("current_streak", 0)
        stars_earned = response.get("stars_earned", 0)

        # Если есть аудио - отправляем голосовое
        if audio_response:
            import base64
            from aiogram.types import BufferedInputFile

            audio_bytes = base64.b64decode(audio_response)
            voice_file = BufferedInputFile(audio_bytes, filename="honzik.ogg")

            caption = f"{get_text('voice_correctness', score=correctness_score)}\n"
            caption += get_text('voice_streak', streak=streak)

            # Кнопка показать текст
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=get_text("btn_show_text"),
                    callback_data=f"show_text_resp:{message.message_id}"
                )]
            ])

            await message.answer_voice(
                voice=voice_file,
                caption=caption,
                reply_markup=keyboard
            )
        else:
            # Если нет аудио - просто текст
            await message.answer(
                f"🗣️ **Honzík:**\n{honzik_text}\n\n"
                f"{get_text('voice_correctness', score=correctness_score)}"
            )

        # Исправления
        mistakes = corrections.get("mistakes", [])
        if mistakes:
            corrections_text = get_text("corrections_header")
            for mistake in mistakes[:3]:
                corrections_text += (
                    f"❌ {mistake.get('original', '')} → "
                    f"✅ {mistake.get('corrected', '')}\n"
                    f"💡 {mistake.get('explanation_cs', '')}\n\n"
                )
            await message.answer(corrections_text, parse_mode="HTML")
        else:
            await message.answer(get_text("no_corrections"))

        # Звёзды
        if stars_earned > 0:
            await message.answer(get_text("voice_stars_earned", stars=stars_earned))

        logger.info(
            "text_processed",
            telegram_id=telegram_id,
            score=correctness_score,
            streak=streak,
        )

    except Exception as e:
        logger.error("text_processing_error", telegram_id=telegram_id, error=str(e))
        await message.answer(get_text("error_general"))


# Добавляем в главный роутер
# bot/handlers/__init__.py
from bot.handlers.text import router as text_router

def get_main_router():
    router = Router()
    router.include_router(start_router)
    router.include_router(voice_router)
    router.include_router(text_router)  # НОВОЕ!
    router.include_router(commands_router)
    return router
```

### 3. API Client: Метод для текста

```python
# bot/services/api_client.py

class APIClient:
    async def process_text(
        self,
        user_id: int,
        text: str,
        include_audio: bool = True,
    ) -> dict | None:
        """
        Отправить текстовое сообщение для обработки.

        Args:
            user_id: Telegram ID
            text: Текст на чешском
            include_audio: Генерировать голосовой ответ
        """
        try:
            form_data = {
                "user_id": user_id,
                "text": text,
                "include_audio": include_audio,
            }

            async with self.session.post(
                f"{self.base_url}/api/v1/lessons/process/text",
                data=form_data,
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(
                        "text_api_error",
                        status=response.status,
                        body=await response.text()
                    )
                    return None
        except Exception as e:
            self.logger.error("text_api_exception", error=str(e))
            return None
```

### 4. Frontend: Улучшенный текстовый ввод

```tsx
// frontend/components/ui/CzechTextInput.tsx
"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Mic, Keyboard } from "lucide-react"
import { motion } from "framer-motion"
import { CS_TEXTS } from "@/lib/localization/cs"

interface CzechTextInputProps {
  onSubmit: (text: string) => void
  onVoiceStart: () => void
  isLoading: boolean
  mode: "text" | "voice"
  onModeChange: (mode: "text" | "voice") => void
}

export function CzechTextInput({
  onSubmit,
  onVoiceStart,
  isLoading,
  mode,
  onModeChange,
}: CzechTextInputProps) {
  const [text, setText] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Чешская клавиатура с диакритикой
  const CZECH_CHARS = ["á", "č", "ď", "é", "ě", "í", "ň", "ó", "ř", "š", "ť", "ú", "ů", "ý", "ž"]

  const insertChar = (char: string) => {
    if (textareaRef.current) {
      const start = textareaRef.current.selectionStart
      const end = textareaRef.current.selectionEnd
      const newText = text.slice(0, start) + char + text.slice(end)
      setText(newText)

      // Устанавливаем курсор после вставленного символа
      setTimeout(() => {
        textareaRef.current?.setSelectionRange(start + 1, start + 1)
        textareaRef.current?.focus()
      }, 0)
    }
  }

  const handleSubmit = () => {
    if (text.trim() && !isLoading) {
      onSubmit(text.trim())
      setText("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="space-y-3">
      {/* Переключатель режима */}
      <div className="flex justify-center gap-2">
        <button
          onClick={() => onModeChange("text")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            mode === "text"
              ? "bg-primary text-white"
              : "bg-gray-100 dark:bg-gray-800 hover:bg-gray-200"
          }`}
        >
          <Keyboard className="h-4 w-4" />
          Text
        </button>
        <button
          onClick={() => onModeChange("voice")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            mode === "voice"
              ? "bg-primary text-white"
              : "bg-gray-100 dark:bg-gray-800 hover:bg-gray-200"
          }`}
        >
          <Mic className="h-4 w-4" />
          Hlas
        </button>
      </div>

      {mode === "text" ? (
        <>
          {/* Чешская клавиатура (диакритика) */}
          <div className="flex flex-wrap gap-1 justify-center">
            {CZECH_CHARS.map((char) => (
              <motion.button
                key={char}
                whileTap={{ scale: 0.9 }}
                onClick={() => insertChar(char)}
                className="w-8 h-8 rounded bg-blue-100 dark:bg-blue-900 hover:bg-blue-200
                           dark:hover:bg-blue-800 text-blue-800 dark:text-blue-200
                           font-medium text-sm transition-colors"
              >
                {char}
              </motion.button>
            ))}
          </div>

          {/* Текстовое поле */}
          <div className="relative">
            <textarea
              ref={textareaRef}
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={CS_TEXTS.practice.input_placeholder}
              disabled={isLoading}
              rows={3}
              className="w-full p-4 pr-12 rounded-xl border-2 border-gray-200 dark:border-gray-700
                         focus:border-primary dark:focus:border-primary
                         bg-white dark:bg-gray-800 resize-none
                         disabled:opacity-50"
            />

            {/* Кнопка отправки */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={handleSubmit}
              disabled={!text.trim() || isLoading}
              className="absolute right-3 bottom-3 p-2 rounded-full
                         bg-primary text-white disabled:opacity-50
                         disabled:cursor-not-allowed"
            >
              <Send className="h-5 w-5" />
            </motion.button>
          </div>

          <p className="text-xs text-center text-gray-500">
            Enter pro odeslání • Shift+Enter pro nový řádek
          </p>
        </>
      ) : (
        // Голосовой режим
        <div className="text-center py-8">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onVoiceStart}
            disabled={isLoading}
            className="w-20 h-20 rounded-full bg-primary text-white shadow-lg
                       flex items-center justify-center mx-auto
                       disabled:opacity-50"
          >
            <Mic className="h-10 w-10" />
          </motion.button>
          <p className="text-sm text-gray-500 mt-3">
            {CS_TEXTS.practice.voice_hint}
          </p>
        </div>
      )}
    </div>
  )
}
```

---

## 💡 ИДЕИ ПО УЛУЧШЕНИЮ И НОВЫЕ ФУНКЦИИ

### Краткосрочные (1-2 месяца)

#### 1. 🎭 Ролевые сценарии с диалогами

Интерактивные мини-диалоги для реальных ситуаций:

| Сценарий | Описание | Уровень |
|----------|----------|---------|
| 🍺 V hospodě | Заказ пива и еды в чешском пабе | A1-A2 |
| 🏥 U lékaře | Визит к врачу, описание симптомов | A2-B1 |
| 🏦 Na cizinecké policii | Подача документов на ВНЖ | B1 |
| 💼 Pracovní pohovor | Собеседование на работу | B1-B2 |
| 🏠 Pronájem bytu | Аренда квартиры, общение с хозяином | A2-B1 |
| 🚋 V tramvaji | Покупка билета, уточнение маршрута | A1 |
| 🛒 V obchodě | Покупки в магазине | A1-A2 |
| 📞 Telefonní hovor | Телефонный разговор (сложнее!) | B1 |

```python
# backend/services/scenario_service.py
class ScenarioService:
    """Сервис для ролевых сценариев."""

    async def start_scenario(self, user_id: int, scenario_id: str) -> dict:
        """Начать новый сценарий."""
        scenario = SCENARIOS[scenario_id]

        # Генерируем начальную ситуацию
        initial_prompt = f"""
        Zahajuješ scénář: {scenario['name_cs']}
        Situace: {scenario['situation']}

        Tvoje role: {scenario['honzik_role']}
        Role studenta: {scenario['user_role']}

        Začni dialog jako {scenario['honzik_role']}.
        """

        response = await self.honzik.generate_scenario_response(initial_prompt)

        return {
            "scenario_id": scenario_id,
            "name": scenario['name_cs'],
            "step": 1,
            "total_steps": scenario['steps'],
            "honzik_message": response,
            "hints": scenario['hints'][0],  # Подсказки для первого шага
        }
```

#### 2. 📊 Детальная аналитика произношения

```python
# backend/services/pronunciation_analyzer.py
class PronunciationAnalyzer:
    """Анализ произношения с детализацией по звукам."""

    # Сложные звуки для русско/украиноговорящих
    DIFFICULT_SOUNDS = {
        "ř": {
            "description_cs": "Český zvuk Ř",
            "tip_cs": "Jazyk vibruje za horními zuby",
            "words": ["řeka", "moře", "příliš"],
        },
        "h": {
            "description_cs": "České H (ne ruské Г)",
            "tip_cs": "Měkké H, jako vzdech",
            "words": ["ahoj", "hora", "hodně"],
        },
        "ů/ú": {
            "description_cs": "Dlouhé Ú",
            "tip_cs": "Dlouhé ÚÚÚ, ne krátké У",
            "words": ["dům", "úterý", "průvodce"],
        },
    }

    async def analyze(self, audio: bytes, transcript: str) -> dict:
        """Анализировать произношение."""
        # Используем Whisper word-level timestamps
        detailed = await self.openai_client.transcribe_audio(
            audio,
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )

        issues = []
        for word_info in detailed.get("words", []):
            word = word_info["word"]
            # Проверяем сложные звуки
            for sound, info in self.DIFFICULT_SOUNDS.items():
                if sound in word.lower():
                    issues.append({
                        "word": word,
                        "sound": sound,
                        "tip": info["tip_cs"],
                        "practice_words": info["words"],
                    })

        return {
            "overall_score": self._calculate_score(detailed),
            "pronunciation_issues": issues,
            "recommendation": self._get_recommendation(issues),
        }
```

#### 3. 📚 Интеграция с учебниками

```python
# Привязка уроков к популярным учебникам чешского
TEXTBOOK_INTEGRATION = {
    "czech_step_by_step": {
        "name": "Czech Step by Step",
        "lessons": {
            1: ["pozdravy", "představování"],
            2: ["rodina", "čísla"],
            # ...
        }
    },
    "communicative_czech": {
        "name": "Communicative Czech",
        "lessons": {...}
    }
}

# Пользователь может выбрать учебник и урок
# Хонзик будет использовать лексику из этого урока
```

### Среднесрочные (3-6 месяцев)

#### 4. 🎮 Мини-игры для изучения

| Игра | Описание | Награда |
|------|----------|---------|
| 🎯 Slovní hádanka | Угадай слово по описанию | 3 ⭐ |
| 🔤 Doplň písmeno | Вставь пропущенную букву | 2 ⭐ |
| 🎭 Rychlá odpověď | Ответь за 10 секунд | 5 ⭐ |
| 🧩 Sestav větu | Собери предложение из слов | 4 ⭐ |
| 👂 Co slyšíš? | Напиши услышанное слово | 3 ⭐ |

#### 5. 👥 Групповые функции

```typescript
// Групповые челленджи
interface GroupChallenge {
  id: string;
  name: string;
  participants: User[];
  goal: {
    type: "total_messages" | "total_words" | "avg_accuracy";
    value: number;
    deadline: Date;
  };
  rewards: {
    winner: number;  // звёзды победителю
    participants: number;  // звёзды всем участникам
  };
}
```

#### 6. 🏆 Сезонные события

```python
# Сезонные челленджи и награды
SEASONAL_EVENTS = {
    "christmas": {
        "name_cs": "🎄 Vánoční výzva",
        "duration": "20-31 декабря",
        "theme": "Рождество в Чехии",
        "vocabulary": ["Vánoce", "dárek", "stromeček", "kapr", "cukroví"],
        "special_achievement": "🎄 Vánoční mluvčí",
        "bonus_stars": 50,
    },
    "easter": {
        "name_cs": "🐣 Velikonoční výzva",
        "duration": "Пасхальная неделя",
        "theme": "Чешская Пасха",
        "vocabulary": ["Velikonoce", "pomlázka", "kraslice", "beránek"],
        "special_achievement": "🐣 Velikonoční mistr",
    },
    "october_fest": {
        "name_cs": "🍺 Pivní měsíc",
        "duration": "Октябрь",
        "theme": "Чешское пиво",
        "vocabulary": ["pivo", "hospoda", "čepované", "plzeň", "ležák"],
        "special_achievement": "🍺 Pivní znalec",
    },
}
```

### Долгосрочные (6+ месяцев)

#### 7. 🤖 Множественные AI-персонажи

| Персонаж | Голос | Характер | Специализация |
|----------|-------|----------|---------------|
| 🧔 Honzík | alloy | Весёлый чех | Общие темы, пиво, хоккей |
| 👩 Markéta | nova | Элегантная | Культура, искусство, мода |
| 👴 Dědeček | onyx | Мудрый | История, традиции, пословицы |
| 👧 Terezka | shimmer | Молодёжная | Сленг, современный чешский |
| 👨‍🏫 Pan Profesor | echo | Строгий | Грамматика, формальный стиль |

#### 8. 📱 Мобильное приложение (PWA → Native)

```
Native App Benefits:
- Push уведомления
- Offline режим
- Background audio
- Виджеты на главном экране
- Apple Watch / Wear OS интеграция
```

#### 9. 🎓 Подготовка к экзаменам

```python
# Подготовка к официальным экзаменам по чешскому
EXAM_PREPARATION = {
    "a1_vnzh": {
        "name": "Čeština pro ВНЖ (A1)",
        "description": "Экзамен для получения ВНЖ в Чехии",
        "modules": [
            "listening_comprehension",
            "reading_comprehension",
            "writing",
            "speaking",
        ],
        "mock_tests": 5,
        "duration_weeks": 8,
    },
    "a2_pmzh": {
        "name": "Čeština pro ПМЖ (A2)",
        "description": "Экзамен для получения ПМЖ",
        # ...
    },
    "b1_citizenship": {
        "name": "Čeština pro občanství (B1)",
        "description": "Экзамен для гражданства",
        # ...
    }
}
```

#### 10. 🌐 Расширение на другие славянские языки

```
Потенциальные языки:
- 🇸🇰 Словацкий (очень близок к чешскому)
- 🇵🇱 Польский
- 🇭🇷 Хорватский
- 🇸🇮 Словенский

Архитектура позволяет добавить новый язык:
- Новый персонаж (Jano для словацкого)
- Новые промпты
- Адаптация TTS/STT
- Локализация
```

### Экспериментальные идеи

#### 11. 🎥 Видео-аватар Хонзика

```
Технологии:
- D-ID / HeyGen для генерации видео
- Lip-sync с TTS
- Эмоции по контексту разговора

Применение:
- Приветствие при первом входе
- Поздравление с достижениями
- Объяснение сложной грамматики
```

#### 12. 🔊 Анализ в реальном времени

```
Real-time Pronunciation Feedback:
- WebRTC streaming
- Whisper streaming API
- Мгновенная обратная связь
- "Попробуй ещё раз: ŘŘŘ"
```

#### 13. 📖 Генерация персонализированных историй

```python
async def generate_story_for_user(user: User) -> str:
    """Генерирует историю на чешском под уровень пользователя."""
    prompt = f"""
    Napiš krátký příběh (100-150 slov) na úrovni {user.level}.

    Téma: {random.choice(user.favorite_topics)}
    Slovní zásoba: použij slova, která student zná: {user.known_words[:20]}
    Nová slova: přidej 3-5 nových slov s vysvětlením

    Na konci přidej:
    - 3 otázky k příběhu
    - Slovníček nových slov
    """

    return await openai_client.generate(prompt)
```

#### 14. 🎧 Подкаст от Хонзика

```
Еженедельный AI-генерируемый подкаст:
- 5-10 минут на чешском
- Адаптирован под уровень
- Новости из Чехии
- Интересные факты
- Разбор полезных фраз
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

### Фаза 4: Чешский интерфейс + Текст (2-3 недели)

| Задача | Приоритет | Оценка |
|--------|-----------|--------|
| Локализация UI на чешский | 🔴 Критично | 4 дня |
| Миграция ui_language → native_language | 🔴 Критично | 1 день |
| Текстовый endpoint в backend | 🔴 Критично | 2 дня |
| Обработчик текста в боте | 🔴 Критично | 2 дня |
| Чешская клавиатура с диакритикой | 🟠 Высокий | 1 день |
| Адаптивные объяснения ошибок | 🟠 Высокий | 2 дня |

### Фаза 5: Frontend (1-2 недели)

| Задача | Приоритет | Оценка |
|--------|-----------|--------|
| Server Components | 🟠 Высокий | 3 дня |
| Optimistic updates | 🟠 Высокий | 2 дня |
| Новый Onboarding | 🟡 Средний | 2 дня |
| Анимации достижений | 🟡 Средний | 2 дня |

### Фаза 6: Новые функции (4+ недели)

| Задача | Приоритет | Оценка |
|--------|-----------|--------|
| Ролевые сценарии | 🟠 Высокий | 1 неделя |
| Анализ произношения | 🟡 Средний | 1 неделя |
| Мини-игры | 🟡 Средний | 1 неделя |
| Подготовка к экзаменам | 🟡 Средний | 2 недели |

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
