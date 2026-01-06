import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from agents.job_search_agent import JobSearchAgent
from agents.application_agent import ApplicationAgent

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EnhancedOrchestrator:
    """Enhanced orchestrator for coordinating AI agents in the job application process."""
    
    def __init__(self):
        self.job_search_agent = JobSearchAgent()
        self.application_agent = ApplicationAgent()
        
        self.status = AgentStatus.IDLE
        self.current_task = None
        
    async def search_and_apply(
        self,
        search_criteria: Dict[str, Any],
        user_profile: Dict[str, Any],
        auto_apply: bool = False
    ) -> Dict[str, Any]:
        """
        Orchestrate the complete job search and application process.
        
        Args:
            search_criteria: Job search parameters (keywords, location, etc.)
            user_profile: User's profile information for resume customization
            auto_apply: Whether to automatically apply to matching jobs
            
        Returns:
            Summary of the process results
        """
        try:
            self.status = AgentStatus.RUNNING
            results = {
                "jobs_found": 0,
                "applications_submitted": 0,
                "resumes_generated": 0,
                "errors": []
            }
            
            # Step 1: Search for jobs
            logger.info("Starting job search...")
            # JobSearchAgent currently expects keywords/location fields.
            jobs = await self.job_search_agent.search_jobs(
                keywords=search_criteria.get("keywords") or search_criteria.get("job_role") or "Software Engineer",
                location=search_criteria.get("location") or "",
                max_results=search_criteria.get("max_results") or 25,
            )
            results["jobs_found"] = len(jobs)
            
            # Step 2: Process each job
            for job in jobs:
                try:
                    # Resume generation is optional in this repo; if caller provided resume_data, pass it through.
                    resume = user_profile.get("resume_data") or user_profile.get("resume")
                    if resume:
                        results["resumes_generated"] += 1
                    
                    # Apply if auto_apply is enabled
                    if auto_apply:
                        logger.info(f"Applying to job: {job.get('title')}")
                        application_result = await self.application_agent.apply_to_job(
                            job=job,
                            user_id=user_profile.get("user_id", "default"),
                            resume_data=resume if isinstance(resume, dict) else None,
                            auto_submit=True,
                            force_apply=True,
                        )
                        
                        if application_result.get("status") in ("submitted", "dry_run", "pending_review"):
                            results["applications_submitted"] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing job {job.get('id')}: {str(e)}")
                    results["errors"].append({
                        "job_id": job.get("id"),
                        "error": str(e)
                    })
            
            self.status = AgentStatus.COMPLETED
            return results
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            logger.error(f"Orchestration failed: {str(e)}")
            raise
    
    async def get_application_status(self, user_id: str) -> List[Dict[str, Any]]:
        """Get the status of all applications for a user (not implemented in this orchestrator)."""
        return []
    
    async def update_application_status(
        self,
        application_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update the status of a specific application (not implemented in this orchestrator)."""
        return {"success": False, "message": "Tracking agent not configured"}
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get the current status of the orchestrator."""
        return {
            "status": self.status.value,
            "current_task": self.current_task,
            "timestamp": datetime.now().isoformat()
        }