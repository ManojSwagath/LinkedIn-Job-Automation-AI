#!/usr/bin/env python3
"""
Complete Job Appl        }
        
        # Force visible browser with slower actions for better visibility
        os.environ["HEADLESS_BROWSER"] = "false"
        os.environ["BROWSER_SLOW_MO"] = "300"  # 300ms delay for visibilityon Automation - Working Version
Fixes browser stability and ensures full automation workflow
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Load environment
load_dotenv()

class StableJobApplicationPortal:
    """Job application portal with stable browser management."""
    
    def __init__(self):
        self.config = {
            "linkedin_email": os.getenv("LINKEDIN_EMAIL", ""),
            "linkedin_password": os.getenv("LINKEDIN_PASSWORD", ""),
            "keyword": os.getenv("JOB_KEYWORD", "Software Engineer"),
            "location": os.getenv("JOB_LOCATION", "Remote"),
            "max_applications": int(os.getenv("MAX_APPLICATIONS", "5")),
            "dry_run": False,
            "auto_apply": True,
            "user_profile": {
                "email": os.getenv("LINKEDIN_EMAIL", ""),
                "first_name": os.getenv("FIRST_NAME", ""),
                "last_name": os.getenv("LAST_NAME", ""),
                "phone_number": os.getenv("PHONE_NUMBER", ""),
                "city": os.getenv("CITY", ""),
                "state": os.getenv("STATE", ""),
                "zip_code": os.getenv("ZIP_CODE", ""),
                "linkedin_url": os.getenv("LINKEDIN_URL", ""),
                "github_url": os.getenv("GITHUB_URL", ""),
                "portfolio_url": os.getenv("PORTFOLIO_URL", ""),
            }
        }
        
        # Force visible browser for better stability
        os.environ["HEADLESS_BROWSER"] = "false"
        os.environ["BROWSER_SLOW_MO"] = "50"
    
    async def run_complete_workflow(self):
        """Run the complete application workflow with stable browser."""
        self.print_header()
        
        # Step 1: Validate credentials
        if not self.config["linkedin_email"] or not self.config["linkedin_password"]:
            print("❌ ERROR: LinkedIn credentials not found")
            print("   Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env")
            return
        
        print(f"📧 Email: {self.config['linkedin_email']}")
        print(f"🔍 Search: {self.config['keyword']} in {self.config['location']}")
        print(f"🎯 Max Applications: {self.config['max_applications']}")
        print()
        
        # Step 2: Parse resume
        resume_data = await self.parse_resume()
        if not resume_data:
            print("⚠️  No resume found, using config data")
        else:
            print(f"✅ Resume loaded: {resume_data.get('contact', {}).get('name', 'User')}")
        print()
        
        # Step 3: Initialize automation (ONCE for entire workflow)
        from backend.agents.autoagenthire_bot import AutoAgentHireBot
        
        bot = AutoAgentHireBot(self.config)
        
        try:
            # Step 4: Initialize browser (ONCE)
            print("🌐 Initializing browser (will stay open)...")
            await bot.initialize_browser(use_persistent_profile=True)
            print("✅ Browser initialized")
            print()
            
            # Step 5: Login (ONCE)
            print("🔐 Logging into LinkedIn...")
            login_success = await bot.login_linkedin()
            if not login_success:
                print("❌ Login failed - please check credentials")
                return
            print("✅ Login successful")
            print()
            
            # Step 6: Search jobs (ONCE)
            print(f"🔍 Searching for jobs: {self.config['keyword']} in {self.config['location']}")
            await bot.search_jobs(self.config["keyword"], self.config["location"])
            print("✅ Search completed")
            print()
            
            # Step 7: Collect job listings
            print("📋 Collecting job listings...")
            jobs = await bot.collect_job_listings(max_jobs=self.config["max_applications"])
            
            if not jobs:
                print("❌ No jobs found matching criteria")
                return
            
            print(f"✅ Collected {len(jobs)} Easy Apply jobs")
            print()
            
            # Step 8: Display job cards
            self.display_job_cards(jobs, resume_data)
            print()
            
            # Step 9: Apply to jobs (using SAME browser instance)
            print("🚀 Starting application process...")
            print("⏳ Browser will stay open for all applications")
            print("👀 WATCH THE BROWSER to see automation in action!")
            print()
            
            applied_count = 0
            successful_apps = []
            failed_apps = []
            
            for idx, job in enumerate(jobs, 1):
                job_title = job.get('title', 'Unknown')
                job_company = job.get('company', 'Unknown')
                
                print(f"━" * 80)
                print(f"[{idx}/{len(jobs)}] Applying to: {job_title}")
                print(f"           Company: {job_company}")
                print(f"           URL: {job.get('url', 'N/A')[:60]}...")
                print(f"━" * 80)
                print(f"👁️  WATCH BROWSER: Opening job page and Easy Apply modal...")
                
                try:
                    # Apply using the EXISTING browser/page (no re-initialization)
                    result = await bot.auto_apply_job(job)
                    
                    status = result.get('application_status', 'UNKNOWN')
                    
                    if status in ('APPLIED', 'SUCCESS'):
                        print(f"  ✅ APPLICATION SUBMITTED SUCCESSFULLY")
                        applied_count += 1
                        successful_apps.append({
                            'title': job_title,
                            'company': job_company,
                            'status': status
                        })
                    elif status == 'DRY_RUN':
                        print(f"  🧪 DRY RUN: Reached submit (did not click)")
                    elif status == 'NEEDS_REVIEW':
                        print(f"  ⚠️  NEEDS REVIEW: {result.get('application_reason', 'Manual review required')}")
                        failed_apps.append({
                            'title': job_title,
                            'company': job_company,
                            'reason': 'Needs manual review'
                        })
                    else:
                        reason = result.get('application_reason', 'Unknown error')
                        print(f"  ❌ FAILED: {reason}")
                        failed_apps.append({
                            'title': job_title,
                            'company': job_company,
                            'reason': reason
                        })
                    
                    # Delay between applications (human-like)
                    if idx < len(jobs):
                        delay = 10
                        print(f"  ⏳ Waiting {delay}s before next application...")
                        await asyncio.sleep(delay)
                    
                except KeyboardInterrupt:
                    print("\n⚠️  User interrupted - stopping automation")
                    raise
                except Exception as e:
                    print(f"  ❌ Application error: {str(e)[:100]}")
                    failed_apps.append({
                        'title': job_title,
                        'company': job_company,
                        'reason': str(e)[:100]
                    })
                
                print()
            
            # Step 10: Final Summary
            self.print_summary(jobs, applied_count, successful_apps, failed_apps)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Workflow interrupted by user (Ctrl+C)")
        except Exception as e:
            print(f"\n❌ Workflow failed: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean browser shutdown
            print("\n🔒 Closing browser...")
            await bot.close()
            print("✅ Browser closed gracefully")
    
    def print_header(self):
        """Print application header."""
        print()
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "  🎯 LINKEDIN JOB APPLICATION AUTOMATION - COMPLETE WORKFLOW".ljust(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        print("=" * 80)
        print("🚀 STABLE BROWSER AUTOMATION")
        print("=" * 80)
        print()
    
    async def parse_resume(self) -> Dict[str, Any]:
        """Parse resume and extract data."""
        resume_path = Path("data/resumes")
        
        # Find first resume
        if not resume_path.exists():
            return {}
        
        resumes = list(resume_path.glob("*.pdf")) + list(resume_path.glob("*.txt"))
        if not resumes:
            return {}
        
        print(f"📄 Found resume: {resumes[0].name}")
        
        # Use config data for now
        return {
            "contact": {
                "name": f"{self.config['user_profile'].get('first_name', '')} {self.config['user_profile'].get('last_name', '')}".strip() or "User",
                "email": self.config["linkedin_email"],
                "phone": self.config['user_profile'].get('phone_number', ''),
            },
            "skills": ["Python", "JavaScript", "React", "FastAPI", "Docker"],
        }
    
    def display_job_cards(self, jobs: List[Dict], resume_data: Dict):
        """Display job cards."""
        print("┌" + "─" * 78 + "┐")
        print("│" + " " * 28 + "📋 FOUND JOBS" + " " * 37 + "│")
        print("├" + "─" * 78 + "┤")
        
        for idx, job in enumerate(jobs, 1):
            title = job.get("title", "Unknown")[:45]
            company = job.get("company", "Unknown")[:30]
            location = job.get("location", "Remote")[:25]
            easy_apply = "✅ Easy Apply" if job.get("easy_apply") else "❌ Regular"
            
            print(f"│ [{idx}] {title:<47} │")
            print(f"│     🏢 {company:<44} │")
            print(f"│     📍 {location:<26} {easy_apply:<18} │")
            
            if idx < len(jobs):
                print("├" + "─" * 78 + "┤")
        
        print("└" + "─" * 78 + "┘")
    
    def print_summary(self, jobs: List[Dict], applied_count: int, successful_apps: List, failed_apps: List):
        """Print final summary."""
        print()
        print("=" * 80)
        print("📊 FINAL APPLICATION SUMMARY")
        print("=" * 80)
        print(f"Total jobs found:          {len(jobs)}")
        print(f"Applications submitted:    {applied_count}")
        print(f"Applications failed:       {len(failed_apps)}")
        print(f"Success rate:              {(applied_count/len(jobs)*100) if jobs else 0:.1f}%")
        print()
        
        if successful_apps:
            print("✅ SUCCESSFUL APPLICATIONS:")
            for app in successful_apps:
                print(f"   • {app['title']} at {app['company']}")
            print()
        
        if failed_apps:
            print("❌ FAILED APPLICATIONS:")
            for app in failed_apps:
                print(f"   • {app['title']} at {app['company']}")
                print(f"     Reason: {app['reason']}")
            print()
        
        if applied_count > 0:
            print("🎉 Workflow completed successfully!")
        elif failed_apps:
            print("⚠️  Some applications require manual attention")
        else:
            print("⚠️  No applications were submitted")
        
        print("=" * 80)


async def main():
    """Main entry point."""
    portal = StableJobApplicationPortal()
    await portal.run_complete_workflow()


if __name__ == "__main__":
    asyncio.run(main())
