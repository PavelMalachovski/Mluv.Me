# 🚀 Quick Deployment Guide

## Prerequisites

- ✅ Backend deployed on Railway
- ✅ Telegram Bot Token: `7471812936:AAFoji4k74oAo347ahNaa1K1WAPtiSQ_ox8`
- ✅ GitHub repository
- ✅ Vercel account

---

## Step 1: Prepare Environment Variables

You need these values:
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_TELEGRAM_BOT_ID=7471812936
```

Get your Railway backend URL from Railway dashboard.

---

## Step 2: Deploy to Vercel

### Option A: Vercel Dashboard (Recommended)

1. **Go to Vercel**
   - Visit https://vercel.com
   - Login with GitHub

2. **Import Project**
   - Click "Add New Project"
   - Select your Mluv.Me repository
   - Click "Import"

3. **Configure Project**
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

4. **Add Environment Variables**
   - Click "Environment Variables"
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend.railway.app
     NEXT_PUBLIC_TELEGRAM_BOT_ID=7471812936
     ```

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - ✅ Done!

### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Navigate to frontend
cd frontend

# Deploy
vercel --prod

# Follow prompts:
# - Project name: mluv-me-web
# - Root directory: ./
# - Build command: npm run build
# - Output directory: .next

# Add environment variables when prompted
```

---

## Step 3: Configure Custom Domain (Optional)

1. **In Vercel Dashboard**
   - Go to your project
   - Click "Settings" → "Domains"
   - Add domain: `app.mluv.me`

2. **Update DNS**
   - Go to your domain registrar
   - Add CNAME record:
     ```
     Type: CNAME
     Name: app
     Value: cname.vercel-dns.com
     ```

3. **Wait for SSL**
   - Vercel auto-provisions SSL certificate
   - Usually takes 1-2 minutes

---

## Step 4: Update Backend CORS

In `backend/main.py`, update CORS to allow your Vercel URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.mluv.me",           # Your custom domain
        "https://*.vercel.app",          # Vercel preview URLs
        "http://localhost:3000"          # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy backend on Railway after this change.

---

## Step 5: Test Production

1. **Visit Your URL**
   ```
   https://your-project.vercel.app
   or
   https://app.mluv.me
   ```

2. **Test Authentication**
   - Click "Login with Telegram"
   - Authorize
   - Should redirect to dashboard

3. **Test Practice**
   - Go to dashboard
   - Click "Start Practicing"
   - Type Czech message
   - Should get Honzík response

4. **Check Errors**
   - Open browser console (F12)
   - Check for errors
   - If CORS errors → check backend CORS config

---

## Step 6: Monitor

### Vercel Analytics
- Go to project → "Analytics"
- See page views, visitors, performance

### Vercel Logs
- Go to project → "Deployments"
- Click deployment → "Functions"
- See runtime logs

### Backend Logs
- Check Railway logs for API errors

---

## Troubleshooting

### Issue: "Failed to fetch"
**Solution**: Check CORS configuration in backend

### Issue: "Authentication failed"
**Solution**: Verify `NEXT_PUBLIC_TELEGRAM_BOT_ID` matches bot token

### Issue: "API endpoint not found"
**Solution**: Check `NEXT_PUBLIC_API_URL` points to correct Railway URL

### Issue: Build fails
**Solution**: Check Node.js version (should be 18+)

### Issue: Telegram Login doesn't work
**Solution**:
1. Check bot token is correct
2. Telegram Login Widget script loaded?
3. Check browser console for errors

---

## Environment Variables Reference

### Required
- `NEXT_PUBLIC_API_URL` - Backend API URL (Railway)
- `NEXT_PUBLIC_TELEGRAM_BOT_ID` - Telegram Bot ID

### Optional
- `NEXT_PUBLIC_ANALYTICS_ID` - Analytics tracking (future)

---

## Continuous Deployment

Once set up, Vercel automatically deploys:
- ✅ **Production**: When you push to `main` branch
- ✅ **Preview**: When you create pull request
- ✅ **Rollback**: One-click rollback to previous version

---

## Performance Optimization

Vercel automatically provides:
- ✅ Global CDN
- ✅ Edge caching
- ✅ Image optimization
- ✅ Automatic compression
- ✅ HTTP/2

Expected performance:
- **First Load**: < 2s
- **Subsequent Loads**: < 500ms
- **Lighthouse Score**: > 90

---

## Security

Vercel automatically provides:
- ✅ SSL/TLS certificates
- ✅ DDoS protection
- ✅ Security headers
- ✅ HTTPS redirect

---

## Cost

**Vercel Hobby Plan (Free):**
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ SSL certificates
- ✅ Perfect for MVP

**If you need more:**
- Pro Plan: $20/month
- Unlimited bandwidth
- Advanced analytics

---

## Quick Commands

```bash
# Deploy to production
vercel --prod

# Deploy preview
vercel

# Check deployment status
vercel ls

# View logs
vercel logs

# Remove deployment
vercel rm [deployment-url]

# Check domains
vercel domains ls

# Add environment variable
vercel env add NEXT_PUBLIC_API_URL
```

---

## Success Checklist

- [ ] Backend deployed on Railway
- [ ] Frontend deployed on Vercel
- [ ] Environment variables set
- [ ] CORS configured in backend
- [ ] Custom domain added (optional)
- [ ] SSL certificate active
- [ ] Login works
- [ ] Dashboard loads
- [ ] Practice works
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Performance good (< 2s load)

---

## Need Help?

Check:
1. Vercel Documentation: https://vercel.com/docs
2. Next.js Documentation: https://nextjs.org/docs
3. Project README: `frontend/README.md`
4. Full Guide: `docs/PHASE1_WEB_UI_IMPLEMENTATION.md`

---

**Ready to deploy! 🚀**

Estimated deployment time: **5-10 minutes**
