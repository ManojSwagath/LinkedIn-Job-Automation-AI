#!/bin/bash

# Complete Project Launcher - Frontend + Backend
# Runs both Lovable frontend and FastAPI backend on localhost

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   AutoAgentHire - Full Stack Launch                          ║"
echo "║   Frontend (Lovable) + Backend (FastAPI)                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend/lovable"

# Python executable
if [ -f "$PROJECT_ROOT/venv/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/venv/bin/python"
else
    PYTHON="python3"
fi

# PID files
BACKEND_PID_FILE="$PROJECT_ROOT/backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/frontend.pid"

# Log files
BACKEND_LOG="$PROJECT_ROOT/backend.log"
FRONTEND_LOG="$PROJECT_ROOT/frontend.log"

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo "Stopping backend (PID: $BACKEND_PID)..."
            kill $BACKEND_PID 2>/dev/null || true
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo "Stopping frontend (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID 2>/dev/null || true
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    echo -e "${GREEN}✓ Services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Pre-flight checks
echo -e "${BLUE}📋 PRE-FLIGHT CHECKS${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python
echo -n "Checking Python... "
if ! command -v $PYTHON &> /dev/null; then
    echo -e "${RED}✗${NC} Python not found!"
    exit 1
fi
PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"

# Check Node.js
echo -n "Checking Node.js... "
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗${NC} Node.js not found!"
    echo "Please install Node.js: https://nodejs.org/"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION"

# Check npm
echo -n "Checking npm... "
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗${NC} npm not found!"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓${NC} npm $NPM_VERSION"

# Check .env
echo -n "Checking .env configuration... "
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${RED}✗${NC} .env file not found!"
    exit 1
fi
echo -e "${GREEN}✓${NC} Found"

# Check backend directory
echo -n "Checking backend directory... "
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}✗${NC} Backend directory not found!"
    exit 1
fi
echo -e "${GREEN}✓${NC} Found"

# Check frontend directory
echo -n "Checking frontend directory... "
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}✗${NC} Frontend directory not found!"
    exit 1
fi
echo -e "${GREEN}✓${NC} Found"

# Check database
echo -n "Checking database... "
if [ ! -f "$PROJECT_ROOT/data/autoagenthire.db" ]; then
    echo -e "${YELLOW}⚠${NC} Database not found, creating..."
    mkdir -p "$PROJECT_ROOT/data"
    cd "$PROJECT_ROOT"
    $PYTHON -c "import sys; sys.path.insert(0, '.'); from backend.database.connection import init_db; init_db()" 2>&1 | grep -v "INFO sqlalchemy" || true
    echo -e "${GREEN}✓${NC} Database created"
else
    echo -e "${GREEN}✓${NC} Exists"
fi

# Check OpenAI API key
echo -n "Checking OpenAI API key... "
if grep -q "OPENAI_API_KEY=sk-proj-" "$PROJECT_ROOT/.env" || grep -q "OPENAI_API_KEY=sk-" "$PROJECT_ROOT/.env"; then
    echo -e "${GREEN}✓${NC} Configured"
elif grep -q "OPENAI_API_KEY=YOUR_ACTUAL" "$PROJECT_ROOT/.env"; then
    echo -e "${YELLOW}⚠${NC} Using placeholder - won't work!"
    echo ""
    echo -e "${RED}WARNING: You need to add your real OpenAI API key!${NC}"
    echo "1. Get key from: https://platform.openai.com/api-keys"
    echo "2. Edit .env: OPENAI_API_KEY=sk-proj-YOUR_KEY"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${YELLOW}⚠${NC} Not configured properly"
fi

echo ""

# Install frontend dependencies if needed
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${BLUE}📦 Installing Frontend Dependencies${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    cd "$FRONTEND_DIR"
    npm install
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    echo ""
fi

# Start Backend
echo -e "${BLUE}🚀 STARTING BACKEND${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd "$BACKEND_DIR"

# Kill any existing backend process
if [ -f "$BACKEND_PID_FILE" ]; then
    OLD_PID=$(cat "$BACKEND_PID_FILE")
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Stopping old backend process (PID: $OLD_PID)..."
        kill $OLD_PID 2>/dev/null || true
        sleep 2
    fi
    rm -f "$BACKEND_PID_FILE"
fi

# Start backend server
echo "Starting FastAPI server on http://localhost:8000"
nohup $PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$BACKEND_PID_FILE"

# Wait for backend to start
echo -n "Waiting for backend to start"
for i in {1..30}; do
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Backend started successfully (PID: $BACKEND_PID)${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo ""
        echo -e "${RED}✗ Backend failed to start${NC}"
        echo "Check logs: $BACKEND_LOG"
        exit 1
    fi
done

echo ""
echo "Backend API: ${CYAN}http://localhost:8000${NC}"
echo "API Docs: ${CYAN}http://localhost:8000/docs${NC}"
echo "Logs: $BACKEND_LOG"
echo ""

# Start Frontend
echo -e "${BLUE}🎨 STARTING FRONTEND${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd "$FRONTEND_DIR"

# Kill any existing frontend process
if [ -f "$FRONTEND_PID_FILE" ]; then
    OLD_PID=$(cat "$FRONTEND_PID_FILE")
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Stopping old frontend process (PID: $OLD_PID)..."
        kill $OLD_PID 2>/dev/null || true
        sleep 2
    fi
    rm -f "$FRONTEND_PID_FILE"
fi

# Check if .env exists in frontend
if [ ! -f "$FRONTEND_DIR/.env" ]; then
    echo "Creating frontend .env file..."
    cat > "$FRONTEND_DIR/.env" << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
EOF
    echo -e "${GREEN}✓ Frontend .env created${NC}"
fi

# Start frontend server
echo "Starting Vite dev server on http://localhost:8080"
nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$FRONTEND_PID_FILE"

# Wait for frontend to start
echo -n "Waiting for frontend to start"
for i in {1..30}; do
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Frontend started successfully (PID: $FRONTEND_PID)${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo ""
        echo -e "${YELLOW}⚠ Frontend may still be starting...${NC}"
        echo "Check logs: $FRONTEND_LOG"
    fi
done

echo ""
echo "Frontend: ${CYAN}http://localhost:8080${NC}"
echo "Logs: $FRONTEND_LOG"
echo ""

# Success summary
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🎉 SYSTEM RUNNING! 🎉                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓ Backend API${NC}: http://localhost:8000"
echo -e "${GREEN}✓ API Documentation${NC}: http://localhost:8000/docs"
echo -e "${GREEN}✓ Frontend App${NC}: http://localhost:8080"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}📝 Available API Endpoints:${NC}"
echo "  • POST   /api/agent/run                    - Start job search workflow"
echo "  • GET    /api/agent/status/{run_id}        - Check workflow status"
echo "  • GET    /api/agent/results/{run_id}       - Get workflow results"
echo "  • POST   /api/agent/resume/upload          - Upload resume"
echo "  • GET    /api/agent/applications           - List applications"
echo "  • GET    /api/agent/runs                   - Workflow history"
echo "  • GET    /api/agent/stats                  - User statistics"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}🎯 How to Use:${NC}"
echo ""
echo "1. Open your browser: ${CYAN}http://localhost:8080${NC}"
echo "2. Upload your resume (PDF/DOCX)"
echo "3. Enter job search criteria:"
echo "   • Keywords: e.g., 'Python Developer', 'Data Scientist'"
echo "   • Location: e.g., 'Remote', 'San Francisco'"
echo "   • Max jobs: 5-15 for testing"
echo "4. Click 'Start Job Search'"
echo "5. Monitor progress in real-time"
echo "6. View results and applications"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}📊 Monitoring:${NC}"
echo "  • Backend logs: tail -f $BACKEND_LOG"
echo "  • Frontend logs: tail -f $FRONTEND_LOG"
echo "  • Database: sqlite3 $PROJECT_ROOT/data/autoagenthire.db"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}⚠️  To stop both services, press Ctrl+C${NC}"
echo ""

# Monitor logs (optional)
echo -e "${BLUE}Would you like to monitor the logs?${NC}"
echo "  1) Backend logs (API requests/responses)"
echo "  2) Frontend logs (build/dev server)"
echo "  3) Both (split screen)"
echo "  4) No, just keep services running"
echo ""
read -p "Choose [1-4]: " monitor_choice

case $monitor_choice in
    1)
        echo ""
        echo "Monitoring backend logs (Ctrl+C to exit)..."
        tail -f "$BACKEND_LOG"
        ;;
    2)
        echo ""
        echo "Monitoring frontend logs (Ctrl+C to exit)..."
        tail -f "$FRONTEND_LOG"
        ;;
    3)
        echo ""
        echo "Monitoring both logs (Ctrl+C to exit)..."
        tail -f "$BACKEND_LOG" "$FRONTEND_LOG"
        ;;
    4)
        echo ""
        echo "Services are running in the background."
        echo ""
        echo "To stop them later, run:"
        echo "  ./stop_all.sh"
        echo ""
        echo "Or manually:"
        echo "  kill \$(cat $BACKEND_PID_FILE)"
        echo "  kill \$(cat $FRONTEND_PID_FILE)"
        echo ""
        ;;
esac

# Keep script running
wait
