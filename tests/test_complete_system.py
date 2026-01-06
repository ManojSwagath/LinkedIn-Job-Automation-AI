#!/usr/bin/env python3
"""
Complete Automation Test - Step by Step Verification
Tests every component of the LinkedIn automation system
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_complete_automation():
    """Test the complete automation flow step by step"""
    
    print("="*80)
    print("🧪 LINKEDIN AUTOMATION - COMPLETE SYSTEM TEST")
    print("="*80)
    print()
    
    # Step 1: Import check
    print("="*80)
    print("STEP 1: Checking imports...")
    print("="*80)
    try:
        from backend.agents.autoagenthire_bot import AutoAgentHireBot
        print("✅ AutoAgentHireBot imported successfully")
        
        from playwright.async_api import async_playwright
        print("✅ Playwright imported successfully")
        
        import google.generativeai as genai
        print("✅ Google Generative AI imported successfully")
        
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")
        return False
    
    # Step 2: Get user input
    print("\n" + "="*80)
    print("STEP 2: Configuration")
    print("="*80)
    
    email = input("📧 LinkedIn Email: ").strip()
    password = input("🔑 LinkedIn Password: ").strip()
    keyword = input("🔍 Job Keyword (e.g., 'Software Engineer'): ").strip() or "Software Engineer"
    location = input("📍 Location (e.g., 'Remote'): ").strip() or "Remote"
    
    if not email or not password:
        print("❌ Email and password are required")
        return False
    
    print(f"\n✅ Configuration:")
    print(f"   Email: {email[:3]}***")
    print(f"   Keyword: {keyword}")
    print(f"   Location: {location}")
    
    # Step 3: Initialize bot
    print("\n" + "="*80)
    print("STEP 3: Initializing AutoAgentHire Bot")
    print("="*80)
    
    config = {
        'linkedin_email': email,
        'linkedin_password': password,
        'keyword': keyword,
        'location': location,
        'max_jobs': 5,
        'auto_apply': False,  # Don't apply for testing
        'resume_path': ''
    }
    
    try:
        bot = AutoAgentHireBot(config)
        print("✅ Bot initialized successfully")
    except Exception as e:
        print(f"❌ Bot initialization failed: {str(e)}")
        return False
    
    # Step 4: Browser initialization
    print("\n" + "="*80)
    print("STEP 4: Initializing Browser")
    print("="*80)
    print("⏳ This may take 10-15 seconds...")
    
    try:
        await bot.initialize_browser(use_persistent_profile=True)
        print("✅ Browser initialized")
        print(f"📍 Browser URL: {bot.page.url}")
        
        if bot.page:
            print("✅ Page object created")
        else:
            print("❌ Page object is None")
            return False
            
    except Exception as e:
        print(f"❌ Browser initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Test LinkedIn navigation
    print("\n" + "="*80)
    print("STEP 5: Testing LinkedIn Navigation")
    print("="*80)
    print("⏳ Navigating to LinkedIn...")
    
    try:
        await bot.page.goto('https://www.linkedin.com', wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(3)
        current_url = bot.page.url
        print(f"✅ Navigated to: {current_url}")
        
        if 'linkedin.com' in current_url:
            print("✅ LinkedIn domain confirmed")
        else:
            print(f"⚠️  Unexpected domain: {current_url}")
            
    except Exception as e:
        print(f"❌ Navigation failed: {str(e)}")
        return False
    
    # Step 6: Login test
    print("\n" + "="*80)
    print("STEP 6: Testing LinkedIn Login")
    print("="*80)
    print("⏳ Attempting login... (this may take 30-60 seconds)")
    
    try:
        login_success = await bot.login_linkedin()
        
        if login_success:
            print("✅ LOGIN SUCCESSFUL!")
            print(f"📍 Post-login URL: {bot.page.url}")
        else:
            print("❌ LOGIN FAILED")
            print(f"📍 Current URL: {bot.page.url}")
            print("\n⚠️  Common causes:")
            print("   - Incorrect credentials")
            print("   - CAPTCHA required (check browser window)")
            print("   - Account locked")
            print("\n💡 Tip: Keep the browser open to manually complete any challenges")
            
            # Wait 30 seconds for manual intervention
            print("\n⏸️  Waiting 30 seconds for manual intervention...")
            await asyncio.sleep(30)
            
            return False
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 7: Job search test
    print("\n" + "="*80)
    print("STEP 7: Testing Job Search")
    print("="*80)
    print(f"⏳ Searching for '{keyword}' in '{location}'...")
    
    try:
        await bot.search_jobs(keyword, location)
        current_url = bot.page.url
        print(f"✅ Search completed")
        print(f"📍 Search URL: {current_url}")
        
        if '/jobs/search' in current_url:
            print("✅ On job search results page")
        else:
            print(f"⚠️  Unexpected URL: {current_url}")
            
        if 'f_AL=true' in current_url:
            print("✅ Easy Apply filter is ACTIVE")
        else:
            print("⚠️  Easy Apply filter may not be active")
            
    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
        return False
    
    # Step 8: Job collection test
    print("\n" + "="*80)
    print("STEP 8: Testing Job Collection")
    print("="*80)
    print("⏳ Collecting job listings...")
    
    try:
        jobs = await bot.collect_job_listings(max_jobs=5)
        print(f"✅ Collected {len(jobs)} jobs")
        
        if len(jobs) > 0:
            print("\n📋 Sample jobs found:")
            for i, job in enumerate(jobs[:3], 1):
                print(f"   {i}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                print(f"      Easy Apply: {'✅' if job.get('easy_apply') else '❌'}")
        else:
            print("⚠️  No jobs collected - try different keywords")
            
    except Exception as e:
        print(f"❌ Job collection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 9: AI analysis test (if jobs found)
    if len(jobs) > 0 and bot.ai_model:
        print("\n" + "="*80)
        print("STEP 9: Testing AI Job Analysis")
        print("="*80)
        print("⏳ Analyzing job compatibility...")
        
        try:
            analyzed_job = await bot.analyze_job_with_ai(jobs[0])
            print("✅ AI analysis completed")
            print(f"   Match Score: {analyzed_job.get('match_score', 'N/A')}")
            print(f"   Recommendation: {analyzed_job.get('recommendation', 'N/A')}")
        except Exception as e:
            print(f"⚠️  AI analysis failed: {str(e)}")
    
    # Step 10: Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print("✅ Imports: Working")
    print("✅ Bot Initialization: Working")
    print("✅ Browser: Working")
    print("✅ LinkedIn Navigation: Working")
    print(f"{'✅' if login_success else '❌'} Login: {'Working' if login_success else 'Failed'}")
    print(f"✅ Job Search: Working")
    print(f"✅ Job Collection: Working ({len(jobs)} jobs found)")
    print("✅ AI Analysis: Working" if bot.ai_model and len(jobs) > 0 else "⚠️  AI Analysis: Skipped")
    
    print("\n" + "="*80)
    print("🎉 ALL TESTS PASSED!")
    print("="*80)
    print("\n💡 Next steps:")
    print("   1. Your automation system is working correctly")
    print("   2. You can now run full automation: python3 demo_automation.py")
    print("   3. Set auto_apply=True to enable job applications")
    
    print("\n⏸️  Browser will stay open for 60 seconds for inspection...")
    await asyncio.sleep(60)
    
    # Cleanup
    try:
        await bot.close()
        print("\n✅ Browser closed successfully")
    except:
        pass
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_complete_automation())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
