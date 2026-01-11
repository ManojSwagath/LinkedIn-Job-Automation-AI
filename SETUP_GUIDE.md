# 🚀 SETUP GUIDE: Qdrant Vector Database + GitHub API Token + GPT-4o

## ✅ Step 1: Initialize Qdrant Vector Database

### Option A: Local Qdrant (Recommended for Development)

```bash
# Install Qdrant client
pip install qdrant-client

# Start Qdrant locally (requires Docker)
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest

# Or start with persistence
docker run -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  -e QDRANT_API_KEY=your_api_key \
  qdrant/qdrant:latest
```

### Option B: Cloud Qdrant

```bash
# Sign up at: https://qdrant.tech/cloud
# Get your API key and URL from the console
```

### Add to .env file:

```bash
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=linkedin_jobs
VECTOR_DB_TYPE=qdrant  # Options: qdrant, pinecone, chroma
```

---

## ✅ Step 2: Setup GitHub API Token for GPT-4o Access

### Create GitHub API Token:

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Set these scopes:
   - `repo` (full repository access)
   - `user` (user information)
   - `gist` (gist access)
4. Copy the token (you won't see it again!)

### Add to .env file:

```bash
# GitHub Configuration
GITHUB_TOKEN=ghp_YOUR_GITHUB_TOKEN_HERE
GITHUB_USERNAME=your_github_username

# GPT-4o Configuration (via OpenAI)
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY_HERE
OPENAI_MODEL=gpt-4o
LLM_PROVIDER=openai  # or: github, anthropic, gemini

# If using GitHub API for model access
GITHUB_MODEL_ENDPOINT=https://api.github.com/models
```

---

## ✅ Step 3: Initialize Vector Database with Data

Create `initialize_qdrant.py`:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Qdrant client
client = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Create collection for job embeddings
collection_name = os.getenv("QDRANT_COLLECTION_NAME", "linkedin_jobs")

try:
    # Delete existing collection if it exists
    client.delete_collection(collection_name=collection_name)
    print(f"✅ Deleted existing collection: {collection_name}")
except Exception as e:
    print(f"⚠️ Collection doesn't exist yet: {e}")

# Create new collection
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=1536,  # OpenAI embedding size
        distance=Distance.COSINE
    )
)

print(f"✅ Created Qdrant collection: {collection_name}")
print(f"   URL: {os.getenv('QDRANT_URL')}")
print(f"   Collection: {collection_name}")

# List all collections
collections = client.get_collections()
print(f"\n📊 Available collections:")
for collection in collections.collections:
    print(f"   - {collection.name}")
```

Run it:

```bash
python initialize_qdrant.py
```

---

## ✅ Step 4: Update Backend to Use Qdrant

Update `backend/config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Vector Database
    VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "qdrant")
    
    if VECTOR_DB_TYPE == "qdrant":
        QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
        QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
        QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "linkedin_jobs")
    
    # LLM Provider
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")

settings = Settings()
```

---

## ✅ Step 5: Create Helper Class for Qdrant

Create `backend/utils/qdrant_helper.py`:

```python
import os
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import openai

class QdrantHelper:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "linkedin_jobs")
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        response = openai.Embedding.create(
            model="text-embedding-3-small",
            input=text
        )
        return response['data'][0]['embedding']
    
    def add_job(self, job_id: str, job_data: Dict, embedding: List[float]):
        """Add job to Qdrant"""
        point = PointStruct(
            id=hash(job_id) % (2**32),
            vector=embedding,
            payload=job_data
        )
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
    
    def search_similar_jobs(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar jobs"""
        query_embedding = self.embed_text(query)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        return [result.payload for result in results]
    
    def get_collection_info(self) -> Dict:
        """Get collection statistics"""
        return self.client.get_collection(self.collection_name)
```

---

## ✅ Step 6: Complete Setup Script

Create `setup_project.sh`:

```bash
#!/bin/bash

echo "🚀 LinkedIn Job Automation - Complete Setup"
echo "============================================"

# 1. Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
# Application Settings
APP_NAME=AutoAgentHire
APP_ENV=development
DEBUG=True

# LinkedIn
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Vector Database (Qdrant)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=linkedin_jobs
VECTOR_DB_TYPE=qdrant

# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
OPENAI_MODEL=gpt-4o

# GitHub
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
GITHUB_USERNAME=your_username

# Database
DATABASE_URL=sqlite:///./data/autoagenthire.db
EOF
    echo "✅ .env file created. Please update with your credentials!"
fi

# 2. Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# 3. Install Node dependencies
echo "📦 Installing Node dependencies..."
cd frontend/lovable && npm install && cd ../..

# 4. Initialize Qdrant
echo "🗄️  Initializing Qdrant vector database..."
python3 << 'PYTHON'
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
    
    client = QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY", "")
    )
    
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "linkedin_jobs")
    
    try:
        client.delete_collection(collection_name=collection_name)
        print(f"✅ Cleared existing collection: {collection_name}")
    except:
        pass
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )
    print(f"✅ Qdrant initialized successfully!")
    print(f"   URL: {os.getenv('QDRANT_URL')}")
    print(f"   Collection: {collection_name}")
except Exception as e:
    print(f"⚠️  Qdrant initialization failed: {e}")
    print("   Make sure Docker is running and Qdrant is accessible")
PYTHON

# 5. Create required directories
echo "📁 Creating required directories..."
mkdir -p data/logs data/resumes data/job_listings vector_db/data

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Update .env with your credentials"
echo "  2. Make sure Qdrant is running (docker run -p 6333:6333 qdrant/qdrant:latest)"
echo "  3. Run: ./quick_start.sh"
echo ""
```

Make it executable:

```bash
chmod +x setup_project.sh
./setup_project.sh
```

---

## ✅ Step 7: Run the Complete Project

```bash
# Start Qdrant (in separate terminal)
docker run -p 6333:6333 qdrant/qdrant:latest

# In main terminal, run:
chmod +x quick_start.sh
./quick_start.sh
```

---

## ✅ Step 8: Verify Everything is Working

Create `verify_setup.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Verifying Project Setup")
print("=" * 50)

# Check environment variables
checks = [
    ("LINKEDIN_EMAIL", os.getenv("LINKEDIN_EMAIL")),
    ("LINKEDIN_PASSWORD", "***" if os.getenv("LINKEDIN_PASSWORD") else None),
    ("OPENAI_API_KEY", "sk-..." if os.getenv("OPENAI_API_KEY") else None),
    ("GITHUB_TOKEN", "ghp_..." if os.getenv("GITHUB_TOKEN") else None),
    ("QDRANT_URL", os.getenv("QDRANT_URL")),
    ("VECTOR_DB_TYPE", os.getenv("VECTOR_DB_TYPE")),
]

print("\n📋 Configuration Check:")
for key, value in checks:
    status = "✅" if value else "❌"
    print(f"{status} {key}: {value}")

# Check Qdrant connection
try:
    from qdrant_client import QdrantClient
    client = QdrantClient(
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY", "")
    )
    collections = client.get_collections()
    print(f"\n✅ Qdrant Connection: OK")
    print(f"   Collections: {len(collections.collections)}")
except Exception as e:
    print(f"\n❌ Qdrant Connection Failed: {e}")

# Check OpenAI
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print(f"\n✅ OpenAI Configuration: OK")
except Exception as e:
    print(f"\n❌ OpenAI Configuration Failed: {e}")

print("\n" + "=" * 50)
print("✅ Setup verification complete!")
```

Run it:

```bash
python verify_setup.py
```

---

## 📊 Project Structure

```
LinkedIn-Job-Automation-with-AI/
├── backend/
│   ├── agents/
│   │   ├── autoagenthire_bot.py
│   │   └── ultimate_linkedin_bot.py
│   ├── utils/
│   │   └── qdrant_helper.py
│   ├── config.py
│   └── main.py
├── frontend/lovable/
│   ├── src/
│   └── package.json
├── vector_db/
│   └── data/          # Qdrant storage
├── data/
│   ├── logs/
│   ├── resumes/
│   └── job_listings/
├── .env               # Your configuration
├── setup_project.sh   # Run this first!
└── quick_start.sh     # Run this to start

```

---

## 🎯 Summary

✅ **Qdrant** - Vector database for job embeddings  
✅ **GitHub API Token** - For model access via GitHub  
✅ **GPT-4o** - Latest OpenAI model for cover letters  
✅ **Backend & Frontend** - Full project setup  

**Ready to apply to LinkedIn jobs with AI!** 🚀

