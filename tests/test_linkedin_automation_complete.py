#!/usr/bin/env python3
"""
Complete LinkedIn Easy Apply Automation Test
Demonstrates the full workflow matching LinkedIn's actual UI
Uses the ULTIMATE AI Agent Bot implementation
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from backend.agents.ultimate_linkedin_bot import UltimateLinkedInBot

# Load environment variables from .env file
load_dotenv()

# User Profile Data (from your screenshots)
USER_PROFILE = {
    # Contact Information (Page 1 - Contact info)
    "first_name": "SATHWIK",
    "last_name": "ADIGOPPULA",
    "email": "sathwikadigoppula888@gmail.com",
    "phone_number": "7569663306",
    "phone_country_code": "India (+91)",
    "location": "Hyderabad, Telangana, India",
    
    # Professional Information
    "title": "AI Engineer | Generative AI, RAG, NLP, Deep Learning | Final-Year B.Tech AIML @Viswam AI Intern",
    "linkedin_url": "https://www.linkedin.com/in/sathwik-adigoppula",
    
    # Experience (Page 3 - Additional Questions)
    "years_experience_python": "1",
    "years_experience_azure": "1",
    "comfortable_remote": "Yes",
    
    # Work Authorization (Page 4 - Work authorization)
    "can_start_immediately": "Yes",
    "legally_authorized": "Yes",
    "require_sponsorship": "No",
    "willing_to_relocate": True,
    
    # Additional fields for smart filling
    "city": "Hyderabad",
    "state": "Telangana",
    "country": "India",
}

async def test_complete_automation():
    """
    Test complete LinkedIn Easy Apply automation workflow
    Following the exact steps shown in the screenshots
    """
    
    print("=" * 80)
    print("🤖 LinkedIn Easy Apply Automation - Complete Workflow Test")
    print("=" * 80)
    print()
    
    # Configuration
    config = {
        # LinkedIn Credentials
        'linkedin_email': os.getenv('LINKEDIN_EMAIL', ''),
        'linkedin_password': os.getenv('LINKEDIN_PASSWORD', ''),
        
        # Job Search Parameters
        # UPDATED: Using search criteria with actual Easy Apply jobs
        'keyword': 'Software Engineer',  # Better results than "Web Developer"
        'location': 'Remote',            # More Easy Apply jobs than "India"
        'max_applications': 5,           # Test with 5 jobs
        'easy_apply_only': True,      # CRITICAL: Easy Apply filter
        'auto_apply': True,           # Enable auto-apply
        
        # Resume Upload (Page 2 - Resume)
        'resume_path': str(Path('data/resumes/placeholder_resume.pdf').absolute()),
        
        # User Profile for Form Filling
        'user_profile': USER_PROFILE,
        
        # Safety Settings
        'dry_run': False,  # Set to True to test without submitting
        'search_only': False,  # Set to True to only search, not apply
    }
    
    # Validate configuration
    if not config['linkedin_email'] or not config['linkedin_password']:
        print("❌ ERROR: LinkedIn credentials not set!")
        print("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables")
        print()
        print("Example:")
        print("  export LINKEDIN_EMAIL='your_email@example.com'")
        print("  export LINKEDIN_PASSWORD='your_password'")
        return
    
    if not Path(config['resume_path']).exists():
        print(f"❌ ERROR: Resume not found at: {config['resume_path']}")
        print("Please ensure your resume file exists")
        return
    
    print("✅ Configuration validated")
    print(f"   Email: {config['linkedin_email']}")
    print(f"   Search: {config['keyword']} in {config['location']}")
    print(f"   Resume: {Path(config['resume_path']).name}")
    print(f"   Max Applications: {config['max_applications']}")
    print(f"   Dry Run: {config['dry_run']}")
    print()
    
    # Initialize ULTIMATE Bot
    print("🚀 Initializing ULTIMATE LinkedIn Bot...")
    print("   This bot follows the exact LinkedIn Easy Apply workflow")
    print("   from your comprehensive AI agent prompt!")
    print()
    bot = UltimateLinkedInBot(config)
    
    try:
        # Execute automation (bot handles all phases internally with detailed logging)
        result = await bot.run_automation()
        
        # Result summary already printed by bot
        print("\n" + "🎯" * 40)
        print("AUTOMATION COMPLETE!")
        print("🎯" * 40)
        
        # Save detailed log
        log_file = Path('data/logs/automation_log.txt')
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'w') as f:
            f.write("LinkedIn Easy Apply Automation - Complete Log\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Configuration:\n")
            f.write(f"  Search: {config['keyword']} in {config['location']}\n")
            f.write(f"  Max Applications: {config['max_applications']}\n")
            f.write(f"  Dry Run: {config['dry_run']}\n\n")
            f.write(f"Results:\n")
            f.write(f"  Jobs Found: {result.get('jobs_found', 0)}\n")
            f.write(f"  Applications Attempted: {result.get('applications_attempted', 0)}\n")
            f.write(f"  Successful: {result.get('applications_successful', 0)}\n")
            f.write(f"  Failed: {result.get('applications_failed', 0)}\n\n")
            f.write("Detailed Job List:\n")
            for i, job in enumerate(result.get('jobs', []), 1):
                f.write(f"\n{i}. {job.get('title')} at {job.get('company')}\n")
                f.write(f"   Location: {job.get('location')}\n")
                f.write(f"   Status: {job.get('application_status', 'N/A')}\n")
                if job.get('error'):
                    f.write(f"   Error: {job.get('error')}\n")
        
        print(f"\n📝 Detailed log saved to: {log_file}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await bot.close()
        print("\n🧹 Browser closed and resources released")


async def test_search_only():
    """Test job search without applying (demo mode)"""
    print("=" * 80)
    print("🔍 LinkedIn Job Search - Demo Mode (No Applications)")
    print("=" * 80)
    print()
    
    config = {
        'linkedin_email': os.getenv('LINKEDIN_EMAIL', 'demo@example.com'),
        'linkedin_password': os.getenv('LINKEDIN_PASSWORD', 'demo'),
        'keyword': 'Web Developer',
        'location': 'India',
        'max_applications': 0,  # Don't apply
        'dry_run': True,  # Dry run mode
        'user_profile': {},
        'resume_path': ''
    }
    
    bot = UltimateLinkedInBot(config)
    
    try:
        print("📝 Searching for Easy Apply jobs...")
        await bot.initialize_browser()
        login_success = await bot.linkedin_login()
        
        if login_success:
            jobs = await bot.search_jobs()
            print(f"\n✅ Found {len(jobs)} Easy Apply jobs!")
            print("\nJob cards loaded. Review in browser window.")
        else:
            print("❌ Login failed")
        
        # Keep browser open for inspection
        print("\n⏸️  Browser will remain open for inspection.")
        print("   Press Ctrl+C to close...")
        await asyncio.sleep(300)  # Keep open for 5 minutes
        
    except KeyboardInterrupt:
        print("\n👋 Closing...")
    finally:
        await bot.close()


if __name__ == "__main__":
    import sys
    
    print()
    print("LinkedIn Easy Apply Automation Test Suite")
    print("=" * 80)
    print()
    print("Options:")
    print("  1. Run full automation (search + apply)")
    print("  2. Search only (demo mode)")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        asyncio.run(test_search_only())
    else:
        asyncio.run(test_complete_automation())
