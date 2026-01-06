# 🚀 FULL STACK QUICK START GUIDE

## Complete System: Frontend + Backend on Localhost

This guide will help you run the **complete AutoAgentHire system** with:
- ✅ **Frontend**: Lovable React UI on `http://localhost:8080`
- ✅ **Backend**: FastAPI server on `http://localhost:8000`
- ✅ **Integration**: Both working together seamlessly

---

## ⚡ QUICK START (2 Minutes)

### Option 1: Automated Script (Recommended)

```bash
./RUN_FULL_STACK.sh
```

This script will:
1. Check all prerequisites
2. Install frontend dependencies if needed
3. Start backend API server (port 8000)
4. Start frontend dev server (port 8080)
5. Open monitoring interface

**Then open your browser**: `http://localhost:8080`

---

### Option 2: Manual Start

If you prefer to run services separately:

**Terminal 1 - Backend:**
```bash
cd backend
../venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend/lovable
npm install  # First time only
npm run dev
```

---

## ⚙️ REQUIRED CONFIGURATION

Before running, ensure `.env` has your credentials:

```bash
# Edit main .env
nano .env
```

**Update these fields:**
```bash
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
```

**Frontend .env** (auto-created by script, or manually):
```bash
cd frontend/lovable
nano .env
```

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

---

## 🌐 SYSTEM URLS

After starting:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8080 | Main web interface |
| **Backend API** | http://localhost:8000 | REST API server |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| **OpenAPI JSON** | http://localhost:8000/openapi.json | API specification |

---

## 🎯 HOW TO USE THE SYSTEM

### 1. Open Frontend
Navigate to: `http://localhost:8080`

### 2. Upload Resume
- Click "Upload Resume" button
- Select your PDF/DOCX file
- System will parse it automatically with AI

### 3. Configure Job Search
Enter your preferences:
- **Keywords**: "Python Developer", "Data Scientist", "Software Engineer"
- **Location**: "Remote", "San Francisco", "United States"
- **Max Jobs**: 5-15 (recommended for testing)
- **Match Threshold**: 75% (only apply to highly relevant jobs)

### 4. Start Workflow
- Click "Start Job Search"
- Watch real-time progress:
  - ✅ Parsing resume
  - ✅ Searching LinkedIn
  - ✅ Matching jobs
  - ✅ Auto-applying
  - ✅ Generating report

### 5. View Results
- See applications submitted
- View match scores
- Download detailed report
- Check LinkedIn applications

---

## 📡 API ENDPOINTS

The backend provides 7 RESTful endpoints:

### 1. Start Workflow
```bash
POST http://localhost:8000/api/agent/run
Content-Type: application/json

{
  "user_id": 1,
  "job_keywords": "Python Developer",
  "job_location": "Remote",
  "max_jobs": 10,
  "match_threshold": 75.0
}

Response:
{
  "run_id": "abc123",
  "status": "started",
  "message": "Workflow initiated"
}
```

### 2. Check Status
```bash
GET http://localhost:8000/api/agent/status/abc123

Response:
{
  "run_id": "abc123",
  "status": "running",
  "current_step": "matching_jobs",
  "progress": 65,
  "message": "Matching 30 jobs with resume..."
}
```

### 3. Get Results
```bash
GET http://localhost:8000/api/agent/results/abc123

Response:
{
  "run_id": "abc123",
  "status": "completed",
  "report": {
    "applications": 8,
    "success_rate": 87.5,
    "matches": [...]
  }
}
```

### 4. Upload Resume
```bash
POST http://localhost:8000/api/agent/resume/upload
Content-Type: multipart/form-data

file: resume.pdf
user_id: 1

Response:
{
  "resume_id": 123,
  "skills": ["Python", "FastAPI", "React"],
  "experience": "5 years"
}
```

### 5. List Applications
```bash
GET http://localhost:8000/api/agent/applications?user_id=1

Response:
{
  "applications": [
    {
      "id": 1,
      "job_title": "Senior Python Developer",
      "company": "TechCorp",
      "match_score": 94,
      "status": "applied"
    },
    ...
  ]
}
```

### 6. Workflow History
```bash
GET http://localhost:8000/api/agent/runs?user_id=1

Response:
{
  "runs": [
    {
      "run_id": "abc123",
      "status": "completed",
      "applications": 8,
      "created_at": "2026-01-04T15:30:00"
    },
    ...
  ]
}
```

### 7. Statistics
```bash
GET http://localhost:8000/api/agent/stats?user_id=1

Response:
{
  "total_applications": 24,
  "success_rate": 85.0,
  "avg_match_score": 82.3,
  "total_runs": 3
}
```

---

## 🔍 FRONTEND FEATURES

The Lovable React frontend provides:

### Dashboard
- 📊 **Statistics**: Total applications, success rate, avg match score
- 📈 **Charts**: Visual analytics of your job search
- 🎯 **Recent Activity**: Latest applications and matches

### Resume Management
- 📄 **Upload**: PDF/DOCX support
- 🤖 **AI Parsing**: GPT-4o-mini extraction
- ✏️ **Edit**: Manual skill/experience editing
- 📋 **Preview**: View parsed resume data

### Job Search
- 🔍 **Search Form**: Keywords, location, max jobs
- ⚙️ **Settings**: Match threshold, preferences
- ▶️ **Start Button**: Initiate workflow
- ⏸️ **Pause/Stop**: Control execution

### Live Monitoring
- 🔄 **Real-time Progress**: 5-second polling
- 📝 **Step-by-step Updates**: Current agent activity
- 📊 **Progress Bar**: Visual completion indicator
- 🚨 **Error Handling**: Clear error messages

### Results View
- ✅ **Applications List**: All submitted applications
- 🎯 **Match Scores**: Sorted by relevance
- 📄 **Job Details**: Company, title, description
- 🔗 **LinkedIn Links**: Direct links to applications
- 📥 **Export**: Download JSON report

---

## 🛠️ TROUBLESHOOTING

### Problem: Frontend won't connect to backend

**Check:**
```bash
# Verify backend is running
curl http://localhost:8000/docs

# Check frontend .env
cat frontend/lovable/.env
# Should show: VITE_API_BASE_URL=http://localhost:8000
```

**Solution:**
```bash
# Restart both services
./stop_all.sh
./RUN_FULL_STACK.sh
```

---

### Problem: Port already in use

**Error**: `EADDRINUSE: address already in use :::8080`

**Solution:**
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill

# Or use different port
cd frontend/lovable
npm run dev -- --port 3000
```

---

### Problem: Frontend can't find API endpoints

**Check network tab** in browser DevTools:
- Look for 404 errors
- Verify URL is `http://localhost:8000/api/agent/...`

**Solution:**
```bash
# Verify CORS is configured
grep CORS_ORIGINS .env
# Should include: http://localhost:8080
```

---

### Problem: OpenAI API errors

**Error**: "Invalid API key"

**Solution:**
```bash
# Update .env with valid key
nano .env
# OPENAI_API_KEY=sk-proj-...

# Restart backend
./stop_all.sh
./RUN_FULL_STACK.sh
```

---

### Problem: Node modules missing

**Error**: `Cannot find module 'react'`

**Solution:**
```bash
cd frontend/lovable
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 📊 MONITORING

### View Backend Logs
```bash
tail -f backend.log
```

**Look for:**
- API request logs
- Database queries
- Error messages
- Workflow progress

### View Frontend Logs
```bash
tail -f frontend.log
```

**Look for:**
- Vite dev server status
- Build errors
- Hot module replacement

### Database Queries
```bash
sqlite3 data/autoagenthire.db

# View applications
SELECT job_title, company, match_score, status 
FROM applications 
ORDER BY match_score DESC;

# View runs
SELECT * FROM agent_runs ORDER BY created_at DESC;

# Exit
.quit
```

---

## 🔄 WORKFLOW EXAMPLE

### Complete User Flow:

1. **User opens** `http://localhost:8080`
2. **Frontend loads** → Connects to backend
3. **User uploads resume** → POST `/api/agent/resume/upload`
4. **Backend parses** → GPT-4o-mini extraction
5. **Frontend shows** parsed skills/experience
6. **User enters** job search criteria
7. **User clicks** "Start Job Search"
8. **Frontend sends** → POST `/api/agent/run`
9. **Backend returns** `run_id: "abc123"`
10. **Frontend polls** → GET `/api/agent/status/abc123` (every 5s)
11. **Backend updates** progress in real-time
12. **Workflow completes** after 15-20 minutes
13. **Frontend fetches** → GET `/api/agent/results/abc123`
14. **User sees** comprehensive report
15. **User checks** LinkedIn for confirmations

---

## ⏱️ EXPECTED TIMINGS

| Phase | Duration | Description |
|-------|----------|-------------|
| Frontend Load | 1-2s | Initial page load |
| Resume Upload | 5-10s | File upload + parsing |
| Workflow Start | <1s | API call response |
| Resume Parsing | 30-60s | GPT-4 extraction |
| Job Search | 2-5 min | LinkedIn browsing |
| Matching | 5-15s | FAISS similarity |
| Auto-Apply | 5-10 min | 8-12 applications |
| Report | 5-10s | Generate results |
| **Total** | **12-20 min** | Complete workflow |

---

## 🎨 TECH STACK

### Frontend (Lovable)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **UI Library**: shadcn/ui + Radix UI
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query
- **Animations**: Framer Motion
- **HTTP Client**: Fetch API

### Backend (FastAPI)
- **Framework**: FastAPI 0.109
- **Server**: Uvicorn
- **Database**: SQLite + SQLAlchemy
- **AI**: OpenAI GPT-4o-mini
- **Embeddings**: Sentence-Transformers
- **Vector Search**: FAISS
- **Browser**: Playwright
- **Validation**: Pydantic

---

## 📝 DEVELOPMENT TIPS

### Hot Reload
Both frontend and backend support hot reload:
- **Frontend**: Edit files in `frontend/lovable/src/` → instant update
- **Backend**: Edit files in `backend/` → server auto-restarts

### API Testing
Use Swagger UI for testing:
1. Open `http://localhost:8000/docs`
2. Click endpoint → "Try it out"
3. Fill parameters → "Execute"
4. View response

### Component Development
Frontend component structure:
```
frontend/lovable/src/
├── components/        # Reusable UI components
├── pages/            # Route pages
├── lib/              # Utilities, API client
├── hooks/            # Custom React hooks
└── types/            # TypeScript types
```

---

## 🚀 PRODUCTION DEPLOYMENT

### Environment Variables

**Backend (.env)**:
```bash
APP_ENV=production
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=postgresql://...  # Use PostgreSQL in prod
```

**Frontend (.env.production)**:
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_API_TIMEOUT=60000
```

### Build Frontend
```bash
cd frontend/lovable
npm run build

# Output: dist/ directory
# Serve with: nginx, Vercel, Netlify, etc.
```

### Run Backend
```bash
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 🎉 SUCCESS CHECKLIST

After running `./RUN_FULL_STACK.sh`, verify:

- [ ] Backend running on http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Frontend running on http://localhost:8080
- [ ] Frontend connects to backend (no CORS errors)
- [ ] Can upload resume successfully
- [ ] Can start job search workflow
- [ ] Real-time progress updates work
- [ ] Results displayed after completion
- [ ] Database records saved

---

## 📞 SUPPORT

**Issue?** Check:
1. **Backend logs**: `tail -f backend.log`
2. **Frontend logs**: `tail -f frontend.log`
3. **Browser console**: DevTools → Console
4. **Network tab**: DevTools → Network

**Documentation**:
- `RUN_PROJECT_GUIDE.md` - Complete setup guide
- `COMPLETE_DOCUMENTATION.md` - Full system docs
- `README_PRODUCTION.md` - Production deployment

---

## 🛑 STOPPING THE SYSTEM

### Option 1: Graceful Shutdown
If using `RUN_FULL_STACK.sh`, press **Ctrl+C**

### Option 2: Stop Script
```bash
./stop_all.sh
```

### Option 3: Manual
```bash
# Stop backend
kill $(cat backend.pid)

# Stop frontend
kill $(cat frontend.pid)

# Or kill by port
lsof -ti:8000 | xargs kill  # Backend
lsof -ti:8080 | xargs kill  # Frontend
```

---

## 🎯 QUICK REFERENCE

```bash
# Start everything
./RUN_FULL_STACK.sh

# Stop everything
./stop_all.sh

# Backend only
cd backend && ../venv/bin/python -m uvicorn main:app --reload

# Frontend only
cd frontend/lovable && npm run dev

# View logs
tail -f backend.log frontend.log

# Database query
sqlite3 data/autoagenthire.db "SELECT * FROM applications;"

# Check ports
lsof -i:8000  # Backend
lsof -i:8080  # Frontend
```

---

**Happy job hunting! 🚀**

*AutoAgentHire - Your Complete AI Career Assistant*
