# Performance Optimization Roadmap

**Project:** Mluv.Me
**Last Updated:** December 7, 2025
**Status:** Ready for Implementation
**Expected Timeline:** 8-12 weeks
**Priority:** HIGH

---

## 📊 Executive Summary

This roadmap focuses on optimizing Mluv.Me's performance through caching, asynchronous processing, and database improvements. Expected outcomes include:
- **65-70% reduction** in response times
- **60-75% reduction** in database load
- **15-25% reduction** in OpenAI API costs
- **3-5x improvement** in scalability

---

## 🎯 Goals & Success Metrics

### Primary Goals
1. Reduce average response time from 200ms to <70ms
2. Handle 1000+ concurrent users without degradation
3. Reduce infrastructure costs per user by 40-50%
4. Achieve 99.9% uptime

### Key Performance Indicators (KPIs)
| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| API Response Time (p95) | 200ms | <70ms | Prometheus/Sentry |
| Database Query Time (p95) | 80ms | <10ms | Query logs |
| OpenAI API Cost per User | $0.15 | <$0.12 | Cost tracking |
| Concurrent Users Supported | 250 | 1000+ | Load testing |
| Cache Hit Rate | 0% | 85%+ | Redis metrics |

---

## 🚀 Phase 1: Redis Caching Implementation (2 weeks)

### Priority: CRITICAL
**Impact:** Immediate 60-70% latency reduction
**Effort:** 1-2 weeks
**Dependencies:** None

### 1.1 Infrastructure Setup

#### Task 1.1.1: Redis Installation & Configuration
**Duration:** 1-2 days

```yaml
# railway.json - Add Redis service
{
  "services": [
    {
      "name": "redis",
      "plan": "starter",
      "image": "redis:7-alpine"
    }
  ]
}
```

```python
# backend/config.py - Add Redis configuration
REDIS_URL: str = Field(default="redis://localhost:6379/0")
REDIS_MAX_CONNECTIONS: int = Field(default=50)
REDIS_CACHE_TTL_DEFAULT: int = Field(default=3600)
REDIS_CACHE_TTL_USER: int = Field(default=3600)
REDIS_CACHE_TTL_STATS: int = Field(default=900)
REDIS_CACHE_TTL_OPENAI: int = Field(default=86400)
CACHE_ENABLED: bool = Field(default=True)
```

**Acceptance Criteria:**
- [ ] Redis deployed on Railway.com
- [ ] Connection pool configured
- [ ] Health check endpoint responds
- [ ] Configuration loaded from environment

#### Task 1.1.2: Redis Client Implementation
**Duration:** 1 day

```python
# backend/cache/redis_client.py
from redis.asyncio import Redis, ConnectionPool
from typing import Optional, Any
import json
from backend.config import settings

class RedisClient:
    """Async Redis client with connection pooling"""

    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.redis: Optional[Redis] = None

    async def connect(self):
        """Initialize Redis connection pool"""
        self.pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True
        )
        self.redis = Redis(connection_pool=self.pool)

    async def disconnect(self):
        """Close Redis connections"""
        if self.redis:
            await self.redis.close()
        if self.pool:
            await self.pool.disconnect()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not settings.CACHE_ENABLED:
            return None
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = None
    ) -> bool:
        """Set value in cache with TTL"""
        if not settings.CACHE_ENABLED:
            return False
        ttl = ttl or settings.REDIS_CACHE_TTL_DEFAULT
        return await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return await self.redis.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.redis.exists(key) > 0

redis_client = RedisClient()
```

**Acceptance Criteria:**
- [ ] Async connection pool working
- [ ] JSON serialization/deserialization
- [ ] TTL support
- [ ] Unit tests passing

### 1.2 User Data Caching

#### Task 1.2.1: Cache Key Pattern Design
**Duration:** 0.5 days

```python
# backend/cache/cache_keys.py
from typing import Optional

class CacheKeys:
    """Centralized cache key patterns"""

    # User data
    USER_PROFILE = "user:{telegram_id}:profile"
    USER_SETTINGS = "user:{telegram_id}:settings"
    USER_HISTORY = "user:{telegram_id}:history:{limit}"

    # Statistics
    DAILY_STATS = "stats:{user_id}:daily:{date}"
    USER_PROGRESS = "stats:{user_id}:progress"
    LEADERBOARD = "leaderboard:{period}:{limit}"

    # OpenAI responses
    HONZIK_RESPONSE = "honzik:response:{hash}"
    WHISPER_TRANSCRIPTION = "whisper:{audio_hash}"
    TTS_AUDIO = "tts:{text_hash}:{voice}"

    # Vocabulary
    SAVED_WORDS = "words:{user_id}:all"
    WORD_DUE_REVIEW = "words:{user_id}:due"

    @staticmethod
    def user_profile(telegram_id: int) -> str:
        return CacheKeys.USER_PROFILE.format(telegram_id=telegram_id)

    @staticmethod
    def user_settings(telegram_id: int) -> str:
        return CacheKeys.USER_SETTINGS.format(telegram_id=telegram_id)

    @staticmethod
    def user_history(telegram_id: int, limit: int = 10) -> str:
        return CacheKeys.USER_HISTORY.format(
            telegram_id=telegram_id,
            limit=limit
        )

    @staticmethod
    def honzik_response(user_text: str, settings_hash: str) -> str:
        """Create cache key for Honzik response"""
        import hashlib
        content = f"{user_text}:{settings_hash}"
        hash_key = hashlib.sha256(content.encode()).hexdigest()[:16]
        return CacheKeys.HONZIK_RESPONSE.format(hash=hash_key)
```

**Acceptance Criteria:**
- [ ] All key patterns documented
- [ ] Consistent naming convention
- [ ] Helper methods for common keys
- [ ] Type hints included

#### Task 1.2.2: User Repository Caching
**Duration:** 2 days

```python
# backend/db/repositories.py - Add caching to UserRepository

from backend.cache.redis_client import redis_client
from backend.cache.cache_keys import CacheKeys

class UserRepository:

    async def get_by_telegram_id(
        self,
        telegram_id: int,
        use_cache: bool = True
    ) -> Optional[User]:
        """Get user by Telegram ID with caching"""

        # Try cache first
        if use_cache:
            cache_key = CacheKeys.user_profile(telegram_id)
            cached = await redis_client.get(cache_key)
            if cached:
                return User(**cached)

        # Database query
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        # Cache result
        if user and use_cache:
            cache_key = CacheKeys.user_profile(telegram_id)
            await redis_client.set(
                cache_key,
                user.to_dict(),
                ttl=settings.REDIS_CACHE_TTL_USER
            )

        return user

    async def update(self, user_id: int, **kwargs) -> User:
        """Update user and invalidate cache"""
        user = await self._update_db(user_id, **kwargs)

        # Invalidate cache
        if user:
            cache_key = CacheKeys.user_profile(user.telegram_id)
            await redis_client.delete(cache_key)

        return user
```

**Acceptance Criteria:**
- [ ] Cache-first lookup strategy
- [ ] Automatic cache invalidation on updates
- [ ] Configurable cache bypass
- [ ] 85%+ cache hit rate in production

### 1.3 OpenAI Response Caching

#### Task 1.3.1: Response Hash Generation
**Duration:** 1 day

```python
# backend/services/cache_service.py

import hashlib
from typing import Dict, Any

class CacheService:
    """High-level caching logic"""

    def create_openai_cache_key(
        self,
        user_text: str,
        settings: Dict[str, Any],
        model: str
    ) -> str:
        """Create deterministic cache key for OpenAI responses"""
        # Include relevant settings that affect response
        cache_input = {
            "text": user_text.lower().strip(),
            "level": settings.get("czech_level"),
            "correction_level": settings.get("correction_level"),
            "model": model
        }

        # Create hash
        content = json.dumps(cache_input, sort_keys=True)
        hash_key = hashlib.sha256(content.encode()).hexdigest()[:16]

        return CacheKeys.HONZIK_RESPONSE.format(hash=hash_key)

    async def get_cached_honzik_response(
        self,
        user_text: str,
        settings: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached Honzik response if available"""
        cache_key = self.create_openai_cache_key(
            user_text,
            settings,
            "gpt-4o"
        )
        return await redis_client.get(cache_key)

    async def cache_honzik_response(
        self,
        user_text: str,
        settings: Dict[str, Any],
        response: Dict[str, Any]
    ):
        """Cache Honzik response"""
        cache_key = self.create_openai_cache_key(
            user_text,
            settings,
            "gpt-4o"
        )
        await redis_client.set(
            cache_key,
            response,
            ttl=settings.REDIS_CACHE_TTL_OPENAI
        )
```

**Acceptance Criteria:**
- [ ] Deterministic hash generation
- [ ] Cache hit tracking
- [ ] 15-20% hit rate for common phrases
- [ ] Cost savings measurable

### 1.4 Statistics Caching

#### Task 1.4.1: Daily Stats Caching
**Duration:** 1 day

```python
# backend/routers/stats.py - Add caching

@router.get("/api/v1/stats/{user_id}")
async def get_user_stats(user_id: int):
    """Get user statistics with caching"""

    cache_key = CacheKeys.DAILY_STATS.format(
        user_id=user_id,
        date=datetime.now().date()
    )

    # Try cache
    cached_stats = await redis_client.get(cache_key)
    if cached_stats:
        return cached_stats

    # Calculate stats
    stats = await stats_service.calculate_daily_stats(user_id)

    # Cache until end of day
    seconds_until_midnight = (
        datetime.combine(datetime.now().date() + timedelta(days=1), time.min)
        - datetime.now()
    ).seconds

    await redis_client.set(cache_key, stats, ttl=seconds_until_midnight)

    return stats
```

**Acceptance Criteria:**
- [ ] Dynamic TTL based on day end
- [ ] Cache invalidation on new activity
- [ ] Reduced DB load by 70%+

### 1.5 Testing & Monitoring

#### Task 1.5.1: Cache Performance Tests
**Duration:** 1 day

```python
# tests/test_caching.py

import pytest
from backend.cache.redis_client import redis_client

@pytest.mark.asyncio
async def test_cache_hit_rate():
    """Test cache hit rate for user lookups"""
    # Warm up cache
    for i in range(100):
        await user_repo.get_by_telegram_id(123456)

    # Measure hits
    hits = 0
    for i in range(100):
        result = await user_repo.get_by_telegram_id(123456)
        if result:  # Cache hit
            hits += 1

    assert hits >= 85  # 85% hit rate target

@pytest.mark.asyncio
async def test_cache_invalidation():
    """Test cache is invalidated on update"""
    user = await user_repo.get_by_telegram_id(123456)

    # Update user
    await user_repo.update(user.id, first_name="NewName")

    # Verify cache invalidated
    cache_key = CacheKeys.user_profile(123456)
    cached = await redis_client.get(cache_key)
    assert cached is None
```

**Acceptance Criteria:**
- [ ] All cache tests passing
- [ ] Hit rate > 85%
- [ ] Cache invalidation working
- [ ] Load test showing improvement

---

## 🔄 Phase 2: Task Queue System (2 weeks)

### Priority: HIGH
**Impact:** 85-90% reduction in user-perceived latency
**Effort:** 2 weeks
**Dependencies:** Phase 1 (Redis)

### 2.1 Celery Setup

#### Task 2.1.1: Celery Installation & Configuration
**Duration:** 1 day

```python
# backend/tasks/celery_app.py

from celery import Celery
from backend.config import settings

celery_app = Celery(
    'mluv_tasks',
    broker=f'{settings.REDIS_URL}/1',
    backend=f'{settings.REDIS_URL}/2'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)
```

**Acceptance Criteria:**
- [ ] Celery worker starts successfully
- [ ] Redis broker connection working
- [ ] Task routing configured
- [ ] Error handling in place

### 2.2 Background Task Implementation

#### Task 2.2.1: Statistics Aggregation Tasks
**Duration:** 2 days

```python
# backend/tasks/analytics.py

from backend.tasks.celery_app import celery_app
from backend.db.repositories import DailyStatsRepository
from backend.services.gamification import GamificationService

@celery_app.task(bind=True, max_retries=3)
def calculate_daily_statistics(self, user_id: int):
    """Calculate and cache daily statistics"""
    try:
        stats_service = GamificationService()
        stats = await stats_service.calculate_daily_stats(user_id)

        # Cache results
        cache_key = CacheKeys.DAILY_STATS.format(
            user_id=user_id,
            date=datetime.now().date()
        )
        await redis_client.set(cache_key, stats, ttl=86400)

        return stats
    except Exception as exc:
        self.retry(exc=exc, countdown=60)

@celery_app.task(rate_limit='10/m')
def aggregate_platform_metrics():
    """Platform-wide analytics (rate-limited)"""
    # Total users, active users, messages today, etc.
    pass

@celery_app.task
def generate_weekly_report(user_id: int):
    """Generate weekly progress report"""
    pass
```

**Acceptance Criteria:**
- [ ] Tasks execute in background
- [ ] Retry logic working
- [ ] Rate limiting effective
- [ ] Monitoring integrated

#### Task 2.2.2: Notification Tasks
**Duration:** 2 days

```python
# backend/tasks/notifications.py

@celery_app.task(bind=True, max_retries=5)
def send_streak_reminder(self, user_id: int):
    """Send notification if user hasn't practiced today"""
    user = await user_repo.get_by_id(user_id)

    # Check if practiced today
    today_messages = await message_repo.get_by_user_and_date(
        user_id,
        datetime.now().date()
    )

    if not today_messages:
        # Send Telegram notification
        await bot.send_message(
            user.telegram_id,
            _("🔥 Don't lose your streak! Practice today to keep it going!")
        )

@celery_app.task
def send_daily_challenge():
    """Send daily challenge to all active users"""
    pass
```

**Acceptance Criteria:**
- [ ] Notifications sent reliably
- [ ] Retry on failure
- [ ] User preferences respected
- [ ] Deliverability > 95%

### 2.3 Scheduled Tasks

#### Task 2.3.1: Celery Beat Configuration
**Duration:** 1 day

```python
# backend/tasks/celery_app.py - Add beat schedule

from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'check-streaks-daily': {
        'task': 'backend.tasks.gamification.check_and_reset_streaks',
        'schedule': crontab(hour=0, minute=5),  # 00:05 UTC daily
    },
    'send-daily-reminders': {
        'task': 'backend.tasks.notifications.send_daily_reminders',
        'schedule': crontab(hour=18, minute=0),  # 18:00 UTC daily
    },
    'aggregate-metrics': {
        'task': 'backend.tasks.analytics.aggregate_platform_metrics',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'cleanup-old-data': {
        'task': 'backend.tasks.maintenance.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Monday 02:00
    },
}
```

**Acceptance Criteria:**
- [ ] Beat scheduler running
- [ ] Tasks execute on schedule
- [ ] Timezone handling correct
- [ ] Logs show execution

### 2.4 Monitoring & Error Handling

#### Task 2.4.1: Celery Flower Setup
**Duration:** 0.5 days

```bash
# Start Flower for monitoring
celery -A backend.tasks.celery_app flower --port=5555
```

```python
# backend/tasks/monitoring.py

from celery.signals import task_failure, task_success
import sentry_sdk

@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    """Log task failures to Sentry"""
    sentry_sdk.capture_exception(exception)

@task_success.connect
def track_task_success(sender=None, result=None, **kwargs):
    """Track successful task execution"""
    # Log to metrics
    pass
```

**Acceptance Criteria:**
- [ ] Flower dashboard accessible
- [ ] Failed tasks visible
- [ ] Metrics exported to Prometheus
- [ ] Alerts configured

---

## 💾 Phase 3: Database Optimization (2 weeks)

### Priority: HIGH
**Impact:** 10-20x query speedup
**Effort:** 2 weeks
**Dependencies:** None

### 3.1 Index Creation

#### Task 3.1.1: Missing Indexes Migration
**Duration:** 1 day

```python
# alembic/versions/20251208_add_performance_indexes.py

def upgrade():
    # Messages table indexes
    op.create_index(
        'idx_messages_user_created',
        'messages',
        ['user_id', sa.text('created_at DESC')],
        postgresql_concurrently=True
    )

    # Daily stats indexes
    op.create_index(
        'idx_daily_stats_user_date',
        'daily_stats',
        ['user_id', sa.text('date DESC')],
        postgresql_concurrently=True
    )

    # Saved words indexes
    op.create_index(
        'idx_saved_words_user_word',
        'saved_words',
        ['user_id', 'word'],
        postgresql_concurrently=True
    )

    # Full-text search index for messages
    op.execute("""
        CREATE INDEX CONCURRENTLY idx_messages_text_search
        ON messages USING gin(to_tsvector('czech', user_text))
        WHERE user_text IS NOT NULL
    """)

def downgrade():
    op.drop_index('idx_messages_user_created')
    op.drop_index('idx_daily_stats_user_date')
    op.drop_index('idx_saved_words_user_word')
    op.drop_index('idx_messages_text_search')
```

**Acceptance Criteria:**
- [ ] All indexes created successfully
- [ ] EXPLAIN ANALYZE shows index usage
- [ ] Query times reduced by 10-15x
- [ ] No production downtime

### 3.2 Query Optimization

#### Task 3.2.1: Eager Loading Implementation
**Duration:** 2 days

```python
# backend/db/repositories.py

from sqlalchemy.orm import selectinload, joinedload

class UserRepository:

    async def get_by_telegram_id_with_relations(
        self,
        telegram_id: int,
        include: list[str] = None
    ) -> Optional[User]:
        """Get user with related data in single query"""
        query = select(User).where(User.telegram_id == telegram_id)

        if include:
            if 'settings' in include:
                query = query.options(joinedload(User.settings))

            if 'recent_messages' in include:
                query = query.options(
                    selectinload(User.messages)
                    .limit(10)
                    .options(selectinload(Message.corrections))
                )

            if 'daily_stats' in include:
                query = query.options(
                    selectinload(User.daily_stats)
                    .limit(30)
                )

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()
```

**Acceptance Criteria:**
- [ ] N+1 queries eliminated
- [ ] 3-5 queries reduced to 1
- [ ] Response time improved 60%+
- [ ] Tests verify eager loading

### 3.3 Connection Pool Tuning

#### Task 3.3.1: Optimize Pool Settings
**Duration:** 1 day

```python
# backend/db/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool, QueuePool

engine = create_async_engine(
    settings.DATABASE_URL,
    # Connection pool settings
    poolclass=QueuePool,
    pool_size=20,              # Up from default 5
    max_overflow=10,           # Additional connections
    pool_timeout=30,           # Wait time for connection
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Verify connection health
    echo=settings.IS_DEVELOPMENT,
    # Query optimization
    connect_args={
        "server_settings": {
            "application_name": "mluv_backend",
            "jit": "off"  # Disable JIT for simple queries
        }
    }
)
```

**Acceptance Criteria:**
- [ ] Connection pool not exhausted under load
- [ ] Connection acquisition < 10ms
- [ ] No connection timeout errors
- [ ] Pool metrics monitored

### 3.4 Materialized Views

#### Task 3.4.1: Create Analytics Views
**Duration:** 2 days

```sql
-- alembic/versions/20251209_create_materialized_views.py

CREATE MATERIALIZED VIEW user_stats_summary AS
SELECT
    u.id,
    u.telegram_id,
    u.first_name,
    u.created_at,
    COUNT(DISTINCT m.id) as total_messages,
    AVG(m.correctness_score) as avg_correctness,
    MAX(ds.streak) as max_streak,
    COALESCE(SUM(s.count), 0) as total_stars,
    MAX(m.created_at) as last_activity
FROM users u
LEFT JOIN messages m ON m.user_id = u.id
LEFT JOIN daily_stats ds ON ds.user_id = u.id
LEFT JOIN stars s ON s.user_id = u.id
GROUP BY u.id, u.telegram_id, u.first_name, u.created_at;

CREATE INDEX ON user_stats_summary(telegram_id);
CREATE INDEX ON user_stats_summary(total_stars DESC);
CREATE INDEX ON user_stats_summary(max_streak DESC);
```

```python
# backend/tasks/maintenance.py

@celery_app.task
def refresh_materialized_views():
    """Refresh materialized views hourly"""
    await session.execute(text(
        "REFRESH MATERIALIZED VIEW CONCURRENTLY user_stats_summary"
    ))
```

**Acceptance Criteria:**
- [ ] Views created successfully
- [ ] Refresh task running hourly
- [ ] Dashboard queries 10x faster
- [ ] No locking issues

---

## ⚡ Phase 4: Code-Level Optimizations (1 week)

### Priority: MEDIUM
**Impact:** 20-30% improvement
**Effort:** 1 week
**Dependencies:** None

### 4.1 Async I/O Improvements

#### Task 4.1.1: Replace Blocking File Operations
**Duration:** 1 day

```python
# requirements.txt
aiofiles==23.2.1

# backend/routers/lesson.py

import aiofiles

@router.post("/api/v1/lessons/process")
async def process_lesson(audio: UploadFile):
    # Read audio asynchronously
    audio_bytes = await audio.read()

    # Write to temp file asynchronously
    temp_path = f"/tmp/{audio.filename}"
    async with aiofiles.open(temp_path, "wb") as f:
        await f.write(audio_bytes)

    # Process...

    # Clean up asynchronously
    async with aiofiles.open(temp_path, "rb") as f:
        content = await f.read()
```

**Acceptance Criteria:**
- [ ] All file I/O async
- [ ] No blocking operations
- [ ] Tests passing
- [ ] Performance improvement measured

### 4.2 Pydantic V2 Optimization

#### Task 4.2.1: Enable Performance Features
**Duration:** 1 day

```python
# backend/schemas/lesson.py

from pydantic import BaseModel, ConfigDict

class LessonProcessResponse(BaseModel):
    model_config = ConfigDict(
        # Performance optimizations
        use_enum_values=True,
        validate_assignment=False,
        arbitrary_types_allowed=True,
        # Serialization
        ser_json_timedelta='float',
        ser_json_bytes='base64',
        # Validation
        str_strip_whitespace=True,
        str_to_lower=False,
    )

    honzik_text: str
    user_mistakes: list[str]
    suggestions: list[str]
    stars_earned: int
```

**Acceptance Criteria:**
- [ ] All schemas updated
- [ ] Serialization 20-30% faster
- [ ] No breaking changes
- [ ] Benchmarks show improvement

### 4.3 OpenAI API Optimization

#### Task 4.3.1: Token Usage Optimization
**Duration:** 2 days

```python
# backend/services/honzik_personality.py

def optimize_conversation_history(
    self,
    messages: list[Message],
    max_tokens: int = 1500
) -> list[dict]:
    """Intelligently truncate conversation history"""

    # Always keep last 3 messages
    recent = messages[:3]

    # Estimate tokens
    if self._estimate_tokens(messages) <= max_tokens:
        return self._format_all(messages)

    # Summarize older messages
    older = messages[3:]
    summary = await self._summarize_older_messages(older)

    return self._format_all(recent) + [summary]

async def _summarize_older_messages(
    self,
    messages: list[Message]
) -> dict:
    """Summarize older messages using GPT-3.5-turbo"""
    summary_prompt = f"""
    Summarize the following conversation in 2-3 sentences,
    focusing on key mistakes and learning points:
    {self._format_messages(messages)}
    """

    response = await openai_client.generate_chat_completion(
        messages=[{"role": "user", "content": summary_prompt}],
        model="gpt-3.5-turbo"  # Cheaper for summarization
    )

    return {
        "role": "system",
        "content": f"Previous conversation summary: {response}"
    }
```

**Acceptance Criteria:**
- [ ] Token usage reduced 30-40%
- [ ] Conversation quality maintained
- [ ] Cost savings measurable
- [ ] A/B test shows no quality degradation

#### Task 4.3.2: Model Selection Strategy
**Duration:** 1 day

```python
# backend/services/openai_client.py

MODEL_STRATEGY = {
    'transcription': 'whisper-1',
    'tts': 'tts-1',
    'analysis_advanced': 'gpt-4o',
    'analysis_simple': 'gpt-3.5-turbo',
    'summarization': 'gpt-3.5-turbo',
}

def get_analysis_model(czech_level: str) -> str:
    """Select model based on user level"""
    if czech_level in ['A1', 'A2']:
        return MODEL_STRATEGY['analysis_simple']  # 10x cheaper
    return MODEL_STRATEGY['analysis_advanced']
```

**Acceptance Criteria:**
- [ ] Model selection dynamic
- [ ] 40-50% cost savings for beginners
- [ ] Quality maintained per level
- [ ] Metrics tracked

---

## 📊 Phase 5: Load Testing & Validation (1 week)

### Priority: HIGH
**Impact:** Confidence in scalability
**Effort:** 1 week
**Dependencies:** Phases 1-4

### 5.1 Load Testing Setup

#### Task 5.1.1: Locust Load Tests
**Duration:** 2 days

```python
# tests/load/locustfile.py

from locust import HttpUser, task, between
import random

class MluvMeUser(HttpUser):
    wait_time = between(2, 5)

    def on_start(self):
        """Setup test user"""
        self.user_id = random.randint(10000, 99999)

    @task(5)
    def process_voice_message(self):
        """Main user flow - send voice message"""
        with open("test_audio.ogg", "rb") as audio:
            self.client.post(
                f"/api/v1/lessons/process?user_id={self.user_id}",
                files={"audio": audio}
            )

    @task(2)
    def get_user_stats(self):
        """Check statistics"""
        self.client.get(f"/api/v1/stats/{self.user_id}")

    @task(1)
    def get_saved_words(self):
        """View vocabulary"""
        self.client.get(f"/api/v1/words/{self.user_id}")
```

**Run Commands:**
```bash
# Gradually ramp up to 1000 users
locust -f tests/load/locustfile.py \
    --host=https://api.mluv.me \
    --users=1000 \
    --spawn-rate=50 \
    --run-time=30m \
    --html=load_test_report.html
```

**Acceptance Criteria:**
- [ ] 1000 concurrent users supported
- [ ] p95 response time < 500ms
- [ ] Error rate < 1%
- [ ] No memory leaks
- [ ] Database connections stable

### 5.2 Performance Benchmarking

#### Task 5.2.1: Before/After Comparison
**Duration:** 1 day

**Metrics to Track:**
| Metric | Before | Target | Actual |
|--------|--------|--------|--------|
| API Response (p50) | 200ms | <50ms | ___ |
| API Response (p95) | 450ms | <150ms | ___ |
| DB Query Time (avg) | 80ms | <10ms | ___ |
| Cache Hit Rate | 0% | >85% | ___ |
| OpenAI Cost/User | $0.15 | <$0.12 | ___ |
| Concurrent Users | 250 | 1000+ | ___ |

**Acceptance Criteria:**
- [ ] All targets met or exceeded
- [ ] Performance gains documented
- [ ] Regression tests passing
- [ ] Production monitoring confirms improvements

---

## 📈 Success Criteria & Rollout

### Definition of Done
- [ ] All phases completed
- [ ] Tests passing (unit, integration, load)
- [ ] Documentation updated
- [ ] Monitoring dashboards created
- [ ] Rollback plan documented
- [ ] Team training completed

### Rollout Strategy

#### Week 1-2: Staging Environment
- Deploy all optimizations to staging
- Run load tests
- Fix any issues
- Validate performance gains

#### Week 3: Gradual Production Rollout
- **Day 1-2:** Enable caching for 10% of users
- **Day 3-4:** Increase to 50% of users
- **Day 5:** Full rollout if metrics good
- **Day 6-7:** Monitor and optimize

#### Week 4: Task Queue Rollout
- Enable background tasks
- Monitor Celery workers
- Adjust worker count as needed

### Monitoring & Alerts

```python
# backend/monitoring/alerts.py

# Prometheus alerts
alerts = {
    "high_response_time": {
        "condition": "p95_response_time > 200ms",
        "action": "notify_team"
    },
    "low_cache_hit_rate": {
        "condition": "cache_hit_rate < 80%",
        "action": "investigate_cache"
    },
    "celery_queue_backed_up": {
        "condition": "queue_length > 1000",
        "action": "scale_workers"
    }
}
```

---

## 💰 Cost-Benefit Analysis

### Development Costs
| Phase | Effort | Cost (at $75/hr) |
|-------|--------|------------------|
| Phase 1: Redis Caching | 2 weeks | $6,000 |
| Phase 2: Task Queue | 2 weeks | $6,000 |
| Phase 3: Database Optimization | 2 weeks | $6,000 |
| Phase 4: Code Optimizations | 1 week | $3,000 |
| Phase 5: Load Testing | 1 week | $3,000 |
| **Total** | **8 weeks** | **$24,000** |

### Operational Costs
| Service | Monthly Cost |
|---------|--------------|
| Redis (Railway Starter) | $5 |
| Increased DB resources | $10 |
| **Total** | **$15/month** |

### Expected Savings/Benefits
| Benefit | Monthly Value |
|---------|---------------|
| Reduced infrastructure costs (40%) | $200 |
| OpenAI API savings (20%) | $500 |
| Support time savings (faster debugging) | $300 |
| Ability to handle 4x users without scaling | $1,000 |
| **Total Monthly Benefit** | **$2,000** |

### ROI
- **Payback Period:** 12 months
- **3-Year ROI:** 200%+
- **Non-monetary:** Better UX, scalability, reliability

---

## 📚 References & Resources

### Documentation
- FastAPI Performance: https://fastapi.tiangolo.com/advanced/performance/
- Redis Best Practices: https://redis.io/docs/manual/patterns/
- Celery User Guide: https://docs.celeryq.dev/
- SQLAlchemy Performance: https://docs.sqlalchemy.org/en/20/faq/performance.html

### Tools
- Locust (load testing): https://locust.io/
- Redis Commander: https://joeferner.github.io/redis-commander/
- Celery Flower: https://flower.readthedocs.io/

### Benchmarks
- Web API Response Times: https://www.nngroup.com/articles/response-times-3-important-limits/
- Database Query Performance: https://use-the-index-luke.com/

---

**Next Steps:**
1. Review and approve roadmap
2. Allocate development resources
3. Set up project tracking (Jira/Linear)
4. Begin Phase 1: Redis Caching
5. Weekly progress reviews

**Contact:** Development Team
**Last Reviewed:** December 7, 2025
