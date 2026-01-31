#!/usr/bin/env python3
"""
System Readiness Check
Verifies all components are ready for LinkedIn automation
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("🔍 LINKEDIN AUTOMATION SYSTEM - READINESS CHECK")
print("="*80)

all_good = True

# Check 1: Python Environment
print("\n[1/7] Python Environment")
print(f"   Python Version: {sys.version.split()[0]}")
print(f"   ✅ Python OK")

# Check 2: Dependencies
print("\n[2/7] Dependencies")
try:
    import playwright
    print(f"   ✅ Playwright installed")
except ImportError:
    print(f"   ❌ Playwright NOT installed - run: pip install playwright")
    all_good = False

try:
    import google.generativeai as genai
    print(f"   ✅ Google Generative AI installed")
except ImportError:
    print(f"   ❌ Google Generative AI NOT installed - run: pip install google-generativeai")
    all_good = False

try:
    from sqlalchemy import create_engine
    print(f"   ✅ SQLAlchemy installed")
except ImportError:
    print(f"   ❌ SQLAlchemy NOT installed - run: pip install sqlalchemy")
    all_good = False

# Check 3: LinkedIn Credentials
print("\n[3/7] LinkedIn Credentials")
linkedin_email = os.getenv('LINKEDIN_EMAIL', '')
linkedin_password = os.getenv('LINKEDIN_PASSWORD', '')

if linkedin_email and '@' in linkedin_email:
    print(f"   ✅ Email: {linkedin_email}")
else:
    print(f"   ❌ LinkedIn email not configured")
    all_good = False

if linkedin_password and len(linkedin_password) > 3:
    print(f"   ✅ Password: {'*' * len(linkedin_password)}")
else:
    print(f"   ❌ LinkedIn password not configured")
    all_good = False

# Check 4: User Profile
print("\n[4/7] User Profile")
first_name = os.getenv('FIRST_NAME', '')
last_name = os.getenv('LAST_NAME', '')
phone = os.getenv('PHONE_NUMBER', '')

if first_name:
    print(f"   ✅ First Name: {first_name}")
else:
    print(f"   ⚠️  First Name not set (will use defaults)")

if last_name:
    print(f"   ✅ Last Name: {last_name}")
else:
    print(f"   ⚠️  Last Name not set (will use defaults)")

if phone:
    print(f"   ✅ Phone: {phone}")
else:
    print(f"   ⚠️  Phone not set (will use defaults)")

# Check 5: AI Configuration
print("\n[5/7] AI Configuration")
gemini_key = os.getenv('GEMINI_API_KEY', '')
github_key = os.getenv('GITHUB_API_KEY', '')

if gemini_key and not gemini_key.startswith('your'):
    print(f"   ✅ Gemini API Key: {gemini_key[:20]}...")
else:
    print(f"   ⚠️  Gemini API Key not configured (AI features limited)")

if github_key and github_key.startswith('ghp_'):
    print(f"   ✅ GitHub API Key: {github_key[:15]}...")
else:
    print(f"   ⚠️  GitHub API Key not configured (AI features limited)")

# Check 6: Database
print("\n[6/7] Database")
db_url = os.getenv('DATABASE_URL', 'sqlite:///./data/autoagenthire.db')
print(f"   Database: {db_url}")

if 'sqlite' in db_url:
    data_dir = Path('data')
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created data directory")
    else:
        print(f"   ✅ Data directory exists")
    
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"   ✅ Database connection: OK")
    except Exception as e:
        print(f"   ❌ Database connection failed: {str(e)}")
        all_good = False

# Check 7: Automation Scripts
print("\n[7/7] Automation Scripts")
working_script = Path('working_automation.py')
full_script = Path('run_full_automation.py')

if working_script.exists():
    print(f"   ✅ working_automation.py found")
else:
    print(f"   ❌ working_automation.py not found")
    all_good = False

if full_script.exists():
    print(f"   ✅ run_full_automation.py found")
else:
    print(f"   ❌ run_full_automation.py not found")
    all_good = False

# Check AutoAgentHireBot
try:
    from backend.agents.autoagenthire_bot import AutoAgentHireBot
    print(f"   ✅ AutoAgentHireBot module loaded")
except ImportError as e:
    print(f"   ❌ AutoAgentHireBot module error: {str(e)}")
    all_good = False

# Summary
print("\n" + "="*80)
if all_good:
    print("✅ SYSTEM READY!")
    print("="*80)
    print("\n🚀 You can now run the automation:")
    print("\n   Option 1 - Working Version (Recommended):")
    print("   python working_automation.py")
    print("\n   Option 2 - Full Automation:")
    print("   PYTHONPATH=$PWD python run_full_automation.py")
    print("\n   Option 3 - Backend Server:")
    print("   PYTHONPATH=$PWD python -m uvicorn backend.main:app --port 8000")
    print("\n   Option 4 - Complete System Menu:")
    print("   ./start_complete_system.sh")
else:
    print("⚠️  SOME ISSUES DETECTED")
    print("="*80)
    print("\nPlease fix the issues above before running the automation.")
    print("\nQuick fixes:")
    print("   - Install dependencies: pip install playwright google-generativeai sqlalchemy")
    print("   - Configure LinkedIn credentials in .env file")
    print("   - Install Playwright browser: playwright install chromium")

print("\n" + "="*80 + "\n")

sys.exit(0 if all_good else 1)
