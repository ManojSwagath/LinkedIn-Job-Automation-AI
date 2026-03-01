# Azure App Service Deployment Guide - LinkedIn Job Automation

## Prerequisites
- Azure for Students account activated ($100 credit)
- GitHub repository ready
- Docker image setup (we have Dockerfile ready)

---

## Method 1: Deploy via GitHub Actions (Recommended)

### Step 1: Create Azure App Service

1. Go to **Azure Portal**: https://portal.azure.com
2. Click **"Create a resource"** → **"Web App"**
3. Configure:
   - **Subscription**: Azure for Students
   - **Resource Group**: Create new → `linkedin-automation-rg`
   - **Name**: `linkedin-job-automation-ai` (unique globally)
   - **Publish**: **Docker Container**
   - **Operating System**: **Linux**
   - **Region**: Choose closest (e.g., East US)
   - **Pricing Plan**: 
     - Click "Create new"
     - Choose **B1 (Basic)** - $13/month (~87% of your credit saved)
     - Or **F1 (Free)** to test first (limited performance)

4. Click **"Next: Docker"**

### Step 2: Configure Docker

1. **Options**: Single Container
2. **Image Source**: GitHub Actions (we'll set this up)
3. Click **"Review + create"** → **"Create"**

Wait 2-3 minutes for deployment.

### Step 3: Configure Application Settings

1. Go to your App Service → **Configuration** → **Application settings**
2. Click **"+ New application setting"** and add:

```
APP_ENV=production
DEBUG=false
API_RELOAD=false
WEBSITES_PORT=8000

# Database
DATABASE_URL=<your_supabase_postgresql_url>

# Security
SECRET_KEY=<generate_32_character_random_string>

# LinkedIn
LINKEDIN_EMAIL=sathwiksmart88@gmail.com
LINKEDIN_PASSWORD=Sahithi@11

# AI APIs
GROQ_API_KEY=<your_groq_key>
GEMINI_API_KEY=<your_gemini_key>

# Supabase
SUPABASE_URL=<your_supabase_url>
SUPABASE_KEY=<your_supabase_key>

# CORS
CORS_ORIGINS=https://a-beige-omega.vercel.app,https://a-git-main-amanojswagath-blips-projects.vercel.app

# Playwright
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0
```

3. Click **"Save"** → **"Continue"**

### Step 4: Set Up GitHub Actions Deployment

1. In Azure Portal, go to your App Service
2. Left menu → **Deployment Center**
3. **Source**: Select **GitHub**
4. Authenticate with GitHub
5. Configure:
   - **Organization**: Your GitHub username
   - **Repository**: `LinkedIn-Job-Automation-AI`
   - **Branch**: `main`
6. Click **"Save"**

Azure will automatically:
- Create GitHub Action workflow
- Build Docker image
- Deploy to Azure Container Registry
- Start your app

### Step 5: Monitor Deployment

1. Go to **GitHub** → Your repo → **Actions** tab
2. Watch the deployment workflow (takes 10-15 minutes first time)
3. Wait for ✅ green checkmark

### Step 6: Verify Deployment

Visit: `https://linkedin-job-automation-ai.azurewebsites.net/`

Expected response:
```json
{
  "name": "AutoAgentHire",
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

### Step 7: Update Vercel Frontend

1. Go to **Vercel Dashboard** → Your project → **Settings** → **Environment Variables**
2. Update `VITE_API_URL`:
   ```
   VITE_API_URL=https://linkedin-job-automation-ai.azurewebsites.net
   ```
3. **Redeploy** frontend (or push a commit)

---

## Method 2: Quick Deploy via Azure CLI (Alternative)

If you have Azure CLI installed:

```bash
# Login
az login

# Create resource group
az group create --name linkedin-automation-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name linkedin-automation-plan \
  --resource-group linkedin-automation-rg \
  --is-linux \
  --sku B1

# Create web app with Docker
az webapp create \
  --resource-group linkedin-automation-rg \
  --plan linkedin-automation-plan \
  --name linkedin-job-automation-ai \
  --deployment-container-image-name mcr.microsoft.com/appsvc/staticsite:latest

# Configure deployment from GitHub
az webapp deployment source config \
  --name linkedin-job-automation-ai \
  --resource-group linkedin-automation-rg \
  --repo-url https://github.com/YOUR_USERNAME/LinkedIn-Job-Automation-AI \
  --branch main \
  --manual-integration

# Set environment variables
az webapp config appsettings set \
  --name linkedin-job-automation-ai \
  --resource-group linkedin-automation-rg \
  --settings \
    WEBSITES_PORT=8000 \
    APP_ENV=production \
    DATABASE_URL="YOUR_DATABASE_URL"
```

---

## Troubleshooting

### Build fails with "Cannot find Chromium"
- Ensure Dockerfile installs Playwright correctly
- Check build logs in GitHub Actions or Azure Deployment Center

### App crashes on startup
- Check **Log stream** in Azure Portal (your app → Monitoring → Log stream)
- Verify all environment variables are set
- Check that `WEBSITES_PORT=8000` is set

### "Application Error" or 502/503
- Wait 2-3 minutes for first cold start (Docker image pull + Playwright setup)
- Scale up to B1 if using F1 (F1 is too limited for browser automation)

### Can't access logs
- Go to App Service → **Monitoring** → **Log stream**
- Or use: `az webapp log tail --name linkedin-job-automation-ai --resource-group linkedin-automation-rg`

---

## Cost Optimization

**Azure for Students**: $100 credit for 12 months

### Pricing Options:
- **F1 (Free)**: $0/month - Limited, may not work for browser automation
- **B1 (Basic)**: ~$13/month - **Recommended minimum** for Playwright
- **B2 (Basic)**: ~$26/month - Better performance
- **S1 (Standard)**: ~$70/month - Production-grade

### Recommendation:
Start with **B1** ($13/month = ~7-8 months of your $100 credit)

---

## Next Steps After Deployment

1. ✅ Test health endpoint: `https://your-app.azurewebsites.net/`
2. ✅ Test login: POST to `/auth/login`
3. ✅ Test LinkedIn automation: Use frontend to trigger job search
4. ✅ Monitor logs for any Playwright errors
5. ✅ Once confirmed working, pause/delete Render

---

## Benefits Over Other Platforms

| Feature | Azure | Heroku | Render |
|---------|-------|--------|--------|
| Student Credit | $100 | $13/mo | $0 |
| Always On | ✅ | ❌ (sleeps) | ❌ (free tier throttled) |
| Docker Support | ✅ | ⚠️ (buildpacks) | ⚠️ (limited) |
| RAM (B1) | 1.75 GB | 512 MB | 512 MB |
| Performance | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |

---

**Total Setup Time: 15-20 minutes**

Your app will be available at: `https://linkedin-job-automation-ai.azurewebsites.net`

GitHub Actions will auto-deploy on every push to `main` branch!
