#!/usr/bin/env python3
"""
Complete AutoAgentHire Automation Test Script
This script demonstrates the full end-to-end automation workflow
"""

import requests
import json
import time
from pathlib import Path


def ensure_placeholder_resume() -> Path:
    """Ensure there is at least one PDF in data/resumes/.

    This is just for automated smoke-testing the pipeline end-to-end without requiring
    manual UI upload. The backend may still require a real resume for best matching.
    """
    data_dir = Path("data/resumes")
    data_dir.mkdir(parents=True, exist_ok=True)
    placeholder = data_dir / "placeholder_resume.pdf"
    if placeholder.exists():
        return placeholder

    # Minimal valid-ish PDF content so parsers don't instantly crash on empty file.
    pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj<<>>endobj\n"
        b"2 0 obj<< /Length 44 >>stream\n"
        b"BT /F1 12 Tf 72 720 Td (Placeholder Resume) Tj ET\n"
        b"endstream endobj\n"
        b"3 0 obj<< /Type /Catalog /Pages 4 0 R >>endobj\n"
        b"4 0 obj<< /Type /Pages /Kids [5 0 R] /Count 1 >>endobj\n"
        b"5 0 obj<< /Type /Page /Parent 4 0 R /MediaBox [0 0 612 792] /Contents 2 0 R >>endobj\n"
        b"xref\n0 6\n0000000000 65535 f \n"
        b"trailer<< /Root 3 0 R /Size 6 >>\nstartxref\n0\n%%EOF\n"
    )
    placeholder.write_bytes(pdf_bytes)
    return placeholder

# Configuration
BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:8080"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_step(step, message):
    """Print a step with formatting"""
    print(f"[Step {step}] {message}")

def check_backend_health():
    """Check if backend is healthy"""
    print_header("CHECKING BACKEND HEALTH")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend is healthy!")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database')}")
            print(f"   Vector DB: {health_data.get('vector_db')}")
            return True
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def check_resume_uploaded():
    """Check if a resume is already uploaded"""
    print_header("CHECKING UPLOADED RESUMES")
    data_dir = Path("data/resumes")
    if data_dir.exists():
        resumes = list(data_dir.glob("*.pdf"))
        if resumes:
            print(f"✅ Found {len(resumes)} resume(s):")
            for resume in resumes:
                print(f"   - {resume.name}")
            return True, resumes[0]
        else:
            print("⚠️  No resumes found in data/resumes/")
            return False, None
    else:
        print("⚠️  Resume directory doesn't exist")
        return False, None

def upload_resume(file_path):
    """Upload a resume to the system"""
    print_header("UPLOADING RESUME")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/pdf')}
            response = requests.post(
                f"{BASE_URL}/api/autoagenthire/upload-resume",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Resume uploaded successfully!")
            print(f"   Filename: {result.get('filename')}")
            print(f"   Size: {result.get('size')} bytes")
            return True
        else:
            print(f"❌ Resume upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Resume upload error: {e}")
        return False

def start_automation(config):
    """Start the automation with given configuration"""
    print_header("STARTING AUTOMATION")
    
    print("Configuration:")
    print(f"   Job Title: {config['job_title']}")
    print(f"   Location: {config['location']}")
    print(f"   Max Jobs: {config['max_jobs']}")
    print(f"   Max Applications: {config['max_applications']}")
    print(f"   Match Threshold: {config['match_threshold']}%")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/autoagenthire/start",
            json=config,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Automation started successfully!")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Automation start failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Automation start error: {e}")
        return False

def monitor_automation():
    """Monitor automation progress"""
    print_header("MONITORING AUTOMATION PROGRESS")
    
    print("🔄 Monitoring automation (press Ctrl+C to stop monitoring)...")
    print()
    
    try:
        last_status = None
        check_count = 0
        max_checks = 300  # 5 minutes max monitoring
        
        while check_count < max_checks:
            try:
                response = requests.get(
                    f"{BASE_URL}/api/autoagenthire/status",
                    timeout=5
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    current_status = status_data.get('status', 'unknown')
                    
                    # Only print if status changed
                    if current_status != last_status:
                        print(f"[{time.strftime('%H:%M:%S')}] Status: {current_status}")
                        
                        # Print additional details if available
                        if 'current_step' in status_data:
                            print(f"   Current Step: {status_data['current_step']}")
                        if 'jobs_processed' in status_data:
                            print(f"   Jobs Processed: {status_data['jobs_processed']}")
                        if 'applications_submitted' in status_data:
                            print(f"   Applications: {status_data['applications_submitted']}")
                        
                        last_status = current_status
                    
                    # Check if automation is complete or failed
                    if current_status in ['completed', 'failed', 'stopped', 'idle']:
                        print(f"\n✅ Automation finished with status: {current_status}")
                        break
                
                check_count += 1
                time.sleep(1)  # Check every second
                
            except requests.exceptions.Timeout:
                print("⚠️  Status check timed out, retrying...")
                time.sleep(2)
            except Exception as e:
                print(f"⚠️  Status check error: {e}")
                time.sleep(2)
        
        if check_count >= max_checks:
            print("\n⚠️  Monitoring timeout reached (5 minutes)")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped by user")

def get_applications():
    """Get all submitted applications"""
    print_header("FETCHING APPLICATIONS")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/applications",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            applications = result.get('applications', [])
            
            if applications:
                print(f"✅ Found {len(applications)} application(s):\n")
                
                for i, app in enumerate(applications, 1):
                    print(f"Application #{i}:")
                    print(f"   Title: {app.get('title', 'N/A')}")
                    print(f"   Company: {app.get('company', 'N/A')}")
                    print(f"   Status: {app.get('status', 'N/A')}")
                    print(f"   Match Score: {app.get('match_score', 0)}%")
                    print(f"   URL: {app.get('url', 'N/A')}")
                    print(f"   Date: {app.get('applied_date', 'N/A')}")
                    
                    if app.get('reason'):
                        print(f"   Reason: {app.get('reason')}")
                    print()
                
                return applications
            else:
                print("⚠️  No applications found yet")
                return []
        else:
            print(f"❌ Failed to fetch applications: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching applications: {e}")
        return []

def print_summary(applications):
    """Print automation summary"""
    print_header("AUTOMATION SUMMARY")
    
    total = len(applications)
    applied = sum(1 for app in applications if app.get('status') == 'applied')
    skipped = sum(1 for app in applications if app.get('status') == 'skipped')
    failed = sum(1 for app in applications if app.get('status') == 'failed')
    
    print(f"📊 Total Jobs Processed: {total}")
    print(f"✅ Successfully Applied: {applied}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Failed: {failed}")
    
    if applied > 0:
        avg_score = sum(app.get('match_score', 0) for app in applications if app.get('status') == 'applied') / applied
        print(f"📈 Average Match Score: {avg_score:.1f}%")
    
    print(f"\n🌐 View applications at: {FRONTEND_URL}/applications")

def main():
    """Main automation test flow"""
    print_header("🚀 AUTOAGENTHIRE - COMPLETE AUTOMATION TEST")
    
    # Step 1: Check backend health
    print_step(1, "Checking backend health...")
    if not check_backend_health():
        print("\n❌ Backend is not healthy. Please start the backend server first.")
        print("   Run: ./start_servers.sh")
        return
    
    time.sleep(1)
    
    # Step 2: Check for resume
    print_step(2, "Checking for uploaded resume...")
    has_resume, resume_path = check_resume_uploaded()
    
    if not has_resume:
            print("\n⚠️  No resume found in data/resumes/. Creating a placeholder resume for testing...")
            resume_path = ensure_placeholder_resume()
            has_resume = True
    
    time.sleep(1)
    
    # Step 3: Prepare automation configuration
    print_step(3, "Preparing automation configuration...")
    
    # Default configuration (you can modify these)
    config = {
        "email": "your-linkedin-email@example.com",  # Replace with actual email
        "password": "your-password",  # Replace with actual password
        "job_title": "Software Engineer",
        "location": "Remote",
        "skills": "Python, FastAPI, React, TypeScript, AI, Machine Learning",
        "experience_level": "Entry Level",
        "job_type": "Full-time",
        "max_jobs": 10,
        "max_applications": 5,
        "match_threshold": 70,
        "resume_path": str(resume_path)
    }
    
    print("\n⚠️  IMPORTANT: Please update LinkedIn credentials in the config!")
    print("   Edit this script and replace 'your-linkedin-email@example.com' and 'your-password'")
    print("   Or use the web interface at: http://127.0.0.1:8080")
    print()
    
    # Check if credentials are still default
    if config['email'] == "your-linkedin-email@example.com":
        print("❌ Please configure LinkedIn credentials before running automation!")
        print("\n✅ System is ready. Configure credentials and try again.")
        print(f"\n🌐 Frontend: {FRONTEND_URL}")
        print(f"🔧 Backend: {BASE_URL}")
        print(f"📚 API Docs: {BASE_URL}/docs")
        return
    
    time.sleep(1)
    
    # Step 4: Start automation
    print_step(4, "Starting automation...")
    if not start_automation(config):
        print("\n❌ Failed to start automation")
        return
    
    time.sleep(2)
    
    # Step 5: Monitor progress
    print_step(5, "Monitoring automation progress...")
    monitor_automation()
    
    time.sleep(1)
    
    # Step 6: Fetch results
    print_step(6, "Fetching application results...")
    applications = get_applications()
    
    time.sleep(1)
    
    # Step 7: Show summary
    if applications:
        print_summary(applications)
    
    print("\n" + "="*60)
    print("✅ AUTOMATION TEST COMPLETED!")
    print("="*60)
    print(f"\n🌐 View detailed results at: {FRONTEND_URL}/applications")
    print(f"📚 API Documentation: {BASE_URL}/docs")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Automation test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
