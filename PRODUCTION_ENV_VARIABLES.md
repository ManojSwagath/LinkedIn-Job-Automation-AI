# 🎯 PRODUCTION DEPLOYMENT - Environment Variables

## ✅ ALL CONFIGURED FOR RENDER DEPLOYMENT

Copy these EXACT values to your Render dashboard when deploying:

---

## 🔐 **CRITICAL VARIABLES** (Set these in Render)

### Application
```env
APP_NAME=AutoAgentHire
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
```

### Security (IMPORTANT!)
```env
SECRET_KEY=651fd05241ad9e35722c2f7be8bf5a70d486c3a4d82502f6b8d58c7bacf901ed
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Database (Supabase)
```env
DATABASE_URL=postgresql://postgres.erymurdcjgnptietkdaq:Manojswagath%405@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://erymurdcjgnptietkdaq.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVyeW11cmRjamducHRpZXRrZGFxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIzMzg5OTIsImV4cCI6MjA4NzkxNDk5Mn0.7DuM-EMgRtcaIe4D1wpZme7plzi3xNjj2Tv51r9pAGo
```

### AI/LLM (Groq - Free!)
```env
OPENAI_API_KEY=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
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.3-70b-versatile
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7
```

### LinkedIn Automation
```env
LINKEDIN_EMAIL=sathwiksmart88@gmail.com
LINKEDIN_PASSWORD=Sahithi@11
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000
```

### CORS (IMPORTANT - Add your Vercel URL!)
```env
CORS_ORIGINS=https://your-app.vercel.app,https://www.your-app.vercel.app
```
**⚠️ After deploying frontend to Vercel, come back and update this with your actual Vercel URL!**

### Python Runtime
```env
PYTHON_VERSION=3.11.0
```

---

## 📋 **VERCEL ENVIRONMENT VARIABLES**

Set these in Vercel dashboard (Settings → Environment Variables):

```env
VITE_API_URL=https://your-backend.onrender.com
VITE_GOOGLE_CLIENT_ID=840410414563-bjrf1kjfi5kmgmlh0f14te6i61qbaoi6.apps.googleusercontent.com
```

**⚠️ Replace `your-backend.onrender.com` with your actual Render URL after deploying backend!**

---

## 🚀 **DEPLOYMENT STEPS**

### 1. Push to GitHub (If not done)
```bash
git add .
git commit -m "Ready for production deployment"
git push origin main
```

### 2. Deploy Backend to Render
1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** `linkedin-automation-backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && playwright install chromium`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free (or Starter $7/month for no cold starts)
5. Copy ALL environment variables from above section
6. Click "Create Web Service"
7. Wait 5-10 minutes for build
8. **SAVE YOUR RENDER URL:** `https://linkedin-automation-backend.onrender.com`

### 3. Deploy Frontend to Vercel
1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Vercel auto-detects `vercel.json` settings
5. Add environment variables:
   - `VITE_API_URL=https://YOUR-RENDER-URL.onrender.com`
   - `VITE_GOOGLE_CLIENT_ID=840410414563-bjrf1kjfi5kmgmlh0f14te6i61qbaoi6.apps.googleusercontent.com`
6. Click "Deploy"
7. Wait 2-3 minutes
8. **SAVE YOUR VERCEL URL:** `https://your-app.vercel.app`

### 4. Connect Frontend & Backend (CRITICAL!)
1. Go back to Render dashboard
2. Find your backend service → "Environment" tab
3. Update `CORS_ORIGINS` with your Vercel URL:
   ```
   CORS_ORIGINS=https://your-app.vercel.app,https://www.your-app.vercel.app
   ```
4. Click "Save Changes" (this will redeploy backend)

### 5. Test Your Live App! 🎉
1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Test backend: `https://your-backend.onrender.com/docs`
3. Try creating an account and logging in
4. Check that API calls work (F12 → Network tab)

---

## ⚠️ **IMPORTANT NOTES**

### Render Free Tier
- **Cold starts:** Backend sleeps after 15 min inactivity
- **First request:** Takes 30-60 seconds to wake up
- **Solution:** Upgrade to Starter ($7/month) or use UptimeRobot to ping every 10 min

### Passwords with Special Characters
- In `DATABASE_URL`: `@` must be `%40` (already done ✅)
- In `LINKEDIN_PASSWORD`: Use as-is (no encoding needed ✅)

### Session Pooler vs Direct Connection
- ✅ **Session Pooler:** Works with Vercel/Render (IPv4 compatible)
- ❌ **Direct Connection:** Won't work with Vercel/Render (IPv6 only)
- Your setup uses Session Pooler ✅

---

## 🧪 **Testing Checklist**

Before deploying:
- [x] Backend runs locally: `python backend/main.py`
- [x] Supabase connected
- [x] Database tables initialized
- [x] Frontend builds: `cd frontend/lovable && npm run build`
- [x] LinkedIn credentials set
- [x] Secure SECRET_KEY generated

After deploying:
- [ ] Backend health check works
- [ ] Frontend loads without errors
- [ ] API calls from frontend work
- [ ] No CORS errors in browser console
- [ ] Authentication works
- [ ] LinkedIn automation works (optional)

---

## 💡 **Quick Commands**

### Test Backend Locally
```bash
d:/Projects/LinkedIn-Job-Automation-with-AI/.venv/Scripts/python.exe backend/main.py
```

### Test Frontend Locally
```bash
cd frontend/lovable
npm run dev
```

### Test Database Connection
```bash
d:/Projects/LinkedIn-Job-Automation-with-AI/.venv/Scripts/python.exe test_supabase_connection.py
```

### Rebuild Frontend
```bash
cd frontend/lovable
npm run build
```

---

## 📞 **Support Links**

- **Render Dashboard:** https://dashboard.render.com
- **Vercel Dashboard:** https://vercel.com/dashboard
- **Supabase Dashboard:** https://supabase.com/dashboard/project/erymurdcjgnptietkdaq
- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs

---

## ✅ **READY TO DEPLOY!**

All environment variables are configured. Your app is production-ready!

**Estimated deployment time: 30-40 minutes**

🚀 Follow the deployment steps above and you'll have a live website!

---

**Generated:** March 1, 2026
**Status:** READY FOR PRODUCTION ✅
