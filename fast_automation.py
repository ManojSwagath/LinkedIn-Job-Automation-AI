"""
FAST AUTOMATION - Quick test and apply
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from backend.agents.autoagenthire_bot import AutoAgentHireBot

async def fast_automation():
    """Fast automation test"""
    print("🚀 FAST LINKEDIN AUTOMATION")

    email = os.getenv('LINKEDIN_EMAIL', '')
    password = os.getenv('LINKEDIN_PASSWORD', '')

    if not email:
        print("❌ No credentials")
        return

    config = {
        'linkedin_email': email,
        'linkedin_password': password,
        'keyword': 'Python Developer',
        'location': 'India',
        'max_applications': 1,  # Just 1 job
        'dry_run': False
    }

    bot = AutoAgentHireBot(config)

    try:
        print("1. Browser...")
        await bot.initialize_browser()
        print("✅ Ready")

        print("2. Login...")
        if not await bot.login_linkedin():
            print("❌ Login failed")
            return
        print("✅ Logged in")

        print("3. Search...")
        await bot.search_jobs(keyword='Python Developer', location='India')
        print("✅ Search done")

        print("4. Collect jobs...")
        jobs = await bot.collect_job_listings(max_jobs=3)
        print(f"📊 Found {len(jobs)} jobs")

        if len(jobs) == 0:
            print("❌ No Easy Apply jobs found")
            return

        print(f"5. Applying to: {jobs[0].get('title', 'Unknown')}")
        result = await bot.apply_to_single_job(jobs[0].get('url', ''))

        status = result.get('application_status', 'UNKNOWN')
        print(f"📊 Result: {status}")

        if status == 'APPLIED':
            print("🎉 SUCCESS! Application submitted!")
        else:
            print(f"❌ Failed: {result.get('application_reason', 'Unknown')}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(fast_automation())