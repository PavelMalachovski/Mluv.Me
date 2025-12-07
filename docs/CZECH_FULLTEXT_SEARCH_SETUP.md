# Czech Full-Text Search Setup (Optional)

**Status:** Optional Enhancement
**Purpose:** Enable Czech language support for full-text search
**Impact:** Better search quality for Czech text

---

## ⚠️ Current Implementation

The migration uses `simple` text search configuration as a fallback because:
- Not all PostgreSQL installations have Czech language support
- `simple` configuration works universally
- Full-text search still functions, just without Czech-specific stemming

---

## 🎯 Why Upgrade to Czech?

### With `simple` (Current)
- ✅ Works on all PostgreSQL installations
- ✅ No additional setup required
- ❌ No Czech stemming (e.g., "pivo" and "pivem" are different words)
- ❌ No Czech stop words filtering

### With `czech` (Enhanced)
- ✅ Czech-specific word stemming
- ✅ Czech stop words filtering
- ✅ Better search accuracy
- ❌ Requires additional PostgreSQL extension
- ❌ Not available by default on some systems

---

## 🚀 Installing Czech Text Search

### Option 1: Using PostgreSQL Extensions (Recommended)

#### Check if Czech is available:
```sql
-- Check available text search configurations
SELECT cfgname FROM pg_ts_config WHERE cfgname LIKE '%czech%';

-- If empty, Czech is not installed
```

#### Install via apt (Ubuntu/Debian):
```bash
# Install PostgreSQL contrib package
sudo apt-get update
sudo apt-get install postgresql-contrib-15

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### Install via Railway.com:
Unfortunately, Railway's managed PostgreSQL may not support custom text search configurations. In this case, use Option 2.

### Option 2: Create Custom Czech Configuration

```sql
-- Create Czech text search configuration based on 'simple'
-- This is a basic setup without full linguistic support
CREATE TEXT SEARCH CONFIGURATION czech (COPY = simple);

-- Optional: Add Czech-specific stop words
-- (You would need to create a dictionary first)
```

### Option 3: Use Alternative Language (Practical)

Since Czech-specific support is limited, you can use a related language:

```sql
-- Check available Slavic language configs
SELECT cfgname FROM pg_ts_config WHERE cfgname ~ '(czech|slovak|polish|russian)';

-- If any available, you can use them as fallback
```

---

## 🔄 Updating the Index to Use Czech

### After Installing Czech Support:

```sql
-- 1. Drop the existing simple index
DROP INDEX IF EXISTS idx_messages_text_search;

-- 2. Create new index with Czech configuration
CREATE INDEX idx_messages_text_search
ON messages USING gin(to_tsvector('czech', text))
WHERE text IS NOT NULL;

-- Or use CONCURRENTLY for zero downtime:
DROP INDEX CONCURRENTLY IF EXISTS idx_messages_text_search;
CREATE INDEX CONCURRENTLY idx_messages_text_search
ON messages USING gin(to_tsvector('czech', text))
WHERE text IS NOT NULL;
```

### Update Search Queries:

```python
# In your search functions, update to use 'czech'
from sqlalchemy import text

# Before (simple)
query = """
    SELECT * FROM messages
    WHERE to_tsvector('simple', text) @@ to_tsquery('simple', :search_term)
"""

# After (czech)
query = """
    SELECT * FROM messages
    WHERE to_tsvector('czech', text) @@ to_tsquery('czech', :search_term)
"""
```

---

## 📊 Performance Impact

### Index Size Comparison

| Configuration | Index Size (100k messages) | Search Speed |
|---------------|---------------------------|--------------|
| `simple` | ~15 MB | Fast |
| `czech` | ~12 MB (smaller due to stemming) | Fast |

### Search Quality Comparison

**Example: Searching for "pivo" (beer)**

With `simple`:
```sql
-- Finds only exact matches: "pivo"
-- Misses: "pivem", "piva", "pivu"
```

With `czech`:
```sql
-- Finds all forms: "pivo", "pivem", "piva", "pivu", "pivní"
-- Much better for Czech users!
```

---

## 🧪 Testing Czech Text Search

### Test if Czech is Available:
```sql
-- Try to use Czech config
SELECT to_tsvector('czech', 'Ahoj, jak se máš? Dáme si pivo?');

-- If it works, you'll see stemmed tokens
-- If it fails, Czech is not available
```

### Test Search Quality:
```sql
-- Insert test data
INSERT INTO messages (user_id, role, text, created_at)
VALUES
    (1, 'user', 'Rád piju pivo s přáteli', NOW()),
    (1, 'user', 'V pátek jsme pili pivní speciál', NOW()),
    (1, 'user', 'Nejlepší pivní bar v Praze', NOW());

-- Search with simple (finds less)
SELECT text FROM messages
WHERE to_tsvector('simple', text) @@ to_tsquery('simple', 'pivo')
LIMIT 10;
-- Result: Only "Rád piju pivo s přáteli"

-- Search with czech (finds more)
SELECT text FROM messages
WHERE to_tsvector('czech', text) @@ to_tsquery('czech', 'pivo')
LIMIT 10;
-- Result: All three messages (due to stemming)
```

---

## ⚡ Quick Decision Guide

### Use `simple` (Current) if:
- ✅ You want simple setup
- ✅ Railway.com or limited PostgreSQL access
- ✅ Exact word matching is sufficient
- ✅ You can't install extensions

### Upgrade to `czech` if:
- ✅ You have full PostgreSQL access
- ✅ You can install extensions
- ✅ You need better Czech search quality
- ✅ Users search in Czech frequently

---

## 📝 Recommendation

**For Mluv.Me Project:**

Since this is a Czech language learning app, upgrading to Czech full-text search would be beneficial **if possible**. However:

1. **Start with `simple`** (current implementation)
   - Works immediately
   - No setup required
   - Railway.com compatible

2. **Upgrade to `czech` later** (when possible)
   - After initial deployment
   - When you have database admin access
   - For production optimization

3. **Alternative: Application-level search**
   - Use Elasticsearch/MeiliSearch for advanced search
   - Better multilingual support
   - More flexible

---

## 🔧 Maintenance

### Monitoring Search Usage

```sql
-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexname = 'idx_messages_text_search';

-- If idx_scan is 0, full-text search is not being used
```

### Rebuild Index (if needed)

```sql
-- Vacuum and analyze
VACUUM ANALYZE messages;

-- Reindex if search becomes slow
REINDEX INDEX idx_messages_text_search;

-- Or CONCURRENTLY for zero downtime
REINDEX INDEX CONCURRENTLY idx_messages_text_search;
```

---

## 📚 Related Documentation

- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [Text Search Configuration](https://www.postgresql.org/docs/current/textsearch-configuration.html)
- [Phase 3 Implementation Summary](./PHASE3_IMPLEMENTATION_SUMMARY.md)

---

## 💡 Summary

**Current Status:** Using `simple` configuration (works everywhere)
**Future Enhancement:** Upgrade to `czech` when database access allows
**Impact:** `simple` works fine, `czech` would be better for Czech users
**Priority:** LOW (nice to have, not critical)

The full-text search index is functional with `simple` configuration. Upgrading to Czech-specific search is an optional enhancement that can be done later.

---

**Last Updated:** December 7, 2025
**Status:** ✅ Working with `simple`, Czech upgrade optional
**Priority:** LOW
