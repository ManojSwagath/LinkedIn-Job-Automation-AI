#!/usr/bin/env python3
"""
Test LinkedIn Login with improved automation
"""
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.agents.linkedin_automation_agent import LinkedInAutomationAgent
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_login():
    """Test LinkedIn login functionality"""
    
    load_dotenv()
    
    # Get credentials from user input
    print("=" * 60)
    print("🔐 LinkedIn Login Test")
    print("=" * 60)
    print()
    
    email = input("Enter your LinkedIn email: ").strip()
    password = input("Enter your LinkedIn password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required!")
        return
    
    print()
    print("🚀 Starting login test...")
    print("📝 Browser will open in visible mode")
    print("📸 Screenshots will be saved to: ./screenshots/")
    print()
    
    # Create agent
    agent = LinkedInAutomationAgent(
        email=email,
        password=password,
        resume_text="Test resume",
        resume_file_path=None,
        gemini_client=None
    )
    
    try:
        # Initialize browser
        print("🌐 Initializing browser...")
        await agent.initialize_browser()
        
        # Attempt login
        print("🔐 Attempting login...")
        success = await agent.linkedin_login()
        
        if success:
            print()
            print("=" * 60)
            print("✅ LOGIN SUCCESSFUL!")
            print("=" * 60)
            print()
            print("✨ You are now logged into LinkedIn")
            print("📸 Check ./screenshots/ folder for visual confirmation")
            print()
            print("⏸️  Browser will stay open for 30 seconds...")
            print("   You can verify the login manually")
            await asyncio.sleep(30)
        else:
            print()
            print("=" * 60)
            print("❌ LOGIN FAILED")
            print("=" * 60)
            print()
            print("🔍 Debugging info:")
            print("   1. Check screenshots in ./screenshots/ folder")
            print("   2. Common issues:")
            print("      - Incorrect email/password")
            print("      - CAPTCHA required (solve it manually)")
            print("      - Email verification needed")
            print("      - Account locked or suspended")
            print()
            print("⏸️  Browser will stay open for 60 seconds...")
            print("   You can see what went wrong")
            await asyncio.sleep(60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERROR: {e}")
        print("=" * 60)
        logger.error("Test failed", exc_info=True)
        await asyncio.sleep(30)
    
    finally:
        # Cleanup
        print()
        print("🧹 Cleaning up...")
        if agent.browser:
            await agent.browser.close()
        if agent.playwright:
            await agent.playwright.stop()
        print("✅ Browser closed")


if __name__ == "__main__":
    asyncio.run(test_login())
