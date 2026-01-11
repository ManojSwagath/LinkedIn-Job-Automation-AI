#!/usr/bin/env python3
"""
Quick test to find Easy Apply jobs with different search terms
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from backend.agents.ultimate_linkedin_bot import UltimateLinkedInBot

# Load environment variables
load_dotenv()

# User Profile
USER_PROFILE = {
    "first_name": "SATHWIK",
    "last_name": "ADIGOPPULA",
    "email": "sathwikadigoppula888@gmail.com",
    "phone_number": "7569663306",
    "phone_country_code": "India (+91)",
    "location": "Hyderabad, Telangana, India",
    "years_experience_python": "1",
    "years_experience_azure": "1",
    "can_start_immediately": "Yes",
    "legally_authorized": "Yes",
    "require_sponsorship": "No",
}

async def search_jobs(keyword, location):
    """Test search with specific keywords"""
    print(f"\n{'='*80}")
    print(f"🔍 Testing: {keyword} in {location}")
    print(f"{'='*80}")
    
    config = {
        'linkedin_email': os.getenv('LINKEDIN_EMAIL', ''),
        'linkedin_password': os.getenv('LINKEDIN_PASSWORD', ''),
        'keyword': keyword,
        'location': location,
        'max_applications': 0,  # Don't apply, just search
        'easy_apply_only': True,
        'auto_apply': False,  # Just search mode
        'resume_path': str(Path('data/resumes/placeholder_resume.pdf').absolute()),
        'user_profile': USER_PROFILE,
        'dry_run': True,  # Don't actually apply
        'headless': True,
    }
    
    bot = UltimateLinkedInBot(config)
    
    try:
        # Initialize and login
        await bot.initialize_browser()
        await bot.linkedin_login()
        
        # Search for jobs
        jobs = await bot.search_jobs()
        print(f"✅ Found {len(jobs)} Easy Apply jobs")
        
        if bot.browser is not None:
            await bot.browser.close()
        return len(jobs)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if bot.browser is not None:
            await bot.browser.close()
        return 0
        return 0

async def main():
    """Test multiple search combinations"""
    print("\n" + "="*80)
    print("🚀 LinkedIn Easy Apply Job Search Test")
    print("="*80)
    
    # Test different search terms
    search_terms = [
        ("Python Developer", "India"),
        ("Software Engineer", "India"),
        ("Full Stack Developer", "India"),
        ("Backend Developer", "India"),
        ("AI Engineer", "India"),
        ("Data Analyst", "India"),
        ("Python Developer", "Hyderabad"),
        ("Software Engineer", "Hyderabad"),
    ]
    
    results = {}
    for keyword, location in search_terms:
        count = await search_jobs(keyword, location)
        results[f"{keyword} in {location}"] = count
        await asyncio.sleep(2)  # Be polite to LinkedIn
    
    # Summary
    print("\n" + "="*80)
    print("📊 SEARCH RESULTS SUMMARY")
    print("="*80)
    for search, count in results.items():
        print(f"   {search}: {count} jobs")
    
    # Find best option
    best_search = max(results.items(), key=lambda x: x[1])
    print(f"\n🎯 Best Option: {best_search[0]} with {best_search[1]} Easy Apply jobs")

if __name__ == "__main__":
    asyncio.run(main())
