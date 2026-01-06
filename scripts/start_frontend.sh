#!/bin/bash

# Start Frontend Only Script
# Use this if backend is already running

echo "🎨 Starting Frontend..."
echo ""

cd "$(dirname "$0")/frontend/lovable"

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "✅ Starting Vite dev server..."
echo "🌐 Frontend will be available at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
