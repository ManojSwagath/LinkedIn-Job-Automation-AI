#!/usr/bin/env python3
"""
Debug script to visualize LinkedIn search results and diagnose selector issues
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

async def debug_linkedin_search():
    """Debug LinkedIn job search to see actual page structure"""
    
    print("\n" + "="*80)
    print("🔍 LinkedIn Search Debugger")
    print("="*80)
    
    linkedin_email = os.getenv('LINKEDIN_EMAIL')
    linkedin_password = os.getenv('LINKEDIN_PASSWORD')
    
    if not linkedin_email or not linkedin_password:
        print("❌ Missing credentials in .env file")
        return
    
    async with async_playwright() as p:
        print("\n📝 Launching browser (non-headless for visualization)...")
        
        # Launch browser in non-headless mode so you can see
        browser = await p.chromium.launch(
            headless=False,  # Show the browser
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        try:
            # Step 1: Login
            print("\n📝 Step 1: Logging into LinkedIn...")
            await page.goto('https://www.linkedin.com/login')
            await page.wait_for_load_state('networkidle')
            
            # Check if already logged in
            if 'feed' in page.url or 'mynetwork' in page.url:
                print("   ✅ Already logged in!")
            else:
                print("   📝 Entering credentials...")
                await page.fill('#username', linkedin_email)
                await page.fill('#password', linkedin_password)
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                print("   ✅ Logged in successfully!")
            
            # Step 2: Search for jobs
            search_terms = [
                ("Python Developer", "India"),
                ("Software Engineer", "Bangalore"),
                ("Data Analyst", "Remote"),
            ]
            
            for keyword, location in search_terms:
                print(f"\n{'='*80}")
                print(f"🔍 Testing: {keyword} in {location}")
                print(f"{'='*80}")
                
                # Construct search URL with Easy Apply filter
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}&location={location}&f_AL=true&sortBy=DD"
                
                print(f"\n📝 Navigating to: {search_url}")
                await page.goto(search_url)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                
                # Try multiple selectors to find job cards
                selectors = [
                    'li.jobs-search-results__list-item',
                    'div.job-card-container',
                    'div.jobs-search-results__list-item',
                    '[data-job-id]',
                    '.scaffold-layout__list-item',
                ]
                
                print("\n📝 Testing different selectors:")
                for selector in selectors:
                    elements = await page.query_selector_all(selector)
                    print(f"   Selector '{selector}': Found {len(elements)} elements")
                
                # Get page content for inspection
                print("\n📝 Page title:", await page.title())
                print("📝 Current URL:", page.url)
                
                # Check for Easy Apply buttons
                easy_apply_selectors = [
                    'button.jobs-apply-button',
                    'button:has-text("Easy Apply")',
                    '[aria-label*="Easy Apply"]',
                    '.jobs-apply-button',
                ]
                
                print("\n📝 Looking for Easy Apply buttons:")
                for selector in easy_apply_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        print(f"   Selector '{selector}': Found {len(elements)} buttons")
                    except:
                        print(f"   Selector '{selector}': Error")
                
                # Take screenshot
                screenshot_name = f"debug_{keyword.replace(' ', '_')}_{location}.png"
                await page.screenshot(path=screenshot_name)
                print(f"\n📸 Screenshot saved: {screenshot_name}")
                
                print("\n⏸️  Pausing for 10 seconds - check the browser window!")
                await asyncio.sleep(10)
            
            print("\n" + "="*80)
            print("✅ Debug session complete! Check the screenshots.")
            print("="*80)
            
            # Keep browser open for manual inspection
            print("\n📝 Browser will stay open for 30 seconds for manual inspection...")
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()
            print("\n🧹 Browser closed")

if __name__ == "__main__":
    asyncio.run(debug_linkedin_search())
