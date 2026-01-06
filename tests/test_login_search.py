#!/usr/bin/env python3
"""
Quick test script to verify login and search fixes
Tests only the login and search functionality without applying to jobs
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from agents.autoagenthire_bot import AutoAgentHireBot

async def test_login_and_search():
    """Test login and search functionality"""
    
    print("="*70)
    print("🧪 LinkedIn Login & Search Test")
    print("="*70)
    print()
    
    # Get credentials
    email = input("📧 Enter LinkedIn email: ").strip()
    if not email:
        print("❌ Email required")
        return
    
    password = input("🔑 Enter LinkedIn password: ").strip()
    if not password:
        print("❌ Password required")
        return
    
    print()
    
    # Initialize bot
    print("🤖 Initializing AutoAgentHire bot...")
    bot = AutoAgentHireBot({
        "linkedin_email": email,
        "linkedin_password": password,
        # Not needed for this test
        "resume_path": "",
        # Keep browser visible for debugging
        "headless": False,
    })
    
    try:
        # Test 1: Browser initialization
        print("\n" + "="*70)
        print("TEST 1: Browser Initialization")
        print("="*70)
        
        await bot.initialize_browser()
        print("✅ Browser initialized successfully")
        
        # Test 2: Login
        print("\n" + "="*70)
        print("TEST 2: LinkedIn Login")
        print("="*70)

        login_success = await bot.login_linkedin()
        
        if login_success:
            print("\n✅ LOGIN TEST PASSED")
        else:
            print("\n❌ LOGIN TEST FAILED")
            print("Please check:")
            print("  - Email and password are correct")
            print("  - No CAPTCHA is blocking login")
            print("  - LinkedIn account is accessible")
            await bot.close()
            return
        
        # Test 3: Job search
        print("\n" + "="*70)
        print("TEST 3: Job Search with Easy Apply Filter")
        print("="*70)
        
        keyword = input("🔍 Enter job keyword (e.g., 'Python Developer'): ").strip() or "Software Engineer"
        location = input("📍 Enter location (e.g., 'United States'): ").strip() or "United States"
        
        print(f"\nSearching for: {keyword} in {location}")
        
        await bot.search_jobs(keyword, location)
        
        # Verify we're on search results
        current_url = bot.page.url
        print(f"\n📍 Current URL: {current_url}")
        
        if '/jobs/search' in current_url:
            print("✅ On job search results page")
            
            if 'f_AL=true' in current_url:
                print("✅ Easy Apply filter is ACTIVE in URL")
            else:
                print("⚠️  Easy Apply filter may not be active")
            
            # Check for job results
            job_cards = await bot.page.query_selector_all('div.job-card-container, li.jobs-search-results__list-item')
            print(f"📊 Found {len(job_cards)} job cards on page")
            
            if len(job_cards) > 0:
                print("✅ SEARCH TEST PASSED")
            else:
                print("⚠️  No job cards found - try different keywords")
        else:
            print("❌ SEARCH TEST FAILED - Not on search results page")
        
        # Summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"✅ Browser: Working")
        print(f"{'✅' if login_success else '❌'} Login: {'Working' if login_success else 'Failed'}")
        print(f"{'✅' if '/jobs/search' in current_url else '❌'} Search: {'Working' if '/jobs/search' in current_url else 'Failed'}")
        print(f"{'✅' if 'f_AL=true' in current_url else '⚠️ '} Easy Apply Filter: {'Active' if 'f_AL=true' in current_url else 'Check URL'}")
        
        print("\n💡 Next Steps:")
        if login_success and '/jobs/search' in current_url:
            print("  ✅ Login and search are working!")
            print("  ✅ You can now run the full automation:")
            print("     python3 demo_automation.py")
        else:
            print("  ⚠️  Please fix the issues above before running full automation")
        
        print("\n⏸️  Browser will stay open for 30 seconds for you to inspect...")
        await asyncio.sleep(30)
        
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔒 Closing browser...")
        await bot.close()
        print("✅ Test complete")

if __name__ == "__main__":
    asyncio.run(test_login_and_search())
