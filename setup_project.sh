#!/bin/bash

echo "🚀 LinkedIn Job Automation - Complete Setup"
echo "============================================"
echo ""

# 1. Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file with default values..."
    cat > .env << 'EOF'
# Application Settings
APP_NAME=AutoAgentHire
APP_ENV=development
DEBUG=True
LOG_LEVEL=INFO

# LinkedIn Credentials
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Vector Database (Qdrant)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=linkedin_jobs
VECTOR_DB_TYPE=qdrant

# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# GitHub Configuration
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
GITHUB_USERNAME=your_username
GITHUB_MODEL_ENDPOINT=https://api.github.com/models

# Database
DATABASE_URL=sqlite:///./data/autoagenthire.db

# Gemini (Alternative)
GEMINI_API_KEY=your_gemini_key_here

# Redis
REDIS_URL=redis://localhost:6379/0
EOF
    echo "✅ .env file created!"
    echo "⚠️  IMPORTANT: Update .env with your actual credentials:"
    echo "   - LINKEDIN_EMAIL and LINKEDIN_PASSWORD"
    echo "   - OPENAI_API_KEY"
    echo "   - GITHUB_TOKEN"
    echo ""
else
    echo "✅ .env file already exists"
fi

# 2. Create required directories
echo "📁 Creating required directories..."
mkdir -p data/logs
mkdir -p data/resumes
mkdir -p data/job_listings
mkdir -p vector_db/data
mkdir -p backend/logs
echo "✅ Directories created"

# 3. Check Python
echo ""
echo "🐍 Checking Python..."
python3 --version

# 4. Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Python dependencies installed"

# 5. Install Node dependencies
echo ""
echo "📦 Installing Node dependencies..."
cd frontend/lovable
npm install --quiet > /dev/null 2>&1
cd ../..
echo "✅ Node dependencies installed"

# 6. Initialize Qdrant
echo ""
echo "🗄️  Initializing Qdrant vector database..."
python3 << 'PYTHON'
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
    
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "linkedin_jobs")
    
    print(f"   Connecting to: {qdrant_url}")
    
    try:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key if qdrant_api_key else None)
        
        # Test connection
        client.get_collections()
        print(f"   ✅ Connected to Qdrant")
        
        # Delete existing collection if it exists
        try:
            client.delete_collection(collection_name=collection_name)
            print(f"   ✅ Cleared existing collection: {collection_name}")
        except:
            pass
        
        # Create new collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )
        print(f"   ✅ Created collection: {collection_name}")
        
    except Exception as e:
        print(f"   ⚠️  Qdrant not accessible: {e}")
        print(f"   Make sure Qdrant is running:")
        print(f"   docker run -p 6333:6333 qdrant/qdrant:latest")
        
except ImportError:
    print(f"   ⚠️  qdrant-client not installed")
    print(f"   Installing now...")
    os.system("pip install qdrant-client --quiet")
    print(f"   ✅ qdrant-client installed")

PYTHON

# 7. Summary
echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Update .env with your credentials:"
echo "      - LINKEDIN_EMAIL and LINKEDIN_PASSWORD"
echo "      - OPENAI_API_KEY"
echo "      - GITHUB_TOKEN"
echo ""
echo "   2. Start Qdrant (if using local):"
echo "      docker run -p 6333:6333 qdrant/qdrant:latest"
echo ""
echo "   3. Run the project:"
echo "      ./quick_start.sh"
echo ""
echo "   4. Verify setup:"
echo "      python verify_setup.py"
echo ""
echo "================================"
echo "🎉 Ready to automate LinkedIn!"
echo "================================"
