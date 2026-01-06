#!/bin/bash

# =====================================================
# AutoAgentHire Complete Startup Script
# Starts both Backend (FastAPI) and Frontend (React)
# =====================================================

echo "🚀 Starting AutoAgentHire..."
echo ""

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env with your API keys and LinkedIn credentials${NC}"
    else
        echo -e "${RED}❌ .env.example not found${NC}"
    fi
else
    echo -e "${GREEN}✅ .env file found${NC}"
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/lovable/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not installed. Installing...${NC}"
    cd frontend/lovable
    npm install
    cd "$SCRIPT_DIR"
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Frontend dependencies found${NC}"
fi

# Create necessary directories
mkdir -p data/resumes
mkdir -p data/job_listings
mkdir -p uploads/resumes
mkdir -p uploads/cover_letters
echo -e "${GREEN}✅ Data directories created${NC}"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Starting Services${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Kill any existing processes
echo "🔍 Checking for existing processes..."
pkill -f "uvicorn backend.main:app" 2>/dev/null && echo "  ✓ Stopped existing backend"
pkill -f "vite" 2>/dev/null && echo "  ✓ Stopped existing frontend"
sleep 2

# Start Backend
echo ""
echo -e "${BLUE}🔧 Starting Backend (FastAPI)...${NC}"
cd "$SCRIPT_DIR"
source venv/bin/activate
nohup uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "   📊 API: http://localhost:8000"
echo -e "   📖 Docs: http://localhost:8000/docs"

# Wait for backend to start
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start. Check backend.log${NC}"
        exit 1
    fi
done

# Start Frontend
echo ""
echo -e "${BLUE}🎨 Starting Frontend (React)...${NC}"
cd "$SCRIPT_DIR/frontend/lovable"
nohup npm run dev > ../../frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "   🌐 App: http://localhost:5173"

# Wait for frontend to start
echo "⏳ Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:5173/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠️  Frontend may still be starting. Check frontend.log${NC}"
    fi
done

cd "$SCRIPT_DIR"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎉 AutoAgentHire is Running!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "📱 ${BLUE}Frontend:${NC} http://localhost:5173"
echo -e "🔧 ${BLUE}Backend API:${NC} http://localhost:8000"
echo -e "📖 ${BLUE}API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "📝 Logs:"
echo -e "   Backend: ${SCRIPT_DIR}/backend.log"
echo -e "   Frontend: ${SCRIPT_DIR}/frontend.log"
echo ""
echo -e "${YELLOW}To stop all services:${NC}"
echo -e "   pkill -f 'uvicorn backend.main:app'"
echo -e "   pkill -f 'vite'"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop watching logs...${NC}"
echo ""

# Open browser (optional)
if command -v open &> /dev/null; then
    echo "🌐 Opening browser..."
    sleep 2
    open http://localhost:5173
elif command -v xdg-open &> /dev/null; then
    echo "🌐 Opening browser..."
    sleep 2
    xdg-open http://localhost:5173
fi

# Tail logs
tail -f backend.log frontend.log
