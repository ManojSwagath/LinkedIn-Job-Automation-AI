"""
Playwright runner script - runs separately from uvicorn to avoid event loop conflicts
Optimized for LinkedIn's current UI
"""
import asyncio
import sys
import json
import random
import time
import os
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for stdout/stderr on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from playwright.async_api import async_playwright


async def run_automation(config_json: str):
    """Run the full LinkedIn automation flow"""
    config = json.loads(config_json)
    
    # Set up default user profile values for form filling
    default_profile = {
        'first_name': 'Sathwik',
        'last_name': 'Adigoppula', 
        'full_name': 'Sathwik Adigoppula',
        'email': config.get('linkedin_email', ''),
        'phone_number': '7569663306',
        'phone': '7569663306',
        'city': 'Mangalore',
        'state': 'Karnataka',
        'zip_code': '575001',
        'country': 'India',
        'address': 'Mangalore, India',
        'years_experience': '3',
        'relevant_experience': '2',
        'ai_ml_experience': '2',
        'tech_experience': '3',
        'notice_period': '30',
        'current_ctc': '8',
        'expected_ctc': '12',
        'ctc': '8',
        'gpa': '8.5',
        'work_authorization': 'Yes',
        'require_sponsorship': 'No',
        'willing_to_relocate': 'Yes',
        'linkedin_url': 'https://linkedin.com/in/sathwik',
        'github_url': 'https://github.com/sathwik',
    }
    
    # Merge with provided profile, using defaults where not provided
    user_profile = config.get('user_profile', {})
    for key, value in default_profile.items():
        if key not in user_profile or not user_profile.get(key):
            user_profile[key] = value
    
    config['user_profile'] = user_profile
    
    result = {
        "status": "failed",
        "phase": "",
        "jobs_found": 0,
        "applications": [],
        "errors": []
    }
    
    playwright = None
    context = None
    page = None
    
    try:
        print("[INIT] Starting Playwright automation...")
        playwright = await async_playwright().start()
        
        # Profile directory
        profile_dir = Path("browser_profile")
        profile_dir.mkdir(exist_ok=True)
        
        # Screenshots directory
        screenshots_dir = Path("data/screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean up lock files
        for lock_name in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
            lock_file = profile_dir / lock_name
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except:
                    pass
        
        headless = config.get('headless', False)
        
        print(f"[BROWSER] Launching browser (headless={headless})...")
        print(f"[BROWSER] Profile: {profile_dir.absolute()}")
        
        context = await playwright.chromium.launch_persistent_context(
            str(profile_dir),
            headless=headless,
            slow_mo=100,  # Slower for reliability
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ],
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            ignore_https_errors=True,
        )
        
        if len(context.pages) > 0:
            page = context.pages[0]
        else:
            page = await context.new_page()
        
        page.set_default_timeout(60000)
        page.set_default_navigation_timeout(60000)
        
        # Anti-detection
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = {runtime: {}};
        """)
        
        print("[OK] Browser initialized successfully")
        result["phase"] = "browser_initialized"
        
        # Save screenshot
        await page.screenshot(path=str(screenshots_dir / "01_browser_init.png"))
        
        # ============ LOGIN PHASE ============
        print("\n[LOGIN] Starting LinkedIn login...")
        email = config.get('linkedin_email')
        password = config.get('linkedin_password')
        
        if not email or not password:
            raise Exception("LinkedIn credentials not provided")
        
        await page.goto('https://www.linkedin.com', wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(3)
        
        current_url = page.url
        print(f"[DEBUG] Current URL: {current_url}")
        
        # Check if already logged in
        logged_in = False
        if any(path in current_url for path in ['/feed', '/mynetwork', '/jobs', '/in/']):
            logged_in = True
            print("[OK] Already logged in to LinkedIn")
        else:
            # Navigate to login page
            await page.goto('https://www.linkedin.com/login', wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(2)
            
            await page.screenshot(path=str(screenshots_dir / "02_login_page.png"))
            
            # Fill credentials
            print(f"[LOGIN] Entering credentials for: {email[:5]}***")
            
            try:
                # Try multiple selectors for email field
                email_filled = False
                for sel in ['input[name="session_key"]', 'input#username', 'input[autocomplete="username"]']:
                    try:
                        elem = await page.query_selector(sel)
                        if elem:
                            await elem.fill(email)
                            email_filled = True
                            print(f"[DEBUG] Email filled using: {sel}")
                            break
                    except:
                        continue
                
                if not email_filled:
                    raise Exception("Could not find email input field")
                
                await asyncio.sleep(1)
                
                # Fill password
                password_filled = False
                for sel in ['input[name="session_password"]', 'input#password', 'input[type="password"]']:
                    try:
                        elem = await page.query_selector(sel)
                        if elem:
                            await elem.fill(password)
                            password_filled = True
                            print(f"[DEBUG] Password filled using: {sel}")
                            break
                    except:
                        continue
                
                if not password_filled:
                    raise Exception("Could not find password input field")
                
                await asyncio.sleep(1)
                
                # Click submit
                await page.click('button[type="submit"]')
                print("[LOGIN] Submitted login form")
                
                await asyncio.sleep(5)
                
                current_url = page.url
                print(f"[DEBUG] URL after login: {current_url}")
                
                await page.screenshot(path=str(screenshots_dir / "03_after_login.png"))
                
                if any(path in current_url for path in ['/feed', '/mynetwork', '/jobs', '/check/add-phone', '/in/']):
                    logged_in = True
                    print("[OK] Login successful!")
                elif 'checkpoint' in current_url or 'challenge' in current_url:
                    print("[WARN] Security checkpoint detected - waiting 60 seconds...")
                    await asyncio.sleep(60)
                    logged_in = True
                else:
                    raise Exception(f"Login may have failed - URL: {current_url}")
                    
            except Exception as e:
                print(f"[ERROR] Login failed: {str(e)}")
                result["errors"].append(f"Login error: {str(e)}")
                raise
        
        if not logged_in:
            raise Exception("Not logged in to LinkedIn")
        
        result["phase"] = "logged_in"
        
        # ============ JOB SEARCH PHASE ============
        print("\n[SEARCH] Starting job search...")
        
        import urllib.parse
        keyword = config.get('keyword', 'Software Engineer')
        location = config.get('location', 'Remote')
        
        # Build search URL with Easy Apply filter
        search_url = f'https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(keyword)}&location={urllib.parse.quote(location)}&f_AL=true&sortBy=R'
        
        print(f"[SEARCH] Keyword: {keyword}")
        print(f"[SEARCH] Location: {location}")
        print(f"[SEARCH] URL: {search_url}")
        
        await page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(5)
        
        await page.screenshot(path=str(screenshots_dir / "04_job_search.png"))
        
        result["phase"] = "searching"
        
        # ============ JOB COLLECTION PHASE ============
        print("\n[COLLECT] Collecting job listings...")
        
        # Wait for job list to load
        await asyncio.sleep(3)
        
        # Scroll to load more jobs
        for i in range(5):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1.5)
            print(f"[SCROLL] Scroll {i+1}/5")
        
        # Scroll back to top
        await page.evaluate('window.scrollTo(0, 0)')
        await asyncio.sleep(1)
        
        # Try multiple selectors for job cards - LinkedIn changes these frequently
        job_card_selectors = [
            'li.scaffold-layout__list-item',
            'li.jobs-search-results__list-item',
            'div.job-card-container',
            'div[data-job-id]',
            '.jobs-search-results__list > li',
            '.scaffold-layout__list > li',
            'ul.scaffold-layout__list-container > li',
        ]
        
        job_cards = []
        for selector in job_card_selectors:
            try:
                cards = await page.query_selector_all(selector)
                if cards and len(cards) > 0:
                    job_cards = cards
                    print(f"[OK] Found {len(cards)} job cards using: {selector}")
                    break
            except Exception as e:
                print(f"[DEBUG] Selector {selector} failed: {str(e)[:30]}")
                continue
        
        if not job_cards:
            # Last resort - try to get any clickable job elements
            print("[WARN] Standard selectors failed, trying alternative approach...")
            await page.screenshot(path=str(screenshots_dir / "05_no_jobs_found.png"))
            
            # Check if we see the job search container at all
            content = await page.content()
            if 'jobs-search-results' in content or 'scaffold-layout__list' in content:
                print("[DEBUG] Job container exists but couldn't select cards")
            else:
                print("[DEBUG] Job search container not found in page")
        
        jobs = []
        max_jobs = config.get('max_applications', 5)
        
        print(f"[COLLECT] Processing up to {max_jobs * 2} job cards...")
        
        for i, card in enumerate(job_cards[:max_jobs * 2]):
            try:
                # Scroll card into view
                await card.scroll_into_view_if_needed()
                await asyncio.sleep(0.8)
                
                # Click on the card to load details
                await card.click()
                await asyncio.sleep(2)
                
                # Get job details with multiple fallback selectors
                title = None
                company = None
                
                # Title selectors
                title_selectors = [
                    'h1.job-details-jobs-unified-top-card__job-title',
                    'h1.jobs-unified-top-card__job-title',
                    'h1.t-24.t-bold.inline',
                    'h2.job-details-jobs-unified-top-card__job-title',
                    '.job-details-jobs-unified-top-card__job-title',
                    'a.job-card-container__link span',
                    'h3.job-card-list__title',
                ]
                
                for sel in title_selectors:
                    try:
                        elem = await page.query_selector(sel)
                        if elem:
                            title = await elem.text_content()
                            if title:
                                title = title.strip()
                                break
                    except:
                        continue
                
                # Company selectors
                company_selectors = [
                    'a.job-details-jobs-unified-top-card__company-name',
                    'span.job-details-jobs-unified-top-card__company-name',
                    '.jobs-unified-top-card__company-name',
                    '.job-card-container__company-name',
                    'div.job-card-container__primary-description',
                    'a.job-card-container__company-name',
                ]
                
                for sel in company_selectors:
                    try:
                        elem = await page.query_selector(sel)
                        if elem:
                            company = await elem.text_content()
                            if company:
                                company = company.strip()
                                break
                    except:
                        continue
                
                if not company:
                    company = "Unknown Company"
                
                # Check for Easy Apply button
                easy_apply = False
                easy_apply_selectors = [
                    'button.jobs-apply-button',
                    'button[aria-label*="Easy Apply"]',
                    'button:has-text("Easy Apply")',
                    '.jobs-apply-button--top-card',
                ]
                
                for sel in easy_apply_selectors:
                    try:
                        btn = await page.query_selector(sel)
                        if btn:
                            btn_text = await btn.text_content() or ""
                            if 'easy' in btn_text.lower() or 'apply' in btn_text.lower():
                                easy_apply = True
                                break
                    except:
                        continue
                
                if title:
                    job_data = {
                        'index': i + 1,
                        'title': title[:100],
                        'company': company[:50] if company else 'Unknown',
                        'url': page.url,
                        'easy_apply': easy_apply
                    }
                    
                    if easy_apply:
                        jobs.append(job_data)
                        print(f"  [+] Job {len(jobs)}: {title[:45]}... @ {company[:20]}")
                    else:
                        print(f"  [-] Skipped (no Easy Apply): {title[:45]}...")
                    
                    if len(jobs) >= max_jobs:
                        print(f"[OK] Collected target number of jobs: {max_jobs}")
                        break
                        
            except Exception as e:
                print(f"  [WARN] Error processing card {i+1}: {str(e)[:40]}")
                continue
        
        result["jobs_found"] = len(jobs)
        result["phase"] = "jobs_collected"
        print(f"\n[OK] Collected {len(jobs)} Easy Apply jobs")
        
        await page.screenshot(path=str(screenshots_dir / "06_jobs_collected.png"))
        
        if not jobs:
            print("[WARN] No Easy Apply jobs found - trying alternative method...")
            # Take a screenshot for debugging
            await page.screenshot(path=str(screenshots_dir / "07_no_easy_apply_jobs.png"))
        
        # ============ APPLICATION PHASE ============
        dry_run = config.get('dry_run', True)
        user_profile = config.get('user_profile', {})
        
        print(f"\n[APPLY] Starting applications (dry_run={dry_run})...")
        
        for job in jobs[:max_jobs]:
            try:
                print(f"\n[APPLY] Applying to: {job['title'][:40]}")
                print(f"        Company: {job['company']}")
                
                # Navigate to job
                await page.goto(job['url'], wait_until='domcontentloaded', timeout=60000)
                await asyncio.sleep(2)
                
                # Find and click Easy Apply button
                clicked = False
                for sel in ['button.jobs-apply-button', 'button[aria-label*="Easy Apply"]', 'button:has-text("Easy Apply")']:
                    try:
                        btn = await page.query_selector(sel)
                        if btn:
                            await btn.click()
                            clicked = True
                            print("  [OK] Clicked Easy Apply button")
                            break
                    except:
                        continue
                
                if not clicked:
                    job['status'] = 'FAILED'
                    job['error'] = 'Could not click Easy Apply button'
                    result["applications"].append(job)
                    print("  [WARN] Could not find Easy Apply button")
                    continue
                
                await asyncio.sleep(3)
                
                await page.screenshot(path=str(screenshots_dir / f"apply_{job['index']}_modal.png"))
                
                # Process application steps
                for step in range(15):  # Max 15 steps
                    await asyncio.sleep(2)
                    
                    # First, fill any empty form fields using the advanced filler
                    await fill_linkedin_form_questions(page, user_profile, config.get('linkedin_email', ''))
                    await fill_form_fields(page, user_profile, config.get('linkedin_email', ''))
                    await asyncio.sleep(1)
                    
                    # Check for success messages
                    success_found = False
                    try:
                        page_text = await page.text_content('body')
                        if page_text and ('Application sent' in page_text or 'Your application was sent' in page_text):
                            job['status'] = 'APPLIED'
                            success_found = True
                            print("  [SUCCESS] Application submitted successfully!")
                    except:
                        pass
                    
                    if success_found or job.get('status') == 'APPLIED':
                        break
                    
                    # Fill form fields
                    await fill_form_fields(page, user_profile, config.get('linkedin_email', ''))
                    
                    # Click appropriate button - use CSS selectors with query_selector
                    button_clicked = False
                    
                    # Look for buttons in modal footer first
                    modal_footer_selectors = [
                        'footer button[aria-label*="Submit"]',
                        'footer button[aria-label*="Review"]', 
                        'footer button[aria-label*="Next"]',
                        'footer button[aria-label*="Continue"]',
                        '.jobs-easy-apply-modal footer button',
                        'div[role="dialog"] footer button',
                        'div.artdeco-modal footer button',
                    ]
                    
                    # Check for validation errors BEFORE clicking buttons
                    has_errors = False
                    try:
                        error_elements = await page.query_selector_all('[class*="error"], [class*="invalid"], .artdeco-inline-feedback--error')
                        if error_elements:
                            for err_el in error_elements:
                                if await err_el.is_visible():
                                    err_text = await err_el.text_content() or ''
                                    if err_text.strip():
                                        print(f"    [VALIDATION] Error detected: {err_text.strip()[:50]}")
                                        has_errors = True
                                        # Try filling fields again
                                        await fill_form_fields(page, user_profile, config.get('linkedin_email', ''))
                                        await asyncio.sleep(1)
                                        break
                    except:
                        pass
                    
                    # If still has errors after 2nd fill attempt, try filling empty numeric fields with defaults
                    if has_errors:
                        try:
                            empty_inputs = await page.query_selector_all('input:visible')
                            for inp in empty_inputs:
                                val = await inp.input_value() or ''
                                if not val.strip():
                                    input_type = await inp.get_attribute('type') or 'text'
                                    if input_type in ['text', 'number', 'tel']:
                                        await inp.fill('3')  # Default numeric value
                                        await inp.press('Tab')
                            await asyncio.sleep(1)
                        except:
                            pass
                    
                    # Get all visible footer buttons
                    for footer_sel in modal_footer_selectors:
                        try:
                            buttons = await page.query_selector_all(footer_sel)
                            for btn in buttons:
                                if not btn:
                                    continue
                                    
                                # Check if button is enabled
                                disabled = await btn.get_attribute('disabled')
                                if disabled:
                                    continue
                                    
                                btn_text = await btn.text_content() or ''
                                btn_text = btn_text.strip().lower()
                                aria_label = await btn.get_attribute('aria-label') or ''
                                aria_label = aria_label.lower()
                                
                                # Check if this is a submit button
                                if 'submit' in btn_text or 'submit' in aria_label:
                                    if dry_run:
                                        job['status'] = 'DRY_RUN'
                                        print(f"  [DRY RUN] Would submit: {btn_text}")
                                        button_clicked = True
                                    else:
                                        await btn.click()
                                        await asyncio.sleep(3)
                                        job['status'] = 'APPLIED'
                                        print("  [SUCCESS] Submitted application!")
                                        button_clicked = True
                                    break
                                
                                # Check for navigation buttons (but not Back/Cancel)
                                if any(x in btn_text or x in aria_label for x in ['next', 'continue', 'review']):
                                    if 'back' not in btn_text and 'dismiss' not in btn_text and 'cancel' not in btn_text:
                                        await btn.click()
                                        print(f"  [STEP {step+1}] Clicked: {btn_text[:20]}")
                                        button_clicked = True
                                        await asyncio.sleep(2)  # Wait longer after clicking
                                        break
                            
                            if button_clicked:
                                break
                        except Exception as e:
                            continue
                    
                    if job.get('status') in ['APPLIED', 'DRY_RUN']:
                        break
                    
                    # Fallback: Try getting any primary action button
                    if not button_clicked:
                        try:
                            # LinkedIn often uses artdeco primary buttons
                            primary_btns = await page.query_selector_all('button.artdeco-button--primary:visible')
                            for primary_btn in primary_btns:
                                if not primary_btn:
                                    continue
                                disabled = await primary_btn.get_attribute('disabled')
                                if disabled:
                                    continue
                                btn_text = await primary_btn.text_content() or ''
                                if 'back' not in btn_text.lower() and 'dismiss' not in btn_text.lower():
                                    if 'submit' in btn_text.lower():
                                        if dry_run:
                                            job['status'] = 'DRY_RUN'
                                            print(f"  [DRY RUN] Would submit: {btn_text.strip()}")
                                        else:
                                            await primary_btn.click()
                                            job['status'] = 'APPLIED'
                                            print("  [SUCCESS] Submitted!")
                                        button_clicked = True
                                        break
                                    else:
                                        await primary_btn.click()
                                        print(f"  [STEP {step+1}] Clicked primary: {btn_text.strip()[:20]}")
                                        button_clicked = True
                                        break
                        except:
                            pass
                    
                    if not button_clicked:
                        print(f"  [DEBUG] Step {step+1}: No clickable button found")
                        if step >= 8:
                            break
                
                if not job.get('status'):
                    job['status'] = 'INCOMPLETE'
                    print("  [WARN] Application incomplete")
                
                result["applications"].append(job)
                
                # Close modal
                try:
                    for dismiss_sel in ['button[aria-label="Dismiss"]', 'button[aria-label="Close"]', 'button.artdeco-modal__dismiss']:
                        btn = await page.query_selector(dismiss_sel)
                        if btn:
                            await btn.click()
                            break
                except:
                    pass
                
                await asyncio.sleep(2)
                
            except Exception as e:
                job['status'] = 'FAILED'
                job['error'] = str(e)[:100]
                result["applications"].append(job)
                print(f"  [ERROR] {str(e)[:50]}")
        
        result["status"] = "completed"
        result["phase"] = "completed"
        
        print(f"\n[DONE] Automation complete!")
        print(f"       Jobs found: {result['jobs_found']}")
        print(f"       Applications: {len(result['applications'])}")
        
    except Exception as e:
        result["errors"].append(str(e))
        print(f"\n[FATAL] Error: {str(e)}")
    
    finally:
        # Keep browser open briefly for debugging
        await asyncio.sleep(2)
        
        if context:
            try:
                await context.close()
            except:
                pass
        
        if playwright:
            try:
                await playwright.stop()
            except:
                pass
        
        print("[CLOSED] Browser closed")
    
    return result


async def get_field_label(page, element):
    """Get the label text for a form field by checking various sources"""
    label_text = ''
    
    try:
        # Method 1: Check aria-label
        aria_label = await element.get_attribute('aria-label')
        if aria_label:
            label_text += aria_label.lower() + ' '
        
        # Method 2: Check for associated label via 'for' attribute
        elem_id = await element.get_attribute('id')
        if elem_id:
            label_elem = await page.query_selector(f'label[for="{elem_id}"]')
            if label_elem:
                text = await label_elem.text_content()
                if text:
                    label_text += text.lower() + ' '
        
        # Method 3: Check parent label
        parent = await element.evaluate_handle('el => el.closest("label")')
        if parent:
            text = await parent.evaluate('el => el ? el.textContent : ""')
            if text:
                label_text += text.lower() + ' '
        
        # Method 4: Check preceding sibling or parent's text
        parent_text = await element.evaluate_handle('''el => {
            const parent = el.closest(".fb-dash-form-element, .artdeco-text-input, .jobs-easy-apply-form-section__grouping");
            if (parent) {
                const label = parent.querySelector("label, .fb-dash-form-element__label, span.t-bold");
                return label ? label.textContent : "";
            }
            return "";
        }''')
        if parent_text:
            text = await parent_text.json_value()
            if text:
                label_text += text.lower() + ' '
        
        # Method 5: Check name, id, placeholder
        for attr in ['name', 'id', 'placeholder']:
            val = await element.get_attribute(attr)
            if val:
                label_text += val.lower() + ' '
                
    except:
        pass
    
    return label_text


async def fill_form_fields(page, user_profile: dict, email: str):
    """Fill visible form fields with user data - enhanced version"""
    filled_count = 0
    
    try:
        # ============ HANDLE TEXT INPUTS ============
        inputs = await page.query_selector_all('input:visible')
        
        for inp in inputs:
            try:
                input_type = await inp.get_attribute('type') or 'text'
                if input_type in ['hidden', 'submit', 'button', 'checkbox', 'radio', 'file']:
                    continue
                
                # Check if field is disabled or readonly
                disabled = await inp.get_attribute('disabled')
                readonly = await inp.get_attribute('readonly')
                if disabled or readonly:
                    continue
                
                # Get existing value
                current_value = await inp.input_value() or ''
                if current_value.strip():
                    continue  # Already filled
                
                # Get comprehensive label
                label = await get_field_label(page, inp)
                
                # Determine fill value based on field context
                fill_value = None
                
                # Personal info fields
                if any(x in label for x in ['first name', 'fname', 'given name']):
                    fill_value = user_profile.get('first_name', 'John')
                elif any(x in label for x in ['last name', 'lname', 'surname', 'family name']):
                    fill_value = user_profile.get('last_name', 'Doe')
                elif any(x in label for x in ['full name', 'your name']) or label.strip() == 'name':
                    fill_value = user_profile.get('full_name', 'John Doe')
                elif 'email' in label:
                    fill_value = user_profile.get('email', email)
                elif any(x in label for x in ['phone', 'mobile', 'cell']):
                    fill_value = user_profile.get('phone_number', user_profile.get('phone', '7569663306'))
                elif 'city' in label:
                    fill_value = user_profile.get('city', 'Bangalore')
                elif 'state' in label or 'province' in label:
                    fill_value = user_profile.get('state', 'Karnataka')
                elif 'zip' in label or 'postal' in label:
                    fill_value = user_profile.get('zip_code', '560001')
                elif 'address' in label:
                    fill_value = user_profile.get('address', 'Bangalore, India')
                elif 'country' in label:
                    fill_value = user_profile.get('country', 'India')
                
                # Experience and numeric fields (IMPORTANT: These need numeric values)
                elif any(x in label for x in ['overall experience', 'total experience', 'years of experience', 'work experience']):
                    fill_value = str(user_profile.get('years_experience', '3'))
                elif any(x in label for x in ['relevant experience', 'experience with', 'years in']):
                    fill_value = str(user_profile.get('relevant_experience', '2'))
                elif any(x in label for x in ['ai/ml', 'machine learning', 'artificial intelligence']):
                    fill_value = str(user_profile.get('ai_ml_experience', '2'))
                elif any(x in label for x in ['python', 'java', 'javascript', 'react', 'angular', 'node']):
                    fill_value = str(user_profile.get('tech_experience', '2'))
                elif 'notice period' in label:
                    fill_value = str(user_profile.get('notice_period', '30'))
                elif any(x in label for x in ['ctc', 'salary', 'compensation', 'current ctc', 'expected ctc']):
                    if 'lakh' in label or 'lpa' in label:
                        fill_value = str(user_profile.get('ctc_lakhs', '8'))
                    else:
                        fill_value = str(user_profile.get('ctc', '800000'))
                elif 'expected' in label and 'salary' in label:
                    fill_value = str(user_profile.get('expected_salary', '1000000'))
                
                # URLs and links
                elif 'linkedin' in label:
                    fill_value = user_profile.get('linkedin_url', 'https://linkedin.com/in/profile')
                elif 'github' in label:
                    fill_value = user_profile.get('github_url', 'https://github.com/username')
                elif 'portfolio' in label or 'website' in label:
                    fill_value = user_profile.get('portfolio_url', '')
                
                # Handle generic number fields that need a value > 0
                elif input_type == 'number':
                    # Check if there's a validation error nearby
                    fill_value = '3'  # Default numeric value
                
                # Fill the field if we have a value
                if fill_value:
                    await inp.clear()
                    await inp.fill(fill_value)
                    await inp.press('Tab')  # Trigger validation
                    filled_count += 1
                    print(f"    [FILL] {label[:30]}: {fill_value[:20]}")
                    
            except Exception as e:
                continue
        
        # ============ HANDLE TEXTAREAS ============
        textareas = await page.query_selector_all('textarea:visible')
        for textarea in textareas:
            try:
                current_value = await textarea.input_value() or ''
                if current_value.strip():
                    continue
                
                label = await get_field_label(page, textarea)
                
                fill_value = None
                if any(x in label for x in ['cover letter', 'why', 'about you', 'summary', 'describe']):
                    fill_value = user_profile.get('cover_letter', 'I am excited about this opportunity and believe my skills align well with your requirements.')
                elif 'additional' in label or 'other' in label or 'comment' in label:
                    fill_value = 'N/A'
                
                if fill_value:
                    await textarea.fill(fill_value)
                    filled_count += 1
                    
            except:
                continue
        
        # ============ HANDLE SELECT DROPDOWNS ============
        selects = await page.query_selector_all('select:visible')
        for select in selects:
            try:
                # Check if already has a value selected
                current_value = await select.input_value()
                if current_value and current_value.strip():
                    continue
                
                label = await get_field_label(page, select)
                options = await select.query_selector_all('option')
                
                if len(options) <= 1:
                    continue
                
                target_value = None
                
                # Try to select based on common patterns
                if any(x in label for x in ['country code', 'phone code']):
                    # Look for India (+91)
                    for opt in options:
                        opt_text = (await opt.text_content() or '').lower()
                        if 'india' in opt_text or '+91' in opt_text:
                            target_value = await opt.get_attribute('value')
                            break
                
                elif any(x in label for x in ['yes', 'no', 'authorized', 'sponsor', 'relocate', 'willing', 'legally']):
                    # Look for "Yes" option for most yes/no questions
                    for opt in options:
                        opt_text = (await opt.text_content() or '').strip().lower()
                        opt_value = await opt.get_attribute('value') or ''
                        if opt_text == 'yes' or opt_value.lower() == 'yes':
                            target_value = await opt.get_attribute('value')
                            break
                
                elif 'experience' in label:
                    # Select a middle option for experience dropdowns
                    for opt in options:
                        opt_text = (await opt.text_content() or '').lower()
                        if any(x in opt_text for x in ['2-3', '3-5', '2+', '3+']):
                            target_value = await opt.get_attribute('value')
                            break
                
                # If no specific match, select first non-empty option
                if not target_value:
                    for opt in options[1:]:  # Skip first (usually "Select...")
                        value = await opt.get_attribute('value')
                        if value and value.strip() and value.lower() not in ['', 'select', 'choose', '-1']:
                            target_value = value
                            break
                
                if target_value:
                    await select.select_option(target_value)
                    filled_count += 1
                    print(f"    [SELECT] {label[:30]}: {target_value[:20]}")
                    
            except:
                continue
        
        # ============ HANDLE RADIO BUTTONS ============
        radio_groups = await page.query_selector_all('fieldset, [role="radiogroup"], .fb-dash-form-element')
        handled_groups = set()
        
        for group in radio_groups:
            try:
                radios = await group.query_selector_all('input[type="radio"]')
                if not radios or len(radios) == 0:
                    continue
                
                # Check if any radio is already selected
                any_checked = False
                for radio in radios:
                    if await radio.is_checked():
                        any_checked = True
                        break
                
                if any_checked:
                    continue
                
                # Get group label
                label = ''
                legend = await group.query_selector('legend, label')
                if legend:
                    label = (await legend.text_content() or '').lower()
                
                # Select appropriate option based on question
                selected = False
                for radio in radios:
                    radio_label = await get_field_label(page, radio)
                    radio_label = radio_label.lower()
                    
                    # For yes/no questions, generally pick "Yes"
                    if 'yes' in radio_label:
                        # Always select "Yes" for these question types
                        if any(x in label for x in [
                            'authorized', 'eligible', 'willing', 'can you', 'do you have', 'are you',
                            'have you', 'completed', 'degree', 'education', 'bachelor', 'master',
                            'doctor', 'phd', 'diploma', 'certificate', 'qualification', 'graduate',
                            'proficient', 'fluent', 'experience with', 'familiar with', 'worked with'
                        ]):
                            await radio.check()
                            selected = True
                            filled_count += 1
                            print(f"    [RADIO] Selected 'Yes' for: {label[:40]}")
                            break
                    elif 'no' in radio_label:
                        if any(x in label for x in ['sponsor', 'require visa', 'need sponsorship']):
                            await radio.check()
                            selected = True
                            filled_count += 1
                            break
                
                # If no specific match, select first option
                if not selected and radios:
                    await radios[0].check()
                    filled_count += 1
                    
            except:
                continue
        
        # ============ HANDLE CHECKBOXES ============
        checkboxes = await page.query_selector_all('input[type="checkbox"]:visible')
        for checkbox in checkboxes:
            try:
                if await checkbox.is_checked():
                    continue
                
                label = await get_field_label(page, checkbox)
                
                # Check boxes for terms, agreements, acknowledgments
                if any(x in label for x in ['agree', 'accept', 'acknowledge', 'confirm', 'terms', 'privacy', 'consent']):
                    await checkbox.check()
                    filled_count += 1
                    
            except:
                continue
        
        if filled_count > 0:
            print(f"    [FORM] Filled {filled_count} fields")
            
    except Exception as e:
        print(f"  [FORM] Error filling fields: {str(e)[:50]}")


async def fill_linkedin_form_questions(page, user_profile: dict, email: str):
    """
    LinkedIn-specific form filler that handles question-based form elements
    by scanning for visible question text and finding associated inputs
    """
    filled_count = 0
    
    try:
        # Find all form sections/groups in the modal
        form_sections = await page.query_selector_all(
            '.jobs-easy-apply-form-section__grouping, '
            '.fb-dash-form-element, '
            '.artdeco-text-input, '
            '.jobs-easy-apply-form-element'
        )
        
        for section in form_sections:
            try:
                # Get the question/label text for this section
                question_text = ''
                label_elem = await section.query_selector('label, .fb-dash-form-element__label, span.t-14, span.t-bold')
                if label_elem:
                    question_text = await label_elem.text_content() or ''
                    question_text = question_text.lower().strip()
                
                if not question_text:
                    # Try getting all text in the section
                    question_text = (await section.text_content() or '').lower()
                
                # Find input in this section
                inp = await section.query_selector('input:not([type="hidden"]):not([type="submit"]):not([type="radio"]):not([type="checkbox"])')
                if inp:
                    current_value = await inp.input_value() or ''
                    if current_value.strip():
                        continue  # Already filled
                    
                    fill_value = None
                    
                    # Match question patterns
                    if any(x in question_text for x in ['overall experience', 'total experience', 'years of experience']):
                        fill_value = str(user_profile.get('years_experience', '3'))
                    elif 'relevant experience' in question_text or 'experience with' in question_text:
                        fill_value = str(user_profile.get('relevant_experience', '2'))
                    elif any(x in question_text for x in ['ai/ml', 'machine learning', 'ai experience', 'ml experience']):
                        fill_value = str(user_profile.get('ai_ml_experience', '2'))
                    elif any(x in question_text for x in ['python', 'java', 'react', 'angular', 'node', 'javascript']):
                        fill_value = str(user_profile.get('tech_experience', '3'))
                    elif 'notice period' in question_text:
                        fill_value = str(user_profile.get('notice_period', '30'))
                    elif any(x in question_text for x in ['current ctc', 'your ctc', 'current salary', 'current compensation']):
                        fill_value = str(user_profile.get('current_ctc', '8'))
                    elif any(x in question_text for x in ['expected ctc', 'expected salary', 'salary expectation']):
                        fill_value = str(user_profile.get('expected_ctc', '12'))
                    elif 'ctc' in question_text:
                        fill_value = str(user_profile.get('ctc', '8'))
                    elif 'gpa' in question_text or 'cgpa' in question_text:
                        fill_value = str(user_profile.get('gpa', '3.5'))
                    elif 'age' in question_text and 'year' not in question_text:
                        fill_value = str(user_profile.get('age', '25'))
                    elif 'phone' in question_text or 'mobile' in question_text:
                        fill_value = user_profile.get('phone_number', user_profile.get('phone', '7569663306'))
                    
                    # Default for numeric fields that require a value > 0
                    if not fill_value:
                        # Check if there's a validation error requiring numeric input
                        error_nearby = await section.query_selector('[class*="error"], .artdeco-inline-feedback--error')
                        if error_nearby:
                            error_text = await error_nearby.text_content() or ''
                            if 'decimal' in error_text.lower() or 'number' in error_text.lower() or 'larger than' in error_text.lower():
                                fill_value = '3'  # Default positive number
                    
                    if fill_value:
                        await inp.clear()
                        await inp.fill(fill_value)
                        await inp.press('Tab')
                        filled_count += 1
                        print(f"    [Q&A] {question_text[:40]}: {fill_value}")
                
                # Handle select dropdown in this section
                select = await section.query_selector('select')
                if select:
                    current_value = await select.input_value() or ''
                    if current_value.strip():
                        continue
                    
                    options = await select.query_selector_all('option')
                    target_value = None
                    
                    # Determine best option based on question
                    if any(x in question_text for x in ['country code', 'phone code']):
                        for opt in options:
                            opt_text = (await opt.text_content() or '').lower()
                            if 'india' in opt_text or '+91' in opt_text or '91' in opt_text:
                                target_value = await opt.get_attribute('value')
                                break
                    elif any(x in question_text for x in ['experience with', 'have you', 'completed', 'do you have']):
                        # Look for "Yes" for qualification/experience questions
                        for opt in options:
                            opt_text = (await opt.text_content() or '').strip()
                            if opt_text.lower() == 'yes':
                                target_value = await opt.get_attribute('value')
                                print(f"    [Q&A SELECT] Selected 'Yes' for: {question_text[:30]}")
                                break
                    elif 'gender' in question_text:
                        for opt in options:
                            opt_text = (await opt.text_content() or '').lower()
                            if 'male' in opt_text and 'female' not in opt_text:
                                target_value = await opt.get_attribute('value')
                                break
                    elif 'degree' in question_text or 'education' in question_text:
                        for opt in options:
                            opt_text = (await opt.text_content() or '').lower()
                            if any(x in opt_text for x in ['bachelor', 'b.tech', 'b.e.', 'undergraduate']):
                                target_value = await opt.get_attribute('value')
                                break
                    
                    # Default: select first valid option
                    if not target_value and len(options) > 1:
                        for opt in options[1:]:
                            val = await opt.get_attribute('value')
                            if val and val.strip() and val.lower() not in ['', 'select', 'choose', '-1']:
                                target_value = val
                                break
                    
                    if target_value:
                        await select.select_option(target_value)
                        filled_count += 1
                        print(f"    [Q&A SELECT] {question_text[:35]}")
                
            except Exception as e:
                continue
        
        # Also scan for any remaining empty inputs with validation errors
        error_inputs = await page.query_selector_all('.artdeco-inline-feedback--error')
        for error_elem in error_inputs:
            try:
                error_text = await error_elem.text_content() or ''
                if 'decimal' in error_text.lower() or 'number' in error_text.lower():
                    # Find the input near this error
                    parent = await error_elem.evaluate_handle('el => el.closest(".fb-dash-form-element, .jobs-easy-apply-form-section__grouping")')
                    if parent:
                        inp = await parent.as_element().query_selector('input')
                        if inp:
                            current = await inp.input_value() or ''
                            if not current.strip():
                                await inp.fill('3')
                                await inp.press('Tab')
                                filled_count += 1
            except:
                continue
        
        if filled_count > 0:
            print(f"    [Q&A] Filled {filled_count} question fields")
            
    except Exception as e:
        print(f"  [Q&A] Error: {str(e)[:40]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python playwright_runner.py <config_json>")
        sys.exit(1)
    
    config_json = sys.argv[1]
    
    # Run the automation
    result = asyncio.run(run_automation(config_json))
    
    # Output result as JSON
    print("\n===RESULT_JSON===")
    print(json.dumps(result, indent=2))
