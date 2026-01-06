#!/usr/bin/env python3
"""
End-to-end validation script for LinkedIn Job Automation project
Tests all critical endpoints and features
"""
import requests
import sys
import time
from typing import Dict, List, Tuple

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://127.0.0.1:8080"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.BLUE}{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}{Colors.END}\n")

def test_endpoint(name: str, url: str, method: str = "GET", **kwargs) -> bool:
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5, **kwargs)
        elif method == "POST":
            response = requests.post(url, timeout=10, **kwargs)
        elif method == "OPTIONS":
            response = requests.options(url, timeout=5, **kwargs)
        else:
            print(f"{Colors.RED}❌ {name}: Unknown method{Colors.END}")
            return False
        
        if response.status_code in [200, 201]:
            print(f"{Colors.GREEN}✅ {name}: {response.status_code}{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ {name}: {response.status_code}{Colors.END}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ {name}: {str(e)}{Colors.END}")
        return False

def main():
    """Run all validation tests"""
    print(f"{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   LinkedIn Job Automation - Complete Validation Suite    ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    all_results: List[Tuple[str, bool]] = []
    
    # ============================================================
    # 1. Infrastructure Tests
    # ============================================================
    print_section("🏗️  Infrastructure Tests")
    
    all_results.append((
        "Backend Health",
        test_endpoint("Backend Health", f"{API_BASE}/api/health")
    ))
    
    all_results.append((
        "Frontend Availability",
        test_endpoint("Frontend Availability", FRONTEND_BASE)
    ))
    
    # ============================================================
    # 2. CORS Configuration Tests
    # ============================================================
    print_section("🌐 CORS Configuration Tests")
    
    all_results.append((
        "CORS Preflight - Upload Resume",
        test_endpoint(
            "CORS Preflight - Upload Resume",
            f"{API_BASE}/api/upload-resume",
            method="OPTIONS",
            headers={
                "Origin": FRONTEND_BASE,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
    ))
    
    all_results.append((
        "CORS Preflight - Run Agent",
        test_endpoint(
            "CORS Preflight - Run Agent",
            f"{API_BASE}/api/run-agent",
            method="OPTIONS",
            headers={
                "Origin": FRONTEND_BASE,
                "Access-Control-Request-Method": "POST"
            }
        )
    ))
    
    # ============================================================
    # 3. Agent Control Endpoints
    # ============================================================
    print_section("🤖 Agent Control Endpoints")
    
    all_results.append((
        "Agent Status",
        test_endpoint("Agent Status", f"{API_BASE}/api/agent/status")
    ))
    
    # Test run agent with multipart form data
    print("Testing Run Agent (multipart)...")
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test Resume\nSoftware Engineer\nPython, JavaScript")
            temp_file = f.name
        
        with open(temp_file, 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            data = {
                'keyword': 'software engineer',
                'location': 'Remote',
                'skills': 'python',
                'linkedin_email': 'test@example.com',
                'linkedin_password': 'test123',
                'max_applications': '1',
                'auto_apply': 'false'
            }
            response = requests.post(f"{API_BASE}/api/run-agent", files=files, data=data, timeout=10)
        
        import os
        os.unlink(temp_file)
        
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Run Agent Endpoint: 200{Colors.END}")
            all_results.append(("Run Agent Endpoint", True))
        else:
            print(f"{Colors.RED}❌ Run Agent Endpoint: {response.status_code}{Colors.END}")
            all_results.append(("Run Agent Endpoint", False))
    except Exception as e:
        print(f"{Colors.RED}❌ Run Agent Endpoint: {str(e)}{Colors.END}")
        all_results.append(("Run Agent Endpoint", False))
    
    time.sleep(1)  # Give agent time to start
    
    # Test pause (might fail if agent not running, that's OK)
    pause_resp = requests.post(f"{API_BASE}/api/agent/pause", timeout=5)
    pause_ok = pause_resp.status_code in [200, 400]  # 400 is OK if not running
    if pause_ok:
        print(f"{Colors.GREEN}✅ Pause Agent: {pause_resp.status_code} (OK){Colors.END}")
    else:
        print(f"{Colors.RED}❌ Pause Agent: {pause_resp.status_code}{Colors.END}")
    all_results.append(("Pause Agent", pause_ok))
    
    # Test resume (might fail if not paused, that's OK)
    resume_resp = requests.post(f"{API_BASE}/api/agent/resume", timeout=5)
    resume_ok = resume_resp.status_code in [200, 400]  # 400 is OK if not paused
    if resume_ok:
        print(f"{Colors.GREEN}✅ Resume Agent: {resume_resp.status_code} (OK){Colors.END}")
    else:
        print(f"{Colors.RED}❌ Resume Agent: {resume_resp.status_code}{Colors.END}")
    all_results.append(("Resume Agent", resume_ok))
    
    # Test stop
    stop_resp = requests.post(f"{API_BASE}/api/agent/stop", timeout=5)
    stop_ok = stop_resp.status_code in [200, 400]  # 400 is OK if not running
    if stop_ok:
        print(f"{Colors.GREEN}✅ Stop Agent: {stop_resp.status_code} (OK){Colors.END}")
    else:
        print(f"{Colors.RED}❌ Stop Agent: {stop_resp.status_code}{Colors.END}")
    all_results.append(("Stop Agent", stop_ok))
    
    # ============================================================
    # 4. Application History
    # ============================================================
    print_section("📋 Application History")
    
    all_results.append((
        "Get Applications",
        test_endpoint("Get Applications", f"{API_BASE}/api/applications")
    ))
    
    # ============================================================
    # 5. Job Search
    # ============================================================
    print_section("🔍 Job Search")
    
    all_results.append((
        "Search Jobs",
        test_endpoint(
            "Search Jobs",
            f"{API_BASE}/api/jobs/search?keywords=python%20developer&location=remote&max_results=5",
            method="GET"
        )
    ))
    
    # ============================================================
    # Summary
    # ============================================================
    print_section("📊 Test Summary")
    
    passed = sum(1 for _, result in all_results if result)
    total = len(all_results)
    
    for test_name, result in all_results:
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"   {status} - {test_name}")
    
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 All tests passed! ({passed}/{total}){Colors.END}")
        print(f"\n{Colors.GREEN}✨ Project is ready to use!{Colors.END}")
        print(f"\n{Colors.BLUE}Next steps:{Colors.END}")
        print(f"   1. Open {FRONTEND_BASE} in your browser")
        print(f"   2. Complete the onboarding process")
        print(f"   3. Upload your resume")
        print(f"   4. Configure LinkedIn credentials")
        print(f"   5. Start the automation agent")
        exit_code = 0
    else:
        failed = total - passed
        print(f"{Colors.YELLOW}⚠️  Some tests failed ({passed}/{total} passed, {failed} failed){Colors.END}")
        print(f"\n{Colors.YELLOW}Please check the failed endpoints above.{Colors.END}")
        exit_code = 1
    
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}\n")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
