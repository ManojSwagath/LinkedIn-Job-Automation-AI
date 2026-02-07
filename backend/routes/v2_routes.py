"""
V2 API Routes - Frontend Compatible Endpoints
"""

import asyncio
import subprocess
import sys
import uuid
import json
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from backend.agents.autoagenthire_bot import AutoAgentHireBot

router = APIRouter(prefix="/api/v2", tags=["V2 Automation"])

active_tasks = {}
automation_results = {}


@router.post("/start-automation")
async def start_automation_v2(
    linkedin_email: str = Form(...),
    linkedin_password: str = Form(...),
    job_keywords: str = Form("Software Engineer"),
    job_location: str = Form("Remote"),
    max_applications: int = Form(5),
    first_name: str = Form(""),
    last_name: str = Form(""),
    phone: str = Form(""),
    phone_number: str = Form(""),  # Accept both phone and phone_number from frontend
    email: str = Form(""),
    city: str = Form(""),
    state: str = Form(""),
    zip_code: str = Form(""),
    country: str = Form("United States"),
    address: str = Form(""),
    linkedin_url: str = Form(""),
    github_url: str = Form(""),
    portfolio_url: str = Form(""),
    current_company: str = Form(""),
    current_title: str = Form(""),
    years_experience: str = Form("0"),
    work_authorization_us: str = Form("Yes"),
    require_sponsorship: str = Form("No"),
    willing_to_relocate: str = Form("Yes"),
    dry_run: str = Form("false"),  # CHANGED: Default to false (actually submit)
    headless: str = Form("false"),
    resume: UploadFile = File(None)
):
    """V2: Start automation with multipart form data"""
    session_id = str(uuid.uuid4())[:8]
    
    is_dry_run = dry_run.lower() == "true"
    
    # Use phone_number if phone is empty (frontend sends phone_number)
    actual_phone = phone or phone_number
    
    print(f"\n[AUTOMATION V2] Starting with dry_run={is_dry_run}")
    print(f"[AUTOMATION V2] User: {first_name} {last_name}, Email: {email}, Phone: {actual_phone}")
    print(f"[AUTOMATION V2] Location: {job_location}, City: {city}")
    
    resume_path = None
    if resume:
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        resume_path = uploads_dir / f"{session_id}_{resume.filename}"
        with open(resume_path, "wb") as f:
            content = await resume.read()
            f.write(content)
        resume_path = str(resume_path)
    
    user_profile = {
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{first_name} {last_name}".strip(),
        "email": email,
        "phone_number": actual_phone,
        "phone": actual_phone,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "country": country,
        "address": address,
        "street_address": address,
        "linkedin_url": linkedin_url,
        "github_url": github_url,
        "portfolio_url": portfolio_url,
        "current_company": current_company,
        "current_title": current_title,
        "years_experience": years_experience,
        "work_authorization_us": work_authorization_us,
        "require_sponsorship": require_sponsorship,
        "willing_to_relocate": willing_to_relocate == "Yes",
        "visa_status": "Authorized to work" if work_authorization_us == "Yes" else "Requires sponsorship",
        # Also store location for form filling
        "location": job_location,
        "preferred_location": job_location,
    }
    
    active_tasks[session_id] = {
        "status": "initializing",
        "phase": "setup",
        "jobs_found": 0,
        "current_job": 0,
        "total_jobs": 0,
        "current_job_title": "",
        "applications_submitted": 0,
        "applications_failed": 0,
        "error": None,
    }
    
    automation_results[session_id] = {"results": [], "summary": {}}
    
    config = {
        "keyword": job_keywords,
        "location": job_location,
        "max_applications": min(max_applications, 20),
        "easy_apply_only": True,
        "auto_apply": not is_dry_run,
        "dry_run": is_dry_run,
        "headless": headless.lower() == "true",
        "linkedin_email": linkedin_email,
        "linkedin_password": linkedin_password,
        "resume_path": resume_path,
        "user_profile": user_profile,
    }
    
    active_tasks[session_id]["config"] = config
    asyncio.create_task(run_automation_v2(session_id, config))
    
    return {
        "status": "started",
        "session_id": session_id,
        "message": f"Automation started",
        "dry_run": is_dry_run
    }


async def run_playwright_subprocess(session_id: str, config: dict):
    """Run Playwright in a subprocess to avoid event loop conflicts on Windows"""
    import threading
    
    task = active_tasks[session_id]
    
    def run_in_thread():
        """Run subprocess in a separate thread to avoid asyncio conflicts"""
        try:
            # Build config for the subprocess
            subprocess_config = {
                "linkedin_email": config.get("linkedin_email"),
                "linkedin_password": config.get("linkedin_password"),
                "keyword": config.get("keyword", "Software Engineer"),
                "location": config.get("location", "Remote"),
                "max_applications": config.get("max_applications", 5),
                "dry_run": config.get("dry_run", True),
                "headless": config.get("headless", False),
                "user_profile": config.get("user_profile", {}),
            }
            
            config_json = json.dumps(subprocess_config)
            
            # Run the playwright_runner.py script
            runner_path = Path(__file__).parent.parent / "playwright_runner.py"
            python_exe = sys.executable
            
            print(f"🚀 Starting Playwright subprocess: {runner_path}")
            print(f"🐍 Python: {python_exe}")
            print(f"📂 CWD: {Path(__file__).parent.parent.parent}")
            
            task["status"] = "running"
            task["phase"] = "subprocess_started"
            
            # Use subprocess.Popen with threading instead of asyncio
            process = subprocess.Popen(
                [python_exe, str(runner_path), config_json],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=str(Path(__file__).parent.parent.parent),
                text=True,
                bufsize=1
            )
            
            # Stream output
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                line_str = line.strip()
                output_lines.append(line_str)
                print(f"[SUBPROCESS] {line_str}")
                
                # Update task status based on output
                if "Browser initialized" in line_str:
                    task["phase"] = "browser_initialized"
                elif "Login successful" in line_str or "Already logged in" in line_str:
                    task["phase"] = "logged_in"
                elif "Searching for jobs" in line_str:
                    task["phase"] = "searching_jobs"
                elif "Collected" in line_str and "jobs" in line_str:
                    task["phase"] = "jobs_collected"
                    try:
                        import re
                        match = re.search(r'Collected (\d+) jobs', line_str)
                        if match:
                            task["jobs_found"] = int(match.group(1))
                            task["total_jobs"] = min(int(match.group(1)), config.get("max_applications", 5))
                    except:
                        pass
                elif "Applying to:" in line_str:
                    task["phase"] = "applying"
                    task["current_job"] = task.get("current_job", 0) + 1
                    task["current_job_title"] = line_str.split("Applying to:")[-1].strip()[:50]
                elif "Application submitted" in line_str or "[SUCCESS]" in line_str:
                    task["applications_submitted"] = task.get("applications_submitted", 0) + 1
                elif "DRY RUN" in line_str:
                    task["applications_submitted"] = task.get("applications_submitted", 0) + 1
            
            process.wait()
            
            # Parse result JSON from output - find the JSON block after ===RESULT_JSON===
            result_json = None
            json_started = False
            json_lines = []
            for line in output_lines:
                if "===RESULT_JSON===" in line:
                    json_started = True
                    continue
                if json_started:
                    # Stop at first non-JSON line (exception traces, etc)
                    if line.startswith("Exception") or line.startswith("Traceback"):
                        break
                    json_lines.append(line)
            
            if json_lines:
                result_json = "\n".join(json_lines)
            
            if result_json:
                try:
                    result = json.loads(result_json)
                    automation_results[session_id]["results"] = [
                        {
                            "title": app.get("title", "Unknown"),
                            "company": app.get("company", "Unknown"),
                            "status": "applied" if app.get("status") in ["APPLIED", "DRY_RUN"] else "failed",
                            "reason": app.get("error", ""),
                            "appliedAt": datetime.now().isoformat(),
                        }
                        for app in result.get("applications", [])
                    ]
                    task["applications_submitted"] = len([a for a in result.get("applications", []) if a.get("status") in ["APPLIED", "DRY_RUN"]])
                    task["applications_failed"] = len([a for a in result.get("applications", []) if a.get("status") not in ["APPLIED", "DRY_RUN"]])
                except json.JSONDecodeError as e:
                    print(f"Failed to parse result JSON: {e}")
                    pass
            
            task["status"] = "completed"
            task["phase"] = "finished"
            
            print(f"\n{'='*60}")
            print(f"✅ SUBPROCESS AUTOMATION COMPLETE")
            print(f"{'='*60}")
            
        except Exception as e:
            import traceback
            print(f"\n❌ SUBPROCESS ERROR: {str(e)}")
            traceback.print_exc()
            task["status"] = "failed"
            task["error"] = str(e)
    
    # Start thread and return immediately
    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()


async def run_automation_v2(session_id: str, config: dict):
    """Run the automation workflow - uses subprocess on Windows to avoid event loop issues"""
    
    # On Windows, use subprocess approach to avoid Playwright event loop conflicts
    import platform
    if platform.system() == "Windows":
        print("🪟 Windows detected - using subprocess for Playwright")
        await run_playwright_subprocess(session_id, config)
        return
    
    # On other platforms, use direct async approach
    bot = None
    try:
        task = active_tasks[session_id]
        task["status"] = "running"
        task["phase"] = "logging_in"
        
        print(f"\n{'='*60}")
        print(f"🚀 AUTOMATION SESSION: {session_id}")
        print(f"{'='*60}")
        print(f"Config: keyword={config.get('keyword')}, location={config.get('location')}")
        print(f"Max applications: {config.get('max_applications')}")
        print(f"Dry run: {config.get('dry_run')}")
        
        bot = AutoAgentHireBot(config)
        
        if config.get("resume_path"):
            try:
                print(f"📄 Loading resume from: {config.get('resume_path')}")
                bot.parse_resume(config["resume_path"])
            except Exception as e:
                print(f"⚠️  Resume load warning: {e}")
        
        if config.get("user_profile"):
            bot.user_profile = config["user_profile"]
            print(f"👤 User profile loaded: {config['user_profile'].get('first_name')} {config['user_profile'].get('last_name')}")
        
        # Initialize browser
        print("\n📍 Initializing browser...")
        await bot.initialize_browser()
        print("✅ Browser initialized")
        
        print("\n📍 Logging into LinkedIn...")
        login_success = await bot.login_linkedin()
        
        if not login_success:
            task["status"] = "failed"
            task["error"] = "Failed to login to LinkedIn - check your credentials"
            print("❌ Login failed!")
            return
        
        print("✅ LinkedIn login successful")
        task["phase"] = "searching_jobs"
        
        print(f"\n📍 Searching for jobs: '{config['keyword']}' in '{config['location']}'...")
        await bot.search_jobs(
            keyword=config["keyword"],
            location=config["location"]
        )
        
        # Collect job listings after search
        print(f"📍 Collecting job listings (max {config['max_applications'] * 2})...")
        jobs = await bot.collect_job_listings(max_jobs=config["max_applications"] * 2)
        
        task["jobs_found"] = len(jobs)
        task["total_jobs"] = min(len(jobs), config["max_applications"])
        
        print(f"✅ Found {len(jobs)} jobs")
        
        if not jobs:
            task["status"] = "completed"
            task["phase"] = "no_jobs_found"
            task["error"] = "No jobs found matching your criteria"
            print("⚠️  No jobs found!")
            return
        
        task["phase"] = "applying"
        results = []
        
        print(f"\n📍 Starting applications (up to {config['max_applications']})...")
        for i, job in enumerate(jobs[:config["max_applications"]]):
            task["current_job"] = i + 1
            task["current_job_title"] = job.get("title", "Unknown")
            
            try:
                result = await bot.auto_apply_job(job)
                
                # Check application status from result dict
                # auto_apply_job returns a job dict with 'application_status' field
                app_status = result.get("application_status", "FAILED")
                is_success = app_status in ["APPLIED", "DRY_RUN"]
                
                app_result = {
                    "title": result.get("title", job.get("title", "Unknown")),
                    "company": result.get("company", job.get("company", "Unknown")),
                    "location": result.get("location", job.get("location", "")),
                    "url": result.get("url", job.get("url", "")),
                    "status": "applied" if is_success else "failed",
                    "reason": result.get("application_reason", result.get("message", "")),
                    "appliedAt": datetime.now().isoformat(),
                    "matchScore": result.get("match_score", job.get("match_score", 80))
                }
                
                results.append(app_result)
                
                if is_success:
                    task["applications_submitted"] += 1
                else:
                    task["applications_failed"] += 1
                    
            except Exception as e:
                print(f"❌ Application error for {job.get('title', 'Unknown')}: {str(e)}")
                task["applications_failed"] += 1
                results.append({
                    "title": job.get("title", "Unknown"),
                    "company": job.get("company", "Unknown"),
                    "location": job.get("location", ""),
                    "url": job.get("url", ""),
                    "status": "error",
                    "reason": str(e),
                    "appliedAt": datetime.now().isoformat(),
                })
            
            await asyncio.sleep(2)
        
        automation_results[session_id]["results"] = results
        task["status"] = "completed"
        task["phase"] = "finished"
        
        print(f"\n{'='*60}")
        print(f"✅ AUTOMATION COMPLETE")
        print(f"{'='*60}")
        print(f"Jobs found: {task['jobs_found']}")
        print(f"Applications submitted: {task['applications_submitted']}")
        print(f"Applications failed: {task['applications_failed']}")
        
    except Exception as e:
        import traceback
        print(f"\n❌ AUTOMATION ERROR: {str(e)}")
        traceback.print_exc()
        active_tasks[session_id]["status"] = "failed"
        active_tasks[session_id]["error"] = str(e)
    finally:
        if bot:
            try:
                await bot.close()
                print("🔒 Browser closed")
            except:
                pass



@router.get("/automation-status/{session_id}")
async def get_automation_status_v2(session_id: str):
    """V2: Get real-time automation status"""
    if session_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Session not found")
    
    task = active_tasks[session_id]
    return {
        "session_id": session_id,
        "status": task.get("status", "unknown"),
        "phase": task.get("phase", ""),
        "jobs_found": task.get("jobs_found", 0),
        "current_job": task.get("current_job", 0),
        "total_jobs": task.get("total_jobs", 0),
        "current_job_title": task.get("current_job_title", ""),
        "applications_submitted": task.get("applications_submitted", 0),
        "applications_failed": task.get("applications_failed", 0),
        "error": task.get("error"),
    }


@router.get("/automation-results/{session_id}")
async def get_automation_results_v2(session_id: str):
    """V2: Get automation results"""
    if session_id not in automation_results:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return automation_results[session_id]
