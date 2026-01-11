"""
WORKING AUTOMATION - Ready to use!
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

from backend.agents.autoagenthire_bot import AutoAgentHireBot

async def run_working_automation():
    """Run the automation with working search terms"""

    print("=" * 80)
    print("🚀 LINKEDIN AUTOMATION - READY TO APPLY!")
    print("=" * 80)

    # Check credentials
    email = os.getenv('LINKEDIN_EMAIL', '')
    password = os.getenv('LINKEDIN_PASSWORD', '')

    if not email or not password:
        print("❌ ERROR: LinkedIn credentials not found")
        print("   Add to .env file:")
        print("   LINKEDIN_EMAIL=your_email@example.com")
        print("   LINKEDIN_PASSWORD=your_password")
        return

    print(f"✅ Credentials loaded: {email}")

    # CONFIGURATION - WORKING SEARCH TERMS
    config = {
        'linkedin_email': email,
        'linkedin_password': password,
        'keyword': 'Python Developer',  # ✅ WORKING: Found 5 jobs
        'location': 'India',            # ✅ WORKING: Found jobs
        'resume_path': 'data/resumes/Sathwika Digoppula Resume.pdf',
        'user_profile': {
            'first_name': 'Sathwika',
            'last_name': 'Digoppula',
            'email': email,
            'phone_number': '7569663306',
            'phone_country_code': 'India (+91)',
            'location': 'Hyderabad, India',
        },
        'max_applications': 2,  # Apply to 2 jobs
        'dry_run': False       # Actually submit applications
    }

    print("\n📋 CONFIGURATION:")
    print(f"   Search: '{config['keyword']}' in '{config['location']}'")
    print(f"   Resume: {config['resume_path']}")
    print(f"   Max Applications: {config['max_applications']}")
    print(f"   Dry Run: {config['dry_run']}")
    print()

    bot = AutoAgentHireBot(config)

    try:
        print("1️⃣ INITIALIZING BROWSER...")
        await bot.initialize_browser(use_persistent_profile=True)
        print("   ✅ Browser ready")

        print("\n2️⃣ LINKEDIN LOGIN...")
        login_success = await bot.login_linkedin()
        if not login_success:
            print("   ❌ Login failed")
            return
        print("   ✅ Login successful")

        print("\n3️⃣ JOB SEARCH...")
        await bot.search_jobs(
            keyword=config['keyword'],
            location=config['location']
        )
        print("   ✅ Search executed")

        print("\n4️⃣ COLLECTING JOBS...")
        jobs = await bot.collect_job_listings(max_jobs=10)
        print(f"   📊 Found {len(jobs)} Easy Apply jobs")

        if len(jobs) == 0:
            print("\n❌ No Easy Apply jobs found")
            print("   Try different search terms:")
            print("   - 'Junior Developer' in 'India'")
            print("   - 'Python Developer' in 'United States'")
            print("   - 'Full Stack Developer' in 'Remote'")
            return

        print("\n📋 Jobs to apply to:")
        for i, job in enumerate(jobs[:config['max_applications']], 1):
            print(f"   {i}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")

        print(f"\n5️⃣ APPLYING TO {min(len(jobs), config['max_applications'])} JOBS...")

        applied_count = 0
        successful_count = 0

        for i, job in enumerate(jobs[:config['max_applications']], 1):
            print(f"\n─" * 60)
            print(f"APPLICATION #{i}")
            print(f"─" * 60)
            print(f"Job: {job.get('title', 'Unknown')}")
            print(f"Company: {job.get('company', 'Unknown')}")
            print(f"URL: {job.get('url', 'Unknown')}")

            try:
                result = await bot.apply_to_single_job(
                    job_url=job.get('url', '')
                )

                status = result.get('application_status', 'UNKNOWN')
                applied_count += 1

                if status == 'APPLIED':
                    successful_count += 1
                    print("   ✅ SUCCESS: Application submitted!")
                elif status == 'NEEDS_REVIEW':
                    print("   ⚠️ NEEDS REVIEW: Manual input required")
                    print(f"   Reason: {result.get('application_reason', 'Unknown')}")
                else:
                    print("   ❌ FAILED: Application not completed")
                    print(f"   Reason: {result.get('application_reason', 'Unknown')}")

                # Wait between applications
                if i < config['max_applications']:
                    print("   ⏳ Waiting 8 seconds before next application...")
                    await asyncio.sleep(8)

            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")

        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Jobs Found: {len(jobs)}")
        print(f"Applications Attempted: {applied_count}")
        print(f"Successful: {successful_count}")
        print(f"Failed: {applied_count - successful_count}")

        if successful_count > 0:
            print("\n🎉 SUCCESS! Applications submitted:")
            for job in bot.applied_jobs:
                if job.get('application_status') == 'APPLIED':
                    print(f"   ✅ {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")

        print("\n✅ AUTOMATION COMPLETE!")
        print("   Check your LinkedIn applications to verify submissions.")

    except KeyboardInterrupt:
        print("\n\n⚠️ Automation interrupted by user")
        print("   Applications may have been partially submitted")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🧹 Cleaning up...")
        await bot.close()
        print("✅ Done")

if __name__ == "__main__":
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "LinkedIn Job Automation - WORKING VERSION" + " " * 15 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    asyncio.run(run_working_automation())