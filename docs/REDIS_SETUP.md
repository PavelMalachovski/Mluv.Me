# Redis Caching Setup Guide

## 📌 Overview

This guide explains how to set up and configure Redis caching for the Mluv.Me application, following **Phase 1: Redis Caching Implementation** from the performance optimization roadmap.

## 🚀 Features Implemented

✅ **Infrastructure Setup**
- Async Redis client with connection pooling
- Centralized cache key patterns
- Environment-based configuration

✅ **User Data Caching**
- User profile caching with automatic invalidation
- User settings caching
- Cache-first lookup strategy
- Configurable cache bypass

✅ **OpenAI Response Caching**
- Honzik response caching (24 hour TTL)
- Deterministic cache keys based on user text and settings
- 15-20% expected hit rate for common phrases
- Significant cost savings on OpenAI API calls

✅ **Statistics Caching**
- Daily stats caching with dynamic TTL (until end of day)
- Automatic cache invalidation on updates
- 70%+ reduction in database load

✅ **Health Monitoring**
- Redis health check in `/health` endpoint
- Connection status reporting
- Graceful degradation when Redis unavailable

## 🏗️ Architecture

### Cache Layers

```
┌─────────────────────────────────────────────────┐
│              Application Layer                   │
│  (Routers, Services, Repositories)              │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│            Cache Service Layer                   │
│  - CacheService (OpenAI responses)              │
│  - Repository caching (User, Stats)             │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│            Redis Client Layer                    │
│  - Connection pooling                            │
│  - JSON serialization                            │
│  - TTL management                                │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Redis Server                        │
│  (Railway.com or local)                         │
└──────────────────────────────────────────────────┘
```

### Cache Key Patterns

```python
# User data
user:{telegram_id}:profile          # TTL: 1 hour
user:{telegram_id}:settings         # TTL: 1 hour
user:{telegram_id}:history:{limit}  # TTL: 1 hour

# Statistics
stats:{user_id}:daily:{date}        # TTL: until midnight
stats:{user_id}:progress            # TTL: 15 minutes

# OpenAI responses
honzik:response:{hash}              # TTL: 24 hours
whisper:{audio_hash}                # TTL: 24 hours
tts:{text_hash}:{voice}             # TTL: 24 hours

# Vocabulary
words:{user_id}:all                 # TTL: 1 hour
words:{user_id}:due                 # TTL: 1 hour
```

## 🔧 Configuration

### Environment Variables

Add to `.env` or Railway environment:

```bash
# Redis Connection
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true
REDIS_MAX_CONNECTIONS=50

# Cache TTLs (in seconds)
REDIS_CACHE_TTL_DEFAULT=3600      # 1 hour
REDIS_CACHE_TTL_USER=3600         # 1 hour
REDIS_CACHE_TTL_STATS=900         # 15 minutes
REDIS_CACHE_TTL_OPENAI=86400      # 24 hours
```

### Railway.com Setup

#### Step 1: Add Redis Service

In Railway dashboard:
1. Click "New" → "Database" → "Redis"
2. Railway will automatically create `REDIS_URL` variable
3. The URL format: `redis://default:password@host:port`

#### Step 2: Configure Environment

Set these variables in Railway:

```bash
CACHE_ENABLED=true
REDIS_MAX_CONNECTIONS=50
```

#### Step 3: Verify Connection

Check `/health` endpoint:

```bash
curl https://your-app.railway.app/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "mluv-me",
  "version": "1.0.0",
  "environment": "production",
  "redis": "healthy"
}
```

## 🧪 Local Development

### Using Docker

```bash
# Start Redis container
docker run -d \
  --name mluv-redis \
  -p 6379:6379 \
  redis:7-alpine

# Verify
redis-cli ping
# Should return: PONG
```

### Using Local Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Windows (WSL2)
sudo apt-get install redis-server
sudo service redis-server start
```

### Test Connection

```python
import redis.asyncio as redis

async def test_connection():
    client = await redis.from_url("redis://localhost:6379/0")
    print(await client.ping())  # Should print: True
    await client.aclose()
```

## 📊 Performance Impact

### Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| User lookup latency | 50-100ms | 5-10ms | **85-90%** ↓ |
| Stats endpoint latency | 100-200ms | 10-20ms | **85-90%** ↓ |
| OpenAI API costs | 100% | 80-85% | **15-20%** ↓ |
| Database load | 100% | 30% | **70%** ↓ |

### Cache Hit Rates (Expected)

- User profile: **85-90%**
- User settings: **85-90%**
- Daily stats: **70-80%**
- OpenAI responses: **15-20%** (common phrases)

## 🔍 Monitoring

### Redis Health Check

```bash
# Check connection
curl http://localhost:8000/health | jq .redis

# Expected: "healthy" or "disabled"
```

### Cache Statistics (Future Enhancement)

Add to monitoring dashboard:
- Cache hit rate per endpoint
- Cache size and memory usage
- Average latency with/without cache
- OpenAI cost savings

### Railway Metrics

Monitor in Railway dashboard:
- Redis memory usage
- Connection count
- Commands per second

## 🐛 Troubleshooting

### Redis Connection Failed

**Symptoms:**
- `/health` shows `"redis": "unavailable"`
- Logs show "redis_connect_failed"

**Solutions:**

1. Verify `REDIS_URL` is set correctly:
```bash
echo $REDIS_URL
```

2. Check Redis server is running:
```bash
redis-cli ping
```

3. Test connection:
```bash
redis-cli -u $REDIS_URL ping
```

4. Check firewall/network:
```bash
telnet redis-host 6379
```

### Cache Not Working

**Symptoms:**
- All requests go to database
- No performance improvement

**Solutions:**

1. Check `CACHE_ENABLED=true`
2. Verify Redis connection in logs
3. Check cache keys exist:
```bash
redis-cli --scan --pattern "user:*"
```

### Stale Cache Data

**Symptoms:**
- Updated data not reflected
- Old user settings shown

**Solutions:**

1. Cache invalidation should happen automatically on updates
2. Manually clear cache:
```bash
redis-cli FLUSHDB
```

3. Check TTL values are appropriate

### High Memory Usage

**Symptoms:**
- Redis memory growing
- OOM errors

**Solutions:**

1. Check TTL configuration
2. Implement cache eviction policy:
```bash
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET maxmemory 256mb
```

3. Monitor cache size:
```bash
redis-cli INFO memory
```

## 🧪 Testing

### Run Cache Tests

```bash
# Set cache enabled for tests
export CACHE_ENABLED=true
export REDIS_URL=redis://localhost:6379/1

# Run cache tests
pytest tests/test_caching.py -v

# Run all tests
pytest tests/ -v
```

### Manual Testing

```python
# Test user caching
import asyncio
from backend.db.repositories import UserRepository
from backend.cache.redis_client import redis_client

async def test_user_cache():
    await redis_client.connect()

    # First call - cache miss
    user = await user_repo.get_by_telegram_id(123456)

    # Second call - cache hit (much faster)
    user = await user_repo.get_by_telegram_id(123456)

    await redis_client.disconnect()
```

## 📈 Next Steps

### Phase 2: Task Queue (Celery)
- Offload heavy operations to background tasks
- Further reduce user-perceived latency
- See `docs/roadmaps/performance_optimization_roadmap.md`

### Future Enhancements
- Cache warming strategies
- Distributed caching for multi-instance deployments
- Real-time cache analytics dashboard
- Intelligent cache prefetching

## 📚 Related Documentation

- [Performance Optimization Roadmap](./roadmaps/performance_optimization_roadmap.md)
- [Railway Setup Guide](./RAILWAY_SETUP.md)
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)

## ❓ Support

For issues or questions:
1. Check logs: `railway logs`
2. Test Redis connection: `/health` endpoint
3. Review cache configuration in `backend/config.py`
4. Check Railway Redis service status

---

**Status:** ✅ Phase 1 Complete
**Last Updated:** December 2024
**Next Phase:** Task Queue Implementation (Phase 2)
