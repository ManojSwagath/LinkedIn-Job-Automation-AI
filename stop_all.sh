#!/bin/bash

# Stop all services related to AutoAgentHire

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Stopping AutoAgentHire Services                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PID_FILE="$PROJECT_ROOT/backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/frontend.pid"

STOPPED=0

# Stop backend from PID file
if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        STOPPED=$((STOPPED + 1))
    fi
    rm -f "$BACKEND_PID_FILE"
fi

# Stop frontend from PID file
if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        STOPPED=$((STOPPED + 1))
    fi
    rm -f "$FRONTEND_PID_FILE"
fi

# Kill backend (port 8000)
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Stopping process on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    STOPPED=$((STOPPED + 1))
fi

# Kill frontend (port 8080)
if lsof -ti:8080 > /dev/null 2>&1; then
    echo "Stopping process on port 8080..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    STOPPED=$((STOPPED + 1))
fi

# Kill any node/vite processes
if pgrep -f "vite" > /dev/null; then
    echo "Stopping Vite dev server..."
    pkill -f "vite" 2>/dev/null || true
    STOPPED=$((STOPPED + 1))
fi

# Kill uvicorn processes
if pgrep -f "uvicorn" > /dev/null; then
    echo "Stopping Uvicorn server..."
    pkill -f "uvicorn" 2>/dev/null || true
    STOPPED=$((STOPPED + 1))
fi

echo ""
if [ $STOPPED -eq 0 ]; then
    echo "ℹ️  No services were running"
else
    echo "✅ Stopped $STOPPED service(s)"
fi
echo ""
