"""
ULTIMATE LinkedIn Easy Apply Automation Bot
Complete implementation following the comprehensive AI agent workflow
Matches exact LinkedIn UI shown in screenshots
"""

import asyncio
import random
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json

from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeoutError


class UltimateLinkedInBot:
    """
    Complete LinkedIn Easy Apply automation following the exact 5-page workflow:
    Page 1: Contact Information (Email, Phone)
    Page 2: Resume Upload/Selection
    Page 3: Additional Questions
    Page 4: Work Authorization
    Page 5: Review and Submit
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize bot with user configuration
        
        Args:
            config: Dictionary containing:
                - linkedin_email: User's LinkedIn email
                - linkedin_password: User's LinkedIn password
                - keyword: Job search keywords (e.g., "Web Developer")
                - location: Job location (e.g., "India", "Remote")
                - resume_path: Path to resume PDF file
                - user_profile: Dictionary with user information
                - max_applications: Maximum number of applications (default: 5)
                - dry_run: If True, don't actually submit (default: False)
        """
        self.config = config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Extract configuration
        self.linkedin_email = config.get('linkedin_email', '')
        self.linkedin_password = config.get('linkedin_password', '')
        self.keyword = config.get('keyword', 'Web Developer')
        self.location = config.get('location', 'India')
        self.resume_path = config.get('resume_path', '')
        self.user_profile = config.get('user_profile', {})
        self.max_applications = config.get('max_applications', 5)
        self.dry_run = config.get('dry_run', False)
        
        # Statistics
        self.jobs_found = 0
        self.applications_attempted = 0
        self.applications_successful = 0
        self.applications_failed = 0
        self.applied_jobs: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        
        # Execution log
        self.execution_log: List[str] = []
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.execution_log.append(log_entry)
    
    async def close(self) -> None:
        """Close browser and cleanup resources safely"""
        try:
            # Wait a bit for any pending operations to complete
            await asyncio.sleep(1)
            
            # Close page first if it exists
            if self.page:
                try:
                    await self.page.close()
                    self.page = None
                except Exception as e:
                    self.log(f"   ⚠️  Page close warning: {str(e)[:50]}", "WARNING")
            
            # Close context
            if self.context:
                try:
                    await self.context.close()
                    self.context = None
                except Exception as e:
                    self.log(f"   ⚠️  Context close warning: {str(e)[:50]}", "WARNING")
            
            # Close browser
            if self.browser:
                try:
                    await self.browser.close()
                    self.browser = None
                except Exception as e:
                    self.log(f"   ⚠️  Browser close warning: {str(e)[:50]}", "WARNING")
            
            # Cancel any pending tasks
            try:
                tasks = [t for t in asyncio.all_tasks() if not t.done()]
                for task in tasks:
                    if task != asyncio.current_task():
                        task.cancel()
                        try:
                            await task
                        except (asyncio.CancelledError, Exception):
                            pass
            except:
                pass
            
            self.log("🧹 Browser closed and resources released")
            
        except Exception as e:
            self.log(f"⚠️  Cleanup error: {str(e)}", "WARNING")
    
    async def initialize_browser(self) -> None:
        """
        PHASE 1: INITIALIZATION
        Initialize browser with anti-detection measures
        """
        self.log("=" * 80)
        self.log("PHASE 1: INITIALIZATION")
        self.log("=" * 80)
        self.log("🚀 Initializing browser with anti-detection measures...")
        
        playwright = await async_playwright().start()
        
        # Use persistent profile to reduce CAPTCHA
        profile_dir = Path("browser_profile")
        profile_dir.mkdir(exist_ok=True)
        
        # Clean up lock files
        for lock_file in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
            lock_path = profile_dir / lock_file
            if lock_path.exists():
                try:
                    lock_path.unlink()
                except:
                    pass
        
        self.context = await playwright.chromium.launch_persistent_context(
            str(profile_dir),
            headless=False,  # Visible browser for monitoring
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ],
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Get or create page
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()
        
        # Anti-detection: Override navigator.webdriver
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.log("✅ Browser initialized successfully")
        self.log(f"   User Agent: Chrome 120.0 on macOS")
        self.log(f"   Profile: Persistent (reduces CAPTCHA)")
    
    async def linkedin_login(self) -> bool:
        """
        PHASE 2: LINKEDIN AUTHENTICATION
        Complete LinkedIn login workflow
        """
        self.log("")
        self.log("=" * 80)
        self.log("PHASE 2: LINKEDIN AUTHENTICATION")
        self.log("=" * 80)
        
        if not self.page:
            self.log("❌ ERROR: Browser not initialized", "ERROR")
            return False
        
        try:
            # Step 1: Navigate to login page
            self.log("📝 Step 1: Navigating to LinkedIn login page...")
            await self.page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
            await asyncio.sleep(2)
            self.log("   ✓ Login page loaded")
            
            # Check if already logged in
            if "/feed" in self.page.url or "/in/" in self.page.url:
                self.log("✅ Already logged in - session active")
                return True
            
            # Step 2: Enter credentials
            self.log(f"📝 Step 2: Entering credentials for {self.linkedin_email}...")
            await self.page.fill('#username', self.linkedin_email)
            await asyncio.sleep(random.uniform(0.5, 1.0))
            await self.page.fill('#password', self.linkedin_password)
            await asyncio.sleep(random.uniform(0.5, 1.0))
            self.log("   ✓ Credentials entered")
            
            # Step 3: Submit login form
            self.log("📝 Step 3: Submitting login form...")
            await self.page.click('button[type="submit"]')
            await asyncio.sleep(5)
            
            # Step 4: Handle security verification
            self.log("📝 Step 4: Checking for security verification...")
            if "checkpoint" in self.page.url or "challenge" in self.page.url:
                self.log("⚠️  Security checkpoint detected!", "WARNING")
                self.log("   Please complete verification manually in the browser")
                self.log("   Waiting 60 seconds for manual verification...")
                await asyncio.sleep(60)
                
                # Check if verification completed
                if "feed" not in self.page.url:
                    self.log("❌ Verification not completed. Please try again.", "ERROR")
                    return False
                else:
                    self.log("   ✓ Verification completed")
            
            # Step 5: Verify successful login
            self.log("📝 Step 5: Verifying successful login...")
            await self.page.wait_for_url("**/feed/**", timeout=10000)
            self.log("   ✓ URL contains '/feed'")
            self.log("   ✓ Session cookies saved for future use")
            self.log("✅ LOGIN COMPLETE")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Login failed: {str(e)}", "ERROR")
            self.errors.append(f"Login error: {str(e)}")
            return False
    
    async def search_jobs(self) -> List[Any]:
        """
        PHASE 3: JOB SEARCH WITH EASY APPLY FILTER
        Search for jobs with Easy Apply filter enabled
        
        Returns:
            List of job card elements (ElementHandle objects)
        """
        self.log("")
        self.log("=" * 80)
        self.log("PHASE 3: JOB SEARCH WITH EASY APPLY FILTER")
        self.log("=" * 80)
        
        if not self.page:
            return []
        
        try:
            # Step 1: Construct search URL
            self.log("📝 Step 1: Constructing search URL...")
            from urllib.parse import quote
            
            keyword_encoded = quote(self.keyword)
            location_encoded = quote(self.location)
            
            search_url = (
                f"https://www.linkedin.com/jobs/search/"
                f"?keywords={keyword_encoded}"
                f"&location={location_encoded}"
                f"&f_AL=true"  # CRITICAL: Easy Apply filter
                f"&sortBy=DD"   # Sort by date descending
            )
            
            self.log(f"   ✓ URL constructed: {search_url}")
            self.log(f"   ➜ Keywords: {self.keyword}")
            self.log(f"   ➜ Location: {self.location}")
            self.log(f"   ➜ Easy Apply Filter: ENABLED (f_AL=true)")
            
            # Step 2: Navigate to search results
            self.log("📝 Step 2: Navigating to search results...")
            await self.page.goto(search_url, wait_until="domcontentloaded")
            await asyncio.sleep(3)
            self.log("   ✓ Search page loaded")
            
            # Step 3: Load additional jobs by scrolling
            self.log("📝 Step 3: Loading additional jobs (scrolling 3 times)...")
            job_list_selector = '.scaffold-layout__list-container'
            
            for i in range(3):
                try:
                    await self.page.evaluate(f'''
                        document.querySelector("{job_list_selector}").scrollTo(0, document.querySelector("{job_list_selector}").scrollHeight);
                    ''')
                    await asyncio.sleep(2)
                    self.log(f"   ✓ Scroll {i+1}/3 complete")
                except:
                    pass
            
            # Step 4: Identify job cards
            self.log("📝 Step 4: Identifying job cards...")
            
            # Try multiple selectors for job cards (LinkedIn's HTML can vary)
            selectors_to_try = [
                'li.jobs-search-results__list-item',
                'div.job-card-container',
                'div.jobs-search-results__list-item',
                '.scaffold-layout__list-item',
            ]
            
            job_cards = []
            for selector in selectors_to_try:
                job_cards = await self.page.query_selector_all(selector)
                if job_cards:
                    self.log(f"   ✓ Using selector: {selector}")
                    break
            
            self.log(f"   Found {len(job_cards)} total job cards on page")
            
            # Filter for Easy Apply jobs only
            # LinkedIn shows Easy Apply button AFTER clicking the job card
            easy_apply_count = 0
            easy_apply_jobs = []
            
            self.log(f"📝 Checking jobs for Easy Apply button (clicking each to verify)...")
            
            for i, card in enumerate(job_cards[:20]):  # Check first 20 cards
                try:
                    # Click the job card to load details
                    await card.click()
                    await asyncio.sleep(1.5)  # Wait for job details to load
                    
                    # Now check for Easy Apply button in the job details panel
                    easy_apply_selectors = [
                        'button.jobs-apply-button:has-text("Easy Apply")',
                        'button:has-text("Easy Apply")',
                        'button[aria-label*="Easy Apply"]',
                        '.jobs-apply-button',
                    ]
                    
                    has_easy_apply = False
                    for selector in easy_apply_selectors:
                        easy_apply_button = await self.page.query_selector(selector)
                        if easy_apply_button:
                            # Verify it's actually an Easy Apply button
                            button_text = await easy_apply_button.inner_text()
                            if 'Easy Apply' in button_text or 'easy apply' in button_text.lower():
                                has_easy_apply = True
                                break
                    
                    if has_easy_apply:
                        easy_apply_jobs.append(card)
                        easy_apply_count += 1
                        self.log(f"   ✓ Job {i+1}: Easy Apply available")
                    else:
                        self.log(f"   - Job {i+1}: No Easy Apply")
                    
                    # Exit early if we found enough jobs
                    if easy_apply_count >= self.max_applications:
                        self.log(f"   ✓ Found {easy_apply_count} Easy Apply jobs (enough for max applications)")
                        break
                        
                except Exception as e:
                    self.log(f"   ⚠️  Job {i+1}: Check failed ({str(e)[:30]})")
                    continue
            
            self.jobs_found = easy_apply_count
            self.log(f"✅ Found {easy_apply_count} Easy Apply jobs (out of {len(job_cards)} total checked)")
            
            # CRITICAL FIX: Only return Easy Apply jobs, never fallback to non-Easy Apply jobs
            # This prevents "Connection closed" errors when trying to apply to jobs without Easy Apply
            if not easy_apply_jobs:
                self.log("⚠️  No Easy Apply jobs found. Try different search keywords or location.", "WARNING")
            
            return easy_apply_jobs  # Only return jobs with Easy Apply button
            
        except Exception as e:
            self.log(f"❌ Job search failed: {str(e)}", "ERROR")
            self.errors.append(f"Search error: {str(e)}")
            return []
    
    async def apply_to_job(self, job_card, job_index: int) -> bool:
        """
        PHASE 4-6: COMPLETE APPLICATION WORKFLOW
        Process single job application following 5-page workflow
        
        Returns:
            True if application successful, False otherwise
        """
        if not self.page:
            return False
        
        self.log("")
        self.log("─" * 80)
        self.log(f"APPLICATION #{job_index}")
        self.log("─" * 80)
        
        try:
            # Close any open modals from previous applications
            await self._close_modal()
            await asyncio.sleep(0.5)
            
            # STEP 4.1: SELECT JOB
            self.log("📝 Step 4.1: Selecting job card...")
            await job_card.click()
            await asyncio.sleep(3)  # Increased wait time for page to load
            self.log("   ✓ Job card clicked, details panel updated")
            
            # STEP 4.2: EXTRACT JOB INFORMATION
            self.log("📝 Step 4.2: Extracting job information...")
            
            # Try multiple selectors for job title (LinkedIn's HTML varies)
            job_title = "Unknown Title"
            title_selectors = [
                'h1.job-details-jobs-unified-top-card__job-title',
                'h2.job-details-jobs-unified-top-card__job-title',
                'h1.t-24',
                'h2.t-24',
                '.job-details-jobs-unified-top-card__job-title',
                '.jobs-unified-top-card__job-title',
                'h1[class*="job-title"]',
                'h2[class*="job-title"]',
            ]
            
            for selector in title_selectors:
                try:
                    title_text = await self.page.text_content(selector, timeout=2000)
                    if title_text and title_text.strip():
                        job_title = title_text.strip()
                        self.log(f"   ✓ Job Title: {job_title}")
                        break
                except:
                    continue
            
            # Try multiple selectors for company name
            company_name = "Unknown Company"
            company_selectors = [
                'a.job-details-jobs-unified-top-card__company-name',
                '.job-details-jobs-unified-top-card__company-name',
                '.jobs-unified-top-card__company-name',
                'a[class*="company-name"]',
            ]
            
            for selector in company_selectors:
                try:
                    company_text = await self.page.text_content(selector, timeout=2000)
                    if company_text and company_text.strip():
                        company_name = company_text.strip()
                        self.log(f"   ✓ Company: {company_name}")
                        break
                except:
                    continue
            
            # Try multiple selectors for location
            location = "Unknown Location"
            location_selectors = [
                'span.job-details-jobs-unified-top-card__bullet',
                '.job-details-jobs-unified-top-card__bullet',
                '.jobs-unified-top-card__bullet',
                'span[class*="bullet"]',
            ]
            
            for selector in location_selectors:
                try:
                    location_text = await self.page.text_content(selector, timeout=2000)
                    if location_text and location_text.strip():
                        location = location_text.strip()
                        self.log(f"   ✓ Location: {location}")
                        break
                except:
                    continue
            location = location.strip()
            
            self.log(f"   ✓ Job: {job_title}")
            self.log(f"   ✓ Company: {company_name}")
            self.log(f"   ✓ Location: {location}")
            
            # STEP 4.3: LOCATE EASY APPLY BUTTON
            self.log("📝 Step 4.3: Locating Easy Apply button...")
            easy_apply_button = None
            
            # Try multiple selectors for Easy Apply button
            selectors = [
                'button.jobs-apply-button',
                'button[aria-label*="Easy Apply"]',
                'button:has-text("Easy Apply")',
                '.jobs-apply-button',
                'button.jobs-apply-button--top-card',
                'button[data-job-id]',
            ]
            
            for selector in selectors:
                try:
                    easy_apply_button = await self.page.wait_for_selector(selector, timeout=3000)
                    if easy_apply_button:
                        button_text = await easy_apply_button.text_content()
                        if button_text and "Easy Apply" in button_text:
                            self.log(f"   ✓ Easy Apply button found: {selector}")
                            self.log(f"   ✓ Button text: {button_text.strip()}")
                            break
                        else:
                            easy_apply_button = None
                except:
                    continue
            
            if not easy_apply_button:
                self.log("   ❌ Not an Easy Apply job - Skipping", "WARNING")
                return False
            
            # STEP 4.4: INITIATE APPLICATION
            self.log("📝 Step 4.4: Initiating application (clicking Easy Apply)...")
            await easy_apply_button.click()
            await asyncio.sleep(3)  # Increased wait time for modal to appear
            
            # Wait for modal with multiple selector attempts
            modal_opened = False
            modal_selectors = [
                '.jobs-easy-apply-modal',
                'div[role="dialog"]',
                '.artdeco-modal',
                '[data-test-modal]',
            ]
            
            for selector in modal_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    self.log(f"   ✅ Application modal opened (selector: {selector})")
                    modal_opened = True
                    break
                except:
                    continue
            
            if not modal_opened:
                self.log("   ❌ Modal did not open - trying to proceed anyway", "WARNING")
                await asyncio.sleep(2)
            
            # PHASE 5: MULTI-PAGE FORM FILLING
            self.log("")
            self.log("=" * 80)
            self.log("PHASE 5: FORM FILLING (Multi-Page)")
            self.log("=" * 80)
            
            success = await self._fill_application_pages()
            
            if success:
                self.log(f"✅ Application #{job_index} completed successfully")
                self.log(f"   Job: {job_title} at {company_name}")
                
                self.applied_jobs.append({
                    'index': job_index,
                    'title': job_title,
                    'company': company_name,
                    'location': location,
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat()
                })
                
                return True
            else:
                self.log(f"❌ Application #{job_index} failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error applying to job: {str(e)}", "ERROR")
            self.errors.append(f"Application error: {str(e)}")
            return False
    
    async def _fill_application_pages(self) -> bool:
        """Fill multi-page Easy Apply form following exact workflow"""
        if not self.page:
            return False
        
        try:
            page_num = 1
            max_pages = 10  # Safety limit
            
            while page_num <= max_pages:
                # Detect current page progress
                try:
                    progress_text = await self.page.text_content('.artdeco-modal__header', timeout=2000)
                    self.log(f"📄 Current page: {progress_text}")
                except:
                    pass
                
                # PAGE 1: CONTACT INFORMATION
                if await self._is_contact_info_page():
                    self.log("📝 PAGE 1 (0% → 25%): Filling contact information...")
                    await self._fill_contact_info()
                    await asyncio.sleep(1)  # Wait for auto-save
                    
                # PAGE 2: RESUME UPLOAD
                elif await self._is_resume_page():
                    self.log("📝 PAGE 2 (25% → 50%): Handling resume upload...")
                    await self._fill_resume()
                    await asyncio.sleep(1)  # Wait for upload
                    
                # PAGE 3: ADDITIONAL QUESTIONS
                elif await self._has_questions():
                    self.log("📝 PAGE 3 (50% → 75%): Answering additional questions...")
                    await self._fill_questions()
                    await asyncio.sleep(1)  # Wait for answers to register
                    
                # PAGE 4: WORK AUTHORIZATION
                elif await self._is_work_auth_page():
                    self.log("📝 PAGE 4 (75% → 90%): Work authorization...")
                    await self._fill_work_authorization()
                    await asyncio.sleep(1)  # Wait for selections
                
                # Always wait a moment for page state to update
                await asyncio.sleep(0.5)
                
                # Check for Next/Review/Submit button (check Next FIRST before Submit)
                next_button = await self._find_next_button()
                submit_button = await self._find_submit_button()
                
                if next_button:
                    # NEXT BUTTON FOUND - Continue to next page
                    self.log("   ✓ Next button found - proceeding to next page...")
                    try:
                        await next_button.click()
                        await asyncio.sleep(2)
                        
                        # Verify page changed
                        try:
                            new_progress = await self.page.text_content('.artdeco-modal__header', timeout=2000)
                            if new_progress:
                                self.log(f"   ✓ Page advanced successfully")
                        except:
                            pass
                        
                    except Exception as e:
                        self.log(f"   ⚠️  Next button click issue: {str(e)}", "WARNING")
                        # Try using JavaScript click as fallback (bypasses overlay issues)
                        try:
                            self.log(f"   🔄 Trying JavaScript click...")
                            await next_button.evaluate('button => button.click()')
                            await asyncio.sleep(2)
                            self.log(f"   ✓ JavaScript click successful")
                        except Exception as js_error:
                            self.log(f"   ❌ JavaScript click also failed: {str(js_error)}", "ERROR")
                            return False
                    
                    page_num += 1
                    continue  # Loop back to process next page
                
                elif submit_button:
                    # PAGE 5: REVIEW AND SUBMIT
                    self.log("📝 PAGE 5 (90% → 100%): Review and submit...")
                    
                    if self.dry_run:
                        self.log("🔵 DRY RUN MODE: Skipping actual submission", "WARNING")
                        await self._close_modal()
                        return True
                    
                    # PHASE 6: FINAL SUBMISSION
                    self.log("")
                    self.log("=" * 80)
                    self.log("PHASE 6: FINAL SUBMISSION")
                    self.log("=" * 80)
                    
                    self.log("📝 Step 1: Submitting application...")
                    await submit_button.click()
                    await asyncio.sleep(3)
                    
                    # Step 2: Verify submission success
                    self.log("📝 Step 2: Verifying submission success...")
                    if await self._verify_submission():
                        self.log("   ✅ SUCCESS: Application sent confirmed")
                        self.log("   ✅ Success heading displayed")
                        
                        # Step 3: Close success modal
                        self.log("📝 Step 3: Closing success modal...")
                        await self._close_success_modal()
                        
                        # Step 4: Random delay before next job
                        delay = random.randint(5, 10)
                        self.log(f"📝 Step 4: Waiting {delay} seconds before next application...")
                        await asyncio.sleep(delay)
                        
                        return True
                    else:
                        self.log("   ❌ Could not verify submission", "ERROR")
                        return False
                
                else:
                    self.log("   ⚠️  No Next or Submit button found - checking if done...", "WARNING")
                    # Sometimes the form auto-advances, wait and check again
                    await asyncio.sleep(2)
                    submit_button = await self._find_submit_button()
                    if submit_button:
                        continue  # Loop will handle submission
                    else:
                        self.log("   ❌ Cannot proceed further", "ERROR")
                        break
                
                # Safety check
                if page_num > max_pages:
                    self.log("   ⚠️  Max pages exceeded", "WARNING")
                    break
            
            return False
            
        except Exception as e:
            self.log(f"❌ Form filling error: {str(e)}", "ERROR")
            return False
    
    async def _is_contact_info_page(self) -> bool:
        """Check if current page is contact information"""
        if not self.page:
            return False
        try:
            # Look for email or phone fields
            email_field = await self.page.query_selector('input[type="email"]')
            phone_field = await self.page.query_selector('input[type="tel"]')
            return email_field is not None or phone_field is not None
        except:
            return False
    
    async def _fill_contact_info(self) -> None:
        """Fill contact information page"""
        if not self.page:
            return
        
        try:
            # Email (usually pre-filled)
            email_field = await self.page.query_selector('input[type="email"]')
            if email_field:
                current_email = await email_field.input_value()
                if current_email:
                    self.log(f"   ✓ Email confirmed: {current_email}")
                else:
                    email = self.user_profile.get('email', self.linkedin_email)
                    await email_field.fill(email)
                    self.log(f"   ✓ Email entered: {email}")
            
            # Phone country code dropdown
            phone_code_select = await self.page.query_selector('select[id*="phoneNumber"][id*="country"]')
            if phone_code_select:
                country_code = self.user_profile.get('phone_country_code', 'India (+91)')
                # Try to select by visible text
                options = await phone_code_select.query_selector_all('option')
                for option in options:
                    option_text = await option.text_content()
                    if option_text and (country_code in option_text or '+91' in option_text):
                        option_value = await option.get_attribute('value')
                        await phone_code_select.select_option(option_value)
                        self.log(f"   ✓ Phone code selected: {country_code}")
                        break
            
            # Phone number
            phone_field = await self.page.query_selector('input[type="tel"]')
            if phone_field:
                phone = self.user_profile.get('phone_number', '7569663306')
                await phone_field.fill(phone)
                self.log(f"   ✓ Phone number entered: {phone}")
                
        except Exception as e:
            self.log(f"   ⚠️  Contact info error: {str(e)}", "WARNING")
    
    async def _is_resume_page(self) -> bool:
        """Check if current page is resume upload"""
        if not self.page:
            return False
        try:
            # Look for resume heading or upload button
            resume_heading = await self.page.query_selector('h3:has-text("Resume")')
            upload_button = await self.page.query_selector('button:has-text("Upload resume")')
            return resume_heading is not None or upload_button is not None
        except:
            return False
    
    async def _fill_resume(self) -> None:
        """Handle resume upload/selection page"""
        if not self.page:
            return
        
        try:
            # First, check if a resume is already selected (green checkmark present)
            selected_resume = await self.page.query_selector('input[type="radio"][name*="resume"]:checked')
            if selected_resume:
                self.log("   ✓ Resume already selected")
                
                # Verify with green checkmark
                checkmark = await self.page.query_selector('.artdeco-icon[data-test-icon="check-mark"]')
                if checkmark:
                    self.log("   ✓ Resume verified with green checkmark")
                return  # Resume already selected, nothing to do
            
            # Check for existing resumes (radio buttons)
            existing_resumes = await self.page.query_selector_all('input[type="radio"][name*="resume"]')
            
            if existing_resumes and len(existing_resumes) > 0:
                # Select first existing resume (most recently used)
                self.log(f"   ✓ Found {len(existing_resumes)} existing resume(s)")
                await existing_resumes[0].click()
                await asyncio.sleep(1)
                self.log("   ✓ Selected most recent resume")
                
                # Verify selection with green checkmark
                checkmark = await self.page.query_selector('.artdeco-icon[data-test-icon="check-mark"]')
                if checkmark:
                    self.log("   ✓ Resume selection confirmed")
            else:
                # No existing resumes, upload new one
                if self.resume_path and Path(self.resume_path).exists():
                    upload_button = await self.page.query_selector('input[type="file"]')
                    if upload_button:
                        await upload_button.set_input_files(self.resume_path)
                        await asyncio.sleep(2)
                        self.log(f"   ✓ Resume uploaded: {Path(self.resume_path).name}")
                else:
                    self.log("   ⚠️  No resume path provided or file not found", "WARNING")
                    
        except Exception as e:
            self.log(f"   ⚠️  Resume handling error: {str(e)}", "WARNING")
    
    async def _has_questions(self) -> bool:
        """Check if page has additional questions"""
        if not self.page:
            return False
        try:
            # Look for form fields that aren't email/phone
            questions = await self.page.query_selector_all('input:not([type="email"]):not([type="tel"]), select, textarea')
            return len(questions) > 0
        except:
            return False
    
    async def _fill_questions(self) -> None:
        """Answer additional questions dynamically with smart defaults"""
        if not self.page:
            return
        
        try:
            # Only target fields INSIDE the Easy Apply modal
            modal = await self.page.query_selector('.jobs-easy-apply-modal, .jobs-easy-apply-content')
            if not modal:
                return
            
            # TEXT INPUTS - Handle experience, salary, and other text fields
            text_inputs = await modal.query_selector_all('input[type="text"], input[type="number"]')
            for inp in text_inputs:
                try:
                    # Check if field is enabled (skip disabled fields)
                    is_disabled = await inp.get_attribute('disabled')
                    is_readonly = await inp.get_attribute('readonly')
                    if is_disabled is not None or is_readonly is not None:
                        continue
                    
                    # Check if field is visible
                    is_visible = await inp.is_visible()
                    if not is_visible:
                        continue
                    
                    # Skip if already filled
                    current_value = await inp.input_value()
                    if current_value and current_value.strip():
                        continue
                    
                    label = await self._get_field_label(inp)
                    label_lower = label.lower()
                    
                    # Skip generic/filter labels (not actual form questions)
                    if any(skip in label_lower for skip in ['filter results', 'sort by', 'date posted']):
                        continue
                    
                    if label and label != "Unknown field":
                        self.log(f"   📋 Question: {label[:80]}")
                    
                    # Experience questions - ALWAYS answer with 1 or 2 years
                    if any(word in label_lower for word in ['experience', 'years', 'year', 'how long']):
                        # Check if asking for specific technology
                        if any(tech in label_lower for tech in ['python', 'java', 'javascript', 'react', 'node']):
                            value = '2'  # 2 years for specific tech
                        else:
                            value = '1'  # 1 year for general experience
                        await inp.fill(value, timeout=5000)
                        self.log(f"      ✓ Answered: {value} years")
                    
                    # Salary questions
                    elif any(word in label_lower for word in ['salary', 'compensation', 'pay', 'expected salary']):
                        value = '1000000'  # 10 LPA or similar
                        await inp.fill(value, timeout=5000)
                        self.log(f"      ✓ Answered: {value}")
                    
                    # Notice period
                    elif any(word in label_lower for word in ['notice', 'availability', 'join']):
                        value = '30'  # 30 days or immediate
                        await inp.fill(value, timeout=5000)
                        self.log(f"      ✓ Answered: {value} days")
                    
                    # Location/City
                    elif any(word in label_lower for word in ['location', 'city', 'where']):
                        value = self.user_profile.get('location', 'Hyderabad, India')
                        await inp.fill(value, timeout=5000)
                        self.log(f"      ✓ Answered: {value}")
                    
                    # Default for other text fields
                    else:
                        value = '1'  # Safe default
                        await inp.fill(value, timeout=5000)
                        if label and label != "Unknown field":
                            self.log(f"      ✓ Answered: {value}")
                        
                except Exception as e:
                    # Skip fields that can't be filled (disabled, etc.)
                    continue
            
            # RADIO BUTTONS - Always click Yes or first option
            radio_groups = await modal.query_selector_all('fieldset')
            for group in radio_groups:
                try:
                    # Check if already selected
                    selected = await group.query_selector('input[type="radio"]:checked')
                    if selected:
                        continue
                    
                    legend = await group.query_selector('legend')
                    legend_text = ""
                    if legend:
                        legend_text = await legend.text_content() or ""
                        if legend_text and legend_text.strip():
                            self.log(f"   📋 Question: {legend_text[:80]}")
                    
                    legend_lower = legend_text.lower()
                    
                    # For "comfortable/willing" questions - Always Yes
                    if any(word in legend_lower for word in ['comfortable', 'willing', 'relocate', 'remote', 'onsite']):
                        yes_radio = await group.query_selector('input[value="Yes"], label:has-text("Yes") input, input[id*="yes"]')
                        if yes_radio:
                            await yes_radio.click()
                            await asyncio.sleep(0.5)
                            self.log("      ✓ Answered: Yes")
                            continue
                    
                    # For sponsorship questions - No
                    if any(word in legend_lower for word in ['sponsor', 'visa']):
                        no_radio = await group.query_selector('input[value="No"], label:has-text("No") input, input[id*="no"]')
                        if no_radio:
                            await no_radio.click()
                            await asyncio.sleep(0.5)
                            self.log("      ✓ Answered: No")
                            continue
                    
                    # Default: Click first available radio button or Yes
                    yes_radio = await group.query_selector('input[value="Yes"], label:has-text("Yes") input, input[id*="yes"]')
                    if yes_radio:
                        await yes_radio.click()
                        await asyncio.sleep(0.5)
                        self.log("      ✓ Answered: Yes")
                    else:
                        # Click first radio button
                        first_radio = await group.query_selector('input[type="radio"]')
                        if first_radio:
                            await first_radio.click()
                            await asyncio.sleep(0.5)
                            self.log("      ✓ Answered: First option")
                            
                except Exception as e:
                    continue
            
            # SELECT DROPDOWNS - Choose first reasonable option
            selects = await modal.query_selector_all('select')
            for select in selects:
                try:
                    # Check if already selected
                    current_value = await select.input_value()
                    if current_value:
                        continue
                    
                    label = await self._get_field_label(select)
                    label_lower = label.lower()
                    if label and label != "Unknown field":
                        self.log(f"   📋 Question: {label[:80]}")
                    
                    # Get all options
                    options = await select.query_selector_all('option')
                    if len(options) > 1:  # Skip if only placeholder
                        # Select second option (first is usually placeholder)
                        option_value = await options[1].get_attribute('value')
                        if option_value:
                            await select.select_option(option_value, timeout=5000)
                            option_text = await options[1].text_content()
                            self.log(f"      ✓ Answered: {option_text}")
                            
                except Exception as e:
                    continue
            
            # TEXTAREAS - Provide brief answers
            textareas = await modal.query_selector_all('textarea')
            for textarea in textareas:
                try:
                    current_value = await textarea.input_value()
                    if current_value and current_value.strip():
                        continue
                    
                    label = await self._get_field_label(textarea)
                    if label and label != "Unknown field":
                        self.log(f"   📋 Question: {label[:80]}")
                    
                    # Provide generic professional answer
                    answer = "I am very interested in this position and believe my skills and experience make me a strong candidate. I am eager to contribute to your team."
                    await textarea.fill(answer, timeout=5000)
                    self.log(f"      ✓ Answered with brief statement")
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.log(f"   ⚠️  Questions error: {str(e)}", "WARNING")
    
    async def _is_work_auth_page(self) -> bool:
        """Check if current page is work authorization"""
        if not self.page:
            return False
        try:
            heading = await self.page.query_selector('h3:has-text("Work authorization")')
            return heading is not None
        except:
            return False
    
    async def _fill_work_authorization(self) -> None:
        """Fill work authorization questions"""
        if not self.page:
            return
        
        try:
            # Question 1: Can start immediately
            immediately_yes = await self.page.query_selector('label:has-text("Yes") input[type="radio"]')
            if immediately_yes:
                await immediately_yes.click()
                self.log("   ✓ Can start immediately: Yes")
            
            # Question 2: Legally authorized
            authorized_yes = await self.page.query_selector_all('label:has-text("Yes") input[type="radio"]')
            if len(authorized_yes) > 1:
                await authorized_yes[1].click()
                self.log("   ✓ Legally authorized: Yes")
            
            # Question 3: Sponsorship
            sponsorship_no = await self.page.query_selector('label:has-text("No") input[type="radio"]')
            if sponsorship_no:
                await sponsorship_no.click()
                self.log("   ✓ Require sponsorship: No")
                
        except Exception as e:
            self.log(f"   ⚠️  Work auth error: {str(e)}", "WARNING")
    
    async def _get_field_label(self, field) -> str:
        """Get label text for a form field"""
        if not self.page:
            return "Unknown field"
        
        try:
            # Try getting label by 'for' attribute
            field_id = await field.get_attribute('id')
            if field_id:
                label = await self.page.query_selector(f'label[for="{field_id}"]')
                if label:
                    return await label.text_content() or ""
            
            # Try getting parent label
            parent = await field.evaluate_handle('el => el.closest("label")')
            if parent:
                return await parent.text_content() or ""
            
            # Try aria-label
            aria_label = await field.get_attribute('aria-label')
            if aria_label:
                return aria_label
            
            return "Unknown field"
        except:
            return "Unknown field"
    
    async def _find_next_button(self):
        """Find Next button with multiple strategies (excludes Submit buttons)"""
        if not self.page:
            return None
        
        # Try multiple selectors in order of reliability
        selectors = [
            'button[aria-label="Continue to next step"]',
            'button[aria-label*="next" i]',
            'button:has-text("Next")',
            'button.artdeco-button--primary:has-text("Next")',
            'button[data-easy-apply-next-button]',
            'button:has-text("Continue")',
            'button:has-text("Review")',
        ]
        
        for selector in selectors:
            try:
                button = await self.page.query_selector(selector)
                if button:
                    # Check if button is visible and enabled
                    is_visible = await button.is_visible()
                    is_enabled = await button.is_enabled()
                    button_text = (await button.text_content() or "").strip().lower()
                    
                    # EXCLUDE Submit buttons
                    if "submit" in button_text:
                        continue  # This is a submit button, not next
                    
                    # ACCEPT Next, Continue, or Review buttons
                    if is_visible and is_enabled:
                        self.log(f"   ✓ Next button found with text: '{button_text}'")
                        return button
            except:
                continue
        
        # Last resort: Check footer for primary button with Next/Continue/Review text
        try:
            footer_buttons = await self.page.query_selector_all('footer button.artdeco-button--primary')
            for btn in footer_buttons:
                btn_text = (await btn.text_content() or "").strip().lower()
                
                # EXCLUDE Submit buttons
                if "submit" in btn_text:
                    continue
                
                # ACCEPT Next, Continue, Review
                if any(word in btn_text for word in ['next', 'continue', 'review']):
                    is_visible = await btn.is_visible()
                    is_enabled = await btn.is_enabled()
                    if is_visible and is_enabled:
                        self.log(f"   ✓ Next button found in footer: '{btn_text}'")
                        return btn
        except:
            pass
        
        return None
    
    async def _find_submit_button(self):
        """Find Submit button with multiple strategies (excludes Next/Review buttons)"""
        if not self.page:
            return None
        
        # Try multiple selectors - MUST be actual Submit button, not Next or Review
        selectors = [
            'button[aria-label="Submit application"]',
            'button:has-text("Submit application")',
            'button.artdeco-button--primary:has-text("Submit")',
            'button[data-easy-apply-submit-button]',
        ]
        
        for selector in selectors:
            try:
                button = await self.page.query_selector(selector)
                if button:
                    # Check if button is visible and enabled
                    is_visible = await button.is_visible()
                    is_enabled = await button.is_enabled()
                    button_text = (await button.text_content() or "").strip().lower()
                    
                    # EXCLUDE Next and Review buttons
                    if "next" in button_text or "review" in button_text or "continue" in button_text:
                        continue  # Skip this button
                    
                    # ONLY accept Submit buttons
                    if is_visible and is_enabled and "submit" in button_text:
                        self.log(f"   ✓ Submit button found: {selector} (text: '{button_text}')")
                        return button
            except:
                continue
        
        # Check for Review button (sometimes comes before Submit)
        try:
            review_button = await self.page.query_selector('button:has-text("Review")')
            if review_button:
                is_visible = await review_button.is_visible()
                is_enabled = await review_button.is_enabled()
                if is_visible and is_enabled:
                    return review_button
        except:
            pass
        
        return None
    
    async def _verify_submission(self) -> bool:
        """Verify application was submitted successfully"""
        if not self.page:
            return False
        
        try:
            # Method 1: Look for success heading (multiple variations)
            success_selectors = [
                'h3:has-text("Application sent")',
                'h2:has-text("Application sent")',
                'h3:has-text("Your application was sent")',
                '[data-test-modal-id="application-sent-modal"]',
                '.artdeco-modal__header:has-text("Application sent")',
                '.artdeco-inline-feedback--success',
            ]
            
            for selector in success_selectors:
                try:
                    success_element = await self.page.wait_for_selector(selector, timeout=3000)
                    if success_element:
                        self.log(f"   ✓ Success detected with selector: {selector}")
                        return True
                except:
                    continue
            
            # Method 2: Check if modal is gone (sometimes modal closes after submission)
            await asyncio.sleep(2)
            modal = await self.page.query_selector('.jobs-easy-apply-modal')
            if not modal:
                self.log(f"   ✓ Success detected: Modal closed")
                return True
            
            # Method 3: Check page source for success keywords
            content = await self.page.content()
            success_keywords = ['application sent', 'successfully applied', 'your application was sent', 'application submitted']
            for keyword in success_keywords:
                if keyword in content.lower():
                    self.log(f"   ✓ Success detected: Found keyword '{keyword}'")
                    return True
            
            return False
            
        except Exception as e:
            self.log(f"   ⚠️  Verification error: {str(e)}", "WARNING")
            return False
    
    async def _close_modal(self) -> None:
        """Close Easy Apply modal"""
        if not self.page:
            return
        
        try:
            close_button = await self.page.query_selector('button[aria-label="Dismiss"]')
            if close_button:
                await close_button.click()
                await asyncio.sleep(1)
        except:
            pass
    
    async def _close_success_modal(self) -> None:
        """Close success confirmation modal"""
        if not self.page:
            return
        
        try:
            dismiss_button = await self.page.query_selector('button[aria-label="Dismiss"]')
            if dismiss_button:
                await dismiss_button.click()
                await asyncio.sleep(1)
        except:
            # Try pressing Escape
            await self.page.keyboard.press('Escape')
            await asyncio.sleep(1)
    
    async def run_automation(self) -> Dict[str, Any]:
        """
        Main automation workflow
        Execute complete LinkedIn Easy Apply automation
        """
        start_time = datetime.now()
        
        self.log("=" * 80)
        self.log("🤖 LINKEDIN EASY APPLY AUTOMATION - COMPLETE WORKFLOW")
        self.log("=" * 80)
        self.log("")
        self.log(f"SESSION INITIALIZED")
        self.log(f"- User: {self.user_profile.get('first_name', 'Unknown')} {self.user_profile.get('last_name', '')}")
        self.log(f"- Target Role: {self.keyword}")
        self.log(f"- Location: {self.location}")
        self.log(f"- Max Applications: {self.max_applications}")
        self.log(f"- Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"- Dry Run: {self.dry_run}")
        
        try:
            # Initialize browser
            await self.initialize_browser()
            
            # Login to LinkedIn
            login_success = await self.linkedin_login()
            if not login_success:
                return self._generate_summary(start_time, "Login failed")
            
            # Search for jobs
            job_cards = await self.search_jobs()
            if not job_cards:
                self.log("")
                self.log("⚠️  No Easy Apply jobs found with current search criteria")
                self.log("   Try different keywords or location (e.g., 'Software Engineer' in 'Remote')")
                self.log("")
                return self._generate_summary(start_time, "No Easy Apply jobs found")
            
            self.log(f"\n✅ Found {len(job_cards)} Easy Apply jobs - starting applications...\n")
            
            # Apply to jobs
            self.log("")
            self.log("=" * 80)
            self.log("PHASE 4-6: APPLICATION PROCESSING")
            self.log("=" * 80)
            
            jobs_to_apply = min(len(job_cards), self.max_applications)
            self.log(f"   Will attempt to apply to {jobs_to_apply} jobs")
            
            for i in range(jobs_to_apply):
                self.applications_attempted += 1
                
                success = await self.apply_to_job(job_cards[i], i + 1)
                
                if success:
                    self.applications_successful += 1
                else:
                    self.applications_failed += 1
                
                # Check if we should continue
                if self.applications_successful >= self.max_applications:
                    self.log(f"\n✅ Reached maximum applications limit ({self.max_applications})")
                    break
            
            # Generate summary
            return self._generate_summary(start_time, "Complete")
            
        except Exception as e:
            self.log(f"❌ CRITICAL ERROR: {str(e)}", "ERROR")
            return self._generate_summary(start_time, f"Error: {str(e)}")
        
        finally:
            await self.close()
    
    def _generate_summary(self, start_time: datetime, status: str) -> Dict[str, Any]:
        """
        PHASE 7: SESSION SUMMARY
        Generate comprehensive session summary
        """
        end_time = datetime.now()
        duration = end_time - start_time
        
        self.log("")
        self.log("=" * 80)
        self.log("PHASE 7: SESSION SUMMARY")
        self.log("=" * 80)
        self.log("")
        
        self.log(f"📊 Total Runtime: {duration.seconds // 60} minutes {duration.seconds % 60} seconds")
        self.log(f"📊 Jobs Found: {self.jobs_found}")
        self.log(f"📝 Applications Attempted: {self.applications_attempted}")
        self.log(f"✅ Successful: {self.applications_successful}")
        self.log(f"❌ Failed: {self.applications_failed}")
        
        if self.applications_attempted > 0:
            success_rate = (self.applications_successful / self.applications_attempted) * 100
            self.log(f"📈 Success Rate: {success_rate:.1f}%")
        
        self.log("")
        self.log("Successful Applications:")
        if self.applied_jobs:
            for job in self.applied_jobs:
                self.log(f"   ✅ {job['title']} at {job['company']}")
        else:
            self.log("   (None)")
        
        self.log("")
        self.log("Failed Applications:")
        if self.applications_failed > 0:
            self.log(f"   ❌ {self.applications_failed} applications failed")
        else:
            self.log("   (None)")
        
        self.log("")
        self.log("=" * 80)
        self.log(f"AGENT STATUS: {status} 🎯")
        self.log("=" * 80)
        
        return {
            'status': status,
            'jobs_found': self.jobs_found,
            'applications_attempted': self.applications_attempted,
            'applications_successful': self.applications_successful,
            'applications_failed': self.applications_failed,
            'success_rate': (self.applications_successful / self.applications_attempted * 100) if self.applications_attempted > 0 else 0,
            'applied_jobs': self.applied_jobs,
            'errors': self.errors,
            'execution_log': self.execution_log,
            'duration_seconds': duration.seconds
        }
