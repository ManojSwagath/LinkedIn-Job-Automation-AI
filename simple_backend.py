"""
Simplified FastAPI server for testing automation
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, UTC
import uvicorn

app = FastAPI(
    title="LinkedIn Automation API",
    description="Simplified API for testing automation features",
    version="1.0.0"
)

# Store active automation sessions
active_sessions = {}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "LinkedIn Job Automation API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/api/v2/start-automation")
async def start_automation_v2(
    linkedin_email: str = Form(...),
    linkedin_password: str = Form(...),
    job_keywords: str = Form("Software Engineer"),
    job_location: str = Form("Remote"),
    max_applications: int = Form(5),
    first_name: str = Form(""),
    last_name: str = Form(""),
    phone: str = Form(""),
    phone_number: str = Form(""),
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
    dry_run: str = Form("false"),
    headless: str = Form("false"),
    resume: UploadFile = File(None)
):
    """
    Start LinkedIn automation process
    """
    import uuid
    import asyncio
    
    # Basic validation
    if not linkedin_email or not linkedin_password:
        raise HTTPException(status_code=400, detail="LinkedIn credentials are required")
    
    if not first_name or not last_name:
        raise HTTPException(status_code=400, detail="Name is required")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Save resume file if provided
    resume_path = None
    if resume and resume.filename:
        resume_path = f"./data/resumes/{session_id}_{resume.filename}"
        import os
        os.makedirs("./data/resumes", exist_ok=True)
        with open(resume_path, "wb") as buffer:
            content = await resume.read()
            buffer.write(content)
    
    # Prepare configuration
    config = {
        'linkedin_email': linkedin_email,
        'linkedin_password': linkedin_password,
        'keyword': job_keywords,  # Fixed: bot expects 'keyword'
        'location': job_location,  # Fixed: bot expects 'location'
        'max_applications': max_applications,
        'test_mode': dry_run == "true",
        'headless': headless == "true",
        'user_profile': {
            'full_name': f"{first_name} {last_name}".strip(),
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone or phone_number,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'country': country,
            'address': address,
            'linkedin_url': linkedin_url,
            'github_url': github_url,
            'portfolio_url': portfolio_url,
            'current_company': current_company,
            'current_title': current_title,
            'years_experience': years_experience,
            'work_authorization_us': work_authorization_us,
            'require_sponsorship': require_sponsorship,
            'willing_to_relocate': willing_to_relocate,
        },
        'resume_path': resume_path
    }
    
    # Store active session
    active_sessions[session_id] = {
        'status': 'starting',
        'config': config,
        'created_at': datetime.now(UTC),
        'results': []
    }
    
    # Start automation in background
    async def run_automation():
        try:
            # Import here to avoid startup issues
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent))
            from backend.agents.autoagenthire_bot import AutoAgentHireBot
            
            active_sessions[session_id]['status'] = 'running'
            
            # Initialize and run automation
            bot = AutoAgentHireBot(config)
            await bot.run_automation()
            
            active_sessions[session_id]['status'] = 'completed'
            active_sessions[session_id]['results'] = bot.applied_jobs
            
        except Exception as e:
            active_sessions[session_id]['status'] = 'error'
            active_sessions[session_id]['error'] = str(e)
            print(f"Automation error: {e}")
    
    # Start the automation task
    asyncio.create_task(run_automation())
    
    return {
        "session_id": session_id,
        "status": "started",
        "message": "Automation session started successfully",
        "config": {
            "linkedin_email": linkedin_email,
            "job_keywords": job_keywords,
            "job_location": job_location,
            "max_applications": max_applications,
            "dry_run": dry_run == "true",
            "headless": headless == "true"
        }
    }

@app.get("/api/v2/automation-status/{session_id}")
async def get_automation_status(session_id: str):
    """
    Get automation status
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    # Calculate progress based on status
    progress = 0
    if session['status'] == 'starting':
        progress = 10
    elif session['status'] == 'running':
        progress = 50
    elif session['status'] == 'completed':
        progress = 100
    elif session['status'] == 'error':
        progress = 0
    
    return {
        "session_id": session_id,
        "status": session['status'],
        "phase": "automation" if session['status'] == 'running' else session['status'],
        "jobs_found": len(session.get('results', [])),
        "current_job": 1,
        "total_jobs": len(session.get('results', [])),
        "current_job_title": "Processing...",
        "applications_submitted": len([r for r in session.get('results', []) if r.get('status') == 'applied']),
        "applications_failed": len([r for r in session.get('results', []) if r.get('status') == 'failed']),
        "progress": progress,
        "error": session.get('error')
    }

@app.get("/api/v2/automation-results/{session_id}")
async def get_automation_results(session_id: str):
    """Get automation results"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    results = session.get('results', [])
    
    return {
        "session_id": session_id,
        "results": results,
        "total": len(results),
        "successful": len([r for r in results if r.get('status') == 'applied']),
        "failed": len([r for r in results if r.get('status') == 'failed'])
    }

@app.post("/api/ats/match")
async def ats_match():
    """Mock ATS matching endpoint"""
    return {"match_score": 85, "status": "good_match"}

@app.get("/api/agent/status")
async def agent_status():
    """Mock agent status endpoint"""
    return {"status": "running", "agents": []}

if __name__ == "__main__":
    import sys
    print("🚀 Starting Simple Backend Server...")
    print("📝 Server will run on http://127.0.0.1:8000")
    print("📝 Press Ctrl+C to stop")
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("🛑 Server stopped by user")
        sys.exit(0)