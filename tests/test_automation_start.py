#!/usr/bin/env python3
"""
Test the automation start endpoint
Verifies that the Start Automation button works correctly
"""
import requests
import sys
import time

API_BASE = "http://localhost:8000"
FRONTEND_ORIGIN = "http://127.0.0.1:8080"

def test_automation_start():
    """Test starting the automation agent"""
    print("🤖 Testing Automation Start Endpoint")
    print("=" * 60)
    
    # Step 1: Check backend health
    print("\n1️⃣  Checking backend health...")
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
        else:
            print(f"   ❌ Backend returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend is unreachable: {e}")
        return False
    
    # Step 2: Test CORS preflight
    print("\n2️⃣  Testing CORS preflight...")
    response = requests.options(
        f"{API_BASE}/api/run-agent",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }
    )
    
    if response.status_code == 200:
        print(f"   ✅ CORS preflight passed")
        print(f"      Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
    else:
        print(f"   ❌ CORS preflight failed: {response.status_code}")
        return False
    
    # Step 3: Create test resume
    print("\n3️⃣  Creating test resume...")
    test_resume_content = """
John Doe
Senior Software Engineer
john.doe@example.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced Python developer with 5+ years building scalable web applications
and machine learning systems.

TECHNICAL SKILLS
- Languages: Python, JavaScript, SQL
- Frameworks: FastAPI, React, TensorFlow
- Tools: Docker, AWS, Git

EXPERIENCE
Senior Software Engineer | Tech Corp | 2020-Present
- Built ML-powered job matching system
- Led team of 5 engineers
- Improved system performance by 40%

EDUCATION
B.S. Computer Science | University of Tech | 2019
"""
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_resume_content)
        test_resume_path = f.name
    
    print(f"   ✅ Test resume created: {test_resume_path}")
    
    # Step 4: Start automation
    print("\n4️⃣  Starting automation agent...")
    try:
        with open(test_resume_path, 'rb') as f:
            files = {'file': ('test_resume.txt', f, 'text/plain')}
            data = {
                'keyword': 'Python developer',
                'location': 'Remote',
                'skills': 'python,machine learning,generative ai',
                'linkedin_email': 'test@example.com',
                'linkedin_password': 'testpassword123',
                'experience_level': 'Mid-level',
                'job_type': 'Full-time',
                'max_jobs': '5',
                'max_applications': '2',
                'similarity_threshold': '0.6',
                'auto_apply': 'false'
            }
            
            response = requests.post(
                f"{API_BASE}/api/run-agent",
                files=files,
                data=data,
                headers={'Origin': FRONTEND_ORIGIN},
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Agent started successfully")
            print(f"      Status: {result.get('status')}")
            print(f"      Message: {result.get('message')}")
        else:
            print(f"   ❌ Failed to start agent: {response.status_code}")
            print(f"      Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error starting agent: {e}")
        return False
    finally:
        # Clean up test file
        import os
        if os.path.exists(test_resume_path):
            os.unlink(test_resume_path)
    
    # Step 5: Check agent status
    print("\n5️⃣  Checking agent status...")
    time.sleep(1)  # Give it a moment to start
    
    try:
        response = requests.get(f"{API_BASE}/api/agent/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Agent status retrieved")
            print(f"      Status: {status.get('status')}")
            print(f"      Phase: {status.get('detail', {}).get('phase')}")
            
            # Show logs if available
            logs = status.get('detail', {}).get('logs', [])
            if logs:
                print(f"\n   📋 Recent logs:")
                for log in logs[-3:]:
                    print(f"      [{log['level']}] {log['message']}")
        else:
            print(f"   ⚠️  Could not get status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Error checking status: {e}")
    
    # Step 6: Stop agent
    print("\n6️⃣  Stopping agent...")
    try:
        response = requests.post(f"{API_BASE}/api/agent/stop", timeout=5)
        if response.status_code in [200, 400]:  # 400 is OK if already stopped
            print(f"   ✅ Stop command sent")
        else:
            print(f"   ⚠️  Stop returned: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Error stopping agent: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All automation tests passed!")
    print("\n💡 The 'Start Automation' button should now work in the UI")
    print(f"   Go to: {FRONTEND_ORIGIN}")
    print("=" * 60 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_automation_start()
    sys.exit(0 if success else 1)
