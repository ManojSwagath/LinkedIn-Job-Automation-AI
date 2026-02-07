#!/usr/bin/env bash
# Quick local test of the deployment setup

set -e

echo "🔍 Checking deployment files..."

# Check required files
files=("runtime.txt" "build.sh" "render.yaml" "Procfile" "requirements.txt" ".env.example")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing!"
        exit 1
    fi
done

echo ""
echo "🐍 Checking Python version..."
python_version=$(cat runtime.txt)
echo "Target Python version: $python_version"

echo ""
echo "📦 Checking requirements.txt..."
if grep -q "pydantic==2.9.2" requirements.txt; then
    echo "✅ Pydantic updated to 2.9.2"
else
    echo "⚠️  Pydantic version might need updating"
fi

if grep -q "fastapi==0.115.0" requirements.txt; then
    echo "✅ FastAPI updated to 0.115.0"
else
    echo "⚠️  FastAPI version might need updating"
fi

echo ""
echo "🔧 Checking config.py..."
if grep -q "validation_alias=\"PORT\"" backend/config.py; then
    echo "✅ PORT environment variable support added"
else
    echo "⚠️  PORT validation alias might be missing"
fi

echo ""
echo "✅ All deployment files are ready!"
echo ""
echo "Next steps:"
echo "1. Create .env file from .env.example"
echo "2. Fill in required environment variables"
echo "3. Commit and push to GitHub"
echo "4. Deploy on Render.com"
echo ""
echo "📖 See RENDER_DEPLOYMENT.md for detailed instructions"
