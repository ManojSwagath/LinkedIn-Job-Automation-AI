"""
Test script for LinkedIn Recommended Jobs feature
Run this to test the scraper without the full API
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.automation.linkedin_recommended_jobs import fetch_recommended_jobs


async def test_scraper():
    """Test the LinkedIn recommended jobs scraper"""
    print("="*60)
    print("TESTING LINKEDIN RECOMMENDED JOBS SCRAPER")
    print("="*60)
    print()
    
    print("⚠️  REQUIREMENTS:")
    print("  1. LINKEDIN_EMAIL set in .env")
    print("  2. LINKEDIN_PASSWORD set in .env")
    print("  3. Playwright Chromium installed")
    print()
    input("Press Enter to continue...")
    print()
    
    try:
        jobs = await fetch_recommended_jobs()
        
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        print(f"\n✅ Total Jobs Found: {len(jobs)}")
        print()
        
        if jobs:
            print("📋 First 5 Jobs:")
            print("-"*60)
            for job in jobs[:5]:
                print(f"\n{job['index']}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Location: {job['location']}")
                print(f"   URL: {job['url'][:80]}...")
                
            print("\n" + "="*60)
            print("✅ TEST PASSED - Scraper working correctly!")
            print("="*60)
        else:
            print("⚠️  No jobs found - check LinkedIn login or page structure")
            
    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED")
        print("="*60)
        print(f"Error: {str(e)}")
        print()
        print("Common issues:")
        print("  1. Invalid LinkedIn credentials")
        print("  2. LinkedIn CAPTCHA/security check")
        print("  3. Playwright not installed: playwright install chromium")
        print("  4. LinkedIn UI changed (selectors need update)")


if __name__ == "__main__":
    asyncio.run(test_scraper())
