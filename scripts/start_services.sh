#!/bin/bash

# AutoAgentHire - Complete Startup Script
# This script starts both backend and frontend services

set -e

PROJECT_ROOT="/Users/sathwikadigoppula/Documents/GitHub/LinkedIn-Job-Automation-with-AI"
FRONTEND_DIR="$PROJECT_ROOT/frontend/lovable"

echo "=========================================="
echo "🚀 AutoAgentHire - Starting All Services"
echo "=========================================="
echo ""

# Check if already running
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Backend already running on port 8000"
    echo "   Kill it? (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        lsof -ti:8000 | xargs kill -9
        echo "   ✅ Killed existing backend"
    fi
fi

if lsof -ti:8080 > /dev/null 2>&1; then
    echo "⚠️  Frontend already running on port 8080"
    echo "   Kill it? (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        lsof -ti:8080 | xargs kill -9
        echo "   ✅ Killed existing frontend"
    fi
fi

echo ""
echo "📋 Starting services..."
echo ""

# Start Backend
echo "1️⃣  Starting Backend (FastAPI + Agents)..."
cd "$PROJECT_ROOT"
source venv/bin/activate

# Start backend in background
nohup python3 -m uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   ✅ Backend starting (PID: $BACKEND_PID)"
echo "   📝 Logs: logs/backend.log"

# Wait for backend to be ready
echo "   ⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Backend is ready!"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# Start Frontend
echo ""
echo "2️⃣  Starting Frontend (React + Vite)..."
cd "$FRONTEND_DIR"

# Start frontend in background
nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "   ✅ Frontend starting (PID: $FRONTEND_PID)"
echo "   📝 Logs: logs/frontend.log"

# Wait for frontend to be ready
echo "   ⏳ Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo "   ✅ Frontend is ready!"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# Verify services
echo ""
echo "=========================================="
echo "✅ Services Started Successfully!"
echo "=========================================="
echo ""
echo "📊 Status:"
echo ""

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo '{"status":"unknown"}')
    echo "   ✅ Backend:  http://localhost:8000"
    echo "      Health:  $HEALTH"
else
    echo "   ❌ Backend:  Not responding"
fi

# Check frontend
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "   ✅ Frontend: http://localhost:8080"
else
    echo "   ❌ Frontend: Not responding"
fi

echo ""
echo "=========================================="
echo "🌐 Access URLs:"
echo "=========================================="
echo ""
echo "   Frontend:        http://localhost:8080"
echo "   Backend API:     http://localhost:8000"
echo "   API Docs:        http://localhost:8000/docs"
echo "   Health Check:    http://localhost:8000/health"
echo ""
echo "=========================================="
echo "📝 Logs:"
echo "=========================================="
echo ""
echo "   Backend:  tail -f $PROJECT_ROOT/logs/backend.log"
echo "   Frontend: tail -f $PROJECT_ROOT/logs/frontend.log"
echo ""
echo "=========================================="
echo "🛑 Stop Services:"
echo "=========================================="
echo ""
echo "   All:      $PROJECT_ROOT/stop_services.sh"
echo "   Backend:  kill $BACKEND_PID"
echo "   Frontend: kill $FRONTEND_PID"
echo ""
echo "=========================================="
echo ""

# Save PIDs to file for stop script
echo "$BACKEND_PID" > "$PROJECT_ROOT/.backend.pid"
echo "$FRONTEND_PID" > "$PROJECT_ROOT/.frontend.pid"

# Open browser
echo "🌐 Opening browser..."
sleep 2
open http://localhost:8080

echo ""
echo "✅ AutoAgentHire is now running!"
echo "   Press Ctrl+C to see logs, or run stop_services.sh to stop"
echo ""

# Follow logs
echo "📝 Showing combined logs (Ctrl+C to exit)..."
echo ""
tail -f "$PROJECT_ROOT/logs/backend.log" "$PROJECT_ROOT/logs/frontend.log"
