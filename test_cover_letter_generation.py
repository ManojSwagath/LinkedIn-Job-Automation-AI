#!/usr/bin/env python3
"""
Test Cover Letter Generation API
Tests the Gemini-powered cover letter endpoint
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_cover_letter_generation():
    """Test cover letter generation with sample data"""
    
    print("🧪 Testing Cover Letter Generation API\n")
    print("=" * 60)
    
    # Sample resume text
    resume_text = """
    John Doe
    Senior Software Engineer
    
    EXPERIENCE:
    - 5 years of Python development
    - Expert in FastAPI, Django, Flask
    - Experience with PostgreSQL, MongoDB
    - CI/CD pipeline setup and maintenance
    - Team leadership and mentoring
    
    SKILLS:
    Python, JavaScript, React, Node.js, Docker, Kubernetes,
    AWS, Azure, Git, Agile/Scrum
    
    EDUCATION:
    Bachelor of Science in Computer Science
    """
    
    # Sample job description
    job_description = """
    Senior Python Developer
    
    We are looking for an experienced Python developer to join our team.
    
    REQUIREMENTS:
    - 5+ years of Python experience
    - Strong knowledge of FastAPI or Django
    - Experience with PostgreSQL
    - Docker and Kubernetes experience
    - CI/CD pipeline knowledge
    - Excellent communication skills
    
    RESPONSIBILITIES:
    - Design and develop RESTful APIs
    - Mentor junior developers
    - Implement best practices
    - Collaborate with cross-functional teams
    """
    
    # Prepare request
    payload = {
        "resume_text": resume_text.strip(),
        "job_description": job_description.strip()
    }
    
    print("\n📤 Sending request to /api/cover-letter/generate...")
    print(f"Resume length: {len(resume_text)} characters")
    print(f"Job description length: {len(job_description)} characters")
    
    try:
        # Make API call
        response = requests.post(
            f"{API_BASE_URL}/api/cover-letter/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            cover_letter = data.get("cover_letter", "")
            
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Cover Letter Generated:")
            print("=" * 60)
            print(f"\n{cover_letter}\n")
            print("=" * 60)
            print(f"\n📊 Statistics:")
            print(f"   - Length: {len(cover_letter)} characters")
            print(f"   - Words: {len(cover_letter.split())} words")
            print(f"   - Lines: {len(cover_letter.split(chr(10)))} lines")
            print("\n✅ Test PASSED!")
            
            return True
        else:
            error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
            print(f"\n❌ FAILED: {error_data.get('detail', response.text)}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ FAILED: Request timeout (>30s)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ FAILED: Cannot connect to {API_BASE_URL}")
        print("   Make sure the backend server is running:")
        print("   cd backend && python -m uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False


def test_backend_health():
    """Quick health check"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print("⚠️  Backend responded but not healthy")
            return False
    except:
        print("❌ Backend is not responding")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🤖 Cover Letter Generation Test Suite")
    print("=" * 60)
    
    # Check backend health first
    print("\n1️⃣  Checking backend health...")
    if not test_backend_health():
        print("\n❌ Cannot proceed without healthy backend")
        exit(1)
    
    # Test cover letter generation
    print("\n2️⃣  Testing cover letter generation...")
    success = test_cover_letter_generation()
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Cover letter generation is working correctly")
        print("✅ Gemini API integration successful")
        print("✅ Frontend can now generate cover letters")
    else:
        print("❌ TESTS FAILED")
        print("=" * 60)
        print("\nPlease check:")
        print("  1. Backend server is running (port 8000)")
        print("  2. GOOGLE_API_KEY is set in backend/.env")
        print("  3. Gemini API key has proper permissions")
    
    print("\n" + "=" * 60)
