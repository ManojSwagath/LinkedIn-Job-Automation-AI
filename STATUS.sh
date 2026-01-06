#!/bin/bash
# CHECK STATUS - See if everything is running

echo "🔍 Checking System Status..."
echo ""

# Check Backend
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Backend: Running on http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
else
    echo "❌ Backend: Not running"
    echo "   Check: tail -f backend.log"
fi

echo ""

# Check Frontend
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ Frontend: Running on http://localhost:8080"
else
    echo "❌ Frontend: Not running"
    echo "   Check: tail -f frontend.log"
fi

echo ""

# Show processes
echo "📊 Running Processes:"
ps aux | grep -E "(uvicorn|vite)" | grep -v grep | awk '{print "   "$2, $11, $12, $13}'

echo ""
echo "📝 View Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 Stop All:  ./stop_all.sh"
echo "🚀 Restart:   ./GO.sh"
echo ""
