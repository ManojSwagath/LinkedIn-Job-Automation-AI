#!/bin/bash

# ========================================
# 🎨 START LOVABLE FRONTEND + BACKEND
# ========================================
# Complete startup script for Lovable frontend
# ========================================

set -e

cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🎨 LinkedIn Job Automation - Lovable Frontend           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found"
    exit 1
fi
echo "✅ npm: $(npm --version)"

# Check Python dependencies
echo ""
echo "📦 Checking Python dependencies..."
if ! python3 -c "import fastapi, uvicorn, playwright, google.generativeai" 2>/dev/null; then
    echo "⚠️  Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Check Playwright browsers
echo ""
echo "🌐 Checking Playwright browsers..."
if ! python3 -c "from playwright.sync_api import sync_playwright; sync_playwright().start().stop()" 2>/dev/null; then
    echo "⚠️  Installing Playwright browsers..."
    python3 -m playwright install chromium
fi

# Check Node dependencies
echo ""
echo "📦 Checking Node dependencies..."
cd frontend/lovable
if [ ! -d "node_modules" ]; then
    echo "⚠️  Installing Node dependencies..."
    npm install
fi
cd ../..

# Check API key
echo ""
echo "🔑 Checking Gemini API key..."
if ! python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); key = os.getenv('GEMINI_API_KEY'); exit(0 if key and not key.startswith('your_') else 1)" 2>/dev/null; then
    echo "⚠️  GEMINI_API_KEY not configured in .env file"
    echo "    Get your key from: https://makersuite.google.com/app/apikey"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Starting Services..."
echo "════════════════════════════════════════════════════════════"
echo ""

# Kill existing processes
echo "🧹 Cleaning up old processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
sleep 2

# Start Backend
echo ""
echo "🔧 Starting Backend API (port 8000)..."
nohup uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   └─ Backend PID: $BACKEND_PID"

# Wait for backend
echo "   └─ Waiting for backend..."
sleep 5

# Check backend health
if curl -s http://localhost:8000/api/health | grep -q "healthy"; then
    echo "   └─ ✅ Backend healthy"
else
    echo "   └─ ❌ Backend failed to start"
    echo "   └─ Check logs: tail -f backend.log"
    exit 1
fi

# Start Frontend
echo ""
echo "🎨 Starting Lovable Frontend (port 8080)..."
cd frontend/lovable
nohup npm run dev > lovable-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   └─ Frontend PID: $FRONTEND_PID"
cd ../..

# Wait for frontend
echo "   └─ Waiting for frontend..."
sleep 8

# Check frontend
if curl -s http://localhost:8080 2>&1 | grep -q "DOCTYPE"; then
    echo "   └─ ✅ Frontend healthy"
else
    echo "   └─ ⚠️  Frontend may still be starting..."
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ✅ READY TO USE!                        ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  🎨 Lovable Frontend (React/Vite):                        ║"
echo "║     👉 http://localhost:8080                               ║"
echo "║                                                            ║"
echo "║  🔧 Backend API (FastAPI):                                 ║"
echo "║     http://localhost:8000                                  ║"
echo "║     API Docs: http://localhost:8000/docs                   ║"
echo "║                                                            ║"
echo "║  📝 Logs:                                                  ║"
echo "║     Backend:  tail -f backend.log                         ║"
echo "║     Frontend: tail -f frontend/lovable/lovable-frontend.log ║"
echo "║                                                            ║"
echo "║  🛑 Stop Services:                                         ║"
echo "║     kill $BACKEND_PID $FRONTEND_PID                        ║"
echo "║     OR: ./stop_all.sh                                     ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 Quick Start Guide:"
echo ""
echo "   1. Open: http://localhost:8080"
echo "   2. Navigate to Dashboard → Search"
echo "   3. Upload your resume (PDF)"
echo "   4. Configure job search:"
echo "      • Job Title: 'Python Developer'"
echo "      • Location: 'Remote'"
echo "      • Max applications: 5"
echo "   5. Enter LinkedIn credentials"
echo "   6. Click '🚀 Start Automation'"
echo ""
echo "📚 Documentation:"
echo "   • Full Guide: LOVABLE_FRONTEND_COMPLETE.md"
echo "   • Architecture: docs/ARCHITECTURE.md"
echo "   • API Reference: http://localhost:8000/docs"
echo ""
echo "⚠️  IMPORTANT:"
echo "   • Browser window will open automatically"
echo "   • Bot will type credentials slowly (looks human)"
echo "   • You may need to solve CAPTCHA on first login"
echo "   • Easy Apply filter is ENABLED by default"
echo ""
echo "Press Ctrl+C to stop (will kill both services)"
echo ""

# Keep script running and handle Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ Services stopped'; exit 0" INT TERM

# Monitor processes
while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend process died!"
        kill $FRONTEND_PID 2>/dev/null
        exit 1
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend process died!"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 5
done
