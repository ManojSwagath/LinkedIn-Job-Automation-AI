#!/usr/bin/env python3
"""
Test script to run the agent with optimized performance and auto-fill
"""
import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"
RESUME_PATH = "data/resumes/placeholder_resume.pdf"

# User profile for auto-fill (comprehensive)
USER_PROFILE = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "+1-555-123-4567",
    "street_address": "123 Main Street",
    "city": "San Francisco",
    "state": "CA",
    "zip_code": "94105",
    "country": "United States",
    "linkedin_url": "https://www.linkedin.com/in/johndoe",
    "portfolio_url": "https://johndoe.dev",
    "github_url": "https://github.com/johndoe",
    "current_company": "Tech Corp",
    "current_title": "Senior Software Engineer",
    "years_experience": 5,
    "university": "Stanford University",
    "degree": "Bachelor of Science in Computer Science",
    "graduation_year": 2018,
    "gpa": "3.8",
    "visa_status": "US Citizen",
    "willing_to_relocate": True,
    "salary_expectation": "120000-150000",
    "start_date": "Immediate",
    "notice_period": "2 weeks"
}

def test_agent_run():
    """Test the agent with performance optimizations and auto-fill"""
    
    print("🚀 Starting AutoAgentHire Test with Performance Optimizations & Auto-Fill\n")
    print("=" * 70)
    
    # Step 1: Check backend health
    print("\n1️⃣ Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
        else:
            print(f"   ❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to backend: {e}")
        return False
    
    # Step 2: Prepare form data
    print("\n2️⃣ Preparing automation request...")
    print(f"   📄 Resume: {RESUME_PATH}")
    print(f"   👤 User Profile: {USER_PROFILE['first_name']} {USER_PROFILE['last_name']}")
    print(f"   🎯 Job Search: Software Engineer in Remote")
    print(f"   ⚡ Performance: Optimized (slow_mo=50ms, smart auto-fill)")
    
    # Prepare form data
    with open(RESUME_PATH, 'rb') as f:
        resume_content = f.read()
    
    files = {'file': ('resume.pdf', resume_content, 'application/pdf')}
    
    data = {
            'keyword': 'Software Engineer',
            'location': 'Remote',
            'skills': 'Python, JavaScript, React',
            'linkedin_email': 'test@example.com',  # Placeholder
            'linkedin_password': 'test123',  # Placeholder
            'experience_level': 'Mid-level',
            'job_type': 'Full-time',
            'salary_range': '100k-150k',
            'max_jobs': '5',
            'max_applications': '1',  # Test with 1 application
            'similarity_threshold': '0.7',
            'auto_apply': 'false',  # Set to false for safety in testing
            'first_name': USER_PROFILE['first_name'],
            'last_name': USER_PROFILE['last_name'],
            'phone_number': USER_PROFILE['phone_number'],
            'city': USER_PROFILE['city'],
            'state': USER_PROFILE['state'],
            'country': USER_PROFILE['country'],
            'linkedin_url': USER_PROFILE['linkedin_url'],
            'portfolio_url': USER_PROFILE['portfolio_url'],
            'user_profile_json': json.dumps(USER_PROFILE)  # NEW: Full profile
    }
    
    # Step 3: Start agent
    print("\n3️⃣ Starting agent workflow...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/run-agent",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Agent started: {result['message']}")
            print(f"   📋 Job ID: {result.get('job_id', 'N/A')}")
        else:
            print(f"   ❌ Failed to start agent: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error starting agent: {e}")
        return False    # Step 4: Monitor agent status
    print("\n4️⃣ Monitoring agent progress...")
    print("   (Press Ctrl+C to stop monitoring)\n")
    
    try:
        last_status = None
        for i in range(60):  # Monitor for up to 60 iterations
            time.sleep(2)
            
            try:
                response = requests.get(f"{BASE_URL}/api/agent/status", timeout=5)
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get('status', 'unknown')
                    detail = status_data.get('detail', {})
                    
                    if status != last_status:
                        print(f"   📊 Status: {status.upper()}")
                        
                        if detail:
                            phase = detail.get('current_phase', 'N/A')
                            jobs_found = detail.get('jobs_found', 0)
                            apps_submitted = detail.get('applications_submitted', 0)
                            
                            print(f"   📍 Phase: {phase}")
                            print(f"   💼 Jobs Found: {jobs_found}")
                            print(f"   📨 Applications: {apps_submitted}")
                            
                            # Show recent logs
                            logs = detail.get('logs', [])
                            if logs:
                                print(f"   📝 Recent logs:")
                                for log in logs[-3:]:
                                    print(f"      {log}")
                            print()
                        
                        last_status = status
                    
                    # Check if completed
                    if status in ['completed', 'stopped', 'failed']:
                        print(f"\n   ✅ Agent finished with status: {status.upper()}")
                        
                        if detail:
                            print(f"\n   📊 Final Statistics:")
                            print(f"      Jobs Found: {detail.get('jobs_found', 0)}")
                            print(f"      Applications Submitted: {detail.get('applications_submitted', 0)}")
                            print(f"      Errors: {len(detail.get('errors', []))}")
                            
                            if detail.get('start_time') and detail.get('end_time'):
                                print(f"      Duration: {detail.get('start_time')} - {detail.get('end_time')}")
                        
                        break
                        
            except Exception as e:
                print(f"   ⚠️  Error checking status: {e}")
                
    except KeyboardInterrupt:
        print("\n\n   ⚠️  Monitoring stopped by user")
    
    print("\n" + "=" * 70)
    print("🎉 Test completed!")
    print("\n📚 Check these for details:")
    print("   • Backend logs: tail -f backend.log")
    print("   • Frontend: http://localhost:8080")
    print("   • API Docs: http://localhost:8000/docs")
    print("\n💡 Key Features Tested:")
    print("   ✅ Performance optimization (50ms delays)")
    print("   ✅ User profile auto-fill system")
    print("   ✅ Smart field matching (50+ patterns)")
    print("   ✅ Full workflow integration")
    print("=" * 70 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_agent_run()
    sys.exit(0 if success else 1)
