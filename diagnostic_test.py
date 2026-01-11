"""
Quick Diagnostic Test - Find the exact issue
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

from backend.agents.autoagenthire_bot import AutoAgentHireBot

async def diagnostic_test():
    """Run diagnostic to find the exact issue"""
    print("=" * 80)
    print("🔍 AUTOMATION DIAGNOSTIC TEST")
    print("=" * 80)

    # Check credentials
    email = os.getenv('LINKEDIN_EMAIL', '')
    password = os.getenv('LINKEDIN_PASSWORD', '')

    if not email or not password:
        print("❌ ERROR: LinkedIn credentials not found in .env file")
        print("   Please add:")
        print("   LINKEDIN_EMAIL=your_email@example.com")
        print("   LINKEDIN_PASSWORD=your_password")
        return

    print(f"✅ Credentials loaded: {email}")

    # Simple config
    config = {
        'linkedin_email': email,
        'linkedin_password': password,
        'keyword': 'Python Developer',  # Try different keyword
        'location': 'India',  # Try different location
        'resume_path': 'data/resumes/Sathwika Digoppula Resume.pdf',
        'user_profile': {
            'first_name': 'Sathwika',
            'last_name': 'Digoppula',
            'email': email,
            'phone_number': '7569663306',
            'phone_country_code': 'India (+91)',
            'location': 'Hyderabad, India',
        },
        'max_applications': 1,  # Just test 1 application
        'dry_run': True  # Don't actually submit
    }

    print(f"🔍 Testing search: '{config['keyword']}' in '{config['location']}'")
    print(f"🎯 Max applications: {config['max_applications']}")
    print(f"🧪 Dry run: {config['dry_run']}")
    print()

    bot = AutoAgentHireBot(config)

    try:
        print("1️⃣ INITIALIZING BROWSER...")
        await bot.initialize_browser(use_persistent_profile=True)
        print("   ✅ Browser initialized")

        print("\n2️⃣ TESTING LINKEDIN LOGIN...")
        login_success = await bot.login_linkedin()
        if not login_success:
            print("   ❌ Login failed")
            return
        print("   ✅ Login successful")

        print("\n3️⃣ TESTING JOB SEARCH...")
        await bot.search_jobs(
            keyword=config['keyword'],
            location=config['location']
        )
        print("   ✅ Search executed")

        print("\n4️⃣ COLLECTING JOB LISTINGS...")
        jobs = await bot.collect_job_listings(max_jobs=10)
        print(f"   📊 Found {len(jobs)} jobs")

        if len(jobs) == 0:
            print("\n❌ NO JOBS FOUND!")
            print("   This means your LinkedIn account has no Easy Apply jobs")
            print("   for the search criteria.")
            print("\n💡 Try these solutions:")
            print("   1. Different keywords: 'Junior Developer', 'Entry Level'")
            print("   2. Different location: 'United States', 'Remote'")
            print("   3. Check manually on LinkedIn if Easy Apply jobs exist")
            return

        print("\n📋 First few jobs found:")
        for i, job in enumerate(jobs[:3], 1):
            print(f"   {i}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")

        print("\n5️⃣ TESTING SINGLE APPLICATION...")
        if len(jobs) > 0:
            test_job = jobs[0]
            print(f"   Testing application to: {test_job.get('title', 'Unknown')}")

            result = await bot.apply_to_single_job(
                job_url=test_job.get('url', '')
            )

            status = result.get('application_status', 'UNKNOWN')
            print(f"   📊 Application status: {status}")

            if status == 'APPLIED':
                print("   ✅ Application successful!")
            elif status == 'DRY_RUN':
                print("   🧪 Dry run completed (reached submit page)")
            elif status == 'NEEDS_REVIEW':
                print("   ⚠️ Needs manual review")
                print(f"   Reason: {result.get('application_reason', 'Unknown')}")
            else:
                print("   ❌ Application failed")
                print(f"   Reason: {result.get('application_reason', 'Unknown')}")

        print("\n✅ DIAGNOSTIC COMPLETE")
        print("   If you see jobs above, automation is working!")
        print("   If no jobs found, try different search terms.")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🧹 Cleaning up...")
        await bot.close()
        print("✅ Done")

if __name__ == "__main__":
    asyncio.run(diagnostic_test())