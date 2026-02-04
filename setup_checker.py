#!/usr/bin/env python3
"""
Setup and Configuration Helper for LinkedIn Job Automation
Helps user configure environment variables and test the setup
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_python_packages():
    """Check if required Python packages are installed"""
    print("📦 Checking Python packages...")
    
    packages = {
        'playwright': 'playwright',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'google-generativeai': 'google.generativeai',
        'PyPDF2': 'PyPDF2',
        'python-dotenv': 'dotenv',
    }
    
    missing = []
    for package, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n⚠️  Install missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    return True

def check_playwright_browsers():
    """Check if playwright browsers are installed"""
    print("\n🌐 Checking Playwright browsers...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("✅ Chromium browser installed")
                return True
            except:
                print("❌ Chromium browser not installed")
                print("Run: playwright install chromium")
                return False
    except:
        print("❌ Playwright not properly installed")
        return False

def check_environment_config():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    load_dotenv()
    
    required_vars = {
        'LINKEDIN_EMAIL': 'Your LinkedIn email address',
        'LINKEDIN_PASSWORD': 'Your LinkedIn password',
    }
    
    optional_vars = {
        'GEMINI_API_KEY': 'Google Gemini API key for AI features',
        'GITHUB_API_KEY': 'GitHub token for profile data',
        'JOB_KEYWORDS': 'Job search keywords (default: Software Engineer)',
        'JOB_LOCATION': 'Job location preference (default: Remote)',
        'MAX_APPLICATIONS': 'Maximum applications per run (default: 5)',
        'TEST_MODE': 'Set to true for safe testing (default: true)',
    }
    
    missing_required = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            missing_required.append((var, description))
            print(f"❌ {var}: {description}")
        else:
            masked_value = value[:3] + '*' * (len(value) - 3) if len(value) > 3 else '***'
            print(f"✅ {var}: {masked_value}")
    
    print(f"\n📋 Optional configuration:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and not value.startswith('your_'):
            if 'key' in var.lower() or 'token' in var.lower():
                masked_value = value[:8] + '*' * (len(value) - 8) if len(value) > 8 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚪ {var}: {description}")
    
    return len(missing_required) == 0

def create_sample_env():
    """Create a sample .env file"""
    env_path = Path('.env')
    if env_path.exists():
        print(f"\n📄 .env file already exists")
        return
    
    sample_content = '''# LinkedIn Job Automation Configuration

# LinkedIn Credentials (REQUIRED)
LINKEDIN_EMAIL=your_linkedin_email@example.com
LINKEDIN_PASSWORD=your_linkedin_password

# API Keys for AI Features (OPTIONAL but recommended)
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_API_KEY=your_github_token_here
OPENAI_API_KEY=your_openai_api_key_here

# Job Search Configuration
JOB_KEYWORDS=Software Engineer
JOB_LOCATION=Remote
MAX_APPLICATIONS=5
TEST_MODE=true

# User Profile Information
USER_FULL_NAME=Your Full Name
USER_PHONE=+1-555-0123
USER_LOCATION=United States
YEARS_EXPERIENCE=3

# Application Settings
APP_NAME=AutoAgentHire
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
'''
    
    env_path.write_text(sample_content)
    print(f"\n📄 Created sample .env file")
    print(f"   Please edit .env with your actual credentials")

def test_automation_setup():
    """Test if automation can be initialized"""
    print("\n🧪 Testing automation setup...")
    
    try:
        # Test basic imports
        from backend.agents.autoagenthire_bot import AutoAgentHireBot
        
        # Test configuration
        test_config = {
            'linkedin_email': 'test@example.com',
            'linkedin_password': 'test_password',
            'keyword': 'Software Engineer',
            'location': 'Remote',
            'max_applications': 1,
            'test_mode': True,
            'headless': True
        }
        
        bot = AutoAgentHireBot(test_config)
        print("✅ AutoAgentHireBot can be initialized")
        return True
        
    except Exception as e:
        print(f"❌ Automation setup error: {e}")
        return False

def main():
    """Main setup checker"""
    print("=" * 60)
    print("🚀 LinkedIn Job Automation - Setup Checker")
    print("=" * 60)
    
    # Check if .env exists, create if not
    if not Path('.env').exists():
        create_sample_env()
        print("\n⚠️  Please edit the .env file with your credentials before running automation")
        return
    
    # Run all checks
    checks = [
        check_python_packages(),
        check_playwright_browsers(),
        check_environment_config(),
        test_automation_setup()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ SETUP COMPLETE - Ready to run automation!")
        print("=" * 60)
        print("\n🎯 Next Steps:")
        print("   1. Web UI: http://127.0.0.1:8080/dashboard/automation")
        print("   2. Command Line: python run_full_automation.py")
        print("   3. Start servers: python simple_backend.py (in one terminal)")
        print("                    cd frontend/lovable && npm run dev (in another)")
        
    else:
        print("❌ SETUP INCOMPLETE - Please fix the issues above")
        print("=" * 60)
    
    print(f"\n📖 For detailed instructions, see README.md")

if __name__ == "__main__":
    main()