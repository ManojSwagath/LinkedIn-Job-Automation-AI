#!/bin/bash

# AutoAgentHire - Stop All Services Script

set -e

PROJECT_ROOT="/Users/sathwikadigoppula/Documents/GitHub/LinkedIn-Job-Automation-with-AI"

echo "=========================================="
echo "🛑 AutoAgentHire - Stopping All Services"
echo "=========================================="
echo ""

# Stop backend
echo "1️⃣  Stopping Backend..."
if [ -f "$PROJECT_ROOT/.backend.pid" ]; then
    BACKEND_PID=$(cat "$PROJECT_ROOT/.backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        echo "   ✅ Backend stopped (PID: $BACKEND_PID)"
    else
        echo "   ℹ️  Backend not running"
    fi
    rm "$PROJECT_ROOT/.backend.pid"
else
    # Fallback: kill by port
    if lsof -ti:8000 > /dev/null 2>&1; then
        lsof -ti:8000 | xargs kill -9
        echo "   ✅ Backend stopped (port 8000)"
    else
        echo "   ℹ️  Backend not running"
    fi
fi

# Stop frontend
echo ""
echo "2️⃣  Stopping Frontend..."
if [ -f "$PROJECT_ROOT/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "$PROJECT_ROOT/.frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        echo "   ✅ Frontend stopped (PID: $FRONTEND_PID)"
    else
        echo "   ℹ️  Frontend not running"
    fi
    rm "$PROJECT_ROOT/.frontend.pid"
else
    # Fallback: kill by port
    if lsof -ti:8080 > /dev/null 2>&1; then
        lsof -ti:8080 | xargs kill -9
        echo "   ✅ Frontend stopped (port 8080)"
    else
        echo "   ℹ️  Frontend not running"
    fi
fi

# Kill any remaining processes
echo ""
echo "3️⃣  Cleaning up remaining processes..."

# Kill uvicorn processes
if pgrep -f "uvicorn" > /dev/null; then
    pkill -f "uvicorn"
    echo "   ✅ Killed uvicorn processes"
fi

# Kill vite processes
if pgrep -f "vite" > /dev/null; then
    pkill -f "vite"
    echo "   ✅ Killed vite processes"
fi

# Kill browser automation processes
if pgrep -f "chromium" > /dev/null; then
    pkill -f "chromium"
    echo "   ✅ Killed chromium processes"
fi

if pgrep -f "playwright" > /dev/null; then
    pkill -f "playwright"
    echo "   ✅ Killed playwright processes"
fi

# Verify services stopped
echo ""
echo "=========================================="
echo "✅ Verification:"
echo "=========================================="
echo ""

if ! lsof -ti:8000 > /dev/null 2>&1; then
    echo "   ✅ Backend stopped (port 8000 free)"
else
    echo "   ⚠️  Port 8000 still in use"
fi

if ! lsof -ti:8080 > /dev/null 2>&1; then
    echo "   ✅ Frontend stopped (port 8080 free)"
else
    echo "   ⚠️  Port 8080 still in use"
fi

echo ""
echo "=========================================="
echo "✅ All Services Stopped!"
echo "=========================================="
echo ""
echo "To restart: $PROJECT_ROOT/start_services.sh"
echo ""
