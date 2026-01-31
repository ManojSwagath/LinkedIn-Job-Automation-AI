# LinkedIn Job Automation Project Structure

## 📁 Project Overview
A clean, organized structure for LinkedIn job application automation using AI agents.

```
LinkedIn-Job-Automation-with-AI/
│
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # Project license
├── 📄 pyrightconfig.json          # Python type checking configuration
├── 📄 .gitignore                  # Git ignore rules
├── 📄 .env                        # Environment variables (not in git)
│
├── 🚀 Main Scripts
│   ├── run_full_automation.py     # Main automation script
│   └── start_system.py            # System initialization script
│
├── 📂 backend/                    # Backend application code
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── demo_automation.py         # Demo automation script
│   ├── clean_and_run.py          # Cleanup and run utility
│   │
│   ├── agents/                    # AI agent implementations
│   │   ├── __init__.py
│   │   ├── autoagenthire_bot.py  # Main automation bot
│   │   ├── enhanced_linkedin_bot.py
│   │   ├── linkedin_bot.py
│   │   ├── orchestrator.py       # Agent orchestration
│   │   ├── graph_state.py        # State management
│   │   └── ... (other agent files)
│   │
│   ├── api/                       # API integrations
│   │   ├── __init__.py
│   │   ├── autoagenthire.py      # Main API
│   │   └── linkedin_integration.py
│   │
│   ├── automation/                # Automation modules
│   │   ├── __init__.py
│   │   ├── application_handler.py
│   │   ├── intelligent_form_filler.py
│   │   └── linkedin_auto_apply.py
│   │
│   ├── database/                  # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py          # Database connections
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── schemas.py             # Pydantic schemas
│   │   ├── crud.py                # CRUD operations
│   │   ├── init_db.py             # Database initialization
│   │   ├── file_storage.py        # File storage utilities
│   │   └── vector_store.py        # Vector database operations
│   │
│   ├── llm/                       # LLM integrations
│   │   ├── __init__.py
│   │   └── ... (LLM related files)
│   │
│   ├── matching/                  # Job matching logic
│   ├── parsers/                   # Document parsers
│   ├── rag/                       # RAG implementations
│   ├── routes/                    # API routes
│   └── utils/                     # Utility functions
│
├── 📂 data/                       # Application data
│   ├── applications.json          # Application records
│   ├── autoagenthire.db          # SQLite database
│   ├── cover_letters/            # Generated cover letters
│   ├── job_listings/             # Scraped job listings
│   ├── resumes/                  # User resumes
│   ├── screenshots/              # Automation screenshots
│   ├── temp/                     # Temporary files
│   ├── templates/                # Document templates
│   └── vectors/                  # Vector embeddings
│
├── 📂 database/                   # Database schemas
│   └── init.sql                  # Initial SQL schema
│
├── 📂 docker/                     # Docker configuration
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
│
├── 📂 frontend/                   # Frontend applications
│   ├── lovable/                  # Lovable frontend
│   └── streamlit/                # Streamlit dashboard
│
├── 📂 scripts/                    # Utility scripts
│   ├── setup_db.py               # Database setup
│   ├── setup_complete.py         # Complete system setup
│   ├── smoke_check.py            # Quick system check
│   ├── smoke_login.py            # Login verification
│   ├── validate_structure.py     # Structure validation
│   └── add_sample_applications.py
│
├── 📂 uploads/                    # File uploads
│   ├── resumes/                  # Uploaded resumes
│   └── test/                     # Test files
│
├── 📂 vector_db/                  # Vector database
│   └── data/                     # Vector data storage
│
├── 📂 docs/                       # Documentation
│
└── 📂 venv/                       # Virtual environment (not in git)
```

## 🎯 Key Components

### Core Automation
- **run_full_automation.py**: Main entry point for LinkedIn automation
- **start_system.py**: System initialization and configuration

### Backend Services
- **FastAPI Server**: RESTful API for frontend communication
- **AI Agents**: Intelligent automation using LangGraph
- **Database**: SQLite for local storage, Supabase integration available

### Data Management
- **Applications**: Tracks all job applications
- **Resumes**: Stores user resumes and profiles
- **Job Listings**: Caches job postings
- **Cover Letters**: AI-generated cover letters

### Automation Features
- LinkedIn Easy Apply automation
- Intelligent form filling using AI
- Job matching and filtering
- Application tracking
- Screenshot capture for debugging

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run Automation**
   ```bash
   python run_full_automation.py
   ```

## 📝 Configuration

All configuration is managed through `.env` file:
- LinkedIn credentials
- User profile information
- Job search preferences
- API keys (Gemini AI, GitHub, Supabase)
- Automation settings

## 🔒 Security

- `.env` file is git-ignored
- Sensitive data never committed
- Browser profile excluded from git
- Credentials encrypted in database

## 📊 Data Storage

- **SQLite**: Local database for development
- **Supabase**: Cloud PostgreSQL for production
- **Vector DB**: Semantic search capabilities
- **File Storage**: Documents and screenshots

## 🧪 Development

- Python 3.13+ required
- Virtual environment recommended
- Playwright for browser automation
- FastAPI for backend API
- SQLAlchemy for database ORM

## 📚 Documentation

- **README.md**: Main project documentation
- **Backend**: See `backend/README.md`
- **Frontend**: See `frontend/README.md`
- **API**: See `docs/API.md`

---

Last Updated: January 31, 2026
