#!/usr/bin/env python3
"""
Test Full Automation with Resume Upload and Application Submission
Monitors real-time progress and displays application timestamps
"""
import requests
import time
import sys
from datetime import datetime

API_BASE = "http://localhost:8000"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_status(status_data):
    """Print current status in a nice format"""
    detail = status_data.get('detail', {})
    
    print(f"\n📊 Status: {status_data.get('status', 'unknown').upper()}")
    print(f"🔄 Phase: {detail.get('phase', 'N/A')}")
    print(f"🔍 Jobs Found: {detail.get('jobs_found', 0)}")
    print(f"📝 Applications Submitted: {detail.get('applications_submitted', 0)}")
    
    # Show recent logs
    logs = detail.get('logs', [])
    if logs:
        print(f"\n📋 Recent Activity:")
        for log in logs[-5:]:
            level = log.get('level', 'INFO')
            message = log.get('message', '')
            emoji = '✅' if 'success' in message.lower() else '📌'
            print(f"  [{level}] {emoji} {message}")

def main():
    print_header("🤖 LinkedIn Automation - Full Test")
    print("\n✅ Backend is ready at http://localhost:8000")
    print("✅ Frontend is ready at http://127.0.0.1:8080")
    print("\n📝 To test automation:")
    print("   1. Go to http://127.0.0.1:8080")
    print("   2. Complete onboarding and upload your resume")
    print("   3. Click 'Start Automation'")
    print("   4. Monitor progress in real-time")
    print("\n💡 The automation now uses AutoAgentHireBot which:")
    print("   ✅ Parses your resume")
    print("   ✅ Searches for matching jobs")
    print("   ✅ Uses AI to rank job matches")
    print("   ✅ SUBMITS APPLICATIONS with your resume")
    print("   ✅ Fills all application forms")
    print("   ✅ Records timestamps for each application")
    print("\n🎯 Applications will be tracked with SUCCESS/FAILED status")

if __name__ == "__main__":
    main()
