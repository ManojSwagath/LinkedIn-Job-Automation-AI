"""
Production API Routes for AutoAgentHire Multi-Agent System
==========================================================
FastAPI endpoints for running the autonomous agent workflow.
"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database import crud
from backend.agents.multi_agent_orchestrator import MultiAgentOrchestrator
from backend.agents.browser_adapter import create_browser_automation
from backend.rag.resume_intelligence import ResumeIntelligence
from backend.config import settings
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent", tags=["agent"])

# Global orchestrator instances (keyed by run_id)
active_orchestrators: Dict[str, MultiAgentOrchestrator] = {}


# ===========================
# REQUEST/RESPONSE MODELS
# ===========================

class RunAgentRequest(BaseModel):
    """Request to start agent workflow"""
    user_id: str = Field(..., description="User identifier")
    resume_file_path: str = Field(..., description="Path to uploaded resume")
    keywords: str = Field(..., description="Job search keywords", example="Machine Learning Engineer")
    location: str = Field(default="United States", description="Job location")
    max_jobs: int = Field(default=30, description="Maximum jobs to process", ge=1, le=100)
    similarity_threshold: float = Field(default=0.75, description="Match threshold (0-1)", ge=0.5, le=1.0)
    linkedin_email: Optional[str] = Field(None, description="LinkedIn email (or uses env)")
    linkedin_password: Optional[str] = Field(None, description="LinkedIn password (or uses env)")


class RunAgentResponse(BaseModel):
    """Response after starting agent workflow"""
    run_id: str
    status: str
    message: str
    started_at: str


class AgentStatusResponse(BaseModel):
    """Agent workflow status"""
    run_id: str
    user_id: str
    status: str
    current_phase: str
    agents: Dict
    metrics: Dict
    timestamps: Dict


class UploadResumeResponse(BaseModel):
    """Resume upload response"""
    resume_id: int
    filename: str
    file_path: str
    parsed: bool
    message: str


# ===========================
# BACKGROUND TASK
# ===========================

async def run_agent_workflow_background(
    orchestrator: MultiAgentOrchestrator,
    run_id: str,
    user_id: str,
    resume_file_path: str,
    keywords: str,
    location: str,
    max_jobs: int,
    db_session: Session
):
    """Run agent workflow in background and save results to database"""
    try:
        logger.info(f"Starting background workflow: {run_id}")
        
        # Run workflow
        report = await orchestrator.run(
            user_id=user_id,
            resume_file_path=resume_file_path,
            keywords=keywords,
            location=location,
            max_jobs=max_jobs
        )
        
        # Save results to database
        crud.update_agent_run(db_session, run_id, {
            'status': 'completed',
            'current_phase': 'completed',
            'agent_states': {name: agent.__dict__ for name, agent in orchestrator.state.agents.items()},
            'jobs_found': len(orchestrator.state.jobs_found),
            'jobs_matched': len(orchestrator.state.jobs_matched),
            'applications_attempted': len(orchestrator.state.jobs_applied),
            'applications_successful': sum(1 for a in orchestrator.state.jobs_applied if a['status'] == 'success'),
            'final_report': report
        })
        
        # Save applications
        for app_data in orchestrator.state.jobs_applied:
            crud.create_application(db_session, {
                'user_id': int(user_id.split('_')[-1]) if '_' in user_id else 1,
                'job_data': {
                    'job_id': app_data['job_id'],
                    'title': app_data['job_title'],
                    'company': app_data['company']
                },
                'agent_run_id': orchestrator.state.run_id,
                'status': app_data['status'],
                'match_score': app_data['match_score'],
                'success': app_data['status'] == 'success',
                'error_message': app_data.get('error')
            })
        
        logger.info(f"Workflow completed: {run_id}")
        
    except Exception as e:
        logger.error(f"Workflow failed: {run_id} - {e}")
        
        # Update database with failure
        try:
            crud.update_agent_run(db_session, run_id, {
                'status': 'failed',
                'current_phase': 'failed'
            })
        except:
            pass
    
    finally:
        # Remove from active orchestrators
        if run_id in active_orchestrators:
            del active_orchestrators[run_id]


# ===========================
# ENDPOINTS
# ===========================

@router.post("/run", response_model=RunAgentResponse)
async def run_agent(
    request: RunAgentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start autonomous agent workflow.
    
    This endpoint:
    1. Creates agent run record in database
    2. Initializes Multi-Agent Orchestrator
    3. Runs workflow in background
    4. Returns run_id for status polling
    """
    try:
        # Generate run_id
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Validate resume file exists
        if not Path(request.resume_file_path).exists():
            raise HTTPException(status_code=404, detail=f"Resume file not found: {request.resume_file_path}")
        
        # Get or create user
        user_email = request.linkedin_email or settings.LINKEDIN_EMAIL or os.getenv("LINKEDIN_EMAIL", "default@example.com")
        user = crud.get_user_by_email(db, user_email)
        if not user:
            user = crud.create_user(db, email=user_email, linkedin_email=user_email)
        
        # Create agent run record
        crud.create_agent_run(db, {
            'run_id': run_id,
            'user_id': user.id,
            'keywords': request.keywords,
            'location': request.location,
            'max_jobs': request.max_jobs,
            'similarity_threshold': request.similarity_threshold
        })
        
        # Initialize components
        resume_intelligence = ResumeIntelligence(
            openai_api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        )
        
        browser_automation = create_browser_automation({
            'linkedin_email': request.linkedin_email or settings.LINKEDIN_EMAIL or os.getenv("LINKEDIN_EMAIL"),
            'linkedin_password': request.linkedin_password or settings.LINKEDIN_PASSWORD or os.getenv("LINKEDIN_PASSWORD"),
            'auto_apply': True,
            'max_results': request.max_jobs
        })
        
        # Create orchestrator
        orchestrator = MultiAgentOrchestrator(
            resume_intelligence=resume_intelligence,
            browser_automation=browser_automation,
            similarity_threshold=request.similarity_threshold
        )
        
        # Store orchestrator
        active_orchestrators[run_id] = orchestrator
        
        # Run in background
        background_tasks.add_task(
            run_agent_workflow_background,
            orchestrator,
            run_id,
            request.user_id,
            request.resume_file_path,
            request.keywords,
            request.location,
            request.max_jobs,
            db
        )
        
        return RunAgentResponse(
            run_id=run_id,
            status="running",
            message="Agent workflow started successfully",
            started_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to start agent workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{run_id}", response_model=AgentStatusResponse)
async def get_agent_status(run_id: str, db: Session = Depends(get_db)):
    """
    Get real-time status of agent workflow.
    Frontend should poll this endpoint every 5 seconds.
    """
    # Check if orchestrator is active (in-memory)
    if run_id in active_orchestrators:
        orchestrator = active_orchestrators[run_id]
        status = orchestrator.get_status()
        return AgentStatusResponse(**status)
    
    # Otherwise, check database
    agent_run = crud.get_agent_run(db, run_id)
    if not agent_run:
        raise HTTPException(status_code=404, detail=f"Agent run not found: {run_id}")
    
    return AgentStatusResponse(
        run_id=agent_run.run_id,
        user_id=str(agent_run.user_id),
        status=agent_run.status,
        current_phase=agent_run.current_phase or "unknown",
        agents=agent_run.agent_states or {},
        metrics={
            'jobs_found': agent_run.jobs_found,
            'jobs_matched': agent_run.jobs_matched,
            'jobs_applied': agent_run.applications_attempted
        },
        timestamps={
            'started_at': agent_run.started_at.isoformat(),
            'completed_at': agent_run.completed_at.isoformat() if agent_run.completed_at else None
        }
    )


@router.get("/results/{run_id}")
async def get_agent_results(run_id: str, db: Session = Depends(get_db)):
    """Get final results for a completed workflow"""
    agent_run = crud.get_agent_run(db, run_id)
    if not agent_run:
        raise HTTPException(status_code=404, detail=f"Agent run not found: {run_id}")
    
    if agent_run.status not in ['completed', 'failed']:
        raise HTTPException(status_code=400, detail=f"Workflow still running. Current status: {agent_run.status}")
    
    # Get applications
    applications = crud.get_agent_run_applications(db, run_id)
    
    return {
        'run_id': run_id,
        'status': agent_run.status,
        'final_report': agent_run.final_report,
        'applications': [
            {
                'job_title': app.job.title,
                'company': app.job.company,
                'match_score': app.match_score,
                'status': app.status,
                'success': app.success,
                'applied_at': app.applied_at.isoformat()
            }
            for app in applications
        ],
        'summary': {
            'jobs_found': agent_run.jobs_found,
            'jobs_matched': agent_run.jobs_matched,
            'applications_attempted': agent_run.applications_attempted,
            'applications_successful': agent_run.applications_successful
        }
    }


@router.post("/resume/upload", response_model=UploadResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """
    Upload and parse resume.
    
    Accepts: PDF, DOCX, TXT files
    """
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file
        upload_dir = Path("data/resumes")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        file_path = upload_dir / filename
        
        # Write file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse resume
        try:
            resume_intelligence = ResumeIntelligence()
            resume_data = resume_intelligence.parse_resume_file(str(file_path))
            
            # Get or create user
            user = crud.get_user_by_email(db, user_id)
            if not user:
                user = crud.create_user(db, email=user_id)
            
            # Save to database
            resume_dict = {
                'filename': filename,
                'file_path': str(file_path),
                'file_type': file_extension.lstrip('.'),
                'raw_text': resume_data.raw_text,
                'name': resume_data.name,
                'email': resume_data.email,
                'phone': resume_data.phone,
                'skills': resume_data.skills,
                'experience_years': resume_data.experience_years,
                'experience': resume_data.experience,
                'education': resume_data.education,
                'tools': resume_data.tools,
                'keywords': resume_data.keywords,
                'summary': resume_data.summary,
                'embedding': resume_data.embedding.tolist() if resume_data.embedding is not None else None
            }
            
            resume_record = crud.create_resume(db, user.id, resume_dict)
            
            # Deactivate other resumes
            crud.deactivate_other_resumes(db, user.id, resume_record.id)
            
            return UploadResumeResponse(
                resume_id=resume_record.id,
                filename=filename,
                file_path=str(file_path),
                parsed=True,
                message=f"Resume parsed successfully. Found {len(resume_data.skills)} skills."
            )
            
        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            return UploadResumeResponse(
                resume_id=0,
                filename=filename,
                file_path=str(file_path),
                parsed=False,
                message=f"Resume saved but parsing failed: {str(e)}"
            )
        
    except Exception as e:
        logger.error(f"Resume upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applications")
async def get_applications(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get applications for a user"""
    if not user_id:
        user_id = "default_user"
    
    user = crud.get_user_by_email(db, user_id)
    if not user:
        return {'applications': [], 'total': 0}
    
    applications = crud.get_user_applications(db, user.id, status=status, limit=limit)
    
    return {
        'applications': [
            {
                'id': app.id,
                'job_title': app.job.title,
                'company': app.job.company,
                'location': app.job.location,
                'status': app.status,
                'match_score': app.match_score,
                'success': app.success,
                'applied_at': app.applied_at.isoformat(),
                'error': app.error_message
            }
            for app in applications
        ],
        'total': len(applications)
    }


@router.get("/runs")
async def get_agent_runs(
    user_id: str = "default_user",
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get agent run history for a user"""
    user = crud.get_user_by_email(db, user_id)
    if not user:
        return {'runs': [], 'total': 0}
    
    runs = crud.get_user_agent_runs(db, user.id, limit=limit)
    
    return {
        'runs': [
            {
                'run_id': run.run_id,
                'status': run.status,
                'current_phase': run.current_phase,
                'keywords': run.keywords,
                'location': run.location,
                'jobs_found': run.jobs_found,
                'applications_successful': run.applications_successful,
                'started_at': run.started_at.isoformat(),
                'completed_at': run.completed_at.isoformat() if run.completed_at else None
            }
            for run in runs
        ],
        'total': len(runs)
    }


@router.get("/stats")
async def get_user_stats(user_id: str = "default_user", db: Session = Depends(get_db)):
    """Get user statistics"""
    user = crud.get_user_by_email(db, user_id)
    if not user:
        return {'error': 'User not found'}
    
    stats = crud.get_user_stats(db, user.id)
    return stats
