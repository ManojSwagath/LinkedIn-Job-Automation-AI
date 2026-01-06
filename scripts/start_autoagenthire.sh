#!/bin/bash

# 🚀 AutoAgentHire - Quick Start Script
# One command to rule them all!

echo "🚀 Starting AutoAgentHire..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to project directory
cd "$(dirname "$0")"

# Check if backend is already running
if lsof -ti:8000 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Backend already running on port 8000${NC}"
else
    echo -e "${BLUE}🔧 Starting Backend (FastAPI)...${NC}"
    nohup uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    sleep 3
    
    # Check if backend started successfully
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend running on http://localhost:8000${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend may still be starting... Check backend.log${NC}"
    fi
fi

echo ""

# Check if frontend is already running
if lsof -ti:8080 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Frontend already running on port 8080${NC}"
else
    echo -e "${BLUE}🎨 Starting Frontend (AutoAgentHire Dashboard)...${NC}"
    nohup python3 serve_frontend.py > frontend.log 2>&1 &
    sleep 3
    
    if lsof -ti:8080 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend running on http://localhost:8080${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend may still be starting... Check frontend.log${NC}"
    fi
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 AutoAgentHire is ready!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📍 Access Points:${NC}"
echo -e "   🔹 Dashboard:  ${GREEN}http://localhost:8080${NC}"
echo -e "   🔹 Backend API: ${GREEN}http://localhost:8000${NC}"
echo -e "   🔹 API Docs:    ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Enter YOUR LinkedIn credentials!${NC}"
echo -e "   1. Open: ${GREEN}http://localhost:8080${NC}"
echo -e "   2. Click: ${BLUE}🔐 LinkedIn${NC} tab (first tab)"
echo -e "   3. Enter: Your email and password"
echo -e "   4. Upload: Your resume (PDF)"
echo -e "   5. Configure: Job search preferences"
echo -e "   6. Click: ${GREEN}🚀 Run AutoAgent${NC}"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "   Backend:  ${YELLOW}tail -f backend.log${NC}"
echo -e "   Frontend: ${YELLOW}tail -f frontend.log${NC}"
echo ""
echo -e "${BLUE}🛑 Stop Services:${NC}"
echo -e "   ${YELLOW}./stop_autoagenthire.sh${NC}"
echo ""
echo -e "${GREEN}Ready to automate! Open http://localhost:8080${NC}"
echo ""
