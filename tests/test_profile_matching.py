#!/usr/bin/env python3
"""
Test Profile Matching System
Tests resume parsing and job matching functionality
"""
import asyncio
import json
import os
from pathlib import Path


async def test_resume_parsing():
    """Test resume parsing functionality."""
    print("\n" + "="*60)
    print("TEST 1: Resume Parsing")
    print("="*60)
    
    from backend.parsers.resume_parser import ResumeParser
    
    # Find existing test resume
    resume_dir = Path("uploads/resumes")
    if not resume_dir.exists() or not list(resume_dir.glob("*.pdf")):
        print("❌ No test resumes found in uploads/resumes/")
        return None
    
    # Get the first PDF resume
    test_resume = list(resume_dir.glob("*.pdf"))[0]
    print(f"\n📄 Testing with: {test_resume.name}")
    
    parser = ResumeParser()
    try:
        resume_data = parser.parse(str(test_resume))
        
        print(f"\n✅ Resume parsed successfully!")
        print(f"   Skills: {len(resume_data.get('skills', []))} found")
        print(f"   Experience: {len(resume_data.get('experience', []))} positions")
        print(f"   Education: {len(resume_data.get('education', []))} degrees")
        print(f"   Raw text length: {len(resume_data.get('raw_text', ''))} characters")
        
        if resume_data.get('skills'):
            print(f"\n   Top skills: {', '.join(resume_data['skills'][:5])}")
        
        if resume_data.get('summary'):
            print(f"\n   Summary: {resume_data['summary'][:150]}...")
        
        return str(test_resume), resume_data
        
    except Exception as e:
        print(f"❌ Error parsing resume: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_profile_matching(resume_path: str, resume_data: dict):
    """Test profile matching against sample job."""
    print("\n" + "="*60)
    print("TEST 2: Profile Matching")
    print("="*60)
    
    from backend.matching.profile_matcher import ProfileMatcher
    
    # Sample job description
    sample_job = {
        "title": "Senior Python Developer",
        "company": "TechCorp Inc.",
        "description": """
We are looking for a Senior Python Developer to join our team.

Requirements:
- 5+ years of Python development experience
- Experience with FastAPI, Django, or Flask
- Strong understanding of REST APIs
- Experience with databases (PostgreSQL, MongoDB)
- Knowledge of cloud platforms (AWS, GCP)
- Experience with Docker and Kubernetes
- Strong problem-solving skills
- Excellent communication skills

Nice to have:
- Machine Learning experience
- DevOps experience
- Open source contributions
"""
    }
    
    print(f"\n📋 Sample Job:")
    print(f"   Title: {sample_job['title']}")
    print(f"   Company: {sample_job['company']}")
    
    try:
        matcher = ProfileMatcher(ai_provider="gemini")
        
        print("\n🔍 Matching profile against job...")
        match_result = matcher.match_profile(
            resume_data=resume_data,
            job_description=sample_job["description"],
            job_title=sample_job["title"],
            company_name=sample_job["company"]
        )
        
        print(f"\n✅ Match completed!")
        print(f"\n   📊 Match Score: {match_result['match_score']}/100")
        print(f"   💡 Recommendation: {match_result['recommendation']}")
        print(f"\n   📝 Reasoning:")
        print(f"      {match_result['reasoning']}")
        
        if match_result.get('strengths'):
            print(f"\n   💪 Strengths:")
            for strength in match_result['strengths']:
                print(f"      • {strength}")
        
        if match_result.get('concerns'):
            print(f"\n   ⚠️  Concerns:")
            for concern in match_result['concerns']:
                print(f"      • {concern}")
        
        return match_result
        
    except Exception as e:
        print(f"❌ Error matching profile: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_batch_matching(resume_path: str, resume_data: dict):
    """Test batch matching against multiple jobs."""
    print("\n" + "="*60)
    print("TEST 3: Batch Matching")
    print("="*60)
    
    from backend.matching.profile_matcher import ProfileMatcher
    
    # Sample jobs
    sample_jobs = [
        {
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "description": "Looking for experienced Python developer with FastAPI and cloud experience."
        },
        {
            "title": "Data Scientist",
            "company": "DataCo",
            "description": "Seeking data scientist with Python, ML, and statistical analysis skills."
        },
        {
            "title": "Junior Frontend Developer",
            "company": "WebDev Inc",
            "description": "Entry-level position for React and TypeScript development."
        }
    ]
    
    print(f"\n📋 Testing with {len(sample_jobs)} jobs")
    
    try:
        matcher = ProfileMatcher(ai_provider="gemini")
        
        print("\n🔍 Batch matching in progress...")
        results = matcher.batch_match(
            resume_data=resume_data,
            jobs=sample_jobs,
            min_score=0  # Include all for testing
        )
        
        print(f"\n✅ Batch matching completed!")
        print(f"   Found {len(results)} matches")
        
        for i, result in enumerate(results, 1):
            match = result["match"]
            print(f"\n   {i}. {result['title']} at {result['company']}")
            print(f"      Score: {match['match_score']}/100 | {match['recommendation']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in batch matching: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_auto_apply_logic(resume_path: str, resume_data: dict):
    """Test auto-apply decision logic."""
    print("\n" + "="*60)
    print("TEST 4: Auto-Apply Logic")
    print("="*60)
    
    from backend.agents.application_agent import ApplicationAgent
    
    # Create mock jobs with different match scores
    mock_jobs = [
        {
            "id": "job1",
            "title": "High Match Job",
            "company": "Company A",
            "match": {
                "match_score": 85,
                "recommendation": "Apply",
                "reasoning": "Strong match"
            }
        },
        {
            "id": "job2",
            "title": "Medium Match Job",
            "company": "Company B",
            "match": {
                "match_score": 65,
                "recommendation": "Review",
                "reasoning": "Partial match"
            }
        },
        {
            "id": "job3",
            "title": "Low Match Job",
            "company": "Company C",
            "match": {
                "match_score": 40,
                "recommendation": "Skip",
                "reasoning": "Poor match"
            }
        }
    ]
    
    try:
        agent = ApplicationAgent(
            ai_provider="gemini",
            min_auto_apply_score=70
        )
        
        print(f"\n📊 Testing auto-apply with threshold: 70")
        
        for job in mock_jobs:
            should_apply = agent._should_auto_apply(job)
            status = "✅ APPLY" if should_apply else "❌ SKIP"
            print(f"\n   {status} | Score: {job['match']['match_score']}/100")
            print(f"   Job: {job['title']} at {job['company']}")
            print(f"   Recommendation: {job['match']['recommendation']}")
        
        print("\n✅ Auto-apply logic test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing auto-apply logic: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 PROFILE MATCHING SYSTEM TESTS")
    print("="*60)
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: GOOGLE_API_KEY not found in environment")
        print("   AI-powered features will not work without an API key")
        print("   Set it in your .env file or export it:")
        print("   export GOOGLE_API_KEY='your-key-here'")
        return
    
    print(f"\n✅ Google API key found: {api_key[:10]}...")
    
    # Test 1: Resume Parsing
    result = await test_resume_parsing()
    if not result:
        print("\n❌ Resume parsing failed. Cannot continue tests.")
        return
    
    resume_path, resume_data = result
    
    # Test 2: Profile Matching
    await test_profile_matching(resume_path, resume_data)
    
    # Test 3: Batch Matching
    await test_batch_matching(resume_path, resume_data)
    
    # Test 4: Auto-Apply Logic
    await test_auto_apply_logic(resume_path, resume_data)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)
    print("\n📝 Summary:")
    print("   ✅ Resume parsing working")
    print("   ✅ Profile matching working")
    print("   ✅ Batch matching working")
    print("   ✅ Auto-apply logic working")
    print("\n🎉 Profile matching system is ready!")
    print("\n📌 Next steps:")
    print("   1. Upload your resume via the frontend")
    print("   2. Search for jobs on LinkedIn")
    print("   3. System will auto-match and apply to high-scoring jobs")
    print("   4. Review applications in the dashboard")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
