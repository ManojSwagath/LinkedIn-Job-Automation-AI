"""
FINAL WORKING AUTOMATION - Apply to 1 job successfully
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from backend.agents.autoagenthire_bot import AutoAgentHireBot

async def final_automation():
    """Apply to 1 job successfully"""
    print("🎯 FINAL LINKEDIN AUTOMATION - APPLY TO 1 JOB")

    email = os.getenv('LINKEDIN_EMAIL', '')
    password = os.getenv('LINKEDIN_PASSWORD', '')

    if not email or not password:
        print("❌ Missing credentials in .env")
        return

    config = {
        'linkedin_email': email,
        'linkedin_password': password,
        'keyword': 'Python Developer',
        'location': 'India',
        'max_applications': 1,
        'dry_run': False
    }

    print(f"🔍 Search: '{config['keyword']}' in '{config['location']}'")
    print(f"🎯 Will apply to: {config['max_applications']} job")

    bot = AutoAgentHireBot(config)

    try:
        print("\n1️⃣ Starting browser...")
        await bot.initialize_browser()
        print("✅ Browser ready")

        print("\n2️⃣ Logging in...")
        if not await bot.login_linkedin():
            print("❌ Login failed")
            return
        print("✅ Logged in")

        print("\n3️⃣ Searching jobs...")
        await bot.search_jobs(keyword=config['keyword'], location=config['location'])
        jobs = await bot.collect_job_listings(max_jobs=3)
        print(f"📊 Found {len(jobs)} Easy Apply jobs")

        if len(jobs) == 0:
            print("❌ No Easy Apply jobs found")
            print("💡 Try different keywords: 'Junior Developer', 'Entry Level'")
            return

        job = jobs[0]
        print(f"\n🎯 Applying to: {job.get('title', 'Unknown')}")
        print(f"🏢 Company: {job.get('company', 'Unknown')}")

        print("\n4️⃣ Submitting application...")
        result = await bot.apply_to_single_job(job.get('url', ''))

        status = result.get('application_status', 'UNKNOWN')
        print(f"📊 Status: {status}")

        if status == 'APPLIED':
            print("\n🎉 SUCCESS! Application submitted!")
            print("✅ Check your LinkedIn applications to verify")
        elif status == 'NEEDS_REVIEW':
            print("\n⚠️ Needs manual review")
            print(f"Reason: {result.get('application_reason', 'Unknown')}")
        else:
            print("\n❌ Application failed")
            print(f"Reason: {result.get('application_reason', 'Unknown')}")

        print("\n✅ AUTOMATION COMPLETE")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(final_automation())