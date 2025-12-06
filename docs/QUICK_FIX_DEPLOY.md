# Quick Fix & Deploy - Railway Issues

**Quick reference for fixing the current Railway deployment issues.**

## 🚨 Quick Diagnosis

### Symptom 1: Bot Conflict Error
```
TelegramConflictError: Conflict: terminated by other getUpdates request
```
**Fix:** ✅ Applied - Single instance enforcement

### Symptom 2: 500 Error on Voice Processing
```
POST /api/v1/lessons/process HTTP/1.1" 500 Internal Server Error
```
**Fix:** ✅ Applied - Enhanced error logging

---

## 🚀 Deploy Fixed Version

### Step 1: Commit & Push
```bash
# Check status
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "fix: Railway deployment issues (bot conflict & error logging)"

# Push to GitHub (triggers Railway auto-deploy)
git push origin master
```

### Step 2: Monitor Railway Deployment
```bash
# Watch logs in real-time
railway logs -f
```

### Step 3: Verify Deployment

**Look for these success indicators:**

✅ **Migrations:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
```

✅ **Backend Started:**
```
Starting backend server...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Health Check Passes:**
```
INFO:     100.64.0.2:41983 - "GET /health HTTP/1.1" 200 OK
```

✅ **Bot Started (NO CONFLICT):**
```
Starting bot...
INFO:     bot_started mode="polling"
```

---

## ✅ Test After Deployment

### 1. Test Health Endpoint
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "mluv-me",
  "version": "1.0.0",
  "environment": "production"
}
```

### 2. Test Bot
Open Telegram and send to your bot:
- `/start` - Should get welcome message
- `/help` - Should get help text
- Send voice message in Czech - Should get response

### 3. Monitor Logs
```bash
railway logs --tail 100
```

**Look for:**
- ✅ No conflict errors
- ✅ Voice messages processing successfully
- ✅ Clear error messages if something fails

---

## 🔧 If Still Having Issues

### Issue: Bot Still Shows Conflict

**Solution 1: Force Single Instance**
```bash
# Railway Dashboard
Settings → Scaling → Set Min/Max Instances to 1
```

**Solution 2: Stop Other Instances**
```bash
# Check if bot running locally
ps aux | grep "bot.main"

# Kill if found
pkill -f "bot.main"
```

**Solution 3: Delete Webhook (if exists)**
```bash
# Get bot info
curl https://api.telegram.org/bot7471812936:AAFoji4k74oAo347ahNaa1K1WAPtiSQ_ox8/getWebhookInfo

# Delete webhook
curl https://api.telegram.org/bot7471812936:AAFoji4k74oAo347ahNaa1K1WAPtiSQ_ox8/deleteWebhook
```

### Issue: Still Getting 500 Errors

**Check Logs for Details:**
```bash
railway logs | grep "ERROR"
```

Now you should see:
- Error type
- Error message
- Full traceback (in development)
- Context (user_id, etc.)

**Common Causes:**

1. **Missing OpenAI API Key:**
   ```bash
   railway variables set OPENAI_API_KEY=sk-...
   ```

2. **Database Connection:**
   ```bash
   # Check DATABASE_URL is set
   railway variables | grep DATABASE_URL
   ```

3. **OpenAI Rate Limit:**
   - Check https://platform.openai.com/usage
   - Check balance
   - Wait a few minutes

---

## 📊 Key Metrics to Monitor

### CPU & Memory (Railway Dashboard)
- CPU: < 80% normal
- Memory: < 512MB normal

### Response Times
- Health check: < 100ms
- Voice processing: 10-20 seconds (normal)

### Error Rate
- Target: < 1% error rate
- If higher, check OpenAI status

---

## 🎯 Success Checklist

After deployment, verify:

- [ ] Railway deployment successful
- [ ] Health check returns 200 OK
- [ ] Bot responds to /start
- [ ] Bot responds to /help
- [ ] Voice messages processed
- [ ] No conflict errors in logs
- [ ] Errors logged with details
- [ ] Only 1 instance running

---

## 📝 What Was Fixed

### Code Changes:
1. ✅ Enhanced error logging in `backend/routers/lesson.py`
2. ✅ Better exception handling in `backend/main.py`
3. ✅ Bot conflict detection in `bot/main.py`
4. ✅ Single instance in `railway.json`

### Configuration:
1. ✅ `numReplicas: 1` in railway.json
2. ✅ `exc_info=True` for all error logs
3. ✅ Traceback in development mode

### Documentation:
1. ✅ `TROUBLESHOOTING.md` - Full guide
2. ✅ `FIXES_APPLIED.md` - Detailed changes
3. ✅ This quick reference

---

## 🆘 Emergency Rollback

If deployment breaks everything:

```bash
# Revert last commit
git revert HEAD

# Push to trigger redeploy
git push origin master
```

Or in Railway Dashboard:
- Deployments → Previous Version → Redeploy

---

## 📞 Get Help

- **Railway Status:** https://status.railway.app/
- **OpenAI Status:** https://status.openai.com/
- **Logs:** `railway logs -f`
- **Full Guide:** `docs/TROUBLESHOOTING.md`

---

**Hotovo!** ✅ (Done!)
**Hodně štěstí!** 🍀 (Good luck!)
**- Honzík** 🇨🇿

