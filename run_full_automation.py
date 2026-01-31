"""
LinkedIn Job Automation - Main Entry Point
Automates job applications with AI-powered form filling
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure proper path
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

async def run_automation():
    """Main automation function"""
    from backend.agents.autoagenthire_bot import AutoAgentHireBot
    
    print("\n" + "="*70)
    print("🚀 LINKEDIN JOB AUTOMATION")
    print("="*70)
    
    # Configuration
    config = {
        'linkedin_email': os.getenv('LINKEDIN_EMAIL'),
        'linkedin_password': os.getenv('LINKEDIN_PASSWORD'),
        'keywords': os.getenv('JOB_KEYWORDS', 'Software Engineer'),
        'location': os.getenv('JOB_LOCATION', 'United States'),
        'max_applications': int(os.getenv('MAX_APPLICATIONS', '5')),
        'test_mode': os.getenv('TEST_MODE', 'true').lower() == 'true',
        'user_profile': {
            'full_name': os.getenv('USER_FULL_NAME', 'Professional Candidate'),
            'email': os.getenv('LINKEDIN_EMAIL', ''),
            'phone': os.getenv('USER_PHONE', ''),
            'location': os.getenv('USER_LOCATION', 'United States'),
            'years_experience': os.getenv('YEARS_EXPERIENCE', '3'),
            'willing_to_relocate': True
        }
    }
    
    # Validate credentials
    if not config['linkedin_email'] or not config['linkedin_password']:
        print("\n❌ LinkedIn credentials not found in .env file!")
        print("   Add: LINKEDIN_EMAIL and LINKEDIN_PASSWORD")
        return
    
    print(f"\n� Configuration:")
    print(f"   Keywords: {config['keywords']}")
    print(f"   Location: {config['location']}")
    print(f"   Max Apps: {config['max_applications']}")
    print(f"   Test Mode: {config['test_mode']}")
    
    # Initialize bot
    bot = AutoAgentHireBot(config)
    
    try:
        # Initialize browser
        print("\n🌐 Starting browser...")
        await bot.initialize_browser(use_persistent_profile=True)
        
        # Login
        print("🔐 Logging into LinkedIn...")
        await bot.login_linkedin()
        
        # Search for jobs
        print(f"\n🔍 Searching: '{config['keywords']}' in '{config['location']}'...")
        await bot.search_jobs(config['keywords'], config['location'])
        
        # Get job listings
        jobs = await bot.get_job_list()
        print(f"✅ Found {len(jobs)} Easy Apply jobs")
        
        if not jobs:
            print("⚠️ No Easy Apply jobs found. Try different keywords.")
            return
        
        # Verify page is available
        if not bot.page:
            print("❌ Browser page not initialized!")
            return
        
        # Apply to jobs
        max_apps = min(config['max_applications'], len(jobs))
        print(f"\n🎯 Applying to {max_apps} jobs...")
        
        for idx, job in enumerate(jobs[:max_apps], 1):
            try:
                print(f"\n[{idx}/{max_apps}] Processing job...")
                await job.click()
                await asyncio.sleep(2)
                
                # Click Easy Apply
                easy_apply = await bot.page.query_selector('button:has-text("Easy Apply")')
                if not easy_apply:
                    print("   ⚠️ No Easy Apply button, skipping...")
                    continue
                
                await easy_apply.click()
                await asyncio.sleep(2)
                
                # Fill form with AI
                print("   📝 Filling application...")
                await bot._fill_application_form()
                
                # Handle multi-step
                for step in range(5):
                    if not bot.page:
                        break
                        
                    next_btn = await bot.page.query_selector('button:has-text("Next")')
                    if next_btn:
                        print(f"   ➡️ Next (step {step+1})")
                        await next_btn.click()
                        await asyncio.sleep(2)
                        await bot._fill_application_form()
                    else:
                        submit = await bot.page.query_selector('button:has-text("Submit"), button:has-text("Review")')
                        if submit:
                            if config['test_mode']:
                                print("   ✅ [TEST] Would submit here")
                                close = await bot.page.query_selector('button[aria-label*="Dismiss"]')
                                if close:
                                    await close.click()
                            else:
                                print("   📤 Submitting...")
                                await submit.click()
                                await asyncio.sleep(2)
                                print("   ✅ Submitted!")
                        break
                
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:50]}")
                try:
                    if bot.page:
                        close = await bot.page.query_selector('button[aria-label*="Dismiss"]')
                        if close:
                            await close.click()
                except:
                    pass
        
        print("\n" + "="*70)
        print("✅ AUTOMATION COMPLETE!")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n⚠️ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(run_automation())
