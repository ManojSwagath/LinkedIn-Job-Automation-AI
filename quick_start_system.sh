#!/bin/bash

# =============================================================================
# AutoAgentHire - Quick Start (No dependency checks)
# Starts Backend + Frontend quickly
# =============================================================================

set -euo pipefail

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🤖 AutoAgentHire Quick Start                            ║"
echo "║                  LinkedIn Job Automation with AI                           ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=8080
BACKEND_LOG="$ROOT_DIR/backend.log"
FRONTEND_LOG="$ROOT_DIR/frontend.log"
BACKEND_PID_FILE="$ROOT_DIR/backend.pid"
FRONTEND_PID_FILE="$ROOT_DIR/frontend.pid"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    
    if [ -f "$BACKEND_PID_FILE" ]; then
        kill "$(cat "$BACKEND_PID_FILE")" 2>/dev/null || true
        rm -f "$BACKEND_PID_FILE"
    fi
    
    if [ -f "$FRONTEND_PID_FILE" ]; then
        kill "$(cat "$FRONTEND_PID_FILE")" 2>/dev/null || true
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    pkill -f "uvicorn.*backend.main" 2>/dev/null || true
    pkill -f "vite.*frontend/lovable" 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    
    echo "✓ All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Clean previous instances
echo "🧹 Cleaning previous instances..."
pkill -f "uvicorn.*backend.main" 2>/dev/null || true
pkill -f "vite.*frontend/lovable" 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"
sleep 2
echo "✓ Cleanup complete"
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Create necessary directories
mkdir -p data/resumes data/job_listings data/cover_letters data/logs browser_profile
test -f data/applications.json || echo "[]" > data/applications.json

# Start Backend
echo ""
echo "🚀 Starting Backend Server on port $BACKEND_PORT..."
nohup python -m uvicorn backend.main:app \
    --host 127.0.0.1 \
    --port "$BACKEND_PORT" \
    --reload \
    > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$BACKEND_PID_FILE"
echo "   PID: $BACKEND_PID"

# Wait for backend
echo "   Waiting for backend to start..."
sleep 5
if lsof -nP -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "✓ Backend is ready"
else
    echo "⚠ Backend might not be ready yet (check logs)"
fi

# Start Frontend
echo ""
echo "🎨 Starting Frontend Server on port $FRONTEND_PORT..."
cd frontend/lovable
nohup npm run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT" > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
cd "$ROOT_DIR"
echo "$FRONTEND_PID" > "$FRONTEND_PID_FILE"
echo "   PID: $FRONTEND_PID"

# Wait for frontend
echo "   Waiting for frontend to start..."
sleep 8
if lsof -nP -iTCP:8080 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "✓ Frontend is ready"
else
    echo "⚠ Frontend might not be ready yet (check logs)"
fi

# System Ready
echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                        ✅ SYSTEM FULLY OPERATIONAL                         ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Access Points:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 Frontend UI:     http://127.0.0.1:$FRONTEND_PORT"
echo "  🔌 Backend API:     http://127.0.0.1:$BACKEND_PORT"
echo "  📚 API Docs:        http://127.0.0.1:$BACKEND_PORT/docs"
echo ""
echo "📁 Log Files:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📝 Backend:  tail -f $BACKEND_LOG"
echo "  📝 Frontend: tail -f $FRONTEND_LOG"
echo ""
echo "🔧 Test Automation:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  python test_linkedin_automation_complete.py"
echo ""
echo "⚠️  Press Ctrl+C to stop all services"
echo ""

# Open browser
if command -v open &> /dev/null; then
    sleep 2
    echo "🌐 Opening browser..."
    open "http://127.0.0.1:$FRONTEND_PORT"
fi

# Keep running and monitor
echo "📊 Monitoring services (Ctrl+C to stop)..."
while true; do
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "❌ Backend process died!"
        cleanup
    fi
    
    if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo "❌ Frontend process died!"
        cleanup
    fi
    
    sleep 5
done
