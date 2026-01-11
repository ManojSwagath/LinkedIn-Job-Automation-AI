"""
Quick test to identify automation issues
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import the bot
from backend.agents.ultimate_linkedin_bot import UltimateLinkedInBot

async def test_automation():
    """Test the automation quickly"""
    print("=" * 80)
    print("🧪 QUICK AUTOMATION TEST")
    print("=" * 80)
    
    # Configuration
    config = {
        'linkedin_email': os.getenv('LINKEDIN_EMAIL', ''),
        'linkedin_password': os.getenv('LINKEDIN_PASSWORD', ''),
        'keyword': 'Software Engineer',
        'location': 'Remote',
        'resume_path': str(Path('data/resumes/Sathwika Digoppula Resume.pdf')),
        'user_profile': {
            'first_name': 'Sathwika',
            'last_name': 'Digoppula',
            'email': os.getenv('LINKEDIN_EMAIL', ''),
            'phone_number': '7569663306',
            'phone_country_code': 'India (+91)',
            'location': 'Hyderabad, India'
        },
        'max_applications': 2,  # Test with just 2 applications
        'dry_run': False  # Actually submit
    }
    
    # Verify credentials
    if not config['linkedin_email'] or not config['linkedin_password']:
        print("❌ ERROR: LinkedIn credentials not found in .env file")
        print("   Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env")
        return
    
    print(f"\n📧 Email: {config['linkedin_email']}")
    print(f"🔍 Search: {config['keyword']} in {config['location']}")
    print(f"📄 Resume: {config['resume_path']}")
    print(f"🎯 Max Applications: {config['max_applications']}")
    print()
    
    # Create and run bot
    bot = UltimateLinkedInBot(config)
    
    try:
        result = await bot.run_automation()
        
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Jobs Found: {result['jobs_found']}")
        print(f"Applications Attempted: {result['applications_attempted']}")
        print(f"Successful: {result['applications_successful']}")
        print(f"Failed: {result['applications_failed']}")
        
        if result['errors']:
            print("\n❌ Errors:")
            for error in result['errors']:
                print(f"   - {error}")
        
        if result['applied_jobs']:
            print("\n✅ Applied to:")
            for job in result['applied_jobs']:
                print(f"   - {job['title']} at {job['company']}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(test_automation())
