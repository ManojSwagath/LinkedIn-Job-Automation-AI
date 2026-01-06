#!/bin/bash

# AutoAgentHire - Quick Start Script
# This script will guide you through running the complete project

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   AutoAgentHire - Autonomous AI Job Application System   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Python executable
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
else
    PYTHON="python"
fi

echo -e "${BLUE}📋 PRE-FLIGHT CHECKS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python version
echo -n "Checking Python version... "
PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"

# Check if .env exists
echo -n "Checking .env configuration... "
if [ ! -f ".env" ]; then
    echo -e "${RED}✗${NC} .env file not found!"
    echo ""
    echo "Please create a .env file with your credentials."
    echo "See RUN_PROJECT_GUIDE.md for details."
    exit 1
fi
echo -e "${GREEN}✓${NC} Found"

# Check OpenAI API key
echo -n "Checking OpenAI API key... "
if grep -q "OPENAI_API_KEY=sk-" .env; then
    echo -e "${GREEN}✓${NC} Configured"
elif grep -q "OPENAI_API_KEY=your-openai-api-key" .env; then
    echo -e "${YELLOW}⚠${NC} Not configured (using placeholder)"
    echo ""
    echo -e "${YELLOW}WARNING:${NC} You need to add your real OpenAI API key to .env"
    echo "Get one from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Invalid format"
    exit 1
fi

# Check LinkedIn credentials
echo -n "Checking LinkedIn credentials... "
if grep -q "LINKEDIN_EMAIL=.*@.*" .env && ! grep -q "your-email@example.com" .env; then
    echo -e "${GREEN}✓${NC} Configured"
else
    echo -e "${YELLOW}⚠${NC} Not configured"
fi

# Check database
echo -n "Checking database... "
if [ -f "data/autoagenthire.db" ]; then
    echo -e "${GREEN}✓${NC} Exists"
else
    echo -e "${YELLOW}⚠${NC} Not found, will create"
    mkdir -p data
    $PYTHON -c "import sys; sys.path.insert(0, '.'); from backend.database.connection import init_db; init_db()" 2>&1 | grep -v "INFO sqlalchemy"
    echo -e "${GREEN}✓${NC} Database created"
fi

# Check for resume
echo -n "Checking for resume files... "
RESUME_COUNT=$(find data/resumes -name "*.pdf" -o -name "*.docx" 2>/dev/null | wc -l | tr -d ' ')
if [ "$RESUME_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Found $RESUME_COUNT resume(s)"
else
    echo -e "${YELLOW}⚠${NC} No resumes found in data/resumes/"
    echo ""
    echo "Copy your resume to data/resumes/ directory:"
    echo "  mkdir -p data/resumes"
    echo "  cp ~/Downloads/your_resume.pdf data/resumes/"
    echo ""
fi

echo ""
echo -e "${BLUE}🚀 SELECT RUN MODE${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1) 🧪 Quick System Test (2 minutes)"
echo "     Test components without LinkedIn login"
echo ""
echo "  2) 🎯 Run Direct Workflow (15-20 minutes)"
echo "     Complete autonomous job application workflow"
echo ""
echo "  3) 🖥️  Start API Server"
echo "     Run FastAPI backend for frontend integration"
echo ""
echo "  4) 📊 View Database Contents"
echo "     Browse saved applications and jobs"
echo ""
echo "  5) 📖 View Documentation"
echo "     Open complete project documentation"
echo ""
echo "  6) 🔧 Advanced Options"
echo "     Custom parameters and test modes"
echo ""
echo "  0) Exit"
echo ""

read -p "Enter your choice [0-6]: " choice
echo ""

case $choice in
    1)
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  Running Quick System Test${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        
        if [ ! -f "test_quick.py" ]; then
            echo -e "${RED}Error: test_quick.py not found${NC}"
            exit 1
        fi
        
        $PYTHON test_quick.py
        
        echo ""
        echo -e "${GREEN}✓${NC} Quick test complete!"
        echo ""
        echo "Next steps:"
        echo "  - If tests passed: Run option 2 (Direct Workflow)"
        echo "  - If tests failed: Check your API key in .env"
        ;;
        
    2)
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  Direct Workflow - Autonomous Job Application${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        
        # Get resume path
        echo "Available resumes:"
        RESUME_FILES=($(find data/resumes -name "*.pdf" -o -name "*.docx" 2>/dev/null))
        
        if [ ${#RESUME_FILES[@]} -eq 0 ]; then
            echo -e "${RED}No resume files found in data/resumes/${NC}"
            echo ""
            echo "Please add your resume:"
            echo "  mkdir -p data/resumes"
            echo "  cp ~/Downloads/your_resume.pdf data/resumes/"
            exit 1
        fi
        
        for i in "${!RESUME_FILES[@]}"; do
            echo "  $((i+1))) ${RESUME_FILES[$i]}"
        done
        echo ""
        read -p "Select resume [1-${#RESUME_FILES[@]}]: " resume_idx
        RESUME_PATH="${RESUME_FILES[$((resume_idx-1))]}"
        
        # Get job search parameters
        echo ""
        read -p "Job keywords (e.g., 'Python Developer'): " KEYWORDS
        read -p "Job location (e.g., 'Remote', 'San Francisco'): " LOCATION
        read -p "Max jobs to process (recommended: 5-15): " MAX_JOBS
        
        echo ""
        echo -e "${YELLOW}Starting workflow...${NC}"
        echo ""
        echo "Parameters:"
        echo "  Resume: $RESUME_PATH"
        echo "  Keywords: $KEYWORDS"
        echo "  Location: $LOCATION"
        echo "  Max Jobs: $MAX_JOBS"
        echo ""
        
        # Run the orchestrator
        $PYTHON backend/agents/orchestrator_integration_example.py \
            --resume-path "$RESUME_PATH" \
            --keywords "$KEYWORDS" \
            --location "$LOCATION" \
            --max-jobs "$MAX_JOBS" \
            --mode monitor
        
        echo ""
        echo -e "${GREEN}✓${NC} Workflow complete!"
        echo ""
        echo "Check results:"
        echo "  - Console report above"
        echo "  - Database: data/autoagenthire.db"
        echo "  - Reports: reports/ directory"
        ;;
        
    3)
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  Starting API Server${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        
        echo "API Server will start on http://localhost:8000"
        echo ""
        echo "Available endpoints:"
        echo "  POST   /api/agent/run"
        echo "  GET    /api/agent/status/{run_id}"
        echo "  GET    /api/agent/results/{run_id}"
        echo "  POST   /api/agent/resume/upload"
        echo "  GET    /api/agent/applications"
        echo "  GET    /api/agent/runs"
        echo "  GET    /api/agent/stats"
        echo ""
        echo "API Documentation: http://localhost:8000/docs"
        echo ""
        echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
        echo ""
        
        cd backend
        $PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        ;;
        
    4)
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  Database Contents${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        
        if [ ! -f "data/autoagenthire.db" ]; then
            echo -e "${RED}Database not found!${NC}"
            echo "Run option 1 or 2 first to initialize the database."
            exit 1
        fi
        
        echo "📊 Applications Summary:"
        echo ""
        sqlite3 data/autoagenthire.db "SELECT job_title, company, match_score, status, applied_at FROM applications ORDER BY match_score DESC LIMIT 10;" -header -column 2>/dev/null || echo "No applications yet"
        
        echo ""
        echo "📈 Statistics:"
        echo ""
        TOTAL_APPS=$(sqlite3 data/autoagenthire.db "SELECT COUNT(*) FROM applications;" 2>/dev/null)
        SUCCESS_APPS=$(sqlite3 data/autoagenthire.db "SELECT COUNT(*) FROM applications WHERE status='applied';" 2>/dev/null)
        AVG_SCORE=$(sqlite3 data/autoagenthire.db "SELECT AVG(match_score) FROM applications;" 2>/dev/null)
        
        echo "  Total Applications: $TOTAL_APPS"
        echo "  Successful: $SUCCESS_APPS"
        echo "  Average Match Score: ${AVG_SCORE}%"
        
        echo ""
        echo "To explore more, use:"
        echo "  sqlite3 data/autoagenthire.db"
        ;;
        
    5)
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  Documentation${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        
        echo "📖 Available Documentation:"
        echo ""
        echo "  1. RUN_PROJECT_GUIDE.md - Complete setup guide (YOU ARE HERE)"
        echo "  2. COMPLETE_DOCUMENTATION.md - Full system documentation"
        echo "  3. README_PRODUCTION.md - Production deployment guide"
        echo "  4. ORCHESTRATOR_README.md - Multi-agent architecture"
        echo "  5. ALL_PHASES_COMPLETE.md - Project completion summary"
        echo ""
        
        read -p "Open which document? [1-5]: " doc_choice
        
        case $doc_choice in
            1) open "RUN_PROJECT_GUIDE.md" 2>/dev/null || cat "RUN_PROJECT_GUIDE.md" | less ;;
            2) open "COMPLETE_DOCUMENTATION.md" 2>/dev/null || cat "COMPLETE_DOCUMENTATION.md" | less ;;
            3) open "README_PRODUCTION.md" 2>/dev/null || cat "README_PRODUCTION.md" | less ;;
            4) open "backend/agents/ORCHESTRATOR_README.md" 2>/dev/null || cat "backend/agents/ORCHESTRATOR_README.md" | less ;;
            5) open "ALL_PHASES_COMPLETE.md" 2>/dev/null || cat "ALL_PHASES_COMPLETE.md" | less ;;
            *) echo "Invalid choice" ;;
        esac
        ;;
        
    6)
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  Advanced Options${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        
        echo "  1) Run E2E Test (Full workflow test)"
        echo "  2) Run Test Mode (No actual applications)"
        echo "  3) Custom Python Command"
        echo "  4) Install Additional Dependencies"
        echo "  5) Reset Database"
        echo ""
        
        read -p "Enter choice [1-5]: " adv_choice
        
        case $adv_choice in
            1)
                echo "Running end-to-end test..."
                $PYTHON test_e2e_complete.py --mode full
                ;;
            2)
                echo "Running in test mode (no applications)..."
                read -p "Resume path: " RESUME_PATH
                read -p "Keywords: " KEYWORDS
                read -p "Location: " LOCATION
                read -p "Max jobs: " MAX_JOBS
                
                $PYTHON backend/agents/orchestrator_integration_example.py \
                    --resume-path "$RESUME_PATH" \
                    --keywords "$KEYWORDS" \
                    --location "$LOCATION" \
                    --max-jobs "$MAX_JOBS" \
                    --mode test
                ;;
            3)
                echo "Enter Python command to run:"
                read -p "Command: " CUSTOM_CMD
                $PYTHON -c "$CUSTOM_CMD"
                ;;
            4)
                echo "Installing additional dependencies..."
                pip install -r requirements.txt
                playwright install chromium
                echo -e "${GREEN}✓${NC} Dependencies installed"
                ;;
            5)
                echo -e "${YELLOW}⚠  This will delete all data!${NC}"
                read -p "Are you sure? (type 'yes' to confirm): " confirm
                if [ "$confirm" = "yes" ]; then
                    rm -f data/autoagenthire.db
                    $PYTHON -c "import sys; sys.path.insert(0, '.'); from backend.database.connection import init_db; init_db()"
                    echo -e "${GREEN}✓${NC} Database reset complete"
                else
                    echo "Cancelled"
                fi
                ;;
            *)
                echo "Invalid choice"
                ;;
        esac
        ;;
        
    0)
        echo "Goodbye!"
        exit 0
        ;;
        
    *)
        echo -e "${RED}Invalid choice. Please select 0-6.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Thank you for using AutoAgentHire!                      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "For support, check:"
echo "  - RUN_PROJECT_GUIDE.md"
echo "  - backend/logs/orchestrator.log"
echo "  - GitHub Issues: github.com/Sathwik11-hub/LinkedIn-Job-Automation-with-AI"
echo ""
