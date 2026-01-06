#!/usr/bin/env python3
"""
Quick Demo: Run AutoAgentHire Automation
This script runs a quick demonstration of the automation system
"""

import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

print("="*70)
print("  🚀 AutoAgentHire - Quick Automation Demo")
print("="*70)
print()

# Step 1: Health check
print("Step 1: Checking system health...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print("✅ Backend is healthy!")
    else:
        print("❌ Backend health check failed")
        sys.exit(1)
except Exception as e:
    print(f"❌ Cannot connect to backend: {e}")
    print("   Please ensure servers are running: ./start_servers.sh")
    sys.exit(1)

print()

# Step 2: Check for resume
print("Step 2: Checking for uploaded resume...")
import os
from pathlib import Path

resume_dir = Path("uploads/resumes")
if resume_dir.exists():
    resumes = list(resume_dir.glob("*.pdf"))
    if resumes:
        resume_path = resumes[0]
        print(f"✅ Found resume: {resume_path.name}")
    else:
        print("❌ No resumes found in uploads/resumes/")
        print("   Please upload a resume via: http://127.0.0.1:8080/settings")
        sys.exit(1)
else:
    print("❌ Resume directory not found")
    sys.exit(1)

print()

# Step 3: Configuration
print("Step 3: Automation Configuration")
print("-" * 70)

# IMPORTANT: Update these with your actual LinkedIn credentials
LINKEDIN_EMAIL = input("Enter your LinkedIn email: ").strip()
LINKEDIN_PASSWORD = input("Enter your LinkedIn password: ").strip()

if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
    print("❌ Credentials are required!")
    sys.exit(1)

print()
JOB_TITLE = input("Job title to search (e.g., 'Software Engineer'): ").strip() or "Software Engineer"
LOCATION = input("Location (e.g., 'Remote' or 'San Francisco'): ").strip() or "Remote"
MAX_JOBS = input("Max jobs to analyze (default: 10): ").strip() or "10"
MAX_APPLICATIONS = input("Max applications to submit (default: 5): ").strip() or "5"

print()
print("Configuration:")
print(f"  Email: {LINKEDIN_EMAIL}")
print(f"  Job Title: {JOB_TITLE}")
print(f"  Location: {LOCATION}")
print(f"  Max Jobs: {MAX_JOBS}")
print(f"  Max Applications: {MAX_APPLICATIONS}")
print(f"  Resume: {resume_path.name}")
print()

confirm = input("Start automation? (yes/no): ").strip().lower()
if confirm not in ['yes', 'y']:
    print("❌ Automation cancelled")
    sys.exit(0)

# Step 4: Start automation
print()
print("Step 4: Starting automation...")
print("-" * 70)

config = {
    "email": LINKEDIN_EMAIL,
    "password": LINKEDIN_PASSWORD,
    "job_title": JOB_TITLE,
    "location": LOCATION,
    "skills": "Python, JavaScript, React, FastAPI, Machine Learning, AI",
    "experience_level": "Entry Level",
    "job_type": "Full-time",
    "max_jobs": int(MAX_JOBS),
    "max_applications": int(MAX_APPLICATIONS),
    "match_threshold": 70,
    "resume_path": str(resume_path)
}

try:
    response = requests.post(
        f"{BASE_URL}/api/autoagenthire/start",
        json=config,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result.get('message', 'Automation started')}")
    else:
        print(f"❌ Failed to start: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print()

# Step 5: Monitor
print("Step 5: Monitoring automation...")
print("-" * 70)
print("Press Ctrl+C to stop monitoring (automation will continue)")
print()

try:
    last_status = None
    checks = 0
    
    while checks < 600:  # 10 minutes max
        try:
            response = requests.get(f"{BASE_URL}/api/autoagenthire/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                current_status = status.get('status', 'unknown')
                
                if current_status != last_status:
                    timestamp = time.strftime('%H:%M:%S')
                    print(f"[{timestamp}] Status: {current_status}")
                    
                    if 'current_step' in status:
                        print(f"           Step: {status['current_step']}")
                    if 'message' in status:
                        print(f"           {status['message']}")
                    
                    last_status = current_status
                
                if current_status in ['completed', 'failed', 'idle']:
                    print(f"\n✅ Automation finished!")
                    break
            
            checks += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"⚠️  Status check error: {e}")
            time.sleep(2)
    
except KeyboardInterrupt:
    print("\n⚠️  Monitoring stopped (automation continues in background)")

print()

# Step 6: Get results
print("Step 6: Fetching results...")
print("-" * 70)

time.sleep(2)

try:
    response = requests.get(f"{BASE_URL}/api/applications", timeout=10)
    if response.status_code == 200:
        result = response.json()
        apps = result.get('applications', [])
        
        if apps:
            print(f"\n✅ Found {len(apps)} application(s)!\n")
            
            for i, app in enumerate(apps, 1):
                status_icon = "✅" if app.get('status') == 'applied' else "⏭️" if app.get('status') == 'skipped' else "❌"
                print(f"{status_icon} Application #{i}:")
                print(f"   Title: {app.get('title', 'N/A')}")
                print(f"   Company: {app.get('company', 'N/A')}")
                print(f"   Status: {app.get('status', 'N/A').upper()}")
                print(f"   Match: {app.get('match_score', 0)}%")
                print(f"   URL: {app.get('url', 'N/A')[:60]}...")
                if app.get('reason'):
                    print(f"   Reason: {app.get('reason')}")
                print()
        else:
            print("⚠️  No applications recorded yet")
            print("   Check the automation logs for details")
    else:
        print(f"❌ Could not fetch applications: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("="*70)
print("  ✅ Demo Complete!")
print("="*70)
print()
print("📊 View detailed results at:")
print("   http://127.0.0.1:8080/applications")
print()
print("📚 API Documentation:")
print("   http://127.0.0.1:8000/docs")
print()
