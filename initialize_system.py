#!/usr/bin/env python3
"""
System Initialization Script
Initializes Qdrant vector database, checks all services, and prepares the system
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def initialize_qdrant():
    """Initialize Qdrant vector database"""
    print("\n📊 Initializing Qdrant Vector Database...")
    print("-" * 60)
    
    qdrant_url = os.getenv('QDRANT_URL', '')
    qdrant_key = os.getenv('QDRANT_API_KEY', '')
    
    if not qdrant_url or not qdrant_key:
        print("❌ Qdrant configuration missing in .env file")
        print("   Please add:")
        print("   QDRANT_URL=your_qdrant_url")
        print("   QDRANT_API_KEY=your_qdrant_api_key")
        return False
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        
        # Connect to Qdrant
        client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_key,
        )
        
        print(f"✅ Connected to Qdrant: {qdrant_url[:50]}...")
        
        # Create collections
        collections_to_create = [
            ("resumes", 384, "Resume embeddings collection"),
            ("jobs", 384, "Job listings embeddings collection"),
            ("applications", 384, "Application history embeddings collection"),
        ]
        
        existing_collections = [col.name for col in client.get_collections().collections]
        
        for collection_name, vector_size, description in collections_to_create:
            if collection_name not in existing_collections:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created collection: {collection_name} ({description})")
            else:
                print(f"✓  Collection exists: {collection_name}")
        
        # Get collection info
        for collection_name, _, _ in collections_to_create:
            try:
                info = client.get_collection(collection_name)
                # Check if collection has points_count attribute
                points = getattr(info, 'points_count', 0)
                print(f"   └─ {collection_name}: {points} points")
            except Exception as e:
                print(f"   └─ {collection_name}: Created successfully")
        
        print("✅ Qdrant initialization complete!")
        return True
        
    except ImportError:
        print("❌ qdrant-client not installed")
        print("   Install with: pip install qdrant-client")
        return False
    except Exception as e:
        print(f"❌ Qdrant initialization failed: {str(e)}")
        return False

async def check_github_api():
    """Check GitHub API configuration for GPT-4o"""
    print("\n🔑 Checking GitHub API Configuration...")
    print("-" * 60)
    
    github_key = os.getenv('GITHUB_API_KEY', '')
    
    if not github_key or len(github_key) < 10:
        print("⚠️  GitHub API key not configured")
        print("   To use GPT-4o via GitHub Models:")
        print("   1. Go to: https://github.com/settings/tokens")
        print("   2. Create a personal access token")
        print("   3. Add to .env: GITHUB_API_KEY=your_token")
        print("   Or use Gemini API (already configured)")
        return False
    
    print(f"✅ GitHub API Key: {github_key[:20]}...")
    
    # Test if we can import openai (for GitHub models)
    try:
        import openai
        print("✅ OpenAI SDK installed (for GitHub Models)")
        return True
    except ImportError:
        print("⚠️  OpenAI SDK not installed")
        print("   Install with: pip install openai")
        return False

async def check_gemini_api():
    """Check Google Gemini API configuration"""
    print("\n🤖 Checking Gemini API Configuration...")
    print("-" * 60)
    
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    
    if not gemini_key or len(gemini_key) < 10:
        print("⚠️  Gemini API key not configured")
        return False
    
    print(f"✅ Gemini API Key: {gemini_key[:20]}...")
    
    try:
        import google.generativeai as genai
        print("✅ Gemini SDK installed")
        # Note: Configuration will be done when actually using the API
        return True
    except ImportError:
        print("⚠️  Google Generative AI SDK not installed")
        print("   Install with: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"⚠️  Gemini import error: {str(e)}")
        return False

async def check_database():
    """Check SQLite database"""
    print("\n💾 Checking Database...")
    print("-" * 60)
    
    db_path = Path("data/autoagenthire.db")
    
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"✅ Database exists: {db_path} ({size_mb:.2f} MB)")
        return True
    else:
        print(f"⚠️  Database will be created on first run: {db_path}")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return True

async def check_resume_directory():
    """Check resume storage directory"""
    print("\n📄 Checking Resume Directory...")
    print("-" * 60)
    
    resume_dir = Path("data/resumes")
    resume_dir.mkdir(parents=True, exist_ok=True)
    
    resumes = list(resume_dir.glob("*.pdf"))
    
    if resumes:
        print(f"✅ Resume directory: {resume_dir}")
        print(f"   Found {len(resumes)} resume(s):")
        for resume in resumes[:5]:
            print(f"   - {resume.name}")
        if len(resumes) > 5:
            print(f"   ... and {len(resumes) - 5} more")
    else:
        print(f"⚠️  No resumes found in: {resume_dir}")
        print("   Please add your resume PDF to this directory")
    
    return True

async def check_browser_profile():
    """Check browser profile directory"""
    print("\n🌐 Checking Browser Profile...")
    print("-" * 60)
    
    profile_dir = Path("browser_profile")
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Browser profile directory: {profile_dir}")
    
    # Check for session data
    if (profile_dir / "Default").exists():
        print("   ✓ Browser session data exists (LinkedIn login may be saved)")
    else:
        print("   ℹ️  No browser session (will need to login on first run)")
    
    return True

async def initialize_system():
    """Run full system initialization"""
    print("\n" + "=" * 60)
    print("🚀 LinkedIn Job Automation - System Initialization")
    print("=" * 60)
    
    results = {
        'qdrant': await initialize_qdrant(),
        'github_api': await check_github_api(),
        'gemini_api': await check_gemini_api(),
        'database': await check_database(),
        'resumes': await check_resume_directory(),
        'browser': await check_browser_profile(),
    }
    
    print("\n" + "=" * 60)
    print("📊 Initialization Summary")
    print("=" * 60)
    
    for component, status in results.items():
        status_icon = "✅" if status else "⚠️ "
        print(f"{status_icon} {component.replace('_', ' ').title()}: {'Ready' if status else 'Needs attention'}")
    
    all_ready = all(results.values())
    
    if all_ready:
        print("\n✅ All systems ready!")
        print("\n🚀 Next steps:")
        print("   1. Start backend: python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        print("   2. Start frontend: cd frontend/lovable && npm run dev")
        print("   3. Access UI: http://127.0.0.1:8080")
        print("   4. Run automation: python3 final_automation.py")
    else:
        print("\n⚠️  Some components need attention")
        print("   Review the warnings above and configure missing components")
    
    return all_ready

if __name__ == "__main__":
    try:
        asyncio.run(initialize_system())
    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization cancelled")
    except Exception as e:
        print(f"\n❌ Initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
