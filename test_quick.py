"""
Quick Test Runner - Tests core components without LinkedIn
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.rag.resume_intelligence import ResumeIntelligence
from backend.database.connection import get_db_session
from backend.database import crud
import asyncio

print("="*70)
print(" "*20 + "QUICK COMPONENT TEST")
print("="*70 + "\n")

# Test 1: Resume Intelligence
print("1️⃣ Testing Resume Intelligence...")
try:
    # Create test resume
    test_resume = Path("data/resumes/test_quick.txt")
    test_resume.parent.mkdir(parents=True, exist_ok=True)
    
    test_resume.write_text("""
John Smith
john.smith@example.com | (555) 123-4567

PROFESSIONAL SUMMARY
Senior Machine Learning Engineer with 6 years of experience in developing and deploying ML models at scale.

SKILLS
• Programming: Python, TensorFlow, PyTorch, Scikit-learn
• ML/AI: Deep Learning, NLP, Computer Vision, MLOps
• Tools: Docker, Kubernetes, AWS, Git
• Data: SQL, Pandas, NumPy, Spark

EXPERIENCE
Senior ML Engineer | TechCorp | 2021-Present
- Built recommendation system serving 2M+ users
- Improved model accuracy by 30%
- Led team of 4 engineers

ML Engineer | DataCo | 2019-2021
- Developed NLP pipelines
- Deployed models to production

EDUCATION
M.S. Computer Science | Stanford | 2019
B.S. Computer Science | UC Berkeley | 2017
    """)
    
    # Parse resume
    resume_intel = ResumeIntelligence()
    resume_data = resume_intel.parse_resume_file(str(test_resume))
    
    print(f"   ✓ Resume parsed successfully")
    print(f"   Name: {resume_data.name}")
    print(f"   Skills: {len(resume_data.skills)} found")
    print(f"   Experience: {resume_data.experience_years} years")
    print(f"   Embedding: {len(resume_data.embedding) if resume_data.embedding is not None else 0}D vector")
    
    # Test job matching
    test_jobs = [
        {
            'job_id': '123',
            'title': 'Senior Machine Learning Engineer',
            'company': 'AI Corp',
            'description': 'We need an ML engineer with Python, TensorFlow, and production experience. Must have NLP and deep learning skills.'
        },
        {
            'job_id': '456',
            'title': 'Frontend Developer',
            'company': 'WebCo',
            'description': 'React, JavaScript, CSS expert needed for our web team.'
        }
    ]
    
    matches = resume_intel.match_multiple_jobs(test_jobs)
    print(f"\n   Job Matching Results:")
    for match in matches:
        print(f"   • {match.job_title} @ {match.company}")
        print(f"     Match: {match.match_score:.1f}% | Recommendation: {match.recommendation}")
    
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: Database Operations
print("2️⃣ Testing Database Operations...")
try:
    with get_db_session() as db:
        # Create test user
        test_email = f"test_quick@example.com"
        
        # Check if user exists
        user = crud.get_user_by_email(db, test_email)
        if not user:
            user = crud.create_user(db, email=test_email, username="quicktest")
            print(f"   ✓ User created: {user.email}")
        else:
            print(f"   ✓ User found: {user.email}")
        
        # Get user stats
        stats = crud.get_user_stats(db, user.id)
        print(f"   ✓ Stats: {stats['total_applications']} applications, {stats['success_rate']:.1f}% success rate")
        
        # Get agent runs
        runs = crud.get_user_agent_runs(db, user.id, limit=5)
        print(f"   ✓ Agent runs: {len(runs)} found")

except Exception as e:
    print(f"   ❌ Failed: {e}")

print()

# Test 3: API Routes (Import check)
print("3️⃣ Testing API Routes...")
try:
    from backend.routes.agent_routes import router
    print(f"   ✓ Agent routes imported successfully")
    print(f"   ✓ Endpoints: {len([r for r in router.routes])} routes defined")
except Exception as e:
    print(f"   ❌ Failed: {e}")

print()

print("="*70)
print(" "*25 + "✅ TESTS COMPLETE")
print("="*70)
print()

print("Next steps:")
print("1. Add your LinkedIn credentials to .env")
print("2. Run: ./run_autoagenthire.sh")
print("3. Or run API server: cd backend && uvicorn main:app --reload")
print()
