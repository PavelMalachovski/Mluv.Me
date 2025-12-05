# 🚂 Railway.com Setup - Step by Step

## ❌ Current Issue: Healthcheck Failed

The deployment is failing because **DATABASE_URL is not set**. The app builds successfully but can't start without the database.

---

## ✅ Solution: Add PostgreSQL First

### Step 1: Add PostgreSQL Plugin

**Before deploying the app**, you need to add PostgreSQL:

#### Option A: Railway Web UI
1. Go to your Railway project
2. Click **"New"** → **"Database"** → **"Add PostgreSQL"**
3. Wait for PostgreSQL to provision (~30 seconds)
4. Railway will automatically create `DATABASE_URL` variable

#### Option B: Railway CLI
```bash
cd C:\Git\Mluv.Me
railway add --plugin postgresql
```

### Step 2: Verify DATABASE_URL

```bash
# Check that DATABASE_URL exists
railway variables

# Should show:
# DATABASE_URL=postgresql://...
```

### Step 3: Redeploy

After PostgreSQL is added, redeploy:

```bash
# Push changes (if needed)
git add .
git commit -m "Fix Railway deployment"
git push origin main

# Or manual redeploy
railway up
```

---

## 🔧 What I Fixed

### 1. **Dockerfile CMD Format** ✅
Changed from shell form to JSON array format (Railway recommendation):

**Before:**
```dockerfile
CMD alembic upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} & python bot/main.py
```

**After:**
```dockerfile
CMD ["/bin/bash", "/app/start.sh"]
```

### 2. **Startup Script** ✅
Created proper startup script with:
- Database migrations
- Background process for backend
- Foreground process for bot

### 3. **Config Default** ✅
Added default DATABASE_URL for build-time:
```python
database_url: str = Field(
    default="sqlite+aiosqlite:///./temp.db",  # Temporary default
    description="Database connection string"
)
```

This allows the build to succeed even without DATABASE_URL set during build time.

---

## 📋 Complete Deployment Checklist

### ☑️ Before First Deploy

1. **Create Railway Project**
   ```bash
   railway login
   railway init
   ```

2. **Add PostgreSQL** ⚠️ **IMPORTANT - Do this first!**
   ```bash
   railway add --plugin postgresql
   ```

3. **Set Required Variables**
   ```bash
   railway variables set OPENAI_API_KEY=sk-your-key-here
   railway variables set TELEGRAM_BOT_TOKEN=7471812936:AAFoji4k74oAo347ahNaa1K1WAPtiSQ_ox8
   railway variables set ENVIRONMENT=production
   railway variables set LOG_LEVEL=INFO
   ```

4. **Verify All Variables**
   ```bash
   railway variables

   # Must have:
   # ✓ DATABASE_URL (from PostgreSQL plugin)
   # ✓ OPENAI_API_KEY
   # ✓ TELEGRAM_BOT_TOKEN
   # ✓ ENVIRONMENT
   # ✓ LOG_LEVEL
   # ✓ PORT (automatic)
   ```

5. **Deploy**
   ```bash
   railway up
   ```

---

## 🔍 Debugging Healthcheck Failures

### Check Logs
```bash
railway logs

# Look for:
# - "application_startup" ✓
# - Database connection errors ✗
# - Missing environment variables ✗
# - Port binding issues ✗
```

### Common Issues

#### Issue 1: "DATABASE_URL not found"
**Solution:** Add PostgreSQL plugin first
```bash
railway add --plugin postgresql
```

#### Issue 2: "Connection refused"
**Cause:** App not listening on correct PORT
**Check:** Railway sets PORT automatically (usually 8000-9000)
```bash
railway variables | grep PORT
```

#### Issue 3: "Migration failed"
**Cause:** Database not accessible
**Solution:**
```bash
# Check PostgreSQL is running
railway status

# Manually run migrations
railway run alembic upgrade head
```

#### Issue 4: "Module not found"
**Cause:** Missing dependencies in requirements.txt
**Solution:** Update requirements.txt and redeploy

---

## 🧪 Test Locally Before Deploy

### 1. Test with Local PostgreSQL
```bash
# Set local DATABASE_URL
export DATABASE_URL="postgresql://localhost:5432/mluv_me"

# Or use SQLite for quick test
export DATABASE_URL="sqlite+aiosqlite:///./test.db"

# Run migrations
alembic upgrade head

# Start server
uvicorn backend.main:app --reload
```

### 2. Test Health Endpoint
```bash
# In another terminal
curl http://localhost:8000/health

# Should return:
{
  "status": "healthy",
  "service": "mluv-me",
  "version": "1.0.0",
  "environment": "development"
}
```

### 3. Test in Docker
```bash
# Build image
docker build -t mluv-me .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./test.db" \
  -e OPENAI_API_KEY="sk-test" \
  -e TELEGRAM_BOT_TOKEN="test:token" \
  mluv-me

# Test health
curl http://localhost:8000/health
```

---

## 📊 Expected Railway Deployment Flow

### ✅ Successful Deployment

```
1. [Build] Dockerfile build starts
   └─ Installing dependencies... ✓
   └─ Copying files... ✓
   └─ Image built: 191 MB ✓

2. [Deploy] Starting container
   └─ Running migrations... ✓
   └─ Starting backend server... ✓
   └─ Starting bot... ✓

3. [Healthcheck] Testing /health
   └─ Attempt #1: 200 OK ✓
   └─ Deployment successful! ✓
```

### ❌ Failed Deployment (Current)

```
1. [Build] Dockerfile build starts
   └─ Installing dependencies... ✓
   └─ Copying files... ✓
   └─ Image built: 191 MB ✓

2. [Deploy] Starting container
   └─ Running migrations... ✗ (DATABASE_URL missing)
   └─ Container exits or doesn't start

3. [Healthcheck] Testing /health
   └─ Attempt #1: Service unavailable ✗
   └─ Attempt #2-7: Service unavailable ✗
   └─ Healthcheck failed! ✗
```

---

## 🎯 Action Items for You

### Immediate (to fix current deployment):

1. **Add PostgreSQL to your Railway project:**
   - Web UI: Click "New" → "Database" → "Add PostgreSQL"
   - Or CLI: `railway add --plugin postgresql`

2. **Wait for PostgreSQL to provision** (30 seconds)

3. **Verify DATABASE_URL is set:**
   ```bash
   railway variables
   ```

4. **Redeploy:**
   ```bash
   railway up
   ```

5. **Monitor logs:**
   ```bash
   railway logs --follow
   ```

### Expected Result:
```
✓ Database migrations applied
✓ Backend server started on port 8000
✓ Bot started
✓ Healthcheck: 200 OK
✓ Deployment successful!
```

---

## 📞 If Still Failing

### Share These Logs:
```bash
# Full deployment logs
railway logs > deployment.log

# Variable check
railway variables > variables.txt

# Status
railway status > status.txt
```

### Check Railway Dashboard:
1. Go to your project on railway.app
2. Check "Deployments" tab
3. Look for error messages in the latest deployment
4. Check "Metrics" - is CPU/Memory spiking?

---

## ✅ Final Checklist

Before closing this issue, verify:

- [ ] PostgreSQL plugin added
- [ ] DATABASE_URL exists in variables
- [ ] OPENAI_API_KEY set
- [ ] TELEGRAM_BOT_TOKEN set
- [ ] Deployment succeeds (green checkmark)
- [ ] Healthcheck passes
- [ ] `/health` endpoint returns 200
- [ ] Backend accessible at Railway URL
- [ ] No errors in logs

---

## 🎉 Success!

Once deployed successfully, your app will be at:
```
https://your-project-name.railway.app
```

Test it:
```bash
curl https://your-project-name.railway.app/health
```

**Na zdraví! 🍺 Ready for Week 2!**

---

*Updated: 05.12.2025*
*Status: Fixed deployment issues, waiting for PostgreSQL setup*

