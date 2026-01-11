"""
Complete Automation Test - Uses Backend API
Tests the full automation workflow through the backend
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.agents.autoagenthire_bot import AutoAgentHireBot
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_complete_automation():
    """Test complete automation workflow"""
    
    print("=" * 80)
    print("🤖 COMPLETE AUTOMATION TEST")
    print("=" * 80)
    print()
    
    # Check credentials
    email = os.getenv('LINKEDIN_EMAIL', '')
    password = os.getenv('LINKEDIN_PASSWORD', '')
    
    if not email or not password:
        print("❌ ERROR: LinkedIn credentials not found in .env file")
        print("\nPlease add to your .env file:")
        print("LINKEDIN_EMAIL=your_email@example.com")
        print("LINKEDIN_PASSWORD=your_password")
        return
    
    print(f"✅ Credentials loaded: {email}")
    print()
    
    # Configuration
    config = {
        'linkedin_email': email,
        'linkedin_password': password,
        'keyword': 'Software Engineer',  # Try broader search
        'location': 'Remote',
        'resume_path': 'data/resumes/Sathwika Digoppula Resume.pdf',
        'user_profile': {
            'first_name': 'Sathwika',
            'last_name': 'Digoppula',
            'email': email,
            'phone_number': '7569663306',
            'phone_country_code': 'India (+91)',
            'location': 'Hyderabad, India',
        },
        'max_applications': 3,  # Apply to 3 jobs
        'dry_run': False  # Actually submit
    }
    
    print("📋 Configuration:")
    print(f"   Search: {config['keyword']} in {config['location']}")
    print(f"   Max Applications: {config['max_applications']}")
    print(f"   Resume: {config['resume_path']}")
    print(f"   Dry Run: {config['dry_run']}")
    print()
    
    # Create bot
    bot = AutoAgentHireBot(config)
    
    try:
        print("=" * 80)
        print("PHASE 1: BROWSER INITIALIZATION")
        print("=" * 80)
        await bot.initialize_browser(use_persistent_profile=True)
        print("✅ Browser initialized\n")
        
        print("=" * 80)
        print("PHASE 2: LINKEDIN LOGIN")
        print("=" * 80)
        login_success = await bot.login_linkedin()
        
        if not login_success:
            print("❌ Login failed")
            print("\nPossible causes:")
            print("1. Incorrect credentials in .env")
            print("2. LinkedIn CAPTCHA (complete it in the browser)")
            print("3. Account locked or restricted")
            return
        
        print("✅ Login successful\n")
        
        print("=" * 80)
        print("PHASE 3: JOB SEARCH")
        print("=" * 80)
        
        # Search for jobs
        await bot.search_jobs(
            keyword=config['keyword'],
            location=config['location']
        )
        
        # Collect job listings
        print("📊 Collecting job listings...")
        jobs = await bot.collect_job_listings(max_jobs=20)
        
        print(f"✅ Found {len(jobs)} jobs\n")
        
        if len(jobs) == 0:
            print("⚠️  WARNING: No Easy Apply jobs found!")
            print("\nThis could mean:")
            print("1. Your LinkedIn account doesn't show Easy Apply jobs")
            print("2. No jobs match your search criteria with Easy Apply")
            print("3. You need LinkedIn Premium for Easy Apply access")
            print("\n💡 Try:")
            print("   - Different search keywords (e.g., 'Python Developer')")
            print("   - Different location (e.g., 'United States' or 'India')")
            print("   - Log into LinkedIn manually and verify you see 'Easy Apply' button")
            return
        
        print("📋 Found Jobs:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"   {i}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
            print(f"      Location: {job.get('location', 'Unknown')}")
        
        if len(jobs) > 5:
            print(f"   ... and {len(jobs) - 5} more jobs")
        print()
        
        print("=" * 80)
        print("PHASE 4: AUTO-APPLY")
        print("=" * 80)
        
        # Apply to jobs (let the bot handle the workflow)
        jobs_to_apply = min(len(jobs), config['max_applications'])
        print(f"📝 Will attempt to apply to {jobs_to_apply} jobs...")
        print()
        
        for i, job in enumerate(jobs[:jobs_to_apply], 1):
            print(f"─" * 80)
            print(f"APPLICATION #{i}/{jobs_to_apply}")
            print(f"─" * 80)
            print(f"Job: {job.get('title', 'Unknown')}")
            print(f"Company: {job.get('company', 'Unknown')}")
            print()
            
            try:
                result = await bot.apply_to_single_job(
                    job_url=job.get('url', '')
                )
                
                status = result.get('application_status', 'UNKNOWN')
                
                if status == 'APPLIED':
                    print(f"✅ APPLICATION #{i} SUCCESSFUL")
                elif status == 'DRY_RUN':
                    print(f"🧪 DRY RUN COMPLETE (not submitted)")
                elif status == 'NEEDS_REVIEW':
                    print(f"⚠️  NEEDS MANUAL REVIEW")
                    print(f"   Reason: {result.get('application_reason', 'Unknown')}")
                else:
                    print(f"❌ APPLICATION #{i} FAILED")
                    print(f"   Reason: {result.get('application_reason', 'Unknown')}")
                
                print()
                
                # Small delay between applications
                if i < jobs_to_apply:
                    print("⏳ Waiting 5 seconds before next application...")
                    await asyncio.sleep(5)
                    print()
                
            except Exception as e:
                print(f"❌ Error applying to job: {str(e)}")
                print()
        
        print("=" * 80)
        print("PHASE 5: SUMMARY")
        print("=" * 80)
        print(f"✅ Jobs Found: {len(jobs)}")
        print(f"✅ Applications Attempted: {jobs_to_apply}")
        print(f"✅ Successful: {len([j for j in bot.applied_jobs if j.get('application_status') == 'APPLIED'])}")
        print(f"⚠️  Failed: {len([j for j in bot.errors])}")
        print()
        
        if bot.applied_jobs:
            print("Successfully Applied To:")
            for job in bot.applied_jobs:
                if job.get('application_status') == 'APPLIED':
                    print(f"   ✅ {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
        
        print()
        print("=" * 80)
        print("✅ AUTOMATION COMPLETE")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Automation interrupted by user (Ctrl+C)")
        print("Cleaning up...")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🧹 Closing browser...")
        await bot.close()
        print("✅ Done!")

if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "LinkedIn Job Automation Test" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    asyncio.run(test_complete_automation())
