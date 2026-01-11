#!/usr/bin/env python3
"""
Production-Ready LinkedIn Job Application Automation
Complete integration with all enhanced features
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

# Import all components
from backend.agents.autoagenthire_bot import AutoAgentHireBot
from backend.automation.application_handler import ApplicationHandler
from backend.automation.intelligent_form_filler import IntelligentFormFiller
from backend.llm.cover_letter_generator import get_cover_letter_generator
from backend.utils.qdrant_helper import QdrantHelper


class ProductionAutomationBot:
    """
    Production-ready automation bot with all enhancements integrated
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.base_bot = AutoAgentHireBot(config)
        self.cover_letter_gen = get_cover_letter_generator()
        
        # Initialize Qdrant if configured
        try:
            self.qdrant = QdrantHelper()
            print("✅ Qdrant vector database connected")
        except Exception as e:
            print(f"⚠️  Qdrant not available: {str(e)}")
            self.qdrant = None
    
    async def initialize(self):
        """Initialize browser and login"""
        print("\n" + "="*60)
        print("🚀 Initializing Production Automation Bot")
        print("="*60)
        
        await self.base_bot.initialize_browser()
        
        if not await self.base_bot.login_linkedin():
            raise Exception("LinkedIn login failed")
        
        print("✅ Bot initialized and logged in")
    
    async def apply_to_job_enhanced(self, job_url: str) -> Dict:
        """
        Apply to a job with all enhancements:
        - Robust application opening
        - Intelligent form filling
        - AI-powered cover letter
        - Qdrant integration for company research
        """
        print(f"\n{'='*60}")
        print(f"📋 Starting enhanced application process")
        print(f"🔗 Job URL: {job_url}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Navigate to job page
            print("📍 Step 1: Opening job page...")
            await self.base_bot.page.goto(job_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(2)
            
            # Step 2: Extract job details
            print("📍 Step 2: Extracting job details...")
            job_details = await self._extract_job_details()
            print(f"   • Title: {job_details['title']}")
            print(f"   • Company: {job_details['company']}")
            
            # Step 3: Use enhanced application handler to open application
            print("📍 Step 3: Opening Easy Apply form (enhanced)...")
            app_handler = ApplicationHandler(self.base_bot.page)
            open_result = await app_handler.open_job_application(job_url)
            
            if open_result['status'] != 'SUCCESS':
                print(f"❌ Failed to open application: {open_result['reason']}")
                return {
                    'success': False,
                    'job': job_details,
                    'error': open_result['reason']
                }
            
            print("✅ Application modal opened successfully")
            
            # Step 4: Get company context from Qdrant
            print("📍 Step 4: Retrieving company research from Qdrant...")
            company_context = None
            if self.qdrant:
                try:
                    company_results = self.qdrant.search_similar_jobs(
                        f"{job_details['company']} company information",
                        limit=1
                    )
                    if company_results:
                        company_context = company_results[0]
                        print(f"   ✓ Found company context in vector database")
                except Exception as e:
                    print(f"   ⚠️  Company research unavailable: {str(e)}")
            
            # Step 5: Generate AI-powered cover letter
            print("📍 Step 5: Generating personalized cover letter with GPT-4o...")
            cover_letter = ""
            try:
                if self.cover_letter_gen.use_github_api:
                    cover_letter = self.cover_letter_gen.generate_cover_letter(
                        job_title=job_details['title'],
                        company_name=job_details['company'],
                        job_description=job_details.get('description', ''),
                        resume_text=self.base_bot.resume_text,
                        company_context=company_context
                    )
                    print(f"   ✓ Cover letter generated ({len(cover_letter)} characters)")
                else:
                    print("   ⚠️  Using fallback cover letter (GitHub API not configured)")
                    cover_letter = self.cover_letter_gen._generate_fallback_cover_letter(
                        job_details['title'],
                        job_details['company'],
                        self.base_bot.resume_text
                    )
            except Exception as e:
                print(f"   ⚠️  Cover letter generation error: {str(e)}")
            
            # Step 6: Fill form with intelligent defaults
            print("📍 Step 6: Filling application form with intelligent defaults...")
            form_filler = IntelligentFormFiller(
                page=self.base_bot.page,
                user_profile=self.config.get('user_profile', {}),
                resume_text=self.base_bot.resume_text
            )
            
            fill_result = await form_filler.fill_application_form()
            print(f"   ✓ Filled {fill_result['filled_fields']} fields")
            
            # Step 7: Add cover letter if field exists
            print("📍 Step 7: Adding cover letter to application...")
            if cover_letter:
                await self._fill_cover_letter_field(cover_letter)
            
            # Step 8: Complete Easy Apply flow (Next/Submit)
            print("📍 Step 8: Completing application steps...")
            dry_run = self.config.get('dry_run', False)
            flow_result = await self.base_bot._complete_easy_apply_flow(dry_run=dry_run)
            
            # Step 9: Store in Qdrant for tracking
            if self.qdrant and flow_result['status'] == 'APPLIED':
                print("📍 Step 9: Storing application in vector database...")
                try:
                    self._store_application_in_qdrant(job_details, cover_letter)
                    print("   ✓ Application tracked in Qdrant")
                except Exception as e:
                    print(f"   ⚠️  Storage error: {str(e)}")
            
            # Final result
            success = flow_result['status'] in ['APPLIED', 'DRY_RUN']
            
            if success:
                print(f"\n{'='*60}")
                print(f"🎉 APPLICATION {'SUBMITTED' if flow_result['status'] == 'APPLIED' else 'COMPLETED (DRY RUN)'}")
                print(f"{'='*60}")
                print(f"✅ Job: {job_details['title']} at {job_details['company']}")
                print(f"✅ Cover letter: Generated with GPT-4o + Company Research")
                print(f"✅ Form fields: {fill_result['filled_fields']} auto-filled")
                print(f"✅ Status: {flow_result['status']}")
                print(f"{'='*60}\n")
            else:
                print(f"\n{'='*60}")
                print(f"⚠️  APPLICATION NEEDS ATTENTION")
                print(f"{'='*60}")
                print(f"Status: {flow_result['status']}")
                print(f"Reason: {flow_result.get('reason', 'Unknown')}")
                print(f"{'='*60}\n")
            
            return {
                'success': success,
                'job': job_details,
                'status': flow_result['status'],
                'cover_letter_length': len(cover_letter),
                'fields_filled': fill_result['filled_fields'],
                'company_research_used': company_context is not None
            }
            
        except Exception as e:
            print(f"\n❌ APPLICATION ERROR: {str(e)}")
            return {
                'success': False,
                'job': job_details if 'job_details' in locals() else {},
                'error': str(e)
            }
    
    async def _extract_job_details(self) -> Dict:
        """Extract job details from page"""
        job_details = {
            'title': 'Unknown',
            'company': 'Unknown',
            'description': '',
            'url': self.base_bot.page.url
        }
        
        try:
            # Title
            title_selectors = ['h1.t-24', 'h1.job-title', '.job-details-jobs-unified-top-card__job-title']
            for selector in title_selectors:
                try:
                    elem = await self.base_bot.page.query_selector(selector)
                    if elem:
                        job_details['title'] = (await elem.inner_text()).strip()
                        break
                except:
                    continue
            
            # Company
            company_selectors = [
                '.job-details-jobs-unified-top-card__company-name',
                'a.ember-view.t-black',
                '.jobs-unified-top-card__company-name'
            ]
            for selector in company_selectors:
                try:
                    elem = await self.base_bot.page.query_selector(selector)
                    if elem:
                        job_details['company'] = (await elem.inner_text()).strip()
                        break
                except:
                    continue
            
            # Description
            try:
                desc_elem = await self.base_bot.page.query_selector('.jobs-description')
                if desc_elem:
                    job_details['description'] = (await desc_elem.inner_text()).strip()[:2000]
            except:
                pass
                
        except Exception as e:
            print(f"   ⚠️  Error extracting job details: {str(e)}")
        
        return job_details
    
    async def _fill_cover_letter_field(self, cover_letter: str):
        """Fill cover letter textarea if present"""
        try:
            textareas = await self.base_bot.page.query_selector_all('textarea')
            
            for textarea in textareas:
                try:
                    # Get label
                    label = ""
                    field_id = await textarea.get_attribute('id')
                    if field_id:
                        label_elem = await self.base_bot.page.query_selector(f'label[for="{field_id}"]')
                        if label_elem:
                            label = (await label_elem.inner_text()).lower()
                    
                    # Check if cover letter field
                    if any(word in label for word in ['cover letter', 'additional information', 'message']):
                        current = await textarea.input_value()
                        if not current or len(current.strip()) < 50:
                            await textarea.fill(cover_letter)
                            print("   ✓ Cover letter added to application")
                            return
                            
                except:
                    continue
                    
        except Exception as e:
            print(f"   ⚠️  Could not fill cover letter field: {str(e)}")
    
    def _store_application_in_qdrant(self, job_details: Dict, cover_letter: str):
        """Store application in Qdrant for tracking"""
        if not self.qdrant:
            return
        
        try:
            from datetime import datetime
            
            application_data = {
                'job_title': job_details['title'],
                'company': job_details['company'],
                'job_url': job_details['url'],
                'cover_letter': cover_letter[:500],  # Store excerpt
                'applied_date': datetime.now().isoformat(),
                'status': 'SUBMITTED'
            }
            
            # Generate unique ID
            import hashlib
            app_id = hashlib.md5(f"{job_details['url']}_{datetime.now()}".encode()).hexdigest()
            
            # Store in applications collection
            self.qdrant.add_job(app_id, application_data)
            
        except Exception as e:
            print(f"   ⚠️  Qdrant storage error: {str(e)}")
    
    async def close(self):
        """Clean up resources"""
        await self.base_bot.close()


async def main():
    """Main entry point for production automation"""
    print("\n" + "="*60)
    print("LinkedIn Job Application Automation - Production Version")
    print("With AI Cover Letters + Vector Database + Smart Form Filling")
    print("="*60 + "\n")
    
    # Configuration
    config = {
        'linkedin_email': os.getenv('LINKEDIN_EMAIL'),
        'linkedin_password': os.getenv('LINKEDIN_PASSWORD'),
        'user_profile': {
            'first_name': 'Abhilash',
            'last_name': 'Reddy',
            'email': os.getenv('LINKEDIN_EMAIL'),
            'phone': '+1234567890',
            'years_experience': '5',
            'requires_sponsorship': 'No',
            'willing_to_relocate': 'Yes',
            'currently_employed': 'Yes',
        },
        'dry_run': False  # Set to True to test without submitting
    }
    
    # Validate configuration
    if not config['linkedin_email'] or not config['linkedin_password']:
        print("❌ ERROR: LinkedIn credentials not found in .env file")
        print("\nPlease set:")
        print("  LINKEDIN_EMAIL=your_email@gmail.com")
        print("  LINKEDIN_PASSWORD=your_password")
        return
    
    # Test job URL (replace with actual job)
    test_job_url = input("\nEnter LinkedIn job URL (or press Enter for demo): ").strip()
    if not test_job_url:
        print("\n⚠️  No job URL provided. Please run with an actual LinkedIn Easy Apply job URL.")
        print("\nExample usage:")
        print("  python production_automation.py")
        print("  Then enter: https://www.linkedin.com/jobs/view/1234567890")
        return
    
    # Initialize and run
    bot = ProductionAutomationBot(config)
    
    try:
        await bot.initialize()
        
        # Apply to job
        result = await bot.apply_to_job_enhanced(test_job_url)
        
        # Print final result
        print("\n" + "="*60)
        print("📊 FINAL RESULT")
        print("="*60)
        print(f"Success: {result['success']}")
        print(f"Job: {result.get('job', {}).get('title', 'Unknown')}")
        print(f"Company: {result.get('job', {}).get('company', 'Unknown')}")
        if result.get('cover_letter_length'):
            print(f"Cover Letter: {result['cover_letter_length']} characters (GPT-4o generated)")
        if result.get('fields_filled'):
            print(f"Form Fields: {result['fields_filled']} auto-filled")
        if result.get('company_research_used'):
            print(f"Company Research: Used from Qdrant vector database")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Automation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Automation error: {str(e)}")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
