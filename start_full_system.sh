#!/bin/bash

# LinkedIn Job Automation - Full System Startup Script
# This script starts backend, frontend, and optionally runs automation

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🚀 LinkedIn Job Automation - Full System Startup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo -e "${YELLOW}   Please create .env file with required configuration${NC}"
    exit 1
fi

# Check Python virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    playwright install chromium
else
    source venv/bin/activate
fi

# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Kill existing processes on ports
echo -e "${YELLOW}🔍 Checking for existing processes...${NC}"
if check_port 8000; then
    echo -e "${YELLOW}   Killing process on port 8000...${NC}"
    kill -9 $(lsof -t -i:8000) 2>/dev/null || true
fi

if check_port 8080; then
    echo -e "${YELLOW}   Killing process on port 8080...${NC}"
    kill -9 $(lsof -t -i:8080) 2>/dev/null || true
fi

# Create logs directory
mkdir -p logs

# Start Backend
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  1. Starting Backend Server (Port 8000)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
PYTHONPATH=$PROJECT_ROOT python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "${BLUE}  → http://localhost:8000${NC}"
echo -e "${BLUE}  → Docs: http://localhost:8000/docs${NC}"

# Wait for backend to start
sleep 3

# Check if backend is running
if ! check_port 8000; then
    echo -e "${RED}❌ Backend failed to start. Check logs/backend.log${NC}"
    exit 1
fi

# Start Frontend (if exists)
if [ -d "frontend/lovable" ] && [ -f "frontend/lovable/package.json" ]; then
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  2. Starting Frontend (Port 8080)${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    cd frontend/lovable
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}   Installing npm dependencies...${NC}"
        npm install
    fi
    
    # Start frontend
    npm run dev > ../../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd "$PROJECT_ROOT"
    
    echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
    echo -e "${BLUE}  → http://localhost:8080${NC}"
    
    sleep 3
else
    echo -e "${YELLOW}⚠️  Frontend not found, skipping...${NC}"
    FRONTEND_PID=""
fi

# Display status
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  ✅ System Running!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Services:${NC}"
echo -e "  Backend:  ${BLUE}http://localhost:8000${NC}"
if [ -n "$FRONTEND_PID" ]; then
    echo -e "  Frontend: ${BLUE}http://localhost:8080${NC}"
fi
echo ""
echo -e "${GREEN}Logs:${NC}"
echo -e "  Backend:  ${BLUE}tail -f logs/backend.log${NC}"
if [ -n "$FRONTEND_PID" ]; then
    echo -e "  Frontend: ${BLUE}tail -f logs/frontend.log${NC}"
fi
echo ""

# Ask user what to do
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}What would you like to do?${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  1) Run automation now (test mode)"
echo "  2) Run automation and submit (live mode)"
echo "  3) Keep servers running (access via browser)"
echo "  4) Stop all services"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}🤖 Starting automation in TEST mode...${NC}"
        export TEST_MODE=true
        python3 run_full_automation.py
        ;;
    2)
        echo ""
        echo -e "${RED}⚠️  Starting automation in LIVE mode (will submit applications)${NC}"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            export TEST_MODE=false
            python3 run_full_automation.py
        else
            echo -e "${YELLOW}Cancelled.${NC}"
        fi
        ;;
    3)
        echo ""
        echo -e "${GREEN}✓ Servers running in background${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
        
        # Save PIDs
        echo "$BACKEND_PID" > logs/backend.pid
        if [ -n "$FRONTEND_PID" ]; then
            echo "$FRONTEND_PID" > logs/frontend.pid
        fi
        
        # Wait for Ctrl+C
        trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID 2>/dev/null; [ -n '$FRONTEND_PID' ] && kill $FRONTEND_PID 2>/dev/null; echo 'Stopped.'; exit" INT
        wait
        ;;
    4)
        echo ""
        echo -e "${YELLOW}Stopping all services...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        if [ -n "$FRONTEND_PID" ]; then
            kill $FRONTEND_PID 2>/dev/null || true
        fi
        echo -e "${GREEN}✓ All services stopped${NC}"
        ;;
    *)
        echo ""
        echo -e "${YELLOW}Invalid choice. Keeping servers running...${NC}"
        echo -e "${YELLOW}Use 'kill $BACKEND_PID' to stop backend${NC}"
        if [ -n "$FRONTEND_PID" ]; then
            echo -e "${YELLOW}Use 'kill $FRONTEND_PID' to stop frontend${NC}"
        fi
        ;;
esac

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Done!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
