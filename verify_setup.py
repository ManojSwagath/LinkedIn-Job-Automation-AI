import os
from dotenv import load_dotenv
import sys

load_dotenv()

print("\n" + "=" * 60)
print("🔍 VERIFYING PROJECT SETUP")
print("=" * 60 + "\n")

# 1. Check environment variables
print("📋 Environment Configuration:")
print("-" * 60)

checks = {
    "LinkedIn Email": os.getenv("LINKEDIN_EMAIL"),
    "LinkedIn Password": "***" if os.getenv("LINKEDIN_PASSWORD") else None,
    "OpenAI API Key": "sk-..." if os.getenv("OPENAI_API_KEY") else None,
    "OpenAI Model": os.getenv("OPENAI_MODEL", "Not set"),
    "GitHub Token": "ghp_..." if os.getenv("GITHUB_TOKEN") else None,
    "Qdrant URL": os.getenv("QDRANT_URL", "Not set"),
    "Vector DB Type": os.getenv("VECTOR_DB_TYPE", "Not set"),
    "Database URL": os.getenv("DATABASE_URL", "Not set"),
}

missing = []
for key, value in checks.items():
    if value:
        status = "✅"
    else:
        status = "❌"
        missing.append(key)
    print(f"{status} {key:.<40} {value}")

# 2. Check Qdrant connection
print("\n🗄️  Vector Database (Qdrant):")
print("-" * 60)

try:
    from qdrant_client import QdrantClient
    
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
    
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key if qdrant_api_key else None
    )
    
    collections = client.get_collections()
    print(f"✅ Connection to Qdrant............. OK")
    print(f"   URL: {qdrant_url}")
    print(f"   Collections: {len(collections.collections)}")
    
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "linkedin_jobs")
    try:
        info = client.get_collection(collection_name)
        print(f"   Target Collection: {collection_name} ✅")
        print(f"   Points in collection: {info.points_count}")
    except:
        print(f"   Target Collection: {collection_name} ⚠️ (not created yet)")
        
except Exception as e:
    print(f"❌ Qdrant Connection.............. FAILED")
    print(f"   Error: {str(e)}")
    print(f"\n   💡 Fix: Start Qdrant with Docker:")
    print(f"      docker run -p 6333:6333 qdrant/qdrant:latest")

# 3. Check LLM providers
print("\n🤖 LLM Providers:")
print("-" * 60)

# OpenAI
try:
    import openai
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        openai.api_key = api_key
        print(f"✅ OpenAI Configuration............ OK")
        print(f"   Model: {os.getenv('OPENAI_MODEL', 'gpt-4o')}")
    else:
        print(f"❌ OpenAI Configuration............ MISSING API KEY")
except Exception as e:
    print(f"❌ OpenAI Configuration............ FAILED: {e}")

# Gemini
try:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ Gemini Configuration............ OK")
    else:
        print(f"⚠️ Gemini Configuration............ NOT CONFIGURED")
except:
    print(f"⚠️ Gemini Configuration............ NOT AVAILABLE")

# 4. Check GitHub integration
print("\n📱 GitHub Integration:")
print("-" * 60)

github_token = os.getenv("GITHUB_TOKEN")
if github_token and github_token.startswith("ghp_"):
    print(f"✅ GitHub Token.................... OK")
    print(f"   Token: {github_token[:20]}...")
else:
    print(f"❌ GitHub Token.................... MISSING OR INVALID")
    print(f"   Expected format: ghp_...")

# 5. Check database
print("\n💾 Database:")
print("-" * 60)

db_url = os.getenv("DATABASE_URL", "Not set")
print(f"✅ Database URL.................... {db_url}")

# 6. Check file structure
print("\n📁 Project Structure:")
print("-" * 60)

required_dirs = [
    "backend",
    "frontend/lovable",
    "data",
    "data/logs",
    "data/resumes",
    "data/job_listings",
]

for dir_path in required_dirs:
    if os.path.exists(dir_path):
        print(f"✅ {dir_path:.<40} EXISTS")
    else:
        print(f"❌ {dir_path:.<40} MISSING")

# 7. Summary
print("\n" + "=" * 60)
print("📊 VERIFICATION SUMMARY")
print("=" * 60)

if missing:
    print(f"\n⚠️  Missing Configuration ({len(missing)}):")
    for item in missing:
        print(f"   - {item}")
    print(f"\n💡 Update .env file with these credentials:")
    print(f"   nano .env")
else:
    print(f"\n✅ All required configurations are set!")

print("\n🚀 Ready to start?")
print("   Run: ./quick_start.sh")
print("\n" + "=" * 60 + "\n")
