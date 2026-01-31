#!/usr/bin/env python3
"""
VISIBLE AUTOMATION - Watch It Work!
====================================
This version runs SLOWLY so you can see every action in the browser.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Load environment
load_dotenv()

async def main():
    """Run automation with maximum visibility."""
    
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  👁️  VISIBLE AUTOMATION - WATCH IT WORK!".ljust(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    print("=" * 80)
    print("🎯 WHAT YOU'LL SEE IN THE BROWSER:")
    print("=" * 80)
    print("1. ✅ Browser opens (visible window)")
    print("2. ✅ Navigates to LinkedIn login page")
    print("3. ✅ Types your email and password (slowly)")
    print("4. ✅ Clicks Sign In button")
    print("5. ✅ Searches for jobs")
    print("6. ✅ Collects Easy Apply jobs")
    print("7. ✅ Opens each job page")
    print("8. ✅ Clicks 'Easy Apply' button")
    print("9. ✅ Fills ALL form fields one by one:")
    print("   • First Name")
    print("   • Last Name")
    print("   • Phone Number")
    print("   • Email")
    print("   • City, State, Zip")
    print("   • Work authorization questions")
    print("   • Years of experience")
    print("   • And more...")
    print("10. ✅ Clicks 'Next' button (watch it happen!)")
    print("11. ✅ Fills next page (if any)")
    print("12. ✅ Clicks 'Review' button")
    print("13. ✅ Clicks 'Submit' button")
    print("14. ✅ Verifies submission success")
    print("15. ✅ Moves to next job")
    print("=" * 80)
    print()
    
    print("⚙️  VISIBILITY SETTINGS:")
    print("=" * 80)
    print("• Browser: Visible (not headless)")
    print("• Action Speed: SLOW (300ms delay between actions)")
    print("• Console: Detailed progress for every action")
    print("• Window: Will stay open entire time")
    print("=" * 80)
    print()
    
    print("⚠️  IMPORTANT INSTRUCTIONS:")
    print("=" * 80)
    print("1. Keep your eyes on the BROWSER WINDOW")
    print("2. You will see fields being filled automatically")
    print("3. You will see buttons being clicked")
    print("4. DO NOT close the browser manually")
    print("5. DO NOT click anything in the browser")
    print("6. Just watch and enjoy the automation!")
    print("=" * 80)
    print()
    
    input("Press ENTER to start the visible automation...")
    print()
    
    # Configure for maximum visibility
    os.environ["HEADLESS_BROWSER"] = "false"
    os.environ["BROWSER_SLOW_MO"] = "300"  # Slow for visibility
    
    # Import and run
    from backend.agents.autoagenthire_bot import AutoAgentHireBot
    
    config = {
        "linkedin_email": os.getenv("LINKEDIN_EMAIL", ""),
        "linkedin_password": os.getenv("LINKEDIN_PASSWORD", ""),
        "keyword": os.getenv("JOB_KEYWORD", "Software Engineer"),
        "location": os.getenv("JOB_LOCATION", "Remote"),
        "max_applications": int(os.getenv("MAX_APPLICATIONS", "3")),  # Fewer for demo
        "dry_run": False,
        "auto_apply": True,
        "user_profile": {
            "email": os.getenv("LINKEDIN_EMAIL", ""),
            "first_name": os.getenv("FIRST_NAME", "Test"),
            "last_name": os.getenv("LAST_NAME", "User"),
            "phone_number": os.getenv("PHONE_NUMBER", "+1234567890"),
            "city": os.getenv("CITY", "San Francisco"),
            "state": os.getenv("STATE", "CA"),
            "zip_code": os.getenv("ZIP_CODE", "94105"),
            "linkedin_url": os.getenv("LINKEDIN_URL", ""),
            "github_url": os.getenv("GITHUB_URL", ""),
            "portfolio_url": os.getenv("PORTFOLIO_URL", ""),
        }
    }
    
    bot = AutoAgentHireBot(config)
    
    try:
        print("\n🌐 STEP 1: Initializing browser...")
        print("   👁️  Browser window will appear now...\n")
        await bot.initialize_browser(use_persistent_profile=True)
        print("✅ Browser opened!\n")
        
        print("🔐 STEP 2: Logging into LinkedIn...")
        print("   👁️  Watch the browser - credentials being entered...\n")
        login_success = await bot.login_linkedin()
        if not login_success:
            print("❌ Login failed")
            return
        print("✅ Login successful!\n")
        
        print(f"🔍 STEP 3: Searching for jobs...")
        print(f"   Keyword: {config['keyword']}")
        print(f"   Location: {config['location']}")
        print("   👁️  Watch browser - navigating to jobs search...\n")
        await bot.search_jobs(config["keyword"], config["location"])
        print("✅ Search completed!\n")
        
        print("📋 STEP 4: Collecting job listings...")
        print("   👁️  Watch browser - scrolling through results...\n")
        jobs = await bot.collect_job_listings(max_jobs=config["max_applications"])
        
        if not jobs:
            print("❌ No Easy Apply jobs found")
            return
        
        print(f"✅ Collected {len(jobs)} Easy Apply jobs\n")
        
        # Display jobs
        print("┌" + "─" * 78 + "┐")
        print("│" + " " * 25 + "📋 JOBS TO APPLY" + " " * 37 + "│")
        print("├" + "─" * 78 + "┤")
        for idx, job in enumerate(jobs, 1):
            title = job.get("title", "Unknown")[:45]
            company = job.get("company", "Unknown")[:30]
            print(f"│ [{idx}] {title:<47} │")
            print(f"│     🏢 {company:<44} │")
            if idx < len(jobs):
                print("├" + "─" * 78 + "┤")
        print("└" + "─" * 78 + "┘\n")
        
        print("🚀 STEP 5: Applying to jobs...")
        print("   👁️  WATCH BROWSER CAREFULLY - You'll see:")
        print("      • Each job page opening")
        print("      • Easy Apply modal appearing")
        print("      • Form fields being filled")
        print("      • Buttons being clicked")
        print("      • Success confirmation")
        print()
        
        applied = 0
        for idx, job in enumerate(jobs, 1):
            print("\n" + "━" * 80)
            print(f"🎯 JOB {idx}/{len(jobs)}: {job.get('title', 'Unknown')}")
            print(f"   Company: {job.get('company', 'Unknown')}")
            print("━" * 80)
            print("👁️  WATCH THE BROWSER NOW!\n")
            
            result = await bot.auto_apply_job(job)
            
            if result.get('application_status') in ('APPLIED', 'SUCCESS'):
                applied += 1
                print(f"\n✅ APPLICATION #{applied} SUBMITTED!\n")
            else:
                status = result.get('application_status', 'FAILED')
                reason = result.get('application_reason', 'Unknown')
                print(f"\n⚠️  Application {status}: {reason}\n")
            
            if idx < len(jobs):
                print("⏳ Waiting 10 seconds before next application...")
                print("   (Watch for the next job to open in browser)")
                await asyncio.sleep(10)
        
        print("\n" + "=" * 80)
        print("🎉 AUTOMATION COMPLETE!")
        print("=" * 80)
        print(f"Total jobs processed: {len(jobs)}")
        print(f"Applications submitted: {applied}")
        print(f"Success rate: {(applied/len(jobs)*100) if jobs else 0:.1f}%")
        print("=" * 80)
        print()
        print("✅ Did you see all the actions in the browser?")
        print("✅ All form fields were filled automatically!")
        print("✅ All buttons were clicked automatically!")
        print("✅ Applications were submitted!")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔒 Closing browser...")
        await bot.close()
        print("✅ Done!\n")


if __name__ == "__main__":
    asyncio.run(main())
