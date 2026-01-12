#!/usr/bin/env python3
"""
Automated LinkedIn Test - No Interaction Required
Runs the complete automation test and reports results
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from backend.agents.ultimate_linkedin_bot import UltimateLinkedInBot
from datetime import datetime

load_dotenv()

USER_PROFILE = {
    "first_name": "SATHWIK",
    "last_name": "ADIGOPPULA",
    "email": "sathwikadigoppula888@gmail.com",
    "phone_number": "7569663306",
    "phone_country_code": "India (+91)",
    "location": "Hyderabad, Telangana, India",
    "title": "AI Engineer",
    "linkedin_url": "https://www.linkedin.com/in/sathwik-adigoppula",
    "years_experience_python": "1",
    "years_experience_azure": "1",
    "comfortable_remote": "Yes",
    "can_start_immediately": "Yes",
    "legally_authorized": "Yes",
    "require_sponsorship": "No",
    "willing_to_relocate": True,
    "city": "Hyderabad",
    "state": "Telangana",
    "country": "India",
}

async def run_automated_test():
    """Run automated test with predefined configuration"""
    
    print("\n" + "=" * 80)
    print("🤖 AUTOMATED LINKEDIN EASY APPLY TEST")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Configuration
    config = {
        'linkedin_email': os.getenv('LINKEDIN_EMAIL', ''),
        'linkedin_password': os.getenv('LINKEDIN_PASSWORD', ''),
        'keyword': 'Software Engineer',
        'location': 'Remote',
        'max_applications': 2,  # Small number for testing
        'easy_apply_only': True,
        'auto_apply': True,
        'resume_path': str(Path('data/resumes/placeholder_resume.pdf').absolute()),
        'user_profile': USER_PROFILE,
        'dry_run': False,  # Real applications
        'search_only': False,
    }
    
    # Validate credentials
    if not config['linkedin_email'] or not config['linkedin_password']:
        print("❌ ERROR: LinkedIn credentials not set in .env file")
        print("   Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD")
        return
    
    if not Path(config['resume_path']).exists():
        print(f"❌ ERROR: Resume not found at: {config['resume_path']}")
        return
    
    print("✅ Configuration validated")
    print(f"   📧 Email: {config['linkedin_email']}")
    print(f"   🔍 Search: {config['keyword']} in {config['location']}")
    print(f"   📄 Resume: {Path(config['resume_path']).name}")
    print(f"   🎯 Max Applications: {config['max_applications']}")
    print(f"   🧪 Dry Run: {config['dry_run']}")
    print()
    
    # Initialize bot
    print("🚀 Initializing bot...")
    bot = UltimateLinkedInBot(config)
    
    try:
        # Run automation
        result = await bot.run_automation()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        print()
        print(f"Status: {result.get('status', 'Unknown')}")
        print(f"Jobs Found: {result.get('jobs_found', 0)}")
        print(f"Applications Attempted: {result.get('applications_attempted', 0)}")
        print(f"✅ Successful: {result.get('applications_successful', 0)}")
        print(f"❌ Failed: {result.get('applications_failed', 0)}")
        
        if result.get('applications_attempted', 0) > 0:
            success_rate = (result.get('applications_successful', 0) / result.get('applications_attempted', 1)) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print()
        
        # Save detailed report
        report_file = Path('data/logs/automated_test_report.txt')
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write(f"LinkedIn Automation Test Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\n{'=' * 80}\n\n")
            f.write(f"Configuration:\n")
            f.write(f"  Search: {config['keyword']} in {config['location']}\n")
            f.write(f"  Max Applications: {config['max_applications']}\n")
            f.write(f"  Dry Run: {config['dry_run']}\n\n")
            f.write(f"Results:\n")
            f.write(f"  Status: {result.get('status', 'Unknown')}\n")
            f.write(f"  Jobs Found: {result.get('jobs_found', 0)}\n")
            f.write(f"  Applications Attempted: {result.get('applications_attempted', 0)}\n")
            f.write(f"  Successful: {result.get('applications_successful', 0)}\n")
            f.write(f"  Failed: {result.get('applications_failed', 0)}\n")
        
        print(f"📝 Report saved to: {report_file}")
        print()
        
        # Determine test verdict
        if result.get('jobs_found', 0) == 0:
            print("⚠️  TEST STATUS: NO EASY APPLY JOBS FOUND")
            print("   This is NOT a code issue.")
            print("   Your LinkedIn account/search doesn't have Easy Apply jobs.")
            print("   Try: Different search terms or LinkedIn account")
        elif result.get('applications_successful', 0) > 0:
            print("✅ TEST STATUS: SUCCESS")
            print(f"   Successfully applied to {result.get('applications_successful', 0)} job(s)")
        elif result.get('applications_attempted', 0) > 0:
            print("⚠️  TEST STATUS: PARTIAL SUCCESS")
            print("   Applications attempted but encountered issues")
        else:
            print("❌ TEST STATUS: FAILED")
            print("   Check logs for details")
        
        print()
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🧹 Cleaning up...")
        await bot.close()
        print("✅ Cleanup complete")
    
    print()
    print("=" * 80)
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()


if __name__ == "__main__":
    print("\n🔄 Starting automated test...")
    print("   (This will run without requiring user input)")
    print()
    
    asyncio.run(run_automated_test())
    
    print("✅ Test execution complete!")
    print()
