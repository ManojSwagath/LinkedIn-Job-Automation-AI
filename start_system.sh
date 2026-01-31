#!/bin/bash
# Complete system startup script

set -e

PROJECT_ROOT="/Users/sathwikadigoppula/Documents/GitHub/LinkedIn-Job-Automation-with-AI"
cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🚀 Starting LinkedIn Job Automation System               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Stop existing servers
echo "🛑 Stopping existing servers..."
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:8080 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 2

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Check Node/npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found!"
    exit 1
fi

echo "✅ npm found: $(npm --version)"

# Set environment
export PYTHONPATH="$PROJECT_ROOT"
export PATH="$PROJECT_ROOT/venv/bin:$PATH"

# Start Backend
echo ""
echo "🔧 Starting Backend Server (port 8000)..."
python3 -m uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    > backend.log 2>&1 &

BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend
echo "   Waiting for backend to start..."
for i in {1..15}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Backend is healthy!"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "   ❌ Backend failed to start!"
        tail -20 backend.log
        exit 1
    fi
    sleep 1
done

# Start Frontend
echo ""
echo "🎨 Starting Frontend Server (port 8080)..."
cd "$PROJECT_ROOT/frontend/lovable"

npm run dev > "$PROJECT_ROOT/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Wait for frontend
echo "   Waiting for frontend to start..."
for i in {1..15}; do
    if lsof -ti:8080 > /dev/null 2>&1; then
        echo "   ✅ Frontend is running!"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "   ❌ Frontend failed to start!"
        tail -20 "$PROJECT_ROOT/frontend.log"
        exit 1
    fi
    sleep 1
done

cd "$PROJECT_ROOT"

# Display status
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ SYSTEM READY                                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Servers:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:8080"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🎯 Access Points:"
echo "   Automation UI: http://localhost:8080/dashboard/automation"
echo "   Health Check:  http://localhost:8000/health"
echo ""
echo "📊 Process IDs:"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   or: pkill -f 'uvicorn|vite'"
echo ""
echo "Press Ctrl+C to monitor logs..."
echo ""

# Monitor logs
tail -f backend.log frontend.log
