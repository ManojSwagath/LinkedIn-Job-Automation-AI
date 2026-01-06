#!/usr/bin/env python3
"""
Smoke test for resume upload endpoint
Tests both CORS preflight and actual upload functionality
"""
import requests
import sys
import os
from pathlib import Path

API_BASE = "http://localhost:8000"
FRONTEND_ORIGIN = "http://127.0.0.1:8080"

def test_cors_preflight():
    """Test CORS preflight request"""
    print("🔍 Testing CORS preflight...")
    
    response = requests.options(
        f"{API_BASE}/api/upload-resume",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }
    )
    
    if response.status_code == 200:
        print(f"✅ CORS preflight passed (200)")
        print(f"   Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
        print(f"   Allow-Methods: {response.headers.get('Access-Control-Allow-Methods')}")
        return True
    else:
        print(f"❌ CORS preflight failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_health():
    """Test backend health"""
    print("\n🏥 Testing backend health...")
    
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend is unreachable: {e}")
        return False

def create_test_resume():
    """Create a test resume file"""
    test_dir = Path("uploads/test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = test_dir / "test_resume.txt"
    test_file.write_text("""
John Doe
Software Engineer
john.doe@email.com | (555) 123-4567

EXPERIENCE
Senior Software Engineer at Tech Corp (2020-Present)
- Developed scalable web applications using Python and React
- Led team of 5 engineers on cloud migration project
- Improved system performance by 40%

SKILLS
Python, JavaScript, React, FastAPI, Docker, AWS, PostgreSQL

EDUCATION
Bachelor of Science in Computer Science
University of Technology, 2019
""")
    
    return test_file

def test_upload():
    """Test actual resume upload"""
    print("\n📤 Testing resume upload...")
    
    # Create test resume
    test_file = create_test_resume()
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test_resume.txt', f, 'text/plain')}
            data = {'user_email': 'test@example.com'}
            
            response = requests.post(
                f"{API_BASE}/api/upload-resume",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful")
            print(f"   Filename: {result.get('filename')}")
            print(f"   Text length: {result.get('text_length')}")
            print(f"   Skills found: {result.get('metadata', {}).get('skills_count', 0)}")
            
            # Clean up uploaded file
            if 'file_path' in result and os.path.exists(result['file_path']):
                os.remove(result['file_path'])
                print(f"   Cleaned up test file")
            
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()

def test_upload_with_cors():
    """Test upload with CORS headers (simulating browser)"""
    print("\n🌐 Testing upload with CORS headers...")
    
    test_file = create_test_resume()
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test_resume.txt', f, 'text/plain')}
            data = {'user_email': 'test@example.com'}
            headers = {'Origin': FRONTEND_ORIGIN}
            
            response = requests.post(
                f"{API_BASE}/api/upload-resume",
                files=files,
                data=data,
                headers=headers,
                timeout=30
            )
        
        if response.status_code == 200:
            allow_origin = response.headers.get('Access-Control-Allow-Origin')
            print(f"✅ Upload with CORS successful")
            print(f"   CORS header: {allow_origin}")
            
            result = response.json()
            if 'file_path' in result and os.path.exists(result['file_path']):
                os.remove(result['file_path'])
            
            return True
        else:
            print(f"❌ Upload with CORS failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload with CORS error: {e}")
        return False
    finally:
        if test_file.exists():
            test_file.unlink()

def main():
    """Run all smoke tests"""
    print("🧪 Resume Upload Endpoint Smoke Tests")
    print("=" * 50)
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health()))
    
    # Test 2: CORS preflight
    results.append(("CORS Preflight", test_cors_preflight()))
    
    # Test 3: Basic upload
    results.append(("Basic Upload", test_upload()))
    
    # Test 4: Upload with CORS
    results.append(("Upload with CORS", test_upload_with_cors()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
