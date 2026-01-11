#!/bin/bash

set -euo pipefail

# =============================================================================
# AutoAgentHire - Complete System Startup
# Starts Backend + Frontend + Automation in one command
# =============================================================================

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🤖 AutoAgentHire Complete System                        ║"
echo "║                  LinkedIn Job Automation with AI                           ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Configuration
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-8080}
BACKEND_LOG="$ROOT_DIR/backend.log"
FRONTEND_LOG="$ROOT_DIR/frontend.log"
BACKEND_PID_FILE="$ROOT_DIR/backend.pid"
FRONTEND_PID_FILE="$ROOT_DIR/frontend.pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

wait_for_port() {
    local port="$1"
    local name="$2"
    local timeout="${3:-30}"
    
    print_info "Waiting for $name on port $port..."
    local t=0
    while ! lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; do
        sleep 1
        t=$((t+1))
        if [ "$t" -ge "$timeout" ]; then
            print_error "$name did not start (port $port not listening after ${timeout}s)"
            return 1
        fi
    done
    print_status "$name is ready on port $port"
}

cleanup() {
    echo ""
    echo "🛑 Shutting down all services..."
    
    # Stop services
    if [ -f "$BACKEND_PID_FILE" ]; then
        kill "$(cat "$BACKEND_PID_FILE")" 2>/dev/null || true
        rm -f "$BACKEND_PID_FILE"
    fi
    
    if [ -f "$FRONTEND_PID_FILE" ]; then
        kill "$(cat "$FRONTEND_PID_FILE")" 2>/dev/null || true
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    # Kill by process name
    pkill -f "uvicorn.*backend.main" 2>/dev/null || true
    pkill -f "vite.*frontend/lovable" 2>/dev/null || true
    
    # Kill by port
    lsof -ti:"$BACKEND_PORT" | xargs kill -9 2>/dev/null || true
    lsof -ti:"$FRONTEND_PORT" | xargs kill -9 2>/dev/null || true
    
    print_status "All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# =============================================================================
# Pre-flight Checks
# =============================================================================

echo "📋 Pre-flight checks..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi
print_status "Python $(python3 --version | cut -d' ' -f2) found"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi
print_status "Node.js $(node --version) found"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi
print_status "npm $(npm --version) found"

# Check virtual environment
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found, creating..."
    python3 -m venv venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
    print_status "Virtual environment activated"
else
    print_error "Could not activate virtual environment"
    exit 1
fi

# Check .env file
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    if [ -f ".env.example" ]; then
        print_info "Copying .env.example to .env"
        cp .env.example .env
        print_warning "Please edit .env with your credentials"
    else
        print_error "No .env or .env.example found"
        exit 1
    fi
fi
print_status "Environment file found"

# Check dependencies
print_info "Checking Python dependencies..."
if ! pip list | grep -q "fastapi"; then
    print_warning "Installing Python dependencies..."
    pip install -q -r requirements.txt
    print_status "Python dependencies installed"
else
    print_status "Python dependencies OK"
fi

# Check frontend dependencies
if [ ! -d "frontend/lovable/node_modules" ]; then
    print_warning "Installing frontend dependencies..."
    cd frontend/lovable
    npm install
    cd "$ROOT_DIR"
    print_status "Frontend dependencies installed"
else
    print_status "Frontend dependencies OK"
fi

# Create necessary directories
print_info "Creating data directories..."
mkdir -p data/resumes data/job_listings data/cover_letters data/logs data/reports browser_profile
test -f data/applications.json || echo "[]" > data/applications.json
print_status "Data directories ready"

echo ""

# =============================================================================
# Clean Previous Instances
# =============================================================================

echo "🧹 Cleaning previous instances..."
pkill -f "uvicorn.*backend.main" 2>/dev/null || true
pkill -f "vite.*frontend/lovable" 2>/dev/null || true
lsof -ti:"$BACKEND_PORT" | xargs kill -9 2>/dev/null || true
lsof -ti:"$FRONTEND_PORT" | xargs kill -9 2>/dev/null || true
rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE"
sleep 2
print_status "Cleanup complete"
echo ""

# =============================================================================
# Start Backend
# =============================================================================

echo "🚀 Starting Backend Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

nohup python -m uvicorn backend.main:app \
    --host 127.0.0.1 \
    --port "$BACKEND_PORT" \
    --reload \
    > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$BACKEND_PID_FILE"

print_info "Backend PID: $BACKEND_PID"
wait_for_port "$BACKEND_PORT" "Backend API" 40 || exit 1

echo ""

# =============================================================================
# Start Frontend
# =============================================================================

echo "🎨 Starting Frontend Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd frontend/lovable
nohup npm run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT" > "$ROOT_DIR/$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
cd "$ROOT_DIR"
echo "$FRONTEND_PID" > "$FRONTEND_PID_FILE"

print_info "Frontend PID: $FRONTEND_PID"
wait_for_port "$FRONTEND_PORT" "Frontend UI" 40 || exit 1

echo ""

# =============================================================================
# System Ready
# =============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                        ✅ SYSTEM FULLY OPERATIONAL                         ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 System Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}●${NC} Backend API:     http://127.0.0.1:$BACKEND_PORT"
echo -e "  ${GREEN}●${NC} API Docs:        http://127.0.0.1:$BACKEND_PORT/docs"
echo -e "  ${GREEN}●${NC} Frontend UI:     http://127.0.0.1:$FRONTEND_PORT"
echo -e "  ${GREEN}●${NC} Backend PID:     $(cat "$BACKEND_PID_FILE")"
echo -e "  ${GREEN}●${NC} Frontend PID:    $(cat "$FRONTEND_PID_FILE")"
echo ""
echo "📁 Log Files:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📝 Backend:  $BACKEND_LOG"
echo "  📝 Frontend: $FRONTEND_LOG"
echo ""
echo "🎯 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1. Open browser: http://127.0.0.1:$FRONTEND_PORT"
echo "  2. Configure LinkedIn credentials in the UI"
echo "  3. Upload your resume"
echo "  4. Start job automation!"
echo ""
echo "🔧 Automation Testing:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  To test LinkedIn automation directly:"
echo -e "  ${BLUE}python test_linkedin_automation_complete.py${NC}"
echo ""
echo "📊 Monitor Logs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  Backend:  ${BLUE}tail -f $BACKEND_LOG${NC}"
echo -e "  Frontend: ${BLUE}tail -f $FRONTEND_LOG${NC}"
echo ""
echo "⚠️  Press Ctrl+C to stop all services"
echo ""

# Open browser automatically
if command -v open &> /dev/null; then
    sleep 3
    print_info "Opening browser..."
    open "http://127.0.0.1:$FRONTEND_PORT"
fi

# Keep script running and monitor processes
while true; do
    # Check if backend is still running
    if ! kill -0 "$(cat "$BACKEND_PID_FILE" 2>/dev/null)" 2>/dev/null; then
        print_error "Backend process died!"
        cleanup
    fi
    
    # Check if frontend is still running
    if ! kill -0 "$(cat "$FRONTEND_PID_FILE" 2>/dev/null)" 2>/dev/null; then
        print_error "Frontend process died!"
        cleanup
    fi
    
    sleep 5
done
