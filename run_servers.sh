#!/bin/bash
echo "🚀 Starting LinkedIn Job Automation Servers..."

# Start backend
echo "🔧 Starting Backend..."
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend
sleep 5

# Test backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🎨 Starting Frontend..."
cd frontend/lovable
npm run dev &
FRONTEND_PID=$!

# Wait for frontend
sleep 5

echo ""
echo "🎉 Both servers are running!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
