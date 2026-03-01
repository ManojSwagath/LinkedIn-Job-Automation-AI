# 🚀 Complete Deployment Guide: GitHub → Render → Vercel

This guide will take you through the **complete deployment process** from creating a GitHub repository to deploying your backend on Render and frontend on Vercel.

---

## 📋 **Table of Contents**

1. [Prerequisites](#prerequisites)
2. [Step 1: Create GitHub Repository & Push Code](#step-1-create-github-repository--push-code)
3. [Step 2: Setup Supabase Database](#step-2-setup-supabase-database)
4. [Step 3: Deploy Backend to Render](#step-3-deploy-backend-to-render)
5. [Step 4: Deploy Frontend to Vercel](#step-4-deploy-frontend-to-vercel)
6. [Step 5: Connect Frontend to Backend](#step-5-connect-frontend-to-backend)
7. [Testing & Verification](#testing--verification)
8. [Troubleshooting](#troubleshooting)

---

## ✅ **Prerequisites**

Before starting, make sure you have:

- [ ] **GitHub Account** → [Sign up](https://github.com/join)
- [ ] **Render Account** → [Sign up](https://render.com)
- [ ] **Vercel Account** → [Sign up](https://vercel.com/signup)
- [ ] **Supabase Account** → [Sign up](https://supabase.com)
- [ ] **OpenAI API Key** → [Get it](https://platform.openai.com/api-keys)
- [ ] **Git installed** → [Download](https://git-scm.com/downloads)
- [ ] **LinkedIn Credentials** (email & password)

---

## 🎯 **Step 1: Create GitHub Repository & Push Code**

### 1.1 Create a New GitHub Repository

1. **Go to GitHub:** https://github.com/new

2. **Fill in details:**
   - **Repository name:** `linkedin-job-automation-ai` (or your choice)
   - **Description:** `AI-powered LinkedIn Job Application Automation System`
   - **Visibility:** Choose **Private** (recommended) or Public
   - **DO NOT** check "Initialize with README" (you already have one)
   - **DO NOT** add .gitignore or license (already exists)

3. **Click** "Create repository"

4. **Copy the repository URL** - you'll see something like:
   ```
   https://github.com/YOUR_USERNAME/linkedin-job-automation-ai.git
   ```

### 1.2 Push Your Code to GitHub

Open **PowerShell** in your project directory and run these commands:

```powershell
# Navigate to project directory (if not already there)
cd D:\Projects\LinkedIn-Job-Automation-with-AI

# Check git status (verify .gitignore is working)
git status

# If not initialized, initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - LinkedIn Job Automation with AI"

# Add your GitHub repository as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/linkedin-job-automation-ai.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

> **Note:** Replace `YOUR_USERNAME` with your actual GitHub username!

### 1.3 Verify Upload

1. Go to your repository on GitHub
2. Refresh the page - you should see all your files
3. Check that `.env` is **NOT** visible (it should be ignored)

✅ **Checkpoint:** Your code is now on GitHub!

---

## 🗄️ **Step 2: Setup Supabase Database**

### 2.1 Create Supabase Project

1. **Go to:** https://supabase.com

2. **Sign in** with GitHub (recommended)

3. **Click** "New Project"

4. **Fill in details:**
   - **Name:** `linkedin-automation`
   - **Database Password:** Create a **strong password** (SAVE THIS!)
   - **Region:** Choose closest to you (e.g., `US East (Ohio)` or `US West (Oregon)`)
   - **Plan:** Free tier is fine for testing

5. **Click** "Create new project"

6. **Wait 2-3 minutes** for database provisioning

### 2.2 Get Database Credentials

1. Once ready, click **"Project Settings"** (gear icon in sidebar)

2. Go to **"Database"** tab

3. **Copy these values** (you'll need them later):

   - **Connection string (URI mode):**
     ```
     postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
     ```
   
   - **Host:** `db.xxxxxxxxxxxx.supabase.co`
   - **Database name:** `postgres`
   - **Port:** `5432`
   - **User:** `postgres`
   - **Password:** (the one you created)

4. **Also get API credentials:**
   - Go to **"Project Settings"** → **"API"**
   - Copy **Project URL:** `https://xxxxxxxxxxxx.supabase.co`
   - Copy **anon public key:** `eyJhbGc...` (long string)

### 2.3 Initialize Database Tables

1. Go to **"SQL Editor"** in Supabase dashboard

2. Open the file `database/init.sql` from your project

3. **Copy the entire SQL content** and paste it into Supabase SQL Editor

4. **Click** "Run" to create all necessary tables

5. **Verify:** Go to "Table Editor" - you should see tables like `users`, `job_applications`, etc.

### 2.4 Setup Supabase Storage (for Resume Uploads)

**⚠️ IMPORTANT:** Your app needs cloud storage for uploaded resumes. Render's free tier has ephemeral storage (files get deleted on restart).

1. In Supabase Dashboard, click **"Storage"** in left sidebar

2. Click **"Create a new bucket"**

3. Fill in:
   - **Name:** `resumes`
   - **Public:** ✅ Check "Make bucket public" (so users can access files)
   - Click **"Create bucket"**

4. **Save bucket name** - you'll need it: `resumes`

> **Note:** Files will now persist in Supabase Storage instead of server filesystem!

✅ **Checkpoint:** Database AND file storage are ready!

---

## 🖥️ **Step 3: Deploy Backend to Render**

### 3.1 Create Render Account & Connect GitHub

1. **Go to:** https://render.com

2. **Sign up** using GitHub (easiest for auto-deployment)

3. **Authorize** Render to access your repositories

### 3.2 Deploy Backend Service

1. **In Render Dashboard:**
   - Click **"New +"** → **"Web Service"**

2. **Connect Repository:**
   - Click "Connect account" if not already connected
   - Find and select your `linkedin-job-automation-ai` repository
   - Click "Connect"

3. **Configure Service:**

   Render should detect `render.yaml`, but verify these settings:

   | Setting | Value |
   |---------|-------|
   | **Name** | `linkedin-automation-backend` |
   | **Region** | Oregon (or closest to you) |
   | **Branch** | `main` |
   | **Root Directory** | `.` (leave empty or use `.`) |
   | **Runtime** | `Python 3` |
   | **Build Command** | `./build.sh` |
   | **Start Command** | `PYTHONPATH=. gunicorn backend.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 300` |
   | **Instance Type** | Free (or Starter $7/month for better performance) |

4. **Click** "Advanced" → Scroll to **Auto-Deploy**
   - ✅ Enable "Auto-Deploy" (deploys automatically on git push)

### 3.3 Set Environment Variables

This is **CRITICAL**! In the **Environment** section, add these variables:

```bash
# Database (from Supabase)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxxxxxxxxx.supabase.co:5432/postgres

# Security
SECRET_KEY=your-random-32-character-secret-key-here-change-this-value

# OpenAI (Required)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx

# LinkedIn Credentials
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-linkedin-password

# Supabase (from Step 2.2)
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey...
SUPABASE_BUCKET_NAME=resumes

# File Storage (IMPORTANT for production!)
FILE_STORAGE_TYPE=supabase

# Application Settings
APP_ENV=production
DEBUG=false
API_RELOAD=false
PYTHON_VERSION=3.11.11
PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/.cache/ms-playwright

# CORS (Add after Vercel deployment in Step 4)
CORS_ORIGINS=https://your-app.vercel.app

# Optional: Gemini AI (if using)
GEMINI_API_KEY=your-gemini-api-key-if-you-have-one
```

> **Important:** 
> - For `SECRET_KEY`, generate a random 32-character string. You can use: `openssl rand -hex 32` or an online generator
> - Replace ALL placeholder values with your actual credentials
> - For `CORS_ORIGINS`, you'll add your Vercel URL after Step 4

### 3.4 Deploy!

1. **Click** "Create Web Service"

2. **Wait 5-10 minutes** for:
   - Installing Python dependencies
   - Installing Playwright browsers
   - Starting the application

3. **Monitor logs** in real-time (check for errors)

### 3.5 Verify Backend Deployment

Once deployed, Render gives you a URL like:
```
https://linkedin-automation-backend.onrender.com
```

**Test it:**

1. Open your browser and go to:
   ```
   https://linkedin-automation-backend.onrender.com/
   ```
   
   You should see:
   ```json
   {
     "message": "LinkedIn Job Automation API",
     "status": "operational"
   }
   ```

2. Test the health endpoint:
   ```
   https://linkedin-automation-backend.onrender.com/health
   ```

✅ **Checkpoint:** Backend is live on Render!

**IMPORTANT:** Copy your Render backend URL - you'll need it for Vercel!

---

## 🌐 **Step 4: Deploy Frontend to Vercel**

### 4.1 Create Vercel Account

1. **Go to:** https://vercel.com/signup

2. **Sign up** with GitHub (recommended)

3. **Authorize** Vercel to access your repositories

### 4.2 Deploy Frontend

1. **In Vercel Dashboard:**
   - Click **"Add New..."** → **"Project"**

2. **Import Repository:**
   - Find your `linkedin-job-automation-ai` repository
   - Click **"Import"**

3. **Configure Project:**

   Vercel should detect `vercel.json`, but verify/set:

   | Setting | Value |
   |---------|-------|
   | **Framework Preset** | Other / None |
   | **Root Directory** | `.` (leave as is) |
   | **Build Command** | `cd frontend/lovable && npm install && npm run build` |
   | **Output Directory** | `frontend/lovable/dist` |
   | **Install Command** | `cd frontend/lovable && npm install` |

4. **Environment Variables** (click "Environment Variables"):

   Add your **backend URL**:

   ```bash
   VITE_API_URL=https://linkedin-automation-backend.onrender.com
   ```

   > Replace with YOUR actual Render backend URL from Step 3.5

5. **Click** "Deploy"

6. **Wait 2-5 minutes** for build and deployment

### 4.3 Get Your Vercel URL

Once deployed, Vercel gives you URLs like:
```
https://your-project-name.vercel.app
https://your-project-name-xxxxx.vercel.app  (preview deployments)
```

✅ **Checkpoint:** Frontend is live on Vercel!

---

## 🔗 **Step 5: Connect Frontend to Backend**

Now we need to allow your Vercel frontend to communicate with your Render backend.

### 5.1 Update CORS in Render

1. **Go back to Render Dashboard**

2. **Select your backend service**

3. **Go to "Environment"** tab

4. **Find** `CORS_ORIGINS` variable (or add it if missing)

5. **Update value** to include your Vercel URLs:
   ```
   https://your-project-name.vercel.app,https://your-project-name-xxxxx.vercel.app
   ```

   > Use comma separation, NO spaces. Include both your production and preview URLs.

6. **Click** "Save Changes"

7. **Wait** for auto-redeploy (~2 minutes)

### 5.2 Update Frontend API URL

1. **Go to Vercel Dashboard**

2. **Select your project** → **"Settings"** → **"Environment Variables"**

3. **Verify** `VITE_API_URL` is set correctly:
   ```
   VITE_API_URL=https://linkedin-automation-backend.onrender.com
   ```

4. **If you change it**, click "Redeploy" from the Deployments tab

✅ **Checkpoint:** Frontend and Backend are connected!

---

## ✅ **Testing & Verification**

### Test Your Deployment

1. **Open your Vercel URL:**
   ```
   https://your-project-name.vercel.app
   ```

2. **Test these features:**
   - [ ] Homepage loads ✅
   - [ ] Can access login page ✅
   - [ ] Can create an account (registration) ✅
   - [ ] Can login with credentials ✅
   - [ ] Dashboard loads after login ✅
   - [ ] Can upload resume ✅
   - [ ] Can search for jobs ✅
   - [ ] Can start automation ✅

3. **Check browser console** (F12) for any errors

4. **Check Render logs** if API calls fail:
   - Go to Render Dashboard → Your service → Logs

### Common Issues

| Issue | Solution |
|-------|----------|
| **CORS Error** | Update `CORS_ORIGINS` in Render with exact Vercel URL |
| **502 Bad Gateway** | Check Render logs - app may have crashed. Verify env variables. |
| **Build fails on Vercel** | Check build logs. Ensure `frontend/lovable/package.json` exists |
| **Database errors** | Verify `DATABASE_URL` is correct. Check Supabase is running. |
| **OpenAI errors** | Verify `OPENAI_API_KEY` is valid and has credits |
| **LinkedIn login fails** | Check `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD` are correct |

---

## 🎉 **Success!**

Your LinkedIn Job Automation system is now fully deployed!

### Your Deployment URLs:

- **Frontend:** https://your-project-name.vercel.app
- **Backend API:** https://linkedin-automation-backend.onrender.com
- **Database:** Supabase (Managed PostgreSQL)

### Automatic Deployments

✅ **Any time you push to GitHub**, your apps will auto-deploy:
- Render will rebuild and redeploy backend
- Vercel will rebuild and redeploy frontend

### Next Steps:

1. **Test thoroughly** with real LinkedIn account
2. **Monitor Render logs** for any issues
3. **Set up custom domain** (optional):
   - In Vercel: Settings → Domains
   - In Render: Settings → Custom Domain
4. **Monitor usage** to stay within free tier limits

---

## 📊 **Free Tier Limits**

### Render (Free Tier)
- ⏱️ **Spins down after 15 min of inactivity**
- 🔄 **Cold starts take 30-60 seconds**
- 💾 **512 MB RAM**
- ⏱️ **750 hours/month** (enough for 1 service)

**Tip:** Consider upgrading to Starter ($7/month) for:
- No spin down
- Faster performance
- More memory

### Vercel (Hobby Tier)
- ✅ **100 GB bandwidth/month**
- ✅ **Unlimited deployments**
- ✅ **Always on** (no cold starts)
- ✅ **Perfect for frontend**

### Supabase (Free Tier)
- ✅ **500 MB database space**
- ✅ **Unlimited API requests**
- ✅ **2 GB file storage**
- ⏱️ **Pauses after 7 days of inactivity** (auto-resumes)

---

## 🆘 **Need Help?**

### Check Logs:

1. **Render Logs:**
   - Dashboard → Your Service → Logs tab
   - Real-time error tracking

2. **Vercel Logs:**
   - Project → Deployments → Click latest → View Function Logs

3. **Browser Console:**
   - Press F12 → Console tab
   - Check for JavaScript errors

### Debugging Commands:

```powershell
# Test backend locally first
cd D:\Projects\LinkedIn-Job-Automation-with-AI
& .venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload

# Test frontend locally
cd frontend/lovable
npm run dev

# Check git status
git status

# View recent commits
git log --oneline -5

# Force push (use carefully!)
git push -f origin main
```

---

## 🔐 **Security Reminders**

- ✅ **Never** commit `.env` files to GitHub
- ✅ **Verify** `.gitignore` includes `.env`
- ✅ **Use** strong passwords for all services
- ✅ **Rotate** API keys periodically
- ✅ **Enable** 2FA on GitHub, Render, Vercel
- ✅ **Monitor** usage and billing regularly

---

## 📱 **Quick Reference**

### Important URLs:

```bash
# GitHub Repository
https://github.com/YOUR_USERNAME/linkedin-job-automation-ai

# Render Dashboard
https://dashboard.render.com

# Vercel Dashboard  
https://vercel.com/dashboard

# Supabase Dashboard
https://app.supabase.com/project/YOUR_PROJECT_ID
```

### Environment Variables Quick Copy:

```bash
# Backend (Render)
DATABASE_URL=postgresql://postgres:PASSWORD@db.XXXXX.supabase.co:5432/postgres
SECRET_KEY=your-32-char-secret-key
OPENAI_API_KEY=sk-proj-xxxxx
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
SUPABASE_URL=https://XXXXX.supabase.co
SUPABASE_KEY=eyJhbGc...
CORS_ORIGINS=https://your-app.vercel.app
APP_ENV=production
DEBUG=false

# Frontend (Vercel)
VITE_API_URL=https://linkedin-automation-backend.onrender.com
```

---

**🎊 Congratulations! You've successfully deployed a full-stack AI application!**

*Remember: First load may take 30-60 seconds due to Render free tier cold start.*
