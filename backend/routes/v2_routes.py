"""
V2 API Routes - Frontend Compatible Endpoints
"""

import asyncio
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
    email: str = Form(""),
    city: str = Form(""),
    state: str = Form(""),
    zip_code: str = Form(""),
    country: str = Form("United States"),
    years_experience: str = Form("0"),
    dry_run: str = Form("true"),
    headless: str = Form("false"),
    resume: UploadFile = File(None)
):
    """V2: Start automation with multipart form data"""
    session_id = str(uuid.uuid4())[:8]
    
    is_dry_run = dry_run.lower() == "true"
    
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
        "phone": phone,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "country": country,
        "years_experience": years_experience,
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


async def run_automation_v2(session_id: str, config: dict):
    """Run the automation workflow"""
    bot = None
    try:
        task = active_tasks[session_id]
        task["status"] = "running"
        task["phase"] = "logging_in"
        
        bot = AutoAgentHireBot(config)
        
        if config.get("resume_path"):
            try:
                bot.parse_resume(config["resume_path"])
            except Exception as e:
                print(f"Resume load warning: {e}")
        
        if config.get("user_profile"):
            bot.user_profile = config["user_profile"]
        
        # Initialize browser
        await bot.initialize_browser()
        
        login_success = await bot.login_linkedin()
        
        if not login_success:
            task["status"] = "failed"
            task["error"] = "Failed to login to LinkedIn"
            return
        
        task["phase"] = "searching_jobs"
        
        jobs = await bot.search_jobs(
            keyword=config["keyword"],
            location=config["location"]
        )
        
        # Collect job listings after search
        jobs = await bot.collect_job_listings(max_jobs=config["max_applications"] * 2)
        
        task["jobs_found"] = len(jobs)
        task["total_jobs"] = min(len(jobs), config["max_applications"])
        
        if not jobs:
            task["status"] = "completed"
            task["phase"] = "no_jobs_found"
            return
        
        task["phase"] = "applying"
        results = []
        
        for i, job in enumerate(jobs[:config["max_applications"]]):
            task["current_job"] = i + 1
            task["current_job_title"] = job.get("title", "Unknown")
            
            try:
                result = await bot.auto_apply_job(job)
                
                app_result = {
                    "title": job.get("title", "Unknown"),
                    "company": job.get("company", "Unknown"),
                    "location": job.get("location", ""),
                    "url": job.get("url", ""),
                    "status": "applied" if result.get("success") else "failed",
                    "reason": result.get("message", ""),
                    "appliedAt": datetime.now().isoformat(),
                    "matchScore": job.get("match_score", 80)
                }
                
                results.append(app_result)
                
                if result.get("success"):
                    task["applications_submitted"] += 1
                else:
                    task["applications_failed"] += 1
                    
            except Exception as e:
                task["applications_failed"] += 1
                results.append({
                    "title": job.get("title", "Unknown"),
                    "company": job.get("company", "Unknown"),
                    "status": "error",
                    "reason": str(e),
                    "appliedAt": datetime.now().isoformat(),
                })
            
            await asyncio.sleep(2)
        
        automation_results[session_id]["results"] = results
        task["status"] = "completed"
        task["phase"] = "finished"
        
    except Exception as e:
        active_tasks[session_id]["status"] = "failed"
        active_tasks[session_id]["error"] = str(e)
    finally:
        if bot:
            try:
                await bot.close()
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
