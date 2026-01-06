#!/bin/bash

# AutoAgentHire - Simple Startup (Keeps running in foreground)

echo "🚀 Starting AutoAgentHire Backend & Frontend"
echo "============================================="

# Clean ports
pkill -f "uvicorn|vite" 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null
sleep 1

# Ensure directories exist
mkdir -p data/resumes data/job_listings browser_profile
test -f data/applications.json || echo "[]" > data/applications.json

# Start backend in background
echo "Starting backend on port 8000..."
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend
sleep 5

# Start frontend in background
echo "Starting frontend on port 8080..."
cd frontend/lovable
npm run dev -- --host 127.0.0.1 --port 8080 &
FRONTEND_PID=$!
cd ../..

# Wait for frontend
sleep 5

echo ""
echo "✅ Both servers started!"
echo "========================="
echo "🌐 Backend:  http://127.0.0.1:8000"
echo "🌐 Frontend: http://127.0.0.1:8080"
echo "📚 API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Open browser
if command -v open &> /dev/null; then
    sleep 2
    open http://127.0.0.1:8080
fi

# Keep script running
wait
