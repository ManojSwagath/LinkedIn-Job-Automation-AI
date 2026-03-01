"""FastAPI Routes for LinkedIn Recommended Jobs."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import sys
import os
import platform

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from automation.linkedin_recommended_jobs import fetch_recommended_jobs, fetch_recommended_jobs_sync
from matching.job_filter import filter_jobs, get_available_roles
# Import production-grade filtering system
from matching.job_filter_production import (
    filter_jobs_batch,
    detect_filled_job,
    validate_job_freshness,
    create_ai_validation_prompt,
    ROLE_TAXONOMY
)

router = APIRouter(prefix="/api/linkedin", tags=["LinkedIn Jobs"])


class RecommendedJobsRequest(BaseModel):
    """Request body for fetching LinkedIn recommended jobs."""

    linkedin_email: Optional[str] = None
    linkedin_password: Optional[str] = None
    max_jobs: int = 25
    job_role: Optional[str] = "cloud_engineer"  # Default role for filtering
    enable_filtering: bool = True  # Enable smart filtering by default


@router.post("/recommended-jobs")
async def get_recommended_jobs(payload: RecommendedJobsRequest):
    """
    Fetch recommended jobs from LinkedIn with intelligent filtering
    
    Returns:
        JSON response with total count and job list
        
    Example Response:
    {
        "status": "success",
        "total": 15,
        "filtered_from": 50,
        "jobs": [
            {
                "title": "Senior Cloud Engineer",
                "company": "Google",
                "location": "Mountain View, CA",
                "url": "https://www.linkedin.com/jobs/view/123456789",
                "role": "cloud_engineer",
                "index": 1
            },
            ...
        ]
    }
    """
    try:
        print("📨 Received request for recommended jobs")
        print(f"   Role filter: {payload.job_role}")
        print(f"   Filtering enabled: {payload.enable_filtering}")
        
        # Fetch raw jobs from LinkedIn
        # Use sync wrapper on Windows, async on other platforms
        if platform.system() == "Windows":
            print("🪟 Using Windows-compatible sync scraper")
            raw_jobs = fetch_recommended_jobs_sync(
                email=payload.linkedin_email,
                password=payload.linkedin_password,
            )
        else:
            raw_jobs = await fetch_recommended_jobs(
                email=payload.linkedin_email,
                password=payload.linkedin_password,
            )
        
        print(f"✅ Fetched {len(raw_jobs)} raw jobs from LinkedIn")
        
        # ===================================================================
        # PRODUCTION FILTERING PIPELINE
        # ===================================================================
        # Pipeline: Raw Jobs → Structured Metadata → Hard Filters → 
        #           Filled Detection → Freshness → (AI Validation) → Display
        # ===================================================================
        
        # Transform jobs into structured format for filtering
        jobs_for_filtering = []
        for job in raw_jobs:
            job_dict = {
                "job_id": job.get("url", ""),
                "title": job.get("title", ""),
                # LinkedIn recommended jobs scraping doesn't provide full job descriptions reliably.
                # Keep this empty to prevent the production filter from applying description-based
                # skill checks on synthetic placeholders.
                "description": "",
                "company": job.get("company", "Unknown Company"),
                "location": job.get("location", "Unknown Location"),
                "posted_date": datetime.now() - timedelta(days=1),  # LinkedIn recommendations are recent
                "applicant_count": 0,  # Not available from recommendations
                "apply_button_present": True,  # Assume present
                "apply_link": job.get("url", ""),
                "index": job.get("index", 0)
            }
            jobs_for_filtering.append(job_dict)
        
        # Apply production-grade filtering if enabled
        if payload.enable_filtering and payload.job_role:
            print(f"🔍 Applying PRODUCTION filtering for role: {payload.job_role}")
            
            # Convert role to role_key format
            role_key = payload.job_role.lower().replace(" ", "_")
            
            # Validate role exists
            if role_key not in ROLE_TAXONOMY:
                print(f"⚠️  Unknown role '{role_key}', returning all jobs")
                filtered_jobs = jobs_for_filtering
                filter_warning = f"Role '{payload.job_role}' not recognized. Showing all jobs."
            else:
                # Run production filtering pipeline
                filtered_jobs = filter_jobs_batch(
                    jobs=jobs_for_filtering,
                    role_key=role_key,
                    skip_freshness=True,  # Skip freshness for LinkedIn recommendations (already recent)
                    return_reasons=True
                )
                
                print(f"✅ Production filter: {len(filtered_jobs)}/{len(jobs_for_filtering)} jobs passed")
                
                # If filtering is TOO strict (removes everything), provide helpful warning
                if len(filtered_jobs) == 0:
                    print(f"⚠️  ZERO jobs passed production filters!")
                    print(f"   This means NO jobs matched {role_key} criteria (title + skills + not excluded)")
                    print(f"   Recommendation: Either:")
                    print(f"   1. Disable strict filtering (show all LinkedIn recommendations)")
                    print(f"   2. LinkedIn's recommendations don't match your selected role")
                    
                    # Return empty with clear message
                    filter_warning = f"No jobs matched strict '{payload.job_role}' criteria. LinkedIn recommended jobs like '{raw_jobs[0].get('title', 'N/A') if raw_jobs else 'N/A'}' which don't contain required keywords. Try disabling filtering to see all recommendations."
                else:
                    filter_warning = None
        else:
            filtered_jobs = jobs_for_filtering
            filter_warning = None
            print(f"⏭️  Filtering disabled, returning all {len(filtered_jobs)} jobs")
        
        # Transform back to API format
        result_jobs = []
        for idx, job in enumerate(filtered_jobs):
            result_jobs.append({
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "url": job["apply_link"],
                "role": payload.job_role if payload.job_role else "general",
                "index": idx + 1
            })
        
        # Apply max_jobs limit
        if payload.max_jobs and payload.max_jobs > 0:
            result_jobs = result_jobs[:payload.max_jobs]
        
        response_message = f"Successfully fetched {len(result_jobs)} relevant {payload.job_role or 'jobs'} (filtered from {len(raw_jobs)} total)"
        if filter_warning:
            response_message = filter_warning
        
        return {
            "status": "success",
            "total": len(result_jobs),
            "filtered_from": len(raw_jobs),
            "jobs": result_jobs,
            "message": response_message,
            "filter_applied": payload.enable_filtering,
            "warning": filter_warning
        }
        
    except Exception as e:
        msg = str(e)
        print(f"❌ Error in recommended jobs endpoint: {msg}")

        # Common, expected user-facing failures should not crash the UI with 500s.
        if "Login failed" in msg or "Login not confirmed" in msg or "checkpoint" in msg.lower() or "authwall" in msg.lower():
            return {
                "status": "error",
                "total": 0,
                "jobs": [],
                "message": msg,
            }

        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recommended jobs: {msg}"
        )


@router.get("/recommended-jobs/health")
async def health_check():
    """
    Health check endpoint for LinkedIn jobs service
    """
    return {
        "status": "healthy",
        "service": "LinkedIn Recommended Jobs",
        "endpoints": [
            "/api/linkedin/recommended-jobs",
            "/api/linkedin/available-roles"
        ]
    }


@router.get("/available-roles")
async def get_available_roles_endpoint():
    """
    Get list of available job roles for filtering
    
    Returns:
        List of supported role keys and their display names
    """
    roles = get_available_roles()
    role_display_names = {
        "machine_learning_engineer": "Machine Learning Engineer",
        "data_scientist": "Data Scientist",
        "ai_engineer": "AI Engineer",
        "software_engineer": "Software Engineer",
        "data_engineer": "Data Engineer",
        "mlops_engineer": "MLOps Engineer",
        "research_scientist": "Research Scientist",
        "backend_engineer": "Backend Engineer",
        "frontend_engineer": "Frontend Engineer",
        "fullstack_engineer": "Fullstack Engineer",
        "cloud_engineer": "Cloud Engineer",
        "devops_engineer": "DevOps Engineer"
    }
    
    return {
        "status": "success",
        "total": len(roles),
        "roles": [
            {
                "key": role,
                "display_name": role_display_names.get(role, role.replace("_", " ").title())
            }
            for role in roles
        ]
    }
