#!/usr/bin/env python3
"""
Quick test to verify system is running correctly
"""
import requests
import time

def test_backend():
    """Test if backend is responding"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is running and healthy")
            return True
        else:
            print(f"⚠️  Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not responding (connection refused)")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {str(e)}")
        return False

def test_frontend():
    """Test if frontend is responding"""
    try:
        response = requests.get("http://127.0.0.1:8080/", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend UI is running")
            return True
        else:
            print(f"⚠️  Frontend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not responding (connection refused)")
        return False
    except Exception as e:
        print(f"❌ Frontend test failed: {str(e)}")
        return False

def test_qdrant():
    """Test Qdrant connection"""
    try:
        from qdrant_client import QdrantClient
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        
        # Get collections
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        print(f"✅ Qdrant connected: {len(collections)} collections")
        print(f"   Collections: {', '.join(collection_names)}")
        return True
    except Exception as e:
        print(f"❌ Qdrant test failed: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🔍 System Status Check")
    print("=" * 60)
    print()
    
    backend_ok = test_backend()
    print()
    
    frontend_ok = test_frontend()
    print()
    
    qdrant_ok = test_qdrant()
    print()
    
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    if backend_ok and frontend_ok and qdrant_ok:
        print("✅ ALL SYSTEMS OPERATIONAL")
        print()
        print("🎯 Access Points:")
        print("   Backend API: http://127.0.0.1:8000")
        print("   API Docs: http://127.0.0.1:8000/docs")
        print("   Frontend UI: http://127.0.0.1:8080")
        print()
        print("🚀 Ready to run automation!")
    else:
        print("⚠️  Some systems need attention")
        if not backend_ok:
            print("   - Backend server")
        if not frontend_ok:
            print("   - Frontend server")
        if not qdrant_ok:
            print("   - Qdrant vector database")

if __name__ == "__main__":
    main()
