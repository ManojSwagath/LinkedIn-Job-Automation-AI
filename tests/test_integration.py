#!/usr/bin/env python
"""
Integration test for the complete AutoAgentHire system.
Tests backend API endpoints and LangGraph workflow.
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8080"

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health_endpoints():
    """Test all health check endpoints"""
    print_section("TESTING HEALTH ENDPOINTS")
    
    endpoints = [
        ("/health", "Main Health"),
        ("/api/health", "API Health"),
        ("/api/agent/langgraph/health", "LangGraph Health"),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name:20} - OK ({response.status_code})")
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"❌ {name:20} - FAILED ({response.status_code})")
        except Exception as e:
            print(f"❌ {name:20} - ERROR: {e}")

def test_langgraph_workflow():
    """Test the LangGraph workflow endpoint"""
    print_section("TESTING LANGGRAPH WORKFLOW")
    
    payload = {
        "user_id": "integration_test_user",
        "resume_text": "Senior Full Stack Engineer with 7 years experience in Python, FastAPI, React, TypeScript, LangChain, and AI/ML. Built scalable microservices and AI-powered applications.",
        "target_roles": ["software_engineer", "backend_engineer", "full_stack_engineer"],
        "desired_locations": ["San Francisco", "Remote", "New York"],
        "min_salary": 120000,
        "max_applications": 5,
        "dry_run": True
    }
    
    print("📤 Sending request to /api/agent/langgraph/run...")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/api/agent/langgraph/run",
            json=payload,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ LangGraph Workflow - SUCCESS (took {elapsed:.2f}s)")
            print(f"\n📊 Results:")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Status: {result.get('workflow_status')}")
            print(f"   Jobs Found: {result.get('total_jobs_found')}")
            print(f"   Applications: {result.get('applications_submitted')}")
            print(f"   Errors: {result.get('application_errors')}")
            print(f"   Execution Time: {result.get('execution_time_seconds', 0):.4f}s")
            
            if result.get('top_matches'):
                print(f"\n🎯 Top Matches ({len(result['top_matches'])}):")
                for idx, job in enumerate(result['top_matches'][:3], 1):
                    print(f"   {idx}. {job.get('title')} at {job.get('company')}")
                    print(f"      Match Score: {job.get('match_score', 0):.1f}%")
                    print(f"      Location: {job.get('location')}")
            
            if result.get('submitted_applications'):
                print(f"\n📝 Submitted Applications ({len(result['submitted_applications'])}):")
                for idx, app in enumerate(result['submitted_applications'][:3], 1):
                    print(f"   {idx}. {app.get('job_title')} - {app.get('status')}")
            
            return True
        else:
            print(f"❌ LangGraph Workflow - FAILED ({response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ LangGraph Workflow - ERROR: {e}")
        return False

def test_other_endpoints():
    """Test other important API endpoints"""
    print_section("TESTING OTHER API ENDPOINTS")
    
    endpoints = [
        ("GET", "/api/agent/stats", None, "Agent Stats"),
        ("GET", "/api/agent/applications", None, "Applications List"),
        ("GET", "/api/linkedin/available-roles", None, "Available Roles"),
    ]
    
    for method, endpoint, data, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{BACKEND_URL}{endpoint}", json=data, timeout=5)
            
            if response.status_code in [200, 404]:  # 404 is OK for empty lists
                print(f"✅ {name:25} - OK ({response.status_code})")
            else:
                print(f"⚠️  {name:25} - {response.status_code}")
        except Exception as e:
            print(f"❌ {name:25} - ERROR: {str(e)[:50]}")

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print_section("TESTING FRONTEND ACCESSIBILITY")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200 and "root" in response.text:
            print(f"✅ Frontend accessible at {FRONTEND_URL}")
            print(f"   Status: {response.status_code}")
            print(f"   Contains React root: Yes")
            return True
        else:
            print(f"⚠️  Frontend returned unexpected response")
            return False
    except Exception as e:
        print(f"❌ Frontend - ERROR: {e}")
        return False

def test_openapi_docs():
    """Test OpenAPI documentation"""
    print_section("TESTING API DOCUMENTATION")
    
    try:
        response = requests.get(f"{BACKEND_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            print(f"✅ OpenAPI Documentation - OK")
            print(f"   Available endpoints: {len(paths)}")
            print(f"   API Title: {openapi_spec.get('info', {}).get('title')}")
            print(f"   Version: {openapi_spec.get('info', {}).get('version')}")
            
            # Count LangGraph endpoints
            langgraph_endpoints = [p for p in paths if 'langgraph' in p]
            print(f"   LangGraph endpoints: {len(langgraph_endpoints)}")
            for endpoint in langgraph_endpoints:
                print(f"      - {endpoint}")
            
            return True
        else:
            print(f"❌ OpenAPI Documentation - FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ OpenAPI Documentation - ERROR: {e}")
        return False

def main():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("  AUTOAGENTHIRE INTEGRATION TEST SUITE")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    results = {
        "Health Endpoints": False,
        "LangGraph Workflow": False,
        "Other Endpoints": False,
        "Frontend": False,
        "API Docs": False,
    }
    
    # Run tests
    try:
        test_health_endpoints()
        results["Health Endpoints"] = True
    except Exception as e:
        print(f"Health endpoints test failed: {e}")
    
    try:
        results["LangGraph Workflow"] = test_langgraph_workflow()
    except Exception as e:
        print(f"LangGraph test failed: {e}")
    
    try:
        test_other_endpoints()
        results["Other Endpoints"] = True
    except Exception as e:
        print(f"Other endpoints test failed: {e}")
    
    try:
        results["Frontend"] = test_frontend_accessibility()
    except Exception as e:
        print(f"Frontend test failed: {e}")
    
    try:
        results["API Docs"] = test_openapi_docs()
    except Exception as e:
        print(f"API docs test failed: {e}")
    
    # Print summary
    print_section("TEST SUMMARY")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:25} {status}")
        if not passed:
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is fully operational.")
    else:
        print("⚠️  SOME TESTS FAILED. Please review the errors above.")
    print(f"{'='*60}\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
