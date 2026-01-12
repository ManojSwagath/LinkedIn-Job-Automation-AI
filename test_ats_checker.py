#!/usr/bin/env python
"""
Test the ATS Checker endpoint
"""
import requests
import json
from pathlib import Path

BACKEND_URL = "http://localhost:8000"

def test_ats_checker():
    """Test the ATS /api/ats/match endpoint"""
    print("🧪 Testing ATS Checker Endpoint")
    print("=" * 60)
    
    # Create a sample resume file
    sample_resume = """
JOHN DOE
Senior Software Engineer

EXPERIENCE:
- 5+ years of Python development
- Expert in React, FastAPI, and TypeScript
- Built scalable microservices on AWS
- Led team of 5 engineers
- Machine Learning and AI experience

SKILLS:
Python, JavaScript, React, FastAPI, Docker, Kubernetes, AWS, 
PostgreSQL, MongoDB, Git, Agile, Scrum, TensorFlow, PyTorch
    """
    
    # Sample job description
    job_description = """
Senior Software Engineer

Requirements:
- 5+ years of software development experience
- Strong proficiency in Python and JavaScript
- Experience with React and modern web frameworks
- Cloud platform experience (AWS, Azure, or GCP)
- Database design with PostgreSQL or MongoDB
- Docker and Kubernetes experience
- Machine learning experience is a plus
- Excellent problem-solving skills
- Team leadership experience

Tech Stack: Python, React, FastAPI, AWS, PostgreSQL, Docker, Kubernetes
    """
    
    # Save resume to temporary file
    resume_file = Path("test_resume.txt")
    resume_file.write_text(sample_resume)
    
    try:
        print("\n📤 Sending request to /api/ats/match...")
        
        with open(resume_file, 'rb') as f:
            files = {'resume': ('test_resume.txt', f, 'text/plain')}
            data = {'job_description': job_description}
            
            response = requests.post(
                f"{BACKEND_URL}/api/ats/match",
                files=files,
                data=data,
                timeout=10
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ ATS Analysis - SUCCESS")
            print("\n📊 Results:")
            print(f"   Overall Score: {result.get('score', 0)}%")
            print(f"   Match Score: {result.get('match_score', 0)}%")
            print(f"   Matched Keywords: {len(result.get('matched_keywords', []))}")
            print(f"   Missing Keywords: {len(result.get('missing_keywords', []))}")
            print(f"   Matched Skills: {len(result.get('matched_skills', []))}")
            
            if result.get('matched_keywords'):
                print(f"\n🎯 Top Matched Keywords:")
                for kw in result['matched_keywords'][:10]:
                    print(f"      ✓ {kw}")
            
            if result.get('missing_keywords'):
                print(f"\n⚠️  Missing Keywords (first 5):")
                for kw in result['missing_keywords'][:5]:
                    print(f"      ✗ {kw}")
            
            if result.get('matched_skills'):
                print(f"\n💼 Matched Skills:")
                for skill in result['matched_skills']:
                    print(f"      ✓ {skill}")
            
            if result.get('suggestions'):
                print(f"\n💡 Suggestions:")
                for suggestion in result['suggestions']:
                    print(f"      • {suggestion}")
            
            return True
        else:
            print(f"\n❌ ATS Analysis - FAILED ({response.status_code})")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        # Cleanup
        if resume_file.exists():
            resume_file.unlink()
        print("\n" + "=" * 60)

if __name__ == "__main__":
    success = test_ats_checker()
    exit(0 if success else 1)
