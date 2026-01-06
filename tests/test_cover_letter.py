#!/usr/bin/env python3
"""Direct test of cover letter generation"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

async def test_cover_letter():
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.linkedin_auto_apply import LinkedInAutoApply, JobListing
    
    test_resume = Path('./data/resumes/test_resume.txt')
    
    agent = LinkedInAutoApply(
        email='test@example.com',
        password='password',
        resume_path=str(test_resume),
        headless=True,
        use_llm=True
    )
    
    test_job = JobListing(
        job_id="1",
        title="Senior AI Engineer",
        company="TechCorp",
        location="Remote",
        description="Building AI systems with Python and ML. Need expert in TensorFlow, PyTorch, FastAPI.",
        apply_link="https://example.com/job"
    )
    
    print("Testing cover letter generation...")
    print(f"Gemini Key: {agent.gemini_api_key[:20] if agent.gemini_api_key else 'None'}...")
    print(f"OpenAI Key: {agent.openai_api_key[:20] if agent.openai_api_key else 'None'}...")
    
    cover_letter = await agent.generate_cover_letter(test_job)
    
    if cover_letter:
        print("\n✅ SUCCESS! Cover letter generated:")
        print("="*60)
        print(cover_letter)
        print("="*60)
        return True
    else:
        print("\n❌ FAILED: No cover letter generated")
        return False

if __name__ == "__main__":
    asyncio.run(test_cover_letter())
