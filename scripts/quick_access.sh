#!/bin/bash
# Quick Access URLs for AutoAgentHire
# Generated: 2026-01-06

echo "🚀 AutoAgentHire - Quick Access Guide"
echo "====================================="
echo ""

# Check if services are running
BACKEND_RUNNING=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
FRONTEND_RUNNING=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080)

echo "📊 Service Status:"
echo "=================="
if [ "$BACKEND_RUNNING" = "200" ]; then
    echo "✅ Backend:  RUNNING (Port 8000)"
else
    echo "❌ Backend:  NOT RUNNING (Port 8000)"
fi

if [ "$FRONTEND_RUNNING" = "200" ]; then
    echo "✅ Frontend: RUNNING (Port 8080)"
else
    echo "❌ Frontend: NOT RUNNING (Port 8080)"
fi
echo ""

echo "🌐 Access URLs:"
echo "==============="
echo "Frontend:          http://localhost:8080"
echo "Backend API:       http://localhost:8000"
echo "API Docs:          http://localhost:8000/docs"
echo "ReDoc:             http://localhost:8000/redoc"
echo "OpenAPI Spec:      http://localhost:8000/openapi.json"
echo ""

echo "🧪 Test Commands:"
echo "================="
echo "Health Check:      curl http://localhost:8000/health"
echo "LangGraph Health:  curl http://localhost:8000/api/agent/langgraph/health"
echo "Run Integration:   python test_integration.py"
echo "Run Unit Tests:    python tests/test_langgraph_orchestrator.py"
echo ""

echo "🔧 Quick Actions:"
echo "================="
echo "Test LangGraph workflow:"
echo ""
echo 'curl -X POST http://localhost:8000/api/agent/langgraph/run \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{'
echo '    "user_id": "test_user",'
echo '    "resume_text": "Senior Engineer with Python, FastAPI, React",'
echo '    "target_roles": ["software_engineer"],'
echo '    "desired_locations": ["Remote"],'
echo '    "max_applications": 5,'
echo '    "dry_run": true'
echo '  }'"'"''
echo ""

echo "📚 Documentation:"
echo "================="
echo "System Status:     cat SYSTEM_STATUS.md"
echo "Orchestrator:      cat backend/agents/ORCHESTRATOR_README.md"
echo "Quick Start:       cat QUICKSTART.md"
echo ""

# If running in interactive mode, offer to open URLs
if [ -t 0 ]; then
    echo "Would you like to open any of these in your browser? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        echo "1) Frontend"
        echo "2) API Docs"
        echo "3) Both"
        read -r choice
        case $choice in
            1)
                open http://localhost:8080
                echo "✅ Opened frontend in browser"
                ;;
            2)
                open http://localhost:8000/docs
                echo "✅ Opened API docs in browser"
                ;;
            3)
                open http://localhost:8080
                open http://localhost:8000/docs
                echo "✅ Opened both in browser"
                ;;
        esac
    fi
fi
