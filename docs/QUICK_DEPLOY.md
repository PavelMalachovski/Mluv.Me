# ⚡ Quick Deploy Guide - Railway.com

## 🚨 Your Current Issue

**Healthcheck Failed** because PostgreSQL is not added yet.

---

## ✅ 3-Step Fix

### 1️⃣ Add PostgreSQL Plugin

**Web UI:**
```
1. Go to railway.app → Your Project
2. Click "New" button
3. Select "Database"
4. Choose "Add PostgreSQL"
5. Wait 30 seconds for provisioning
```

**CLI:**
```bash
railway add --plugin postgresql
```

### 2️⃣ Verify DATABASE_URL

```bash
railway variables

# Must show:
# DATABASE_URL=postgresql://user:pass@host:port/database
```

### 3️⃣ Redeploy

```bash
# Option A: Push to GitHub (if connected)
git add .
git commit -m "Fix deployment"
git push

# Option B: Manual deploy
railway up
```

---

## 📋 Complete Setup (First Time)

```bash
# 1. Login
railway login

# 2. Initialize project
railway init

# 3. Add PostgreSQL ⚠️ IMPORTANT!
railway add --plugin postgresql

# 4. Set variables
railway variables set OPENAI_API_KEY=sk-your-key
railway variables set TELEGRAM_BOT_TOKEN=7471812936:AAFoji4k74oAo347ahNaa1K1WAPtiSQ_ox8
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO

# 5. Deploy
railway up

# 6. Watch logs
railway logs --follow
```

---

## ✅ Expected Success Output

```
[Build] ✓ Image built (191 MB)
[Deploy] ✓ Running migrations
[Deploy] ✓ Backend started
[Deploy] ✓ Bot started
[Health] ✓ /health returns 200 OK
[Status] ✓ Deployment successful!
```

---

## 🔍 Quick Debug

### Check logs:
```bash
railway logs
```

### Check variables:
```bash
railway variables
```

### Check status:
```bash
railway status
```

### Test health endpoint:
```bash
curl https://your-app.railway.app/health
```

---

## 🆘 Still Not Working?

1. **Check PostgreSQL is running:**
   ```bash
   railway status
   # Should show PostgreSQL service
   ```

2. **Check DATABASE_URL exists:**
   ```bash
   railway variables | grep DATABASE_URL
   ```

3. **Check deployment logs:**
   ```bash
   railway logs
   # Look for errors
   ```

4. **Restart deployment:**
   ```bash
   railway up --force
   ```

---

## 📞 Need Help?

See detailed guide: `RAILWAY_SETUP.md`

**Na zdraví! 🍺**

