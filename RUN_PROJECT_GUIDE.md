# 🚀 STEP-BY-STEP PROJECT RUN GUIDE

## Prerequisites Checklist

Before starting, ensure you have:
- [ ] Python 3.11+ installed
- [ ] OpenAI API key (from https://platform.openai.com/api-keys)
- [ ] LinkedIn account credentials
- [ ] Your resume file (PDF, DOCX, or TXT)

---

## Step 1: Configure Environment Variables ⚙️

**ACTION REQUIRED:** Edit the `.env` file with your actual credentials:

```bash
nano .env
# or
code .env
```

**Update these critical fields:**

```bash
# REQUIRED: Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE

# REQUIRED: Your LinkedIn login
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-actual-password

# RECOMMENDED: Your personal info for auto-filling applications
FIRST_NAME=Your First Name
LAST_NAME=Your Last Name
PHONE_NUMBER=+1234567890
CITY=Your City
STATE=Your State
COUNTRY=United States
LINKEDIN_URL=https://www.linkedin.com/in/yourprofile
```

**Save the file** after editing.

---

## Step 2: Install Dependencies 📦

Install all required Python packages:

```bash
pip install -r requirements.txt
```

**Expected packages:**
- fastapi, uvicorn (API server)
- playwright (browser automation)
- openai (AI integration)
- sqlalchemy (database)
- pydantic (data validation)
- sentence-transformers (embeddings)
- faiss-cpu (vector search)
- pypdf, python-docx (resume parsing)

**Time:** ~2-3 minutes

---

## Step 3: Install Playwright Browsers 🌐

Playwright needs Chromium browser for LinkedIn automation:

```bash
playwright install chromium
```

**Time:** ~1-2 minutes (downloads ~200MB)

---

## Step 4: Initialize Database 💾

Create the SQLite database with all required tables:

```bash
python3 -c "import sys; sys.path.insert(0, '.'); from backend.database.connection import init_db; init_db()"
```

**Expected output:**
```
✅ Loaded embedding model: all-MiniLM-L6-v2
✅ Created new resume index
✅ Created new job index
✅ Database tables created successfully
```

**Tables created:**
- users
- resumes
- agent_runs
- applications
- agent_logs
- job_cache
- file_storage

**Database location:** `data/autoagenthire.db`

---

## Step 5: Prepare Your Resume 📄

Copy your resume to the data directory:

```bash
# Create directory if it doesn't exist
mkdir -p data/resumes

# Copy your resume (replace with your actual file path)
cp ~/Downloads/my_resume.pdf data/resumes/my_resume.pdf
```

**Supported formats:**
- PDF (.pdf)
- Word Document (.docx)
- Text (.txt)

---

## Step 6: Run Quick System Test ✅

Verify all components are working:

```bash
python3 test_quick.py
```

**Expected tests:**
1. ✅ Resume Intelligence - Parsing and matching
2. ✅ Database Operations - CRUD functions
3. ✅ API Routes - 7 endpoints loaded

**If any test fails:**
- Check your OPENAI_API_KEY is valid
- Ensure database was initialized
- Verify dependencies installed correctly

---

## Step 7: Choose Your Run Mode 🎯

You have **3 options** to run the system:

### **Option A: Interactive Runner (Recommended for First Time)**

```bash
./run_autoagenthire.sh
```

**Menu will appear:**
```
========================================
  AutoAgentHire - Autonomous AI Agent
========================================

Select mode:
  1) API Server (for frontend integration)
  2) Direct Workflow (standalone automation)
  3) Component Test (quick validation)
  4) Full E2E Test (comprehensive test)

Enter choice [1-4]:
```

**Choose option 2** for your first run (Direct Workflow).

---

### **Option B: Direct Python Execution**

Run the orchestrator directly with your job search criteria:

```bash
python3 backend/agents/orchestrator_integration_example.py \
  --resume-path "data/resumes/my_resume.pdf" \
  --keywords "Python Developer" \
  --location "San Francisco" \
  --max-jobs 10 \
  --mode basic
```

**Parameters:**
- `--resume-path`: Path to your resume file
- `--keywords`: Job search keywords (e.g., "Software Engineer", "Data Scientist")
- `--location`: Job location (e.g., "Remote", "New York", "United States")
- `--max-jobs`: Maximum number of jobs to process (start with 5-10)
- `--mode`: Execution mode
  - `basic` - Standard workflow
  - `monitor` - Real-time monitoring with status updates
  - `test` - Test mode without actual applications

**Example for Remote Python Developer:**
```bash
python3 backend/agents/orchestrator_integration_example.py \
  --resume-path "data/resumes/john_doe_resume.pdf" \
  --keywords "Python Developer Remote" \
  --location "United States" \
  --max-jobs 15 \
  --mode monitor
```

---

### **Option C: API Server (For Frontend/Production)**

Start the FastAPI server:

```bash
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Access the API:**
- API Docs: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

**Available endpoints:**
1. `POST /api/agent/run` - Start workflow
2. `GET /api/agent/status/{run_id}` - Check status
3. `GET /api/agent/results/{run_id}` - Get results
4. `POST /api/agent/resume/upload` - Upload resume
5. `GET /api/agent/applications` - List applications
6. `GET /api/agent/runs` - Workflow history
7. `GET /api/agent/stats` - Statistics

**Example API usage:**
```bash
# Upload resume
curl -X POST "http://localhost:8000/api/agent/resume/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/resumes/my_resume.pdf" \
  -F "user_id=1"

# Start workflow
curl -X POST "http://localhost:8000/api/agent/run" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "job_keywords": "Python Developer",
    "job_location": "Remote",
    "max_jobs": 10,
    "match_threshold": 75.0
  }'

# Response: {"run_id": "abc123", "status": "started"}

# Check status (poll every 5 seconds)
curl "http://localhost:8000/api/agent/status/abc123"

# Get final results
curl "http://localhost:8000/api/agent/results/abc123"
```

---

## Step 8: Monitor Execution 👀

While the system runs, you can monitor:

### **Console Output**
Real-time logs showing:
- Resume parsing progress
- Job search results
- Matching scores for each job
- Application attempts
- Final report

### **Log Files**
Check detailed logs:
```bash
tail -f backend/logs/orchestrator.log
```

### **Database**
Query live data:
```bash
sqlite3 data/autoagenthire.db

# Check applications
SELECT * FROM applications;

# Check agent runs
SELECT * FROM agent_runs;

# Exit
.quit
```

---

## Step 9: Review Results 📊

### **Console Report**

You'll see a comprehensive report like:

```
╔══════════════════════════════════════════════════════════╗
║          AUTONOMOUS JOB APPLICATION REPORT                ║
╚══════════════════════════════════════════════════════════╝

📊 EXECUTION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Execution Time: 18 minutes 43 seconds
Status: ✅ SUCCESS

📝 RESUME INTELLIGENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resume: john_doe_resume.pdf
Key Skills: Python, FastAPI, React, AWS, Docker
Experience Level: 5 years
Top Expertise: Backend Development, API Design

🔍 JOB SEARCH RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Jobs Found: 47
Jobs Collected: 30
Search Query: "Python Developer"
Location: Remote
Time Taken: 4m 32s

🎯 SEMANTIC MATCHING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Jobs Analyzed: 30
Match Threshold: 75%
High Matches (≥75%): 12 jobs
Medium Matches (60-74%): 11 jobs
Low Matches (<60%): 7 jobs

Top 3 Matches:
  1. Senior Python Developer @ TechCorp - 94% match
  2. Backend Engineer @ StartupXYZ - 89% match
  3. Full Stack Developer @ CloudSolutions - 87% match

✅ APPLICATIONS SUBMITTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Applications: 8
Success Rate: 87.5%
Failed: 1 (form validation error)

Successfully Applied To:
  ✅ Senior Python Developer @ TechCorp (94% match)
  ✅ Backend Engineer @ StartupXYZ (89% match)
  ✅ Full Stack Developer @ CloudSolutions (87% match)
  ✅ Python Engineer @ DataCo (84% match)
  ✅ Software Developer @ AppWorks (81% match)
  ✅ API Developer @ ServiceHub (79% match)
  ✅ Backend Developer @ WebTech (77% match)
  ✅ Python Developer @ CodeFactory (76% match)

⚠️ Failed Applications:
  ❌ Python Developer @ ComplexCorp (form validation error)

💾 DATA PERSISTENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Database: data/autoagenthire.db
Applications Saved: 8
Report Exported: reports/job_report_20260104_153422.json

🎉 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Check your LinkedIn account for application confirmations
2. Monitor your email for recruiter responses
3. Review saved jobs in database: data/autoagenthire.db
4. View detailed report: reports/job_report_20260104_153422.json
```

### **Database Query**

Check your applications:
```bash
sqlite3 data/autoagenthire.db "SELECT job_title, company, match_score, status FROM applications ORDER BY match_score DESC;"
```

### **Report File**

A JSON report is saved in `reports/` directory with:
- Complete job details
- Match scores
- Application timestamps
- Error logs

---

## Troubleshooting 🔧

### **Issue 1: "OpenAI API key is invalid"**
**Solution:**
- Verify your API key in `.env` starts with `sk-proj-`
- Check it's not expired at https://platform.openai.com/api-keys
- Ensure you have credits on your OpenAI account

### **Issue 2: "LinkedIn login failed"**
**Solution:**
- Double-check email/password in `.env`
- LinkedIn may require 2FA - temporarily disable it
- Try logging in manually first to verify credentials
- Check if LinkedIn flagged your account for automation

### **Issue 3: "No module named 'backend'"**
**Solution:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### **Issue 4: "Database not found"**
**Solution:**
```bash
# Reinitialize database
python3 -c "from backend.database.connection import init_db; init_db()"
```

### **Issue 5: "Playwright browser not found"**
**Solution:**
```bash
playwright install chromium
```

### **Issue 6: Browser keeps getting blocked**
**Solution:**
- Set `HEADLESS_BROWSER=false` in `.env` (run in visible mode)
- Increase delays: `BROWSER_SLOW_MO=100`
- Use your existing browser profile (anti-detection)

---

## Performance Tips 🚀

### **For Faster Execution:**
1. Use `max_jobs=5-10` for testing
2. Set match threshold higher (≥80%) to reduce applications
3. Use specific keywords to narrow search

### **For Better Match Quality:**
1. Ensure resume has clear skills section
2. Use detailed job descriptions
3. Lower threshold to 70% to see more matches

### **For Stealth Mode:**
1. Set `HEADLESS_BROWSER=false` (visible browser)
2. Increase `BROWSER_SLOW_MO=100` (slower actions)
3. Add delays between applications
4. Run during normal working hours

---

## Expected Timings ⏱️

| Phase | Duration | Description |
|-------|----------|-------------|
| **Resume Parsing** | 30-60s | PDF extraction + embedding generation |
| **Job Search** | 2-5 min | LinkedIn browsing, scrolling, collecting |
| **Semantic Matching** | 5-15s | FAISS similarity search (30 jobs) |
| **Auto-Apply** | 5-10 min | Form filling, 8-10 applications |
| **Report Generation** | 5-10s | Metrics calculation, JSON export |
| **Total** | 12-20 min | Complete workflow for 30 jobs |

---

## Success Metrics 📈

After running, you should see:
- ✅ 75-90% application success rate
- ✅ 8-12 high-quality matches (≥75%)
- ✅ All data persisted to database
- ✅ Detailed report generated
- ✅ No browser crashes or hangs

---

## What Happens During Execution? 🎬

### **Phase 1: Resume Intelligence** (Agent 1)
```
[Resume Agent] Parsing resume...
[Resume Agent] Extracted: 1,234 words
[Resume Agent] Identified skills: Python, FastAPI, React, AWS, Docker
[Resume Agent] Generated embeddings: 1536 dimensions
[Resume Agent] ✅ Resume indexed in vector store
```

### **Phase 2: Job Search** (Agent 2)
```
[JobSearch Agent] Initializing browser...
[JobSearch Agent] Logging into LinkedIn...
[JobSearch Agent] ✅ Login successful
[JobSearch Agent] Searching: "Python Developer"
[JobSearch Agent] Location: Remote
[JobSearch Agent] Found 47 jobs
[JobSearch Agent] Collecting job details...
[JobSearch Agent] Progress: [████████████████████] 30/47
[JobSearch Agent] ✅ Collected 30 Easy Apply jobs
```

### **Phase 3: Semantic Matching** (Agent 3)
```
[Matching Agent] Analyzing 30 jobs...
[Matching Agent] Job 1: Senior Python Developer @ TechCorp
[Matching Agent] ├─ Similarity score: 0.94 (94%)
[Matching Agent] ├─ Decision: APPLY ✅
[Matching Agent] Job 2: Backend Engineer @ StartupXYZ
[Matching Agent] ├─ Similarity score: 0.89 (89%)
[Matching Agent] ├─ Decision: APPLY ✅
...
[Matching Agent] ✅ Found 12 high matches (≥75%)
```

### **Phase 4: Auto-Apply** (Agent 4)
```
[Apply Agent] Starting applications...
[Apply Agent] [1/12] Applying to: TechCorp - Senior Python Developer
[Apply Agent] ├─ Clicking "Easy Apply"
[Apply Agent] ├─ Filling personal info
[Apply Agent] ├─ Uploading resume
[Apply Agent] ├─ Submitting application
[Apply Agent] ├─ ✅ Success!
[Apply Agent] ├─ Waiting 8 seconds (human-like delay)
[Apply Agent] [2/12] Applying to: StartupXYZ - Backend Engineer
...
[Apply Agent] ✅ Completed: 8/12 successful
```

### **Phase 5: Report Generation** (Agent 5)
```
[Report Agent] Generating comprehensive report...
[Report Agent] ├─ Applications: 8 successful
[Report Agent] ├─ Match scores: 76%-94%
[Report Agent] ├─ Success rate: 87.5%
[Report Agent] ├─ Saving to database...
[Report Agent] ├─ Exporting JSON report...
[Report Agent] ✅ Report saved: reports/job_report_20260104_153422.json
```

---

## Post-Run Actions 🎯

### **1. Verify Applications**
- Check your LinkedIn "Jobs" → "Applications" page
- Look for confirmation emails from companies
- Note application timestamps

### **2. Track Responses**
- Monitor your email for recruiter responses
- Keep a spreadsheet of applications
- Follow up after 1 week

### **3. Analyze Match Quality**
```bash
# Check average match score
sqlite3 data/autoagenthire.db "SELECT AVG(match_score) FROM applications;"

# Find best matches
sqlite3 data/autoagenthire.db "SELECT company, job_title, match_score FROM applications ORDER BY match_score DESC LIMIT 5;"
```

### **4. Run Again**
You can run the system multiple times with different:
- Keywords ("Data Scientist", "DevOps Engineer")
- Locations ("New York", "Remote", "San Francisco")
- Match thresholds (70%, 80%, 90%)

---

## Advanced Usage 🎓

### **Running Multiple Searches**
```bash
# Search 1: Python Developer
python3 backend/agents/orchestrator_integration_example.py \
  --keywords "Python Developer" --location "Remote" --max-jobs 10

# Search 2: Data Engineer
python3 backend/agents/orchestrator_integration_example.py \
  --keywords "Data Engineer" --location "San Francisco" --max-jobs 10

# Search 3: DevOps Engineer
python3 backend/agents/orchestrator_integration_example.py \
  --keywords "DevOps Engineer" --location "United States" --max-jobs 10
```

### **Using Monitor Mode**
Real-time status updates:
```bash
python3 backend/agents/orchestrator_integration_example.py \
  --mode monitor \
  --keywords "Software Engineer" \
  --location "Remote" \
  --max-jobs 20
```

### **Test Mode (No Applications)**
Dry run to test matching:
```bash
python3 backend/agents/orchestrator_integration_example.py \
  --mode test \
  --keywords "Python Developer" \
  --location "Remote" \
  --max-jobs 30
```

---

## Safety Features 🛡️

The system includes multiple safety mechanisms:

1. **Rate Limiting**: Human-like delays (5-10s between actions)
2. **Error Recovery**: 3 retries with exponential backoff
3. **Browser Cleanup**: Always closes browser (success or failure)
4. **Data Persistence**: All actions logged to database
5. **Anti-Detection**: Playwright with stealth mode
6. **Match Threshold**: Only applies to highly relevant jobs (≥75%)
7. **Daily Limits**: Configurable max applications per day

---

## Next Steps After First Run 🎉

1. **Review Results**: Check applications in LinkedIn
2. **Optimize Keywords**: Adjust based on match quality
3. **Update Resume**: Add missing skills found in job descriptions
4. **Schedule Runs**: Set up cron job for daily searches
5. **Build Frontend**: Connect to API for web interface

---

## Questions? 🤔

Check these resources:
- **Complete Documentation**: `COMPLETE_DOCUMENTATION.md`
- **API Reference**: `README_PRODUCTION.md`
- **Architecture**: `ORCHESTRATOR_README.md`
- **Troubleshooting**: `backend/logs/orchestrator.log`

---

**Happy job hunting! 🚀**

*AutoAgentHire - Your Autonomous AI Career Assistant*
