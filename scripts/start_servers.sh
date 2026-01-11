#!/bin/bash

set -euo pipefail

# AutoAgentHire - Simple Startup (Keeps running in foreground)

echo "🚀 Starting AutoAgentHire Backend & Frontend"
echo "============================================="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-8080}

BACKEND_LOG="$ROOT_DIR/backend.log"
FRONTEND_LOG="$ROOT_DIR/frontend.log"
BACKEND_PID_FILE="$ROOT_DIR/backend.pid"
FRONTEND_PID_FILE="$ROOT_DIR/frontend.pid"

wait_for_port() {
    local port="$1"
    local name="$2"
    local timeout="${3:-25}"

    local t=0
    while ! lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; do
        sleep 1
        t=$((t+1))
        if [ "$t" -ge "$timeout" ]; then
            echo "❌ $name did not start (port $port not listening after ${timeout}s)"
            return 1
        fi
    done
}

# Clean ports
pkill -f "uvicorn|vite" 2>/dev/null || true
lsof -ti:"$BACKEND_PORT" | xargs kill -9 2>/dev/null || true
lsof -ti:"$FRONTEND_PORT" | xargs kill -9 2>/dev/null || true
sleep 1

# Ensure directories exist
mkdir -p data/resumes data/job_listings browser_profile
test -f data/applications.json || echo "[]" > data/applications.json

# Start backend in background
echo "Starting backend on port $BACKEND_PORT..."
if [ -f "$ROOT_DIR/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$ROOT_DIR/venv/bin/activate"
fi
nohup python -m uvicorn backend.main:app --host 127.0.0.1 --port "$BACKEND_PORT" --reload > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$BACKEND_PID_FILE"

# Wait for backend (real check)
wait_for_port "$BACKEND_PORT" "Backend" 35

# Start frontend in background
echo "Starting frontend on port $FRONTEND_PORT..."
nohup npm --prefix "$ROOT_DIR/frontend/lovable" run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT" > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$FRONTEND_PID_FILE"

# Wait for frontend (real check)
wait_for_port "$FRONTEND_PORT" "Frontend" 35

echo ""
echo "✅ Both servers started!"
echo "========================="
echo "🌐 Backend:  http://127.0.0.1:$BACKEND_PORT"
echo "🌐 Frontend: http://127.0.0.1:$FRONTEND_PORT"
echo "📚 API Docs: http://127.0.0.1:$BACKEND_PORT/docs"
echo "🪪 PIDs: backend=$(cat "$BACKEND_PID_FILE" 2>/dev/null || true) frontend=$(cat "$FRONTEND_PID_FILE" 2>/dev/null || true)"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Open browser
if command -v open &> /dev/null; then
    sleep 2
    open "http://127.0.0.1:$FRONTEND_PORT"
fi

# Keep script running
wait
