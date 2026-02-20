#  LinkedIn Job Automation with AI

An autonomous AI agent system that discovers and applies to LinkedIn jobs on your behalf — powered by FastAPI, LangChain/LangGraph, and a React/Vite frontend.

---

##  Architecture

| Layer | Technology | Hosting |
|-------|-----------|---------|
| Frontend | React + Vite (TypeScript) | **Vercel** |
| Backend API | FastAPI + Python 3.11 | **Render** |
| Database | PostgreSQL via Supabase | Supabase cloud |
| Browser Automation | Playwright (Chromium) | Render worker |
| AI / LLM | LangChain + LangGraph + Gemini / OpenAI | Render backend |

---

##  Production Deployment

### Deploy Backend  Render

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com)  **New Web Service**  connect your repo.
3. Render auto-detects `render.yaml`; click **Deploy**.
4. Set these environment variables in the Render dashboard:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (from Supabase) |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/service key |
| `OPENAI_API_KEY` | OpenAI API key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `SECRET_KEY` | Random 32-char string for JWT signing |
| `LINKEDIN_EMAIL` | LinkedIn account email |
| `LINKEDIN_PASSWORD` | LinkedIn account password |
| `ALLOWED_ORIGINS` | Your Vercel frontend URL (e.g. `https://yourapp.vercel.app`) |

5. Note your service URL: `https://linkedin-automation-backend.onrender.com`

---

### Deploy Frontend  Vercel

> **Important:** Vercel hosts only the frontend (static React build). The Python backend NEVER runs on Vercel. This avoids the 500 MB Lambda size limit entirely.

1. Go to [vercel.com](https://vercel.com)  **New Project**  import your GitHub repo.
2. Vercel auto-reads `vercel.json` at the repo root — **no manual settings needed**.
3. Add these environment variables in the Vercel dashboard (**Settings  Environment Variables**):

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Your Render backend URL (e.g. `https://linkedin-automation-backend.onrender.com`) |
| `VITE_GOOGLE_CLIENT_ID` | OAuth Client ID from Google Cloud Console |

4. Click **Deploy**.

---

##  Local Development

### 1. Clone & Install

```bash
git clone https://github.com/Sathwik11-hub/LinkedIn-Job-Automation-with-AI.git
cd LinkedIn-Job-Automation-with-AI

# Backend (Python 3.11+)
pip install -r requirements-dev.txt
playwright install chromium

# Frontend
cd frontend/lovable
npm install
```

### 2. Configure Environment

Create `.env` in the project root:

```dotenv
# LinkedIn credentials
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=your_password

# AI Keys
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

# Database (Supabase)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Auth
SECRET_KEY=your-32-char-random-secret

# Automation settings
JOB_KEYWORDS=Software Engineer
JOB_LOCATION=United States
MAX_APPLICATIONS=5
TEST_MODE=true
```

Create `frontend/lovable/.env.local`:

```dotenv
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_google_client_id
```

### 3. Start Servers

```bash
# Terminal 1 — Backend (port 8000)
PYTHONPATH=$PWD uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend (port 8080)
cd frontend/lovable && npm run dev
```

Open: [http://localhost:8080](http://localhost:8080)

---

##  Project Structure

```
 backend/               # FastAPI Python backend
    agents/            # LangGraph automation agents
    api/               # Autoagenthire API module
    auth/              # JWT auth middleware
    automation/        # LinkedIn form filler & apply logic
    database/          # SQLAlchemy models & CRUD
    llm/               # LLM wrappers (Gemini / OpenAI)
    rag/               # Resume intelligence & vector search
    routes/            # All API route handlers
    main.py            # FastAPI app entry point
 frontend/
    lovable/           # React + Vite + TailwindCSS frontend
 data/                  # Local data & uploads (gitignored in prod)
 vercel.json            # Vercel frontend deploy config
 render.yaml            # Render backend deploy config
 requirements.txt       # Production Python deps (Render)
 requirements-dev.txt   # Dev-only deps (tests, etc.)
 .vercelignore          # Tells Vercel to ignore Python backend
```

---

##  API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/auth/signup` | Register new user |
| `POST` | `/auth/login` | Login  JWT token |
| `POST` | `/api/v2/start-automation` | Start job automation |
| `GET` | `/api/v2/automation-status/{id}` | Poll automation progress |
| `GET` | `/api/v2/automation-results/{id}` | Fetch results |
| `POST` | `/api/v1/resume/upload` | Upload resume (PDF/DOCX) |
| `POST` | `/api/run-agent` | Run AI agent pipeline |
| `GET` | `/docs` | Interactive Swagger UI |

---

##  How It Works

1. **Login** — Bot authenticates to LinkedIn using Playwright (headless Chromium).
2. **Search** — Finds jobs matching your keywords/location/filters.
3. **Analyze** — LangGraph agents rank and filter jobs based on your resume.
4. **Apply** — For each Easy Apply job:
   - Opens the application modal.
   - Fills standard fields (name, email, phone) from your profile.
   - Uses Gemini/OpenAI + resume context to answer custom questions.
   - Handles multi-step forms automatically.
   - Submits (or previews in `TEST_MODE=true`).
5. **Track** — All applications logged to the database with status.

---

##  Troubleshooting

| Issue | Fix |
|-------|-----|
| Vercel 500 MB Lambda error | Ensure `vercel.json` and `.vercelignore` are committed. Vercel deploys **frontend only** — backend stays on Render. |
| `playwright install` fails on Render | `render.yaml` runs `build.sh` which calls `playwright install chromium`. |
| CORS errors in production | Set `ALLOWED_ORIGINS=https://yourapp.vercel.app` on Render. |
| Database connection refused | Verify `DATABASE_URL` is set correctly in Render env vars. |
| `psycopg2` binary not found | `psycopg2-binary` is in requirements.txt; Render installs it automatically. |

---

##  License

MIT — see [LICENSE](LICENSE).
