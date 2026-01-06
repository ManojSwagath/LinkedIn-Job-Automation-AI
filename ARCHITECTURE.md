# AutoAgentHire - Production System Architecture

## Executive Summary

**AutoAgentHire** is an autonomous agentic AI system that understands a user's resume, semantically matches job descriptions using RAG and embeddings, and uses Chromium browser automation to search and apply for LinkedIn jobs completely autonomously.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + TypeScript)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Resume Upload│  │ Agent Control│  │   Dashboard  │         │
│  │    Page      │  │    Page      │  │     Page     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                     │                                            │
│                     │ HTTP/WebSocket                             │
└─────────────────────┼────────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────────┐
│                   API LAYER (FastAPI)                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ POST /api/run-agent      │ Start autonomous job search    │ │
│  │ GET  /api/agent/status   │ Poll agent execution status    │ │
│  │ GET  /api/applications   │ Get applied jobs               │ │
│  │ POST /api/resume/upload  │ Upload and process resume      │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────┬────────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────────┐
│              AGENTIC ORCHESTRATION LAYER                         │
│                   (LangGraph / CrewAI)                           │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│  │   Resume    │──▶│  Job Search │──▶│   Matching  │          │
│  │    Agent    │   │    Agent    │   │    Agent    │          │
│  └─────────────┘   └─────────────┘   └─────────────┘          │
│         │                                    │                   │
│         ▼                                    ▼                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│  │    Logger   │   │    Apply    │   │   Report    │          │
│  │    Agent    │   │    Agent    │   │    Agent    │          │
│  └─────────────┘   └─────────────┘   └─────────────┘          │
└─────────────────────┬────────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────────┐
│                  AI & DATA LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ RAG Engine   │  │  LLM (GPT-4/ │  │    FAISS     │         │
│  │ (Embeddings) │  │   Gemini)    │  │ Vector Store │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────┬────────────────────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────────────────────┐
│            BROWSER AUTOMATION LAYER                              │
│                   (Playwright + Chromium)                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • LinkedIn Login (stealth mode)                            │ │
│  │ • Job Search & Filtering                                   │ │
│  │ • Easy Apply Detection                                     │ │
│  │ • Dynamic Form Filling                                     │ │
│  │ • Resume Upload                                            │ │
│  │ • Cover Letter Generation & Submission                    │ │
│  │ • Application Verification                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### 1. Frontend (React + TypeScript + Tailwind)
**Purpose**: User interface for control and observability

**Key Features**:
- **Resume Upload**: Upload PDF/DOCX resume, triggers parsing
- **Agent Control**: Start/stop autonomous agent, configure search parameters
- **Live Status**: Real-time polling of agent status (searching, matching, applying)
- **Results Dashboard**: View applied jobs, match scores, success/fail status

**NOT Included**:
- ❌ No manual job browsing
- ❌ No per-job apply buttons
- ❌ Frontend is observation only, agents do the work

### 2. API Layer (FastAPI)
**Purpose**: RESTful interface between frontend and backend

**Endpoints**:
```python
POST /api/run-agent
  - Body: { resume_id, keywords, location, max_jobs }
  - Response: { job_id, status: "started" }
  - Triggers autonomous agent workflow

GET /api/agent/status/{job_id}
  - Response: { status, current_phase, jobs_found, jobs_applied }
  - Polls agent execution state

GET /api/applications
  - Response: [{ job_title, company, status, match_score, timestamp }]
  - Returns all application results

POST /api/resume/upload
  - Body: multipart/form-data with resume file
  - Response: { resume_id, extracted_skills, experience }
  - Parses and stores resume
```

### 3. Agentic Orchestration Layer
**Purpose**: Multi-agent system that executes job application autonomously

**Agent Architecture**:

**Resume Agent**
- Responsibility: Parse and understand resume
- Input: Resume PDF/DOCX
- Output: Structured data (skills, experience, keywords)
- LLM Task: Extract key information, normalize format
- Storage: Structured JSON + embeddings in FAISS

**Job Search Agent**
- Responsibility: Execute LinkedIn job search
- Input: Keywords, location, filters
- Output: List of job URLs
- Browser Action: Navigate LinkedIn, apply Easy Apply filter, scroll and collect
- Handoff: Send jobs to Matching Agent

**Matching Agent**
- Responsibility: Score jobs against resume
- Input: Resume embeddings + Job descriptions
- Output: Ranked job list with match scores
- AI Action: Compute semantic similarity using FAISS
- Threshold: Only jobs > 75% match proceed to Apply Agent

**Apply Agent**
- Responsibility: Submit applications automatically
- Input: Qualified jobs list
- Output: Application results (success/fail)
- Browser Action: 
  - Click Easy Apply
  - Fill forms dynamically
  - Upload resume
  - Generate AI cover letter
  - Submit application
  - Verify submission
- Error Handling: Skip if not Easy Apply, retry on failure

**Logger Agent**
- Responsibility: Track and record all actions
- Input: Events from all agents
- Output: Structured logs, database entries
- Storage: SQLite database + log files
- Dashboard: Send updates to frontend

**Report Agent**
- Responsibility: Generate summary reports
- Input: Application results
- Output: Summary report (applied, skipped, failed)
- Delivery: Console + email + dashboard

### 4. RAG & Embeddings Layer
**Purpose**: Semantic matching between resume and jobs

**Flow**:
```
Resume Text → OpenAI Embedding Model → Vector (1536 dimensions)
                                               ↓
                                         FAISS Index
                                               ↓
Job Description → OpenAI Embedding Model → Query Vector
                                               ↓
                                    Cosine Similarity Score
                                               ↓
                                   Match Score (0-100%)
```

**Decision Logic**:
- Score >= 75%: High match, proceed to apply
- Score 60-74%: Medium match, apply if slots available
- Score < 60%: Low match, skip

### 5. Browser Automation Layer (Playwright)
**Purpose**: Interact with LinkedIn as a human would

**Key Features**:
- **Stealth Mode**: Bypass bot detection
  - Remove webdriver flags
  - Realistic user agent
  - Human-like delays (1-3 seconds)
  - Random mouse movements
  - Persistent browser profile

- **Login**:
  - Navigate to LinkedIn login
  - Enter credentials with typing delays
  - Handle CAPTCHA (manual for now)
  - Verify successful login

- **Job Search**:
  - Navigate to Jobs section
  - Enter keywords and location
  - Apply Easy Apply filter
  - Scroll to load more jobs
  - Extract job cards (title, company, link)

- **Easy Apply Detection**:
  - Click on job
  - Look for "Easy Apply" button
  - If not present, skip job
  - If present, click to start

- **Dynamic Form Filling**:
  - Detect form fields (text, dropdown, radio, checkbox)
  - Map fields to resume data:
    - Name → Resume name
    - Email → Resume email
    - Phone → Resume phone
    - Years of experience → Extract from resume
    - Skills → Resume skills
  - Fill unknown fields with reasonable defaults

- **Cover Letter**:
  - Detect cover letter field
  - Generate using LLM:
    ```
    Prompt: "Write a professional cover letter for {job_title} at {company}. 
    My background: {resume_summary}. Keep it under 200 words."
    ```
  - Paste generated text

- **Submission**:
  - Navigate through multi-page forms
  - Click "Next" until "Submit" appears
  - Click "Submit application"
  - Wait for confirmation message
  - Capture screenshot as proof

- **Verification**:
  - Look for "Application sent" or similar
  - Record job ID and timestamp
  - Mark as SUCCESS or FAILED

### 6. Data Storage
**Purpose**: Persist data for tracking and reporting

**Database Schema** (SQLite):
```sql
-- Resumes
CREATE TABLE resumes (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    filename TEXT,
    raw_text TEXT,
    structured_data JSON,
    embedding BLOB,
    created_at TIMESTAMP
);

-- Jobs
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    job_id TEXT UNIQUE,
    title TEXT,
    company TEXT,
    location TEXT,
    description TEXT,
    job_url TEXT,
    match_score FLOAT,
    created_at TIMESTAMP
);

-- Applications
CREATE TABLE applications (
    id INTEGER PRIMARY KEY,
    job_id TEXT,
    resume_id INTEGER,
    status TEXT, -- 'APPLIED', 'SKIPPED', 'FAILED'
    error_message TEXT,
    screenshot_path TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);

-- Agent Runs
CREATE TABLE agent_runs (
    id INTEGER PRIMARY KEY,
    run_id TEXT UNIQUE,
    status TEXT, -- 'RUNNING', 'COMPLETED', 'FAILED'
    keywords TEXT,
    location TEXT,
    jobs_found INTEGER,
    jobs_applied INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

## Execution Flow

### Complete Autonomous Workflow

```
1. USER INITIATES
   Frontend: User uploads resume
   Frontend: User clicks "Start Agent" with keywords/location
   API: POST /api/run-agent
   
2. RESUME AGENT ACTIVATES
   - Parse resume file (PDF/DOCX)
   - Extract text using PyPDF2/python-docx
   - Send to LLM: "Extract skills, experience, tools from this resume"
   - Store structured data
   - Generate embeddings using OpenAI
   - Store in FAISS vector index
   - Handoff: Signal Job Search Agent
   
3. JOB SEARCH AGENT ACTIVATES
   - Initialize Playwright browser (stealth mode)
   - Login to LinkedIn
   - Navigate to Jobs section
   - Enter search: {keywords} in {location}
   - Click "Easy Apply" filter
   - Scroll page 10 times (load ~50-100 jobs)
   - For each job card:
     - Extract: title, company, location, job_url
     - Store in memory
   - Close job search phase
   - Handoff: Send job list to Matching Agent
   
4. MATCHING AGENT ACTIVATES
   - For each job:
     - Fetch job description (click job card, scrape text)
     - Generate embedding for job description
     - Query FAISS: similarity(resume_embedding, job_embedding)
     - Compute match score (0-100%)
   - Filter jobs: score >= 75%
   - Sort by score descending
   - Take top N jobs (user-defined, default 10)
   - Handoff: Send qualified jobs to Apply Agent
   
5. APPLY AGENT ACTIVATES
   - For each qualified job:
     a. Navigate to job_url
     b. Click "Easy Apply" button
     c. Application form appears
     d. Detect form fields:
        - Text inputs → fill from resume
        - Dropdowns → select best match
        - Checkboxes → check required ones
     e. Resume upload:
        - Look for file input
        - Upload resume PDF
     f. Cover letter:
        - Generate using LLM
        - Paste into text area
     g. Navigate pages:
        - Click "Next" if multi-page
        - Click "Submit application" on final page
     h. Verify submission:
        - Look for "Application sent" message
        - Capture screenshot
        - Record result
     i. Log result:
        - SUCCESS → applications table
        - FAILED → applications table with error
     j. Human delay (5-10 seconds between applications)
   - Handoff: Send results to Report Agent
   
6. REPORT AGENT ACTIVATES
   - Collect all application results
   - Generate summary:
     - Total jobs found
     - Jobs matched (score >= 75%)
     - Jobs applied
     - Jobs skipped
     - Jobs failed
   - Create report:
     - Console output
     - Save to file
     - Send to frontend dashboard
   - Mark agent run as COMPLETED
   
7. LOGGER AGENT (CONTINUOUS)
   - Runs throughout entire process
   - Logs every action to database
   - Captures screenshots at key steps
   - Handles errors and retries
   
8. FRONTEND UPDATES
   - Poll /api/agent/status every 5 seconds
   - Display: "Searching jobs... 47 found"
   - Display: "Matching jobs... 12 qualified"
   - Display: "Applying... 8/12 complete"
   - Final: "Done! 8 applied, 4 skipped"
   - Show results table with links
```

## Why Agentic Approach?

Traditional automation is sequential and brittle:
```
Script → Login → Search → Apply to Job 1 → Apply to Job 2 → ...
(Fails if any step breaks)
```

Agentic approach is modular and resilient:
```
Orchestrator
    ↓
Resume Agent (independent, can retry)
    ↓
Job Search Agent (can handle failures, retry search)
    ↓
Matching Agent (can re-rank if needed)
    ↓
Apply Agent (applies to each job independently, skips failures)
    ↓
Report Agent (always runs, even if some failed)
```

**Benefits**:
1. **Modularity**: Each agent is independent
2. **Resilience**: One failure doesn't stop entire process
3. **Observability**: Each agent reports status
4. **Scalability**: Can parallelize agents
5. **Testability**: Test each agent separately

## Technology Justification

| Technology | Why This Choice |
|------------|-----------------|
| **Python** | Best ecosystem for AI/ML and automation |
| **FastAPI** | Modern async framework, auto-docs, fast |
| **Playwright** | Most reliable browser automation, anti-detection |
| **LangChain** | Agent orchestration, LLM abstraction |
| **FAISS** | Facebook's vector search, fast and local |
| **OpenAI** | Best embeddings and GPT-4 for generation |
| **React** | Industry standard for dashboards |
| **TypeScript** | Type safety for production apps |
| **Tailwind** | Rapid UI development, professional look |
| **SQLite** | Simple, file-based, no server needed |

## Security & Safety

1. **Credentials**: Stored in .env, never in code
2. **Rate Limiting**: 5-10 second delays between applications
3. **CAPTCHA Handling**: Manual intervention when detected
4. **Browser Profile**: Persistent to reduce detection
5. **Error Handling**: Graceful failures, retry logic
6. **Cooldown**: Stop after 20 applications, resume next day
7. **Stealth**: Remove webdriver flags, realistic user agent

## Production Checklist

- [x] Architecture documented
- [ ] Resume parsing with LLM
- [ ] FAISS vector store integration
- [ ] Multi-agent orchestration
- [ ] Enhanced browser automation
- [ ] API layer implementation
- [ ] Frontend dashboard
- [ ] Error handling & retries
- [ ] Database schema
- [ ] Testing & validation
- [ ] Demo instructions
- [ ] Interview explanation

## Next Steps

Phase 2: Implement Resume Intelligence (RAG + Embeddings)
