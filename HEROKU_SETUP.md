# Heroku Deployment Guide - LinkedIn Job Automation

## Prerequisites
- GitHub Student Developer Pack activated
- Heroku account connected to GitHub Education

## Step 1: Create Heroku App

1. Go to https://dashboard.heroku.com
2. Click **"New"** → **"Create new app"**
3. App name: `linkedin-job-automation-ai` (or your choice)
4. Region: **United States**
5. Click **"Create app"**

## Step 2: Connect GitHub

1. In your Heroku app dashboard, go to **"Deploy"** tab
2. Deployment method: Select **"GitHub"**
3. Search for: `LinkedIn-Job-Automation-AI`
4. Click **"Connect"**
5. Enable **"Automatic Deploys"** from `main` branch

## Step 3: Configure Buildpacks

1. Go to **"Settings"** tab
2. Scroll to **"Buildpacks"** section
3. Click **"Add buildpack"**
4. Add these in order:
   - `heroku/python`
   - `https://github.com/heroku/heroku-buildpack-google-chrome`
   - `https://github.com/mxschmitt/heroku-playwright-buildpack`

## Step 4: Set Environment Variables

1. Still in **"Settings"** tab
2. Click **"Reveal Config Vars"**
3. Add these variables:

```
APP_ENV=production
DEBUG=false
API_RELOAD=false

# Database (from Supabase)
DATABASE_URL=postgresql://postgres.xxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres

# Security
SECRET_KEY=your-32-character-secret-key-here

# LinkedIn Credentials
LINKEDIN_EMAIL=sathwiksmart88@gmail.com
LINKEDIN_PASSWORD=Sahithi@11

# AI API Keys
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# CORS (add your Vercel domain)
CORS_ORIGINS=https://a-beige-omega.vercel.app,https://a-git-main-amanojswagath-blips-projects.vercel.app,https://a-9r7n27rnt-amanojswagath-blips-projects.vercel.app

# Playwright Settings
PLAYWRIGHT_BROWSERS_PATH=/app/.playwright
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0
```

## Step 5: Deploy

1. Go to **"Deploy"** tab
2. Scroll to bottom
3. Click **"Deploy Branch"** (main)
4. Wait 5-10 minutes for build

## Step 6: Update Vercel

1. Go to Vercel dashboard → Your project → Settings → Environment Variables
2. Update `VITE_API_URL` to your Heroku URL:
   ```
   VITE_API_URL=https://linkedin-job-automation-ai.herokuapp.com
   ```
3. Redeploy frontend (or push a dummy commit)

## Step 7: Test!

Visit: `https://linkedin-job-automation-ai.herokuapp.com/`

You should see:
```json
{
  "name": "AutoAgentHire",
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

## Troubleshooting

### Build fails with "cannot find chromium"
- Make sure buildpacks are in correct order (python, chrome, playwright)

### "Application error" on startup
- Check logs: `heroku logs --tail -a linkedin-job-automation-ai`
- Verify all environment variables are set

### Playwright errors
- Ensure `PLAYWRIGHT_BROWSERS_PATH=/app/.playwright`
- Wait for first build to complete (downloads Chromium)

## Student Benefits

With GitHub Student Pack, you get **$13/month credit for 24 months**!

To apply credit:
1. Go to https://education.github.com/pack
2. Find Heroku offer
3. Redeem code
4. Apply to your account

This covers Eco Dyno ($7/month) with room for add-ons!

---

**Total Setup Time: ~10 minutes**

Your app URL will be: `https://[your-app-name].herokuapp.com`
