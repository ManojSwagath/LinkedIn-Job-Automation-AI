#!/bin/bash
# Quick startup script for LinkedIn Job Automation

echo "🚀 Starting LinkedIn Job Automation System..."
echo ""

# Kill existing processes
echo "🧹 Cleaning up old processes..."
lsof -ti:8000,8080 | xargs kill -9 2>/dev/null || true
sleep 2

# Start backend
echo "🔧 Starting Backend (FastAPI)..."
cd "$(dirname "$0")"
source venv/bin/activate
nohup uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > backend.pid
disown $BACKEND_PID 2>/dev/null || true
echo "   Backend PID: $BACKEND_PID"

# Ensure Playwright browsers exist (common cause of 'browser not working')
echo "🌐 Checking Playwright Chromium..."
python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop()" >/dev/null 2>&1 || {
    echo "⚠️  Playwright Chromium not ready. Installing..."
    python3 -m playwright install chromium
}

# Wait for backend
sleep 3

# Start frontend
echo "🎨 Starting Frontend (React + Vite)..."
cd frontend/lovable
nohup npm run dev -- --host 127.0.0.1 --port 8080 > ../../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > ../../frontend.pid
disown $FRONTEND_PID 2>/dev/null || true
echo "   Frontend PID: $FRONTEND_PID"

# Wait for services to start
sleep 5

# Check status
echo ""
echo "=================================================="
echo "           🎉 SERVICES STARTED 🎉"
echo "=================================================="
echo ""

# Test backend
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ Backend:  http://localhost:8000 (RUNNING)"
    echo "   API Docs: http://localhost:8000/docs"
else
    echo "❌ Backend:  http://localhost:8000 (NOT RESPONDING)"
fi

# Test frontend
if curl -s http://localhost:8080/ > /dev/null 2>&1; then
    echo "✅ Frontend: http://localhost:8080 (RUNNING)"
else
    echo "❌ Frontend: http://localhost:8080 (NOT RESPONDING)"
fi

echo ""
echo "=================================================="
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   or: lsof -ti:8000,8080 | xargs kill -9"
echo ""
echo "=================================================="
echo ""
echo "🌐 Open your browser to: http://localhost:8080"
echo ""
