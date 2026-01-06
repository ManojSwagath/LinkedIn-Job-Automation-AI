#!/bin/bash

# 🛑 AutoAgentHire - Stop Script

echo "🛑 Stopping AutoAgentHire..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Kill backend (port 8000)
if lsof -ti:8000 >/dev/null 2>&1; then
    echo -e "Stopping backend (port 8000)..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Backend stopped${NC}"
else
    echo -e "${RED}ℹ️  Backend not running${NC}"
fi

# Kill frontend (port 8080)
if lsof -ti:8080 >/dev/null 2>&1; then
    echo -e "Stopping frontend (port 8080)..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Frontend stopped${NC}"
else
    echo -e "${RED}ℹ️  Frontend not running${NC}"
fi

# Kill any remaining node/uvicorn processes (optional)
# pkill -f "uvicorn backend.main:app" 2>/dev/null
# pkill -f "vite" 2>/dev/null

echo ""
echo -e "${GREEN}✅ All services stopped!${NC}"
