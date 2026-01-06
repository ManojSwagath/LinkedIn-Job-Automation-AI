#!/bin/bash

# FAST START - Run entire project in one command
# Usage: ./FAST_START.sh

clear
echo "🚀 AutoAgentHire - FAST START"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Python path
if [ -f "venv/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/venv/bin/python"
else
    PYTHON="python3"
fi

echo -e "${BLUE}1. Starting Backend (FastAPI)...${NC}"
cd "$PROJECT_ROOT/backend"
$PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo "   URL: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

# Wait for backend to be ready
sleep 3

echo -e "${BLUE}2. Starting Frontend (Lovable)...${NC}"
cd "$PROJECT_ROOT/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}   Installing dependencies (first time only)...${NC}"
    npm install > ../frontend_install.log 2>&1
fi

# Start frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "   URL: http://localhost:8080"
echo ""

# Wait for frontend to be ready
sleep 5

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ ALL SERVICES RUNNING!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📊 Access Points:"
echo "   Frontend: http://localhost:8080"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To Stop: ./stop_all.sh"
echo ""

# Auto-open browser (macOS)
if command -v open &> /dev/null; then
    sleep 2
    echo "🌐 Opening browser..."
    open http://localhost:8080
fi

echo ""
echo -e "${YELLOW}Press Ctrl+C to view this info again (servers keep running)${NC}"
echo ""

# Keep script running to show info
tail -f /dev/null
