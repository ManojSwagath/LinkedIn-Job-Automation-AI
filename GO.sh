#!/bin/bash
# FASTEST WAY TO START - One command does everything!

cd "$(dirname "$0")"

echo "🚀 Starting AutoAgentHire..."
echo ""

# Kill any existing processes
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 1

# Start Backend
echo "▶️  Backend starting..."
export PYTHONPATH="$PWD:$PYTHONPATH"
cd backend
../venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 3

# Start Frontend
echo "▶️  Frontend starting..."
cd frontend/lovable
npm run dev -- --port 8080 --host 0.0.0.0 > ../../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..
sleep 3

# Show status
echo ""
echo "✅ READY!"
echo ""
echo "🌐 Frontend: http://localhost:8080"
echo "⚙️  Backend:  http://localhost:8000/docs"
echo ""
echo "🛑 Stop: ./stop_all.sh"
echo ""

# Open browser
sleep 2
open http://localhost:8080 2>/dev/null || echo "Open http://localhost:8080 in your browser"
