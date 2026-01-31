#!/bin/bash
#
# Complete LinkedIn Job Automation System Startup
# This script starts both the backend server and runs the automation
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/Users/sathwikadigoppula/Documents/GitHub/LinkedIn-Job-Automation-with-AI"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}         ${GREEN}LinkedIn Job Automation with AI - Complete System${NC}              ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

cd "$PROJECT_DIR"

# Step 1: Check Python environment
echo -e "${YELLOW}[1/5]${NC} Checking Python environment..."
if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "   Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
else
    echo -e "${GREEN}✅ Virtual environment found${NC}"
fi

# Step 2: Check dependencies
echo -e "\n${YELLOW}[2/5]${NC} Checking dependencies..."
if ! "$VENV_PYTHON" -c "import playwright" 2>/dev/null; then
    echo "   Installing playwright..."
    "$PROJECT_DIR/venv/bin/pip" install playwright
    "$PROJECT_DIR/venv/bin/playwright" install chromium
fi

if ! "$VENV_PYTHON" -c "import google.generativeai" 2>/dev/null; then
    echo "   Installing google-generativeai..."
    "$PROJECT_DIR/venv/bin/pip" install google-generativeai
fi

if ! "$VENV_PYTHON" -c "import fastapi" 2>/dev/null; then
    echo "   Installing fastapi..."
    "$PROJECT_DIR/venv/bin/pip" install fastapi uvicorn
fi

echo -e "${GREEN}✅ All dependencies installed${NC}"

# Step 3: Check configuration
echo -e "\n${YELLOW}[3/5]${NC} Checking configuration..."
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# Check if LinkedIn credentials are set
if ! grep -q "LINKEDIN_EMAIL=.*@" .env || ! grep -q "LINKEDIN_PASSWORD=..*" .env; then
    echo -e "${RED}❌ LinkedIn credentials not configured in .env${NC}"
    echo "   Please add:"
    echo "   LINKEDIN_EMAIL=your_email@example.com"
    echo "   LINKEDIN_PASSWORD=your_password"
    exit 1
fi

echo -e "${GREEN}✅ Configuration loaded${NC}"

# Step 4: Check database
echo -e "\n${YELLOW}[4/5]${NC} Checking database..."
if [ ! -d "data" ]; then
    mkdir -p data
    echo "   Created data directory"
fi

echo -e "${GREEN}✅ Database ready${NC}"

# Step 5: Show menu
echo -e "\n${YELLOW}[5/5]${NC} Ready to start!"
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}What would you like to do?${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  1) Start Backend Server (FastAPI on port 8000)"
echo "  2) Run LinkedIn Automation (Working Version)"
echo "  3) Run Full Automation with visible browser"
echo "  4) Test Database Connection"
echo "  5) Check System Status"
echo "  6) Exit"
echo ""
read -p "Enter your choice [1-6]: " choice

case $choice in
    1)
        echo -e "\n${GREEN}Starting Backend Server...${NC}"
        echo "   URL: http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
        echo ""
        cd "$PROJECT_DIR"
        PYTHONPATH=$PWD "$VENV_PYTHON" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    2)
        echo -e "\n${GREEN}Running LinkedIn Automation (Working Version)...${NC}"
        echo ""
        cd "$PROJECT_DIR"
        PYTHONPATH=$PWD "$VENV_PYTHON" working_automation.py
        ;;
    3)
        echo -e "\n${GREEN}Running Full Automation with Visible Browser...${NC}"
        echo ""
        cd "$PROJECT_DIR"
        PYTHONPATH=$PWD PLAYWRIGHT_HEADLESS=false "$VENV_PYTHON" run_full_automation.py
        ;;
    4)
        echo -e "\n${GREEN}Testing Database Connection...${NC}"
        echo ""
        cd "$PROJECT_DIR"
        "$VENV_PYTHON" test_all_connections.py
        ;;
    5)
        echo -e "\n${GREEN}System Status:${NC}"
        echo ""
        echo -e "${BLUE}Environment:${NC}"
        echo "  Python: $("$VENV_PYTHON" --version)"
        echo "  Project: $PROJECT_DIR"
        echo ""
        echo -e "${BLUE}Configuration:${NC}"
        grep "LINKEDIN_EMAIL=" .env | sed 's/LINKEDIN_EMAIL=/  Email: /'
        grep "JOB_KEYWORDS=" .env | sed 's/JOB_KEYWORDS=/  Keywords: /'
        grep "JOB_LOCATION=" .env | sed 's/JOB_LOCATION=/  Location: /'
        grep "MAX_APPLICATIONS=" .env | sed 's/MAX_APPLICATIONS=/  Max Apps: /'
        echo ""
        echo -e "${BLUE}Database:${NC}"
        if [ -f "data/autoagenthire.db" ]; then
            echo -e "  ${GREEN}✅ SQLite database exists${NC}"
        else
            echo -e "  ${YELLOW}⚠️  Database will be created on first run${NC}"
        fi
        echo ""
        ;;
    6)
        echo -e "\n${GREEN}Goodbye!${NC}\n"
        exit 0
        ;;
    *)
        echo -e "\n${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
