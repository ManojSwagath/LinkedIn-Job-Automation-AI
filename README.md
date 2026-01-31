# 🎯 LinkedIn Job Automation with AI

Automated LinkedIn job application system with AI-powered form filling.

## Features

- 🤖 **AI Form Filling**: Uses Gemini/OpenAI + GitHub profile for intelligent answers
- 🔄 **Multi-step Applications**: Handles complex Easy Apply forms
- 📄 **Resume Integration**: Parses and uses resume data
- 🔐 **Secure**: Credentials stored in `.env` file
- 🧪 **Test Mode**: Preview applications without submitting

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

Edit `.env` file:
```bash
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=your_password
GEMINI_API_KEY=your_gemini_key
GITHUB_API_KEY=your_github_token
```

### 3. Start Servers

```bash
# Backend (port 8000)
PYTHONPATH=$PWD python3 -m uvicorn backend.main:app --port 8000

# Frontend (port 8080)
cd frontend/lovable && npm run dev
```

### 4. Run Automation

**Option A: Frontend UI**
```
Open: http://localhost:8080/dashboard/automation
```

**Option B: Command Line**
```bash
PYTHONPATH=$PWD python3 run_full_automation.py
```

## Configuration

Set these in `.env`:

| Variable | Description |
|----------|-------------|
| `LINKEDIN_EMAIL` | Your LinkedIn email |
| `LINKEDIN_PASSWORD` | Your LinkedIn password |
| `GEMINI_API_KEY` | Google Gemini API key |
| `GITHUB_API_KEY` | GitHub personal access token |
| `JOB_KEYWORDS` | Job search keywords (default: "Software Engineer") |
| `JOB_LOCATION` | Location filter (default: "United States") |
| `MAX_APPLICATIONS` | Max apps per run (default: 5) |
| `TEST_MODE` | "true" to preview without submitting |

## Project Structure

```
├── backend/              # FastAPI backend
│   ├── agents/          # Automation bots
│   ├── routes/          # API endpoints
│   └── main.py          # Server entry
├── frontend/            # React frontend
│   └── lovable/         # UI components
├── data/                # Database & uploads
├── run_full_automation.py  # CLI automation
└── .env                 # Configuration
```

## API Endpoints

- `POST /api/v2/start-automation` - Start automation
- `GET /api/v2/automation-status/{id}` - Check progress
- `GET /api/v2/automation-results/{id}` - Get results
- `GET /health` - Server health check

## How It Works

1. **Login**: Bot logs into LinkedIn with your credentials
2. **Search**: Finds jobs matching your keywords and location
3. **Apply**: For each Easy Apply job:
   - Opens application modal
   - Fills basic fields (name, email, phone)
   - Uses AI + resume + GitHub for custom questions
   - Handles multi-step forms
   - Submits (or previews in test mode)

## Troubleshooting

**Browser won't start**
```bash
rm -rf browser_profile/SingletonLock
```

**Login fails**
- Check credentials in `.env`
- May need to solve CAPTCHA manually once

**No jobs found**
- Try different keywords
- Check location spelling

## License

MIT
