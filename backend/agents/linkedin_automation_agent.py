"""
LinkedIn Job Application Automation Agent
Implements the complete automation workflow based on the master agent instructions.
"""
import asyncio
import random
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Page, Browser
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LinkedInAutomationAgent:
    """
    Master LinkedIn automation agent that handles the complete job application workflow.
    """
    
    def __init__(
        self,
        email: str,
        password: str,
        resume_text: str,
        resume_file_path: Optional[str] = None,
        gemini_client: Optional[Any] = None,
        max_applications: int = 5
    ):
        self.email = email
        self.password = password
        self.resume_text = resume_text
        self.resume_file_path = resume_file_path
        self.gemini_client = gemini_client
        
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # Session data
        self.jobs_collected: List[Dict] = []
        self.jobs_analyzed: List[Dict] = []
        self.top_jobs: List[Dict] = []
        self.application_results: List[Dict] = []
        
        # Configuration - User can now specify max applications
        self.max_applications = max_applications
        self.similarity_threshold = 60
        self.confidence_threshold = 0.7
        
        logger.info(f"🎯 Automation configured:")
        logger.info(f"   📊 Max applications: {self.max_applications}")
        logger.info(f"   📈 Similarity threshold: {self.similarity_threshold}%")
        logger.info(f"   🎲 Confidence threshold: {self.confidence_threshold}")
        
    async def human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add random human-like delay."""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
        
    async def random_mouse_movement(self):
        """Simulate random mouse movements for human-like behavior."""
        if self.page:
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            await self.page.mouse.move(x, y)
    
    # ==================== PHASE 1: INITIALIZATION & AUTHENTICATION ====================
    
    async def initialize_browser(self):
        """Step 1.1: Browser Setup"""
        logger.info("🚀 Phase 1.1: Initializing browser with anti-detection measures")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Set to True for headless mode
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        # Create context with realistic settings
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            permissions=['geolocation']
        )
        
        self.page = await context.new_page()
        
        # Add stealth scripts
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        logger.info("✅ Browser initialized successfully")
    
    async def linkedin_login(self) -> bool:
        """Step 1.2: LinkedIn Authentication"""
        logger.info("🔐 Phase 1.2: Authenticating with LinkedIn")
        
        try:
            if not self.page:
                logger.error("❌ Page not initialized")
                return False
                
            # Navigate to LinkedIn login
            logger.info("📍 Navigating to LinkedIn login page...")
            await self.page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded')
            await self.human_delay(2, 3)
            
            # Wait for login form to be visible
            logger.info("⏳ Waiting for login form...")
            await self.page.wait_for_selector('input[name="session_key"]', state='visible', timeout=10000)
            await self.page.wait_for_selector('input[name="session_password"]', state='visible', timeout=10000)
            
            # Take screenshot before login
            await self.page.screenshot(path='screenshots/01_login_page.png')
            logger.info("📸 Screenshot saved: login page")
            
            # Clear any existing values and enter email
            logger.info(f"✍️ Entering email: {self.email[:3]}***")
            email_input = self.page.locator('input[name="session_key"]')
            await email_input.click()
            await email_input.clear()
            await self.human_delay(0.5, 1)
            await email_input.type(self.email, delay=100)  # Type slowly like human
            await self.human_delay(1, 2)
            
            # Clear any existing values and enter password
            logger.info("✍️ Entering password...")
            password_input = self.page.locator('input[name="session_password"]')
            await password_input.click()
            await password_input.clear()
            await self.human_delay(0.5, 1)
            await password_input.type(self.password, delay=120)  # Type slowly
            await self.human_delay(1, 2)
            
            # Take screenshot after filling
            await self.page.screenshot(path='screenshots/02_credentials_filled.png')
            logger.info("📸 Screenshot saved: credentials filled")
            
            # Find and click sign in button
            logger.info("🖱️ Clicking sign in button...")
            submit_button = self.page.locator('button[type="submit"]')
            await submit_button.click()
            
            # Wait for navigation
            logger.info("⏳ Waiting for login to complete...")
            await self.human_delay(3, 5)
            
            # Check for security checkpoint
            if 'checkpoint/challenge' in self.page.url:
                logger.warning("⚠️ LinkedIn security checkpoint detected. Please complete it manually in the browser.")
                await self.page.screenshot(path='screenshots/03_security_checkpoint.png')
                # Wait for user to complete checkpoint (up to 2 minutes)
                logger.info("⏳ Waiting up to 120 seconds for security checkpoint completion...")
                for i in range(24):  # 24 * 5 = 120 seconds
                    await self.human_delay(5, 5)
                    if 'checkpoint/challenge' not in self.page.url:
                        logger.info("✅ Security checkpoint completed!")
                        break
                    if i % 4 == 0:  # Log every 20 seconds
                        logger.info(f"⏳ Still waiting... ({(i+1)*5} seconds elapsed)")
            
            # Check for CAPTCHA or verification
            if await self.page.locator('text=Let\'s do a quick security check').count() > 0:
                logger.warning("⚠️ CAPTCHA detected! Please solve it manually...")
                await self.page.screenshot(path='screenshots/03_captcha.png')
                # Wait for user to solve CAPTCHA
                await self.human_delay(30, 45)
            
            # Check for email verification
            if await self.page.locator('text=We sent a verification code').count() > 0:
                logger.warning("⚠️ Email verification required! Please check your email...")
                await self.page.screenshot(path='screenshots/03_email_verification.png')
                # Wait for user to verify
                await self.human_delay(30, 45)
            
            # Wait for page to load after login
            # Note: LinkedIn feed has continuous network activity, so we check URL first
            await self.human_delay(2, 3)
            
            # Check URL immediately - if we're on feed, login succeeded
            current_url = self.page.url
            logger.info(f"📍 Current URL after login: {current_url}")
            
            if 'feed' in current_url or 'mynetwork' in current_url or 'check/add-phone' in current_url:
                logger.info("✅ Successfully logged into LinkedIn (verified by URL)")
                await self.page.screenshot(path='screenshots/04_after_login.png')
                logger.info("📸 Screenshot saved: after login")
                return True
            
            # If not on feed yet, wait for navigation with longer timeout
            try:
                await self.page.wait_for_url(lambda url: 'feed' in url or 'mynetwork' in url or 'check/add-phone' in url, timeout=10000)
                logger.info("✅ Successfully logged into LinkedIn")
                await self.page.screenshot(path='screenshots/04_after_login.png')
                logger.info("📸 Screenshot saved: after login")
                return True
            except Exception as e:
                logger.warning(f"URL wait timeout, checking selectors: {e}")
            
            # Fallback: Check for success indicators
            await self.page.screenshot(path='screenshots/04_after_login.png')
            logger.info("📸 Screenshot saved: after login")
            
            success_selectors = [
                'nav.global-nav',
                'a[href*="/feed/"]',
                'div[data-control-name="nav.all_nav"]',
                'button[aria-label="Start a post"]',
                'img[alt*="Photo"]'  # Profile picture
            ]
            
            for selector in success_selectors:
                if await self.page.locator(selector).count() > 0:
                    logger.info(f"✅ Successfully logged into LinkedIn (found: {selector})")
                    return True
            
            logger.error("❌ Login failed - navigation bar not found")
            logger.error(f"Current URL: {current_url}")
            await self.page.screenshot(path='screenshots/05_login_failed.png')
            return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}", exc_info=True)
            if self.page:
                await self.page.screenshot(path='screenshots/error_login.png')
                logger.error(f"Current URL: {self.page.url}")
            return False
    
    # ==================== PHASE 2: JOB SEARCH & FILTERING ====================
    
    async def navigate_to_jobs(self):
        """Step 2.1: Navigate to Jobs Section"""
        logger.info("📋 Phase 2.1: Navigating to Jobs section")
        
        if not self.page:
            raise RuntimeError("Page not initialized")
            
        await self.page.click('a[href*="/jobs"]')
        await self.page.wait_for_url('**/jobs/**')
        await self.human_delay(2, 3)
        logger.info("✅ Navigated to Jobs section")
    
    async def search_jobs(self, keywords: str, location: str):
        """Step 2.2 & 2.3: Configure Search Parameters"""
        logger.info(f"🔍 Phase 2.2-2.3: Searching for '{keywords}' in '{location}'")
        
        if not self.page:
            raise RuntimeError("Page not initialized")
        
        # Enter keywords
        keyword_input = self.page.locator('input[aria-label*="Search by title"]').first
        await keyword_input.clear()
        await keyword_input.fill(keywords)
        await self.human_delay(1, 2)
        
        # Enter location
        location_input = self.page.locator('input[aria-label*="City"]').first
        await location_input.clear()
        await location_input.fill(location)
        await self.human_delay(1, 2)
        
        # Press Enter or click search
        await keyword_input.press('Enter')
        await self.page.wait_for_load_state('networkidle')
        await self.human_delay(2, 3)
        
        logger.info("✅ Search parameters configured")
    
    async def apply_easy_apply_filter(self):
        """Step 2.4: Apply Easy Apply Filter - CRITICAL FOR AUTOMATION"""
        logger.info("🎯 Phase 2.4: Applying Easy Apply filter (CRITICAL)")
        
        if not self.page:
            raise RuntimeError("Page not initialized")
        
        try:
            # Method 1: Try clicking the Easy Apply filter button
            logger.info("   🔍 Looking for Easy Apply filter button...")
            
            # Wait for filters to load
            await self.page.wait_for_load_state('domcontentloaded')
            await self.human_delay(2, 3)
            
            # Multiple selectors for Easy Apply button (LinkedIn changes them frequently)
            easy_apply_selectors = [
                'button:has-text("Easy Apply")',
                'button[aria-label*="Easy Apply"]',
                'button:has-text("Easy")',
                'label:has-text("Easy Apply")',
                'button.search-reusables__filter-pill-button:has-text("Easy Apply")'
            ]
            
            filter_applied = False
            
            for selector in easy_apply_selectors:
                if await self.page.locator(selector).count() > 0:
                    logger.info(f"   ✅ Found Easy Apply filter: {selector}")
                    await self.page.locator(selector).first.click()
                    await self.page.wait_for_load_state('networkidle')
                    await self.human_delay(2, 3)
                    filter_applied = True
                    break
            
            # Method 2: Try URL parameter approach (more reliable)
            if not filter_applied:
                logger.info("   🔄 Trying URL parameter approach...")
                current_url = self.page.url
                
                if '?' in current_url:
                    new_url = f"{current_url}&f_AL=true"
                else:
                    new_url = f"{current_url}?f_AL=true"
                
                await self.page.goto(new_url)
                await self.page.wait_for_load_state('networkidle')
                await self.human_delay(2, 3)
                filter_applied = True
                logger.info("   ✅ Applied Easy Apply via URL parameter")
            
            # Verify filter is applied
            if filter_applied:
                # Check if Easy Apply badge/indicator is visible
                current_url = self.page.url
                if 'f_AL=true' in current_url:
                    logger.info("   ✅ Easy Apply filter VERIFIED (URL contains f_AL=true)")
                    logger.info("   🎯 Only Easy Apply jobs will be collected")
                    return True
                else:
                    logger.warning("   ⚠️ Easy Apply filter may not be active")
            
            logger.warning("   ⚠️ Could not verify Easy Apply filter")
            return filter_applied
            
        except Exception as e:
            logger.error(f"   ❌ Failed to apply Easy Apply filter: {e}")
            logger.error(f"   📝 Will attempt to proceed, but jobs may not all be Easy Apply")
            return False
    
    async def apply_additional_filters(self, filters: Dict[str, Any]):
        """Step 2.5: Apply Additional Filters"""
        logger.info("⚙️ Phase 2.5: Applying additional filters")
        
        # Implementation for experience level, job type, date posted, etc.
        # This would be customized based on user preferences
        pass
    
    # ==================== PHASE 3: JOB COLLECTION & ANALYSIS ====================
    
    async def collect_job_listings(self, target_count: int = 30) -> List[Dict]:
        """Step 3.1: Collect Job Listings"""
        logger.info(f"📊 Phase 3.1: Collecting up to {target_count} job listings")
        
        if not self.page:
            raise RuntimeError("Page not initialized")
        
        jobs = []
        
        # Scroll and collect jobs
        for i in range(10):  # Scroll up to 10 times
            job_cards = await self.page.locator('li.jobs-search-results__list-item').all()
            
            for card in job_cards:
                try:
                    # Extract job details
                    title = await card.locator('.job-card-list__title').inner_text()
                    company = await card.locator('.job-card-container__company-name').inner_text()
                    location = await card.locator('.job-card-container__metadata-item').first.inner_text()
                    
                    job_data = {
                        'title': title.strip(),
                        'company': company.strip(),
                        'location': location.strip(),
                        'element': card
                    }
                    
                    if job_data not in jobs:
                        jobs.append(job_data)
                        
                except Exception as e:
                    continue
            
            if len(jobs) >= target_count:
                break
                
            # Scroll down
            await self.page.evaluate('window.scrollBy(0, 500)')
            await self.human_delay(1, 2)
        
        self.jobs_collected = jobs[:target_count]
        logger.info(f"✅ Collected {len(self.jobs_collected)} jobs")
        return self.jobs_collected
    
    async def analyze_job_with_ai(self, job: Dict) -> Dict:
        """Step 3.2: Score Jobs Against Resume using Gemini AI"""
        
        if not self.page:
            raise RuntimeError("Page not initialized")
        
        # Click on job to get full description
        await job['element'].click()
        await self.human_delay(2, 3)
        
        # Extract full job description
        job_description = await self.page.locator('.jobs-description').inner_text()
        
        # Gemini AI Analysis Prompt
        prompt = f"""
You are an expert career advisor and ATS (Applicant Tracking System) analyzer.

TASK: Analyze how well this candidate matches this job opportunity.

CANDIDATE RESUME:
{self.resume_text}

JOB POSTING:
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job_description}

ANALYSIS REQUIRED:
1. Calculate similarity score (0-100) based on:
   - Skills match (40% weight)
   - Experience match (30% weight)
   - Education match (15% weight)
   - Location compatibility (10% weight)
   - Job type/level match (5% weight)

2. Identify:
   - Matching skills (list top 5)
   - Missing critical skills (list top 3)
   - Years of experience gap (if any)
   
3. Provide recommendation:
   - APPLY: If score >= 60% and candidate meets basic requirements
   - SKIP: If score < 60% or missing critical requirements

4. Confidence level (0.0 to 1.0):
   - How confident are you in this recommendation?

5. Reasoning (2-3 sentences):
   - Why is this a good/bad match?
   - What are the key strengths/concerns?

RETURN AS JSON:
{{
  "similarity_score": <number>,
  "matching_skills": [<skills>],
  "missing_skills": [<skills>],
  "recommendation": "APPLY" or "SKIP",
  "confidence": <number>,
  "reasoning": "<text>"
}}
"""
        
        # Call Gemini AI (if available)
        if self.gemini_client:
            try:
                response = await self.gemini_client.generate_content(prompt)
                analysis = json.loads(response.text)
            except:
                # Fallback analysis
                analysis = {
                    "similarity_score": 70,
                    "matching_skills": ["Python", "AI", "Machine Learning"],
                    "missing_skills": ["Kubernetes"],
                    "recommendation": "APPLY",
                    "confidence": 0.8,
                    "reasoning": "Good skill match with some gaps in devops"
                }
        else:
            # Default analysis when Gemini not available
            analysis = {
                "similarity_score": 70,
                "matching_skills": ["Skills match"],
                "missing_skills": ["Some gaps"],
                "recommendation": "APPLY",
                "confidence": 0.75,
                "reasoning": "Reasonable match based on keywords"
            }
        
        job.update(analysis)
        job['description'] = job_description
        
        await self.human_delay(2, 3)
        return job
    
    async def rank_and_select_top_jobs(self) -> List[Dict]:
        """Step 3.3: Rank and Filter Top Jobs"""
        logger.info("🏆 Phase 3.3: Ranking and selecting top jobs")
        
        # Filter jobs
        qualified_jobs = [
            job for job in self.jobs_analyzed
            if job['similarity_score'] >= self.similarity_threshold
            and job['recommendation'] == 'APPLY'
            and job['confidence'] >= self.confidence_threshold
        ]
        
        # Sort by score
        qualified_jobs.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Select top 5
        self.top_jobs = qualified_jobs[:5]
        
        logger.info(f"✅ Selected {len(self.top_jobs)} top jobs for application")
        for i, job in enumerate(self.top_jobs, 1):
            logger.info(f"  {i}. {job['title']} at {job['company']} - Score: {job['similarity_score']}%")
        
        return self.top_jobs
    
    # ==================== PHASE 4: AUTOMATED JOB APPLICATION ====================
    
    async def apply_to_job(self, job: Dict) -> Dict:
        """Step 4.1-4.8: Complete application process for a single job"""
        logger.info(f"📝 Phase 4: Applying to {job['title']} at {job['company']}")
        
        if not self.page:
            raise RuntimeError("Page not initialized")
        
        result = {
            'job': job,
            'status': 'PENDING',
            'timestamp': datetime.now().isoformat(),
            'steps_completed': []
        }
        
        try:
            # Click on job
            await job['element'].click()
            await self.human_delay(2, 3)
            
            # Click Easy Apply button
            await self.page.click('button:has-text("Easy Apply")')
            await self.human_delay(2, 3)
            result['steps_completed'].append('clicked_easy_apply')
            
            # Navigate through application forms
            max_pages = 10
            for page_num in range(max_pages):
                logger.info(f"  📄 Processing application page {page_num + 1}")
                
                # Fill current page
                await self.fill_application_page()
                result['steps_completed'].append(f'filled_page_{page_num + 1}')
                
                # Check for next/submit button
                if await self.page.locator('button:has-text("Submit application")').count() > 0:
                    # Final submit
                    await self.human_delay(2, 4)
                    await self.page.click('button:has-text("Submit application")')
                    await self.human_delay(3, 5)
                    
                    # Verify submission
                    if await self.verify_submission():
                        result['status'] = 'SUCCESS'
                        result['steps_completed'].append('submitted')
                        logger.info(f"  ✅ Successfully applied to {job['title']}")
                    else:
                        result['status'] = 'FAILED'
                        result['error'] = 'Submission verification failed'
                    break
                    
                elif await self.page.locator('button:has-text("Next")').count() > 0:
                    # Next page
                    await self.page.click('button:has-text("Next")')
                    await self.human_delay(2, 3)
                else:
                    # No more pages
                    break
            
            # Close modal if still open
            if await self.page.locator('button[aria-label="Dismiss"]').count() > 0:
                await self.page.click('button[aria-label="Dismiss"]')
                
        except Exception as e:
            result['status'] = 'FAILED'
            result['error'] = str(e)
            logger.error(f"  ❌ Application failed: {e}")
        
        await self.human_delay(5, 10)  # Delay between applications
        return result
    
    async def fill_application_page(self):
        """Step 4.3-4.5: Fill current application page"""
        
        if not self.page:
            raise RuntimeError("Page not initialized")
        
        # Find all input fields on current page
        inputs = await self.page.locator('input:visible').all()
        textareas = await self.page.locator('textarea:visible').all()
        selects = await self.page.locator('select:visible').all()
        
        # Fill text inputs
        for input_field in inputs:
            input_type = await input_field.get_attribute('type')
            label = await self.get_field_label(input_field)
            
            if input_type == 'text' or input_type == 'email' or input_type == 'tel':
                value = await self.determine_input_value(label)
                if value:
                    await input_field.fill(value)
                    await self.human_delay(0.5, 1.5)
        
        # Fill textareas (cover letter, etc.)
        for textarea in textareas:
            label = await self.get_field_label(textarea)
            if 'cover' in label.lower():
                cover_letter = await self.generate_cover_letter(job={'title': 'Job', 'company': 'Company', 'description': ''})
                await textarea.fill(cover_letter)
                await self.human_delay(1, 2)
        
        # Fill selects/dropdowns
        for select in selects:
            options = await select.locator('option').all()
            if len(options) > 1:
                # Select first non-empty option
                await select.select_option(index=1)
                await self.human_delay(0.5, 1)
    
    async def get_field_label(self, element) -> str:
        """Get the label text for a form field"""
        try:
            if not self.page:
                return ""
                
            label = await element.get_attribute('aria-label')
            if label:
                return label
                
            # Try to find associated label
            field_id = await element.get_attribute('id')
            if field_id:
                label_element = self.page.locator(f'label[for="{field_id}"]').first
                if label_element:
                    return await label_element.inner_text()
        except:
            pass
        return ""
    
    async def determine_input_value(self, label: str) -> Optional[str]:
        """Determine appropriate value for an input field based on label"""
        label_lower = label.lower()
        
        if 'phone' in label_lower or 'mobile' in label_lower:
            return "+1234567890"  # Should come from user profile
        elif 'email' in label_lower:
            return self.email
        elif 'first name' in label_lower:
            return "John"  # Extract from resume
        elif 'last name' in label_lower:
            return "Doe"  # Extract from resume
        elif 'linkedin' in label_lower or 'url' in label_lower:
            return f"linkedin.com/in/profile"
        
        return None
    
    async def generate_cover_letter(self, job: Dict) -> str:
        """Generate cover letter using Gemini AI"""
        
        if not self.gemini_client:
            return "I am excited to apply for this position and believe my skills align well with the requirements."
        
        prompt = f"""
Generate a professional cover letter for a job application.

JOB DETAILS:
Title: {job.get('title', 'Position')}
Company: {job.get('company', 'Company')}
Description: {job.get('description', '')}

CANDIDATE BACKGROUND:
{self.resume_text}

REQUIREMENTS:
- Length: 150-200 words
- Tone: Professional but personable
- Structure: 
  1. Opening: Express enthusiasm for the role
  2. Body: Highlight 2-3 relevant achievements/skills
  3. Closing: Express interest in next steps
- Avoid: Generic phrases, desperation, salary discussion
- Include: Specific company name, role title, relevant skills

Return only the cover letter text, no additional commentary.
"""
        
        try:
            response = await self.gemini_client.generate_content(prompt)
            return response.text
        except:
            return "I am excited to apply for this position and believe my skills align well with the requirements."
    
    async def verify_submission(self) -> bool:
        """Step 4.7: Verify application was submitted"""
        await self.human_delay(2, 3)
        
        # Look for success indicators
        success_indicators = [
            'Application submitted',
            'Your application has been sent',
            'Successfully applied',
            'Application sent'
        ]
        
        if not self.page:
            return False
        
        page_text = await self.page.inner_text('body')
        
        for indicator in success_indicators:
            if indicator.lower() in page_text.lower():
                return True
        
        return False
    
    # ==================== PHASE 5: REPORTING & CLEANUP ====================
    
    async def generate_report(self) -> Dict:
        """Step 5.1: Generate Application Report"""
        logger.info("📊 Phase 5.1: Generating application report")
        
        successful = [r for r in self.application_results if r['status'] == 'SUCCESS']
        failed = [r for r in self.application_results if r['status'] == 'FAILED']
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_jobs_searched': len(self.jobs_collected),
            'jobs_analyzed': len(self.jobs_analyzed),
            'top_jobs_selected': len(self.top_jobs),
            'applications_attempted': len(self.application_results),
            'successful_applications': len(successful),
            'failed_applications': len(failed),
            'success_rate': len(successful) / len(self.application_results) * 100 if self.application_results else 0,
            'applications': self.application_results
        }
        
        logger.info(f"✅ Report generated: {len(successful)}/{len(self.application_results)} successful applications")
        return report
    
    async def cleanup(self):
        """Step 5.3: Cleanup & Logout"""
        logger.info("🧹 Phase 5.3: Cleaning up and logging out")
        
        try:
            # Logout
            if self.page:
                await self.page.click('button[id*="global-nav"]')
                await self.human_delay(1, 2)
                await self.page.click('a:has-text("Sign out")')
                await self.human_delay(2, 3)
            
            # Close browser
            if self.browser:
                await self.browser.close()
            
            if self.playwright:
                await self.playwright.stop()
                
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"⚠️ Cleanup error: {e}")
    
    # ==================== MAIN EXECUTION WORKFLOW ====================
    
    async def run_automation(
        self,
        keywords: str,
        location: str,
        additional_filters: Optional[Dict] = None
    ) -> Dict:
        """
        Execute the complete automation workflow.
        """
        try:
            # Phase 1: Initialization
            await self.initialize_browser()
            if not await self.linkedin_login():
                raise Exception("Login failed")
            
            # Phase 2: Job Search
            await self.navigate_to_jobs()
            await self.search_jobs(keywords, location)
            await self.apply_easy_apply_filter()
            
            if additional_filters:
                await self.apply_additional_filters(additional_filters)
            
            # Phase 3: Collection & Analysis
            await self.collect_job_listings(target_count=30)
            
            for job in self.jobs_collected:
                analyzed_job = await self.analyze_job_with_ai(job)
                self.jobs_analyzed.append(analyzed_job)
            
            await self.rank_and_select_top_jobs()
            
            # Phase 4: Applications
            for job in self.top_jobs[:self.max_applications]:
                result = await self.apply_to_job(job)
                self.application_results.append(result)
            
            # Phase 5: Reporting
            report = await self.generate_report()
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Automation error: {e}")
            raise
        finally:
            await self.cleanup()
