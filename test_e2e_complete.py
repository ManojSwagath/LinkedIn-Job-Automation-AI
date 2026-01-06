"""
Complete End-to-End Test for AutoAgentHire
==========================================
Tests the entire workflow from resume upload to job application.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.agents.multi_agent_orchestrator import MultiAgentOrchestrator
from backend.agents.browser_adapter import create_browser_automation
from backend.rag.resume_intelligence import ResumeIntelligence
from backend.database.connection import init_db, get_db_session
from backend.database import crud
from backend.config import settings
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("E2ETest")


async def test_complete_workflow():
    """Test complete autonomous workflow"""
    
    print("\n" + "="*70)
    print(" "*15 + "🤖 AUTOAGENTHIRE E2E TEST 🤖")
    print("="*70 + "\n")
    
    # ===========================
    # STEP 1: Database Setup
    # ===========================
    
    print("📦 Step 1: Initialize Database...")
    init_db()
    print("✓ Database ready\n")
    
    # ===========================
    # STEP 2: Test Data
    # ===========================
    
    print("📝 Step 2: Prepare Test Data...")
    
    # Check for test resume
    test_resume_path = "data/resumes/sample_resume.pdf"
    if not Path(test_resume_path).exists():
        print(f"⚠️  Test resume not found: {test_resume_path}")
        print("   Creating a test text resume...")
        
        Path("data/resumes").mkdir(parents=True, exist_ok=True)
        test_resume_path = "data/resumes/test_resume.txt"
        
        with open(test_resume_path, 'w') as f:
            f.write("""
John Doe
Email: john.doe@example.com
Phone: (555) 123-4567

SUMMARY
Senior Machine Learning Engineer with 5+ years of experience in developing and deploying ML models.

SKILLS
- Python, TensorFlow, PyTorch, Scikit-learn
- NLP, Computer Vision, Deep Learning
- AWS, Docker, Kubernetes
- Data Analysis, SQL, Pandas

EXPERIENCE
Senior ML Engineer | TechCorp | 2021-Present
- Developed recommendation systems serving 1M+ users
- Improved model accuracy by 25%
- Led team of 3 engineers

ML Engineer | DataCo | 2019-2021
- Built NLP pipelines for text analysis
- Deployed models to production

EDUCATION
M.S. Computer Science | Stanford University | 2019
B.S. Computer Science | MIT | 2017
            """)
        
        print(f"✓ Created test resume: {test_resume_path}\n")
    
    # Test configuration
    test_config = {
        'user_id': 'test_user_e2e',
        'resume_file': test_resume_path,
        'keywords': 'Machine Learning Engineer',
        'location': 'San Francisco, CA',
        'max_jobs': 5,  # Small number for testing
        'linkedin_email': os.getenv('LINKEDIN_EMAIL'),
        'linkedin_password': os.getenv('LINKEDIN_PASSWORD')
    }
    
    # Validate credentials
    if not test_config['linkedin_email'] or not test_config['linkedin_password']:
        print("❌ ERROR: LinkedIn credentials not found in environment")
        print("   Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env")
        return
    
    print("✓ Test configuration ready\n")
    
    # ===========================
    # STEP 3: Initialize Components
    # ===========================
    
    print("🔧 Step 3: Initialize Components...")
    
    try:
        # Resume Intelligence
        resume_intelligence = ResumeIntelligence(
            openai_api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        )
        print("   ✓ Resume Intelligence")
        
        # Browser Automation
        browser_automation = create_browser_automation({
            'linkedin_email': test_config['linkedin_email'],
            'linkedin_password': test_config['linkedin_password'],
            'auto_apply': True,
            'max_results': test_config['max_jobs']
        })
        print("   ✓ Browser Automation")
        
        # Orchestrator
        orchestrator = MultiAgentOrchestrator(
            resume_intelligence=resume_intelligence,
            browser_automation=browser_automation,
            similarity_threshold=0.75
        )
        print("   ✓ Multi-Agent Orchestrator\n")
        
    except Exception as e:
        print(f"❌ Component initialization failed: {e}")
        return
    
    # ===========================
    # STEP 4: Run Workflow
    # ===========================
    
    print("🚀 Step 4: Execute Autonomous Workflow...")
    print(f"   Resume: {test_config['resume_file']}")
    print(f"   Keywords: {test_config['keywords']}")
    print(f"   Location: {test_config['location']}")
    print(f"   Max Jobs: {test_config['max_jobs']}")
    print("\n" + "─"*70 + "\n")
    
    try:
        report = await orchestrator.run(
            user_id=test_config['user_id'],
            resume_file_path=test_config['resume_file'],
            keywords=test_config['keywords'],
            location=test_config['location'],
            max_jobs=test_config['max_jobs']
        )
        
        print("\n" + "─"*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ===========================
    # STEP 5: Verify Results
    # ===========================
    
    print("✅ Step 5: Verify Results...")
    
    if not report:
        print("❌ No report generated")
        return
    
    summary = report.get('summary', {})
    
    print(f"\n📊 Workflow Results:")
    print(f"   Jobs Found: {summary.get('total_jobs_found', 0)}")
    print(f"   Jobs Matched: {summary.get('total_jobs_matched', 0)}")
    print(f"   Applications Attempted: {summary.get('applications_attempted', 0)}")
    print(f"   Applications Successful: {summary.get('applications_successful', 0)}")
    print(f"   Success Rate: {summary.get('success_rate', '0%')}")
    
    # ===========================
    # STEP 6: Database Verification
    # ===========================
    
    print("\n💾 Step 6: Verify Database Persistence...")
    
    with get_db_session() as db:
        # Check user
        user = crud.get_user_by_email(db, test_config['user_id'])
        if user:
            print(f"   ✓ User record: {user.email}")
        else:
            print(f"   ⚠️  User not found in database")
        
        # Check applications
        if user:
            apps = crud.get_user_applications(db, user.id, limit=10)
            print(f"   ✓ Applications saved: {len(apps)}")
            
            if apps:
                print("\n   Recent Applications:")
                for app in apps[:3]:
                    print(f"     • {app.job.title} at {app.job.company}")
                    print(f"       Match: {app.match_score:.1f}% | Status: {app.status}")
        
        # Check stats
        if user:
            stats = crud.get_user_stats(db, user.id)
            print(f"\n   📈 User Stats:")
            print(f"      Total Applications: {stats['total_applications']}")
            print(f"      Successful: {stats['successful_applications']}")
            print(f"      Success Rate: {stats['success_rate']:.1f}%")
    
    # ===========================
    # FINAL RESULT
    # ===========================
    
    print("\n" + "="*70)
    print(" "*20 + "✅ E2E TEST COMPLETE ✅")
    print("="*70 + "\n")
    
    return report


async def test_individual_components():
    """Test each component individually"""
    
    print("\n🧪 Testing Individual Components...\n")
    
    # Test 1: Resume Intelligence
    print("Test 1: Resume Intelligence")
    try:
        resume_intel = ResumeIntelligence()
        
        # Create test resume if needed
        test_file = "data/resumes/test_resume.txt"
        if not Path(test_file).exists():
            Path("data/resumes").mkdir(parents=True, exist_ok=True)
            with open(test_file, 'w') as f:
                f.write("John Doe\nSoftware Engineer with Python experience\nSkills: Python, Django, SQL")
        
        resume_data = resume_intel.parse_resume_file(test_file)
        print(f"   ✓ Resume parsed: {resume_data.name}")
        print(f"   ✓ Skills found: {len(resume_data.skills)}")
        print(f"   ✓ Embedding: {len(resume_data.embedding) if resume_data.embedding is not None else 0}D")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()
    
    # Test 2: Database Operations
    print("Test 2: Database Operations")
    try:
        init_db()
        
        with get_db_session() as db:
            # Create test user
            test_email = f"test_{int(asyncio.get_event_loop().time())}@example.com"
            user = crud.create_user(db, email=test_email, username="testuser")
            print(f"   ✓ User created: {user.email}")
            
            # Create test resume
            resume_data = {
                'filename': 'test.pdf',
                'file_path': '/tmp/test.pdf',
                'name': 'Test User',
                'skills': ['Python', 'ML']
            }
            resume = crud.create_resume(db, user.id, resume_data)
            print(f"   ✓ Resume created: ID {resume.id}")
            
            # Get stats
            stats = crud.get_user_stats(db, user.id)
            print(f"   ✓ Stats retrieved: {stats}")
            
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()
    
    print("✅ Component tests complete\n")


async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AutoAgentHire E2E Test")
    parser.add_argument(
        '--mode',
        choices=['full', 'components'],
        default='full',
        help='Test mode: full (complete workflow) or components (individual tests)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'full':
        await test_complete_workflow()
    elif args.mode == 'components':
        await test_individual_components()


if __name__ == "__main__":
    asyncio.run(main())
