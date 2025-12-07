# Production Index Creation Guide

**For:** Large databases with existing data
**Purpose:** Create indexes without downtime using CONCURRENTLY

---

## ⚠️ Important Note

The Alembic migrations create indexes **without CONCURRENTLY** because:
1. `CREATE INDEX CONCURRENTLY` cannot run inside a transaction
2. For initial setup with empty/small tables, regular indexes are fine
3. For production databases with significant data, manual CONCURRENTLY creation is recommended

---

## 🚀 Creating Indexes in Production (No Downtime)

If you have an existing production database with data, use these commands to create indexes without blocking:

### 1. Messages Table Indexes

```sql
-- Composite index for user message history
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_user_created
ON messages (user_id, created_at DESC);

-- Full-text search index (Czech)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_text_search
ON messages USING gin(to_tsvector('czech', text))
WHERE text IS NOT NULL;

-- Analytics index for correctness scores
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_correctness_score
ON messages (correctness_score)
WHERE correctness_score IS NOT NULL;
```

### 2. Daily Stats Indexes

```sql
-- Composite index for user statistics
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_stats_user_date
ON daily_stats (user_id, date DESC);
```

### 3. Saved Words Indexes

```sql
-- Composite index for word lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_saved_words_user_word
ON saved_words (user_id, word_czech);

-- Index for spaced repetition queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_saved_words_review
ON saved_words (user_id, last_reviewed_at NULLS FIRST);
```

### 4. Materialized View Indexes

```sql
-- After creating the materialized view, create indexes:

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_stats_summary_telegram_id
ON user_stats_summary(telegram_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_stats_summary_total_stars
ON user_stats_summary(total_stars DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_stats_summary_max_streak
ON user_stats_summary(max_streak DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_stats_summary_total_messages
ON user_stats_summary(total_messages DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_stats_summary_last_activity
ON user_stats_summary(last_activity DESC NULLS LAST);
```

---

## 📊 Monitor Index Creation Progress

```sql
-- Check if index creation is in progress
SELECT
    pid,
    now() - query_start AS duration,
    query
FROM pg_stat_activity
WHERE query LIKE 'CREATE INDEX%'
  AND state = 'active';

-- Check index size (after creation)
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE indexname LIKE 'idx_%'
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## ⏱️ Expected Duration

Index creation time depends on table size:

| Table | Rows | Expected Time (CONCURRENTLY) |
|-------|------|------------------------------|
| messages | 1,000 | ~1-2 seconds |
| messages | 10,000 | ~5-10 seconds |
| messages | 100,000 | ~30-60 seconds |
| messages | 1,000,000 | ~5-10 minutes |
| daily_stats | 10,000 | ~5 seconds |
| saved_words | 10,000 | ~5 seconds |

**Note:** `CONCURRENTLY` is 2-3x slower than regular index creation, but it doesn't block reads/writes.

---

## 🔄 Alternative: Use Migrations + Recreate Indexes

If you want to use Alembic migrations and then recreate with CONCURRENTLY:

```bash
# 1. Apply migrations (creates regular indexes)
alembic upgrade head

# 2. Drop the regular indexes
psql $DATABASE_URL -c "DROP INDEX idx_messages_user_created;"
psql $DATABASE_URL -c "DROP INDEX idx_messages_text_search;"
# ... (drop all)

# 3. Recreate with CONCURRENTLY
psql $DATABASE_URL -f create_indexes_concurrently.sql
```

---

## 📝 Best Practices

### When to Use CONCURRENTLY

✅ **Use CONCURRENTLY when:**
- Database has significant data (10,000+ rows)
- Downtime is not acceptable
- Users are actively using the application

❌ **Don't use CONCURRENTLY when:**
- Database is empty or has minimal data
- Application is not yet in production
- You can afford brief downtime
- Running inside a migration transaction

### Index Creation Strategy

**For New Deployments:**
```bash
# Use regular Alembic migrations
alembic upgrade head
```

**For Existing Production:**
```bash
# 1. Apply migrations without index creation
alembic upgrade head

# 2. Create indexes manually with CONCURRENTLY
# (Run the SQL commands from this document)
```

---

## 🚨 Troubleshooting

### Index Creation Hangs

```sql
-- Check for blocking queries
SELECT
    pid,
    usename,
    state,
    query,
    now() - query_start AS duration
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- Kill blocking query if needed (use with caution!)
SELECT pg_terminate_backend(pid);
```

### Index Creation Failed

```sql
-- Check for invalid indexes
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
  AND NOT pg_index.indisvalid
FROM pg_index
WHERE pg_index.indexrelid = pg_indexes.indexrelid;

-- Drop and recreate invalid index
DROP INDEX CONCURRENTLY IF EXISTS idx_messages_user_created;
CREATE INDEX CONCURRENTLY idx_messages_user_created ON messages (user_id, created_at DESC);
```

---

## 📚 Reference

- [PostgreSQL CREATE INDEX CONCURRENTLY](https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-CONCURRENTLY)
- [Index Best Practices](https://www.postgresql.org/docs/current/indexes-intro.html)

---

**Last Updated:** December 7, 2025
**Status:** Production Ready
**Applies To:** Phase 3 - Database Optimization
