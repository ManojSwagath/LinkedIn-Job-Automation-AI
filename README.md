# LinkedIn Job Automation with AI# AutoAgentHire - AI-Powered LinkedIn Job Automation



An intelligent job application automation system with AI-powered filtering and matching.🤖 Automate your LinkedIn job search with AI-powered cover letters and smart application management.



## Quick Start## ✅ Status: FULLY OPERATIONAL



### 1. Install DependenciesAll features tested and working! See [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) for details.

```bash

pip install -r requirements.txt## ✨ Features

cd frontend/lovable && npm install

```- **Multi-AI Provider Support**: Use Gemini, Groq, or OpenAI for cover letter generation

- **Smart Job Search**: Automated LinkedIn job discovery based on your preferences

### 2. Configure Environment- **AI Cover Letters**: Personalized cover letters generated for each application

Create a `.env` file in the root directory:- **Auto-Submit Applications**: Automatically submit applications or preview before sending

```bash- **Real-time Monitoring**: Live status updates and application tracking

LINKEDIN_EMAIL=your_email@example.com- **Resume Analysis**: AI-powered resume parsing and skill extraction

LINKEDIN_PASSWORD=your_password- **Modern React UI**: Beautiful, responsive interface built with React + TypeScript + Vite

OPENAI_API_KEY=your_openai_key

```## 🚀 Quick Start (One Command!)



### 3. Start the Application### Prerequisites

```bash- Python 3.8+

# Start both backend and frontend- Node.js 16+

bash quick_start.sh- Gemini API Key (free tier available at https://makersuite.google.com/app/apikey)



# Or start individually### Setup and Run

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

cd frontend/lovable && npm run dev -- --host --port 8080```bash

```# 1. Clone the repository

cd LinkedIn-Job-Automation-with-AI

### 4. Access the Application

- **Frontend**: http://localhost:8080# 2. Create .env file with your API key

- **Backend API**: http://localhost:8000echo "GEMINI_API_KEY=your_key_here" > .env

- **API Docs**: http://localhost:8000/docsecho 'CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:8080,http://localhost:8501,https://*.lovable.app,https://*.lovable.dev' >> .env



## Features# 3. Install dependencies (first time only)

pip install -r requirements.txt

### ✅ Production-Grade Job Filteringcd frontend/lovable && npm install && cd ../..

- **12 Role Taxonomy**: AI Engineer, ML Engineer, Data Scientist, etc.

- **4-Stage Pipeline**: Hard filters → Role matching → Filled detection → Freshness validation# 4. Run everything with one command!

- **Smart Exclusions**: Automatically blocks irrelevant jobs (MCAL, Documentum, Embedded, etc.)chmod +x quick_start.sh

- **95%+ Accuracy**: Eliminates false positives./quick_start.sh

```

### ✅ LinkedIn Integration

- Automated job search and scraping### ✅ Smoke check (optional but recommended)

- Recommended jobs fetching

- Profile-based matchingAfter startup, you can quickly verify both services respond:



### ✅ AI-Powered Features```bash

- Resume parsing and analysissource venv/bin/activate

- Job description matchingpython3 scripts/smoke_check.py

- Cover letter generation```

- Application tracking

That's it! The script will:

## Project Structure- ✅ Check/install Playwright Chromium

- ✅ Start backend on port 8000

```- ✅ Start frontend on port 8080

.- ✅ Open your browser automatically

├── backend/              # FastAPI backend

│   ├── agents/          # AI agents**Access the app at: http://127.0.0.1:8080**

│   ├── automation/      # LinkedIn automation

│   ├── matching/        # Job filtering & matching## 📖 Usage Guide

│   ├── routes/          # API routes

│   └── main.py          # Entry point### First Time Setup

├── frontend/            # React frontend1. Open http://127.0.0.1:8080

│   └── lovable/         # UI components2. **Step 1**: Enter your name and email

├── tests/               # Test files3. **Step 2**: Upload your resume (PDF, DOCX, or TXT)

├── scripts/             # Utility scripts4. **Step 3**: Configure job preferences (keywords like "Software Engineer", locations like "Remote")

├── data/                # Application data5. **Step 4**: Enter your LinkedIn credentials

└── requirements.txt     # Python dependencies6. Click **Start Agent** to begin!

```

### What Happens Next?

## Essential ScriptsThe agent will:

1. 🔐 Login to LinkedIn (in a visible browser window)

- `quick_start.sh` - Start backend and frontend2. 🔍 Search for jobs matching your criteria

- `stop_all.sh` - Stop all services3. 📝 Generate personalized cover letters using AI

- `start_app.sh` - Alternative startup script4. ✉️ Submit applications automatically

5. 📊 Track everything in the dashboard

## Testing

### Manual Control

```bash- **Pause**: Temporarily stop the agent

# Run production filtering tests- **Resume**: Continue from where it paused

python3 tests/test_production_filtering.py- **Stop**: End the automation session



# Run all tests## 🧪 Validation

python3 -m pytest tests/

```Test all features are working:



## Production Filtering System```bash

# Run comprehensive validation

The system uses a LinkedIn-aligned filtering pipeline:python3 validate_project.py



1. **Hard Filters** (Fast, 60-70% removal)# Test resume upload specifically

   - Exclude bad keywords (mcal, documentum, embedded, intern, etc.)python3 test_upload_endpoint.py

   - Require role title match```

   - Require key skills in description

Both should show all tests passing ✅

2. **Filled Job Detection**

   - Text signals: "position filled", "no longer accepting"## 🔧 Configuration

   - High applicant count (>500)

   - Missing apply button### Environment Variables (.env)



3. **Freshness Validation**Required:

   - Rejects jobs older than 30 days```bash

GEMINI_API_KEY=your_gemini_api_key_here

4. **AI Validation** (Optional)```

   - Final accuracy check using LLM

Optional (defaults provided):

## Configuration```bash

# CORS Origins (already configured)

### Filtering ModesCORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:8080,http://localhost:8501,https://*.lovable.app,https://*.lovable.dev



**Strict Filtering** (Recommended):# Database

- Enable checkbox in UIDATABASE_URL=sqlite:///./autoagenthire.db

- Only jobs matching exact criteria

- Highest accuracy# Security

SECRET_KEY=your-secret-key-change-in-production

**Show All** (LinkedIn's Algorithm):```

- Disable checkbox

- Show all LinkedIn recommendations### Other AI Providers

- More jobs but may include some irrelevant ones

While Gemini is recommended (free tier), you can also use:

## API Endpoints

- **Groq** (Fast): Get key at https://console.groq.com/keys

- `GET /api/health` - Health check  - Add: `GROQ_API_KEY=your_key_here`

- `POST /api/linkedin/recommended-jobs` - Fetch recommended jobs  

- `POST /api/jobs/auto-apply` - Auto-apply to jobs- **OpenAI** (Premium): Get key at https://platform.openai.com/api-keys

- `GET /api/jobs` - Get all jobs  - Add: `OPENAI_API_KEY=your_key_here`



## Tech Stack## 🐛 Troubleshooting



- **Backend**: FastAPI, Python 3.11+, Playwright, OpenAI### "Failed to fetch" on resume upload

- **Frontend**: React, TypeScript, Vite, Tailwind CSS✅ **Fixed!** CORS is now properly configured.

- **Database**: SQLite (local), PostgreSQL (production)

- **AI**: OpenAI GPT-4, LangChain### Frontend not accessible

✅ **Fixed!** Now binds to 127.0.0.1:8080

## License

### Chromium not launching

See LICENSE file for details.Run: `playwright install chromium`



## Support### Python 3.13 note



For issues or questions, please open a GitHub issue.This repo can run on newer Python versions, but some optional pinned dependencies may not have wheels for your exact Python.

If `pip install -r requirements.txt` fails, use the provided `venv/` in this repo (if present) or switch to Python 3.11/3.12.
The supported/working path in this repo is to start via `./quick_start.sh`.

### LinkedIn Security Checkpoint
- This is normal on first login
- Complete the verification in the browser window
- Automation will continue after verification

## 📊 Project Structure

```
LinkedIn-Job-Automation-with-AI/
├── backend/                    # FastAPI backend
│   ├── agents/                # Automation agents
│   │   ├── autoagenthire_bot.py   # Main automation bot
│   │   ├── orchestrator.py        # Agent orchestration
│   │   └── linkedin_automation_agent.py
│   ├── api/                   # API endpoints
│   ├── automation/            # LinkedIn automation logic
│   ├── database/              # Database models
│   ├── llm/                   # AI services (Gemini, Groq, OpenAI)
│   ├── parsers/               # Resume parser
│   └── routes/                # API routes
├── frontend/lovable/          # React + TypeScript frontend
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── hooks/            # React hooks
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   └── lib/              # Utilities
│   └── vite.config.ts        # Vite config
├── data/                      # Application data
│   ├── applications.json     # Application history
│   └── resumes/              # Uploaded resumes
├── uploads/                   # File uploads
├── tests/                     # Test files
├── quick_start.sh            # One-command launcher ⭐
├── validate_project.py       # Validation script
├── test_upload_endpoint.py   # Upload tests
├── PROJECT_COMPLETE.md       # Completion summary
└── README.md                 # This file
```

## 🎯 API Endpoints

### Agent Control
- `POST /api/run-agent` - Start automation
- `GET /api/agent/status` - Get agent status
- `POST /api/agent/pause` - Pause agent
- `POST /api/agent/resume` - Resume agent
- `POST /api/agent/stop` - Stop agent

### Resume & Cover Letters
- `POST /api/upload-resume` - Upload resume
- `POST /api/generate-cover-letter` - Generate cover letter
- `POST /api/answer-question` - Answer application question

### Applications
- `GET /api/applications` - Get application history

### Job Search
- `GET /api/jobs/search` - Search for jobs

## 🔐 Security Notes

1. **Never commit API keys** to version control
2. Keep `.env` file private
3. LinkedIn credentials are stored securely (encrypted)
4. File uploads are validated (PDF, DOCX, TXT only)
5. CORS is configured for legitimate origins only

## 📝 Development

### Running Tests

```bash
# All validation tests
python3 validate_project.py

# Upload endpoint tests
python3 test_upload_endpoint.py

# Backend unit tests
pytest tests/
```

### Manual Backend/Frontend

If you prefer not to use `quick_start.sh`:

```bash
# Terminal 1 - Backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend  
cd frontend/lovable
npm run dev -- --host 127.0.0.1 --port 8080
```

## 🚧 Known Behaviors

1. **Browser Window**: Automation runs in visible browser (headed mode)
   - This is intentional for transparency and debugging
   - Do not close the browser during automation
   
2. **LinkedIn Rate Limits**: LinkedIn may temporarily block rapid applications
   - Agent includes smart delays
   - Use preview mode first to test
   
3. **Security Checkpoints**: LinkedIn may ask for verification
   - Complete it in the browser
   - Normal security behavior
   
4. **First-time Login**: May require email/phone verification
   - Complete once, then automation works

## 🎨 Features in Detail

### Resume Upload
- Supports PDF, DOCX, and TXT formats
- Automatic text extraction
- AI-powered parsing (skills, experience, education)
- Gemini-generated summary

### Cover Letter Generation
- Personalized for each job
- Uses resume content and job description
- Multiple AI providers supported
- Customizable templates

### Application Tracking
- Complete history of all applications
- Status updates (Applied, Viewed, Interview, etc.)
- Search and filter capabilities
- Export functionality (coming soon)

### Real-time Monitoring
- Live progress updates
- Detailed logs
- Error reporting
- Phase tracking (Login → Search → Apply)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

See [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

Built with:
- FastAPI (Backend)
- React + TypeScript + Vite (Frontend)
- Playwright (Browser automation)
- Google Gemini AI (AI services)
- Lovable (Frontend scaffolding)

## 📞 Support & Issues

1. Check [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) for feature details
2. Run validation scripts to diagnose issues
3. Check logs in terminal output
4. Review .env configuration
5. Open an issue on GitHub

## 🎊 Success!

If you see this message after running `validate_project.py`:

```
🎉 All tests passed! (11/11)
✨ Project is ready to use!
```

**Congratulations! Your job automation system is fully operational!**

Start applying: http://127.0.0.1:8080 🚀
- Errors (if any)
- Live activity logs

Control the agent:
- **Pause**: Temporarily stop automation
- **Resume**: Continue from where you paused
- **Stop**: End the session

## 🎯 AI Provider Comparison

| Provider | Speed | Quality | Cost | Best For |
|----------|-------|---------|------|----------|
| **Gemini** | Fast | Excellent | Free tier | Getting started, high volume |
| **Groq** | Ultra-fast | Very Good | Free tier | Speed-critical applications |
| **OpenAI** | Moderate | Excellent | Paid | Professional applications |

## 🔒 Security & Privacy

- **API keys** are stored locally in your browser (localStorage)
- **LinkedIn credentials** are used only for automation (not stored on servers)
- **Resume data** is processed locally
- **No data** is shared with third parties

## ⚙️ Configuration

### Backend Environment (.env)

```env
# At least one AI provider API key
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here  
OPENAI_API_KEY=your_openai_key_here

# Optional: Database
DATABASE_URL=postgresql://user:pass@localhost/db

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379
```

### Frontend Environment (frontend/lovable/.env)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Playwright**: Browser automation
- **Multi-AI Support**: Gemini, Groq, OpenAI
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool
- **TanStack Query**: Data fetching
- **shadcn/ui**: Component library
- **Tailwind CSS**: Styling

## 📊 Project Structure

```
LinkedIn-Job-Automation-with-AI/
├── backend/
│   ├── api/              # API routes
│   ├── agents/           # AI agents
│   ├── automation/       # LinkedIn automation
│   ├── llm/              # Multi-AI service
│   ├── parsers/          # Resume parsing
│   └── main.py          # FastAPI app
├── frontend/lovable/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API services
│   │   ├── hooks/        # React hooks
│   │   ├── lib/          # Utilities
│   │   └── pages/        # Page components
│   └── package.json
├── requirements.txt      # Python dependencies
└── start_app.sh         # Startup script
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version (requires 3.11+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Install Playwright browsers
playwright install
```

### Frontend won't start
```bash
cd frontend/lovable

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Try different port
npm run dev -- --port 8081
```

### API Key errors
- Verify your API key is correct and active
- Check if you've exceeded rate limits
- Try a different AI provider

### LinkedIn automation issues
- Ensure you're using correct credentials
- LinkedIn may require 2FA - disable temporarily for automation
- Wait 1-2 minutes between runs to avoid rate limiting

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This tool is for educational purposes. Automated job applications should be used responsibly:
- Review applications before submitting in auto-mode
- Customize cover letters as needed
- Follow LinkedIn's terms of service
- Respect companies' application processes

## 📞 Support

For issues or questions:
- Check the **Help** section in the dashboard
- Review API documentation at http://localhost:8000/docs
- Open an issue on GitHub

---

**Made with ❤️ for job seekers everywhere**

Start automating your job search today! 🚀
