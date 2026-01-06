#!/bin/bash

# AutoAgentHire - Complete Startup Script
# This script starts both backend and frontend servers

set -e  # Exit on error

echo "🚀 AutoAgentHire - Starting Complete System"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: Clean up any existing processes
echo -e "\n${YELLOW}📋 Step 1: Cleaning up existing processes...${NC}"
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ Processes cleaned${NC}"

# Step 2: Verify directories
echo -e "\n${YELLOW}📋 Step 2: Verifying data directories...${NC}"
mkdir -p data/resumes data/job_listings data/templates browser_profile
test -f data/applications.json || echo "[]" > data/applications.json
echo -e "${GREEN}✅ Directories ready${NC}"

# Step 3: Check Python dependencies
echo -e "\n${YELLOW}📋 Step 3: Checking Python dependencies...${NC}"
if ! python3 -c "import fastapi, playwright, google.generativeai" 2>/dev/null; then
    echo -e "${RED}⚠️  Missing Python dependencies. Installing...${NC}"
    pip3 install -q -r requirements.txt
fi
echo -e "${GREEN}✅ Python dependencies OK${NC}"

# Step 4: Install Playwright browsers if needed
echo -e "\n${YELLOW}📋 Step 4: Checking Playwright browsers...${NC}"
if [ ! -d "$HOME/Library/Caches/ms-playwright" ]; then
    echo -e "${YELLOW}Installing Playwright browsers (first time only)...${NC}"
    python3 -m playwright install chromium
fi
echo -e "${GREEN}✅ Playwright browsers ready${NC}"

# Step 5: Check frontend dependencies
echo -e "\n${YELLOW}📋 Step 5: Checking frontend dependencies...${NC}"
if [ ! -d "frontend/lovable/node_modules" ]; then
    echo -e "${YELLOW}Installing npm packages...${NC}"
    cd frontend/lovable
    npm install
    cd ../..
fi
echo -e "${GREEN}✅ Frontend dependencies OK${NC}"

# Step 6: Start Backend
echo -e "\n${YELLOW}📋 Step 6: Starting Backend Server (Port 8000)...${NC}"
echo "Backend will run in background. Check logs: backend.log"
nohup python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "\n${YELLOW}⏳ Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start. Check backend.log${NC}"
        cat backend.log
        exit 1
    fi
    sleep 1
done

# Step 7: Start Frontend
echo -e "\n${YELLOW}📋 Step 7: Starting Frontend Server (Port 8080)...${NC}"
echo "Frontend will run in background. Check logs: frontend.log"
cd frontend/lovable
nohup npm run dev -- --host 127.0.0.1 --port 8080 > ../../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..
echo $FRONTEND_PID > frontend.pid
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to be ready
echo -e "\n${YELLOW}⏳ Waiting for frontend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://127.0.0.1:8080 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is ready!${NC}"
        break
    fi
    sleep 1
done

# Final Summary
echo -e "\n${GREEN}=========================================="
echo "✅ AutoAgentHire is Running!"
echo "==========================================${NC}"
echo ""
echo -e "${GREEN}🌐 Backend API:${NC}    http://127.0.0.1:8000"
echo -e "${GREEN}🌐 Frontend UI:${NC}    http://127.0.0.1:8080"
echo -e "${GREEN}📊 API Docs:${NC}       http://127.0.0.1:8000/docs"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo -e "${YELLOW}🛑 To stop servers:${NC}"
echo "   kill \$(cat backend.pid frontend.pid)"
echo ""
echo -e "${GREEN}🎯 Next Steps:${NC}"
echo "   1. Open http://127.0.0.1:8080 in your browser"
echo "   2. Go to Settings and upload your resume"
echo "   3. Enter your LinkedIn credentials"
echo "   4. Configure job search preferences"
echo "   5. Click 'Start Automation' to begin"
echo ""
echo -e "${GREEN}=========================================="
echo "Press Ctrl+C to view logs, or just open the browser!"
echo "==========================================${NC}"

# Optional: Open browser automatically (macOS)
if command -v open &> /dev/null; then
    echo -e "\n${YELLOW}🌐 Opening browser in 3 seconds...${NC}"
    sleep 3
    open http://127.0.0.1:8080
fi

# Keep script running to show status
echo -e "\n${YELLOW}📊 Server Status (updating every 10s, Ctrl+C to exit):${NC}"
while true; do
    sleep 10
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend crashed! Check backend.log${NC}"
        exit 1
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend crashed! Check frontend.log${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Both servers running ($(date '+%H:%M:%S'))${NC}"
done
