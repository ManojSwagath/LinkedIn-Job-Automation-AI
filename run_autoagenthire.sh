#!/bin/bash
# Complete AutoAgentHire Runner
# ============================
# Runs the complete multi-agent system with all phases

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "          🤖 AUTOAGENTHIRE - COMPLETE SYSTEM RUNNER 🤖          "
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================
# PRE-FLIGHT CHECKS
# ============================

echo "📋 Pre-flight Checks..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 3 installed"

# Check .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating .env from template..."
    cat > .env << 'EOF'
# OpenAI API Key (for resume parsing and embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# LinkedIn Credentials
LINKEDIN_EMAIL=your_linkedin_email@example.com
LINKEDIN_PASSWORD=your_linkedin_password_here

# Optional: Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# User Profile (for auto-filling applications)
FIRST_NAME=John
LAST_NAME=Doe
PHONE_NUMBER=555-123-4567
CITY=San Francisco
STATE=CA
COUNTRY=USA
LINKEDIN_URL=https://linkedin.com/in/yourprofile
PORTFOLIO_URL=https://yourportfolio.com
EOF
    echo -e "${YELLOW}⚠️  Please edit .env with your credentials${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} .env file found"

# Check required environment variables
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" == "your_openai_api_key_here" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY not set in .env${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} OpenAI API key configured"

if [ -z "$LINKEDIN_EMAIL" ] || [ "$LINKEDIN_EMAIL" == "your_linkedin_email@example.com" ]; then
    echo -e "${RED}❌ LINKEDIN_EMAIL not set in .env${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} LinkedIn credentials configured"

# Check dependencies
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
    playwright install chromium
else
    source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
fi
echo -e "${GREEN}✓${NC} Dependencies ready"

echo ""

# ============================
# MODE SELECTION
# ============================

echo "Select run mode:"
echo "  1) API Server (for frontend integration)"
echo "  2) Direct Workflow (standalone execution)"
echo "  3) Component Test (test individual parts)"
echo "  4) Full E2E Test (complete workflow test)"
echo ""
read -p "Enter choice [1-4]: " MODE

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

case $MODE in
    1)
        echo "🌐 Starting API Server..."
        echo ""
        echo "API will be available at:"
        echo "  - Main API: http://localhost:8000"
        echo "  - Docs: http://localhost:8000/docs"
        echo "  - Agent API: http://localhost:8000/api/agent/*"
        echo ""
        echo "Available endpoints:"
        echo "  POST /api/agent/run - Start autonomous workflow"
        echo "  GET /api/agent/status/{run_id} - Check workflow status"
        echo "  POST /api/agent/resume/upload - Upload resume"
        echo "  GET /api/agent/applications - Get applications"
        echo ""
        echo "Press Ctrl+C to stop"
        echo ""
        
        cd backend
        python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        ;;
        
    2)
        echo "🚀 Running Direct Workflow..."
        echo ""
        
        # Get parameters
        read -p "Resume file path [data/resumes/sample_resume.pdf]: " RESUME
        RESUME=${RESUME:-data/resumes/sample_resume.pdf}
        
        read -p "Job keywords [Machine Learning Engineer]: " KEYWORDS
        KEYWORDS=${KEYWORDS:-Machine Learning Engineer}
        
        read -p "Location [San Francisco, CA]: " LOCATION
        LOCATION=${LOCATION:-San Francisco, CA}
        
        read -p "Max jobs to process [30]: " MAX_JOBS
        MAX_JOBS=${MAX_JOBS:-30}
        
        echo ""
        echo "Starting workflow with:"
        echo "  Resume: $RESUME"
        echo "  Keywords: $KEYWORDS"
        echo "  Location: $LOCATION"
        echo "  Max Jobs: $MAX_JOBS"
        echo ""
        echo "────────────────────────────────────────────────────────────────"
        echo ""
        
        python3 backend/agents/orchestrator_integration_example.py --mode basic
        ;;
        
    3)
        echo "🧪 Running Component Tests..."
        echo ""
        python3 test_e2e_complete.py --mode components
        ;;
        
    4)
        echo "🔬 Running Full E2E Test..."
        echo ""
        echo "This will:"
        echo "  1. Initialize database"
        echo "  2. Parse test resume"
        echo "  3. Search LinkedIn for jobs"
        echo "  4. Match jobs using AI"
        echo "  5. Auto-apply to qualified positions"
        echo "  6. Generate report"
        echo ""
        read -p "Continue? [y/N]: " CONFIRM
        
        if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
            echo "Cancelled."
            exit 0
        fi
        
        echo ""
        echo "────────────────────────────────────────────────────────────────"
        echo ""
        
        python3 test_e2e_complete.py --mode full
        ;;
        
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "                    ✅ Run Complete                              "
echo "════════════════════════════════════════════════════════════════"
