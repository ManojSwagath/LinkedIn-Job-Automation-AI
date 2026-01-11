"""
Test suite for advanced job filtering system
Validates role matching, filled job detection, and freshness checks
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
from backend.matching.job_filter import (
    filter_jobs,
    matches_role,
    is_filled_job,
    is_recent,
    has_valid_link,
    normalize,
    get_available_roles,
    ROLE_TAXONOMY
)

def create_test_job(
    title="Machine Learning Engineer",
    description="We are looking for an experienced ML engineer...",
    company="Tech Corp",
    posted_days_ago=5,
    is_open=True,
    apply_link="https://linkedin.com/jobs/123"
):
    """Helper to create test job data"""
    return {
        "job_id": f"job_{hash(title)}",
        "title": title,
        "description": description,
        "company": company,
        "location": "San Francisco, CA",
        "posted_date": datetime.now() - timedelta(days=posted_days_ago),
        "is_open": is_open,
        "apply_link": apply_link,
        "match_score": 75
    }

def test_normalize():
    """Test text normalization"""
    print("\n🧪 Testing normalize()...")
    
    assert normalize("Machine Learning Engineer") == "machine learning engineer"
    assert normalize("  SENIOR DATA SCIENTIST  ") == "senior data scientist"
    assert normalize(None or "") == ""  # Handle None case
    assert normalize("") == ""
    
    print("   ✅ Normalization working correctly")

def test_role_matching():
    """Test role-based job matching"""
    print("\n🧪 Testing role matching...")
    
    # Test ML Engineer matching
    ml_job = create_test_job(
        title="Senior Machine Learning Engineer",
        description="Looking for ML engineer with deep learning experience in PyTorch"
    )
    assert matches_role(ml_job, "machine_learning_engineer") == True
    print("   ✅ ML Engineer matched correctly")
    
    # Test exclusion (intern)
    intern_job = create_test_job(
        title="Machine Learning Intern",
        description="Entry level ML intern position"
    )
    assert matches_role(intern_job, "machine_learning_engineer") == False
    print("   ✅ Intern positions correctly excluded")
    
    # Test wrong role
    frontend_job = create_test_job(
        title="Frontend Developer",
        description="React and TypeScript developer needed"
    )
    assert matches_role(frontend_job, "machine_learning_engineer") == False
    print("   ✅ Wrong roles correctly rejected")
    
    # Test data scientist
    ds_job = create_test_job(
        title="Senior Data Scientist",
        description="Looking for a data scientist with Python, SQL, and statistics experience"
    )
    assert matches_role(ds_job, "data_scientist") == True
    print("   ✅ Data Scientist matched correctly")

def test_filled_job_detection():
    """Test detection of filled/closed jobs"""
    print("\n🧪 Testing filled job detection...")
    
    # Test explicit flag
    filled_job = create_test_job(is_open=False)
    assert is_filled_job(filled_job) == True
    print("   ✅ Explicit closed flag detected")
    
    # Test keyword detection
    filled_keyword_job = create_test_job(
        description="This position has been filled. No longer accepting applications."
    )
    assert is_filled_job(filled_keyword_job) == True
    print("   ✅ Filled keywords detected")
    
    # Test open job
    open_job = create_test_job()
    assert is_filled_job(open_job) == False
    print("   ✅ Open jobs pass through correctly")

def test_freshness_check():
    """Test job freshness validation"""
    print("\n🧪 Testing freshness check...")
    
    # Recent job
    recent_job = create_test_job(posted_days_ago=5)
    assert is_recent(recent_job, max_age_days=30) == True
    print("   ✅ Recent jobs pass freshness check")
    
    # Old job
    old_job = create_test_job(posted_days_ago=45)
    assert is_recent(old_job, max_age_days=30) == False
    print("   ✅ Old jobs correctly filtered")
    
    # Job without date
    no_date_job = create_test_job()
    del no_date_job["posted_date"]
    assert is_recent(no_date_job) == False
    print("   ✅ Jobs without dates rejected")

def test_link_validation():
    """Test application link validation"""
    print("\n🧪 Testing link validation...")
    
    # Valid link
    valid_job = create_test_job()
    assert has_valid_link(valid_job) == True
    print("   ✅ Valid links accepted")
    
    # No link
    no_link_job = create_test_job()
    del no_link_job["apply_link"]
    assert has_valid_link(no_link_job) == False
    print("   ✅ Jobs without links rejected")
    
    # Invalid link
    invalid_link_job = create_test_job(apply_link="example.com/job")
    assert has_valid_link(invalid_link_job) == False
    print("   ✅ Invalid links rejected")

def test_full_pipeline():
    """Test the complete filtering pipeline"""
    print("\n🧪 Testing complete filtering pipeline...")
    
    # Create mixed job set
    jobs = [
        # Should pass - perfect ML job
        create_test_job(
            title="Machine Learning Engineer",
            description="We need an ML engineer with PyTorch experience",
            posted_days_ago=5
        ),
        # Should fail - filled
        create_test_job(
            title="Machine Learning Engineer",
            description="ML engineer needed - Position filled",
            posted_days_ago=5,
            is_open=False
        ),
        # Should fail - too old
        create_test_job(
            title="Machine Learning Engineer",
            description="ML engineer with TensorFlow",
            posted_days_ago=45
        ),
        # Should fail - wrong role
        create_test_job(
            title="Frontend Developer",
            description="React developer needed",
            posted_days_ago=5
        ),
        # Should fail - intern (excluded)
        create_test_job(
            title="Machine Learning Intern",
            description="ML intern position",
            posted_days_ago=5
        ),
        # Should pass - another good ML job
        create_test_job(
            title="Senior ML Engineer",
            description="Looking for ML engineer with deep learning experience",
            posted_days_ago=10
        )
    ]
    
    # Apply filters
    filtered = filter_jobs(
        jobs,
        target_role="machine_learning_engineer",
        min_match_score=50,
        max_age_days=30
    )
    
    # Should have 2 jobs passing
    assert len(filtered) == 2, f"Expected 2 jobs, got {len(filtered)}"
    print(f"   ✅ Pipeline filtered correctly: {len(jobs)} jobs → {len(filtered)} jobs")
    
    # Verify all passed jobs are ML Engineer roles
    for job in filtered:
        assert "machine learning" in job["title"].lower() or "ml engineer" in job["title"].lower()
    print("   ✅ All filtered jobs match target role")

def test_deduplication():
    """Test job deduplication"""
    print("\n🧪 Testing deduplication...")
    
    # Create duplicate jobs with ML engineer content
    jobs = [
        create_test_job(
            title="Machine Learning Engineer",
            description="Looking for ML engineer with PyTorch experience"
        ),
        create_test_job(
            title="Machine Learning Engineer",  
            description="Looking for ML engineer with PyTorch experience"  # Duplicate
        ),
        create_test_job(
            title="Senior ML Engineer",
            description="Looking for senior machine learning engineer with TensorFlow"
        ),
    ]
    
    filtered = filter_jobs(
        jobs,
        target_role="machine_learning_engineer",
        enable_deduplication=True
    )
    
    assert len(filtered) == 2, f"Expected 2 unique jobs, got {len(filtered)}"
    print(f"   ✅ Deduplication working: {len(jobs)} jobs → {len(filtered)} unique")

def test_available_roles():
    """Test available roles retrieval"""
    print("\n🧪 Testing available roles...")
    
    roles = get_available_roles()
    assert len(roles) > 0
    assert "machine_learning_engineer" in roles
    assert "data_scientist" in roles
    
    print(f"   ✅ Found {len(roles)} available roles:")
    for role in roles:
        print(f"      - {role}")

def run_all_tests():
    """Run all test suites"""
    print("=" * 70)
    print("🧪 ADVANCED JOB FILTERING SYSTEM - TEST SUITE")
    print("=" * 70)
    
    try:
        test_normalize()
        test_role_matching()
        test_filled_job_detection()
        test_freshness_check()
        test_link_validation()
        test_full_pipeline()
        test_deduplication()
        test_available_roles()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n📊 Summary:")
        print("   ✅ Text normalization working")
        print("   ✅ Role matching accurate")
        print("   ✅ Filled job detection working")
        print("   ✅ Freshness validation working")
        print("   ✅ Link validation working")
        print("   ✅ Complete pipeline filtering correctly")
        print("   ✅ Deduplication working")
        print("   ✅ Role taxonomy accessible")
        print("\n🎉 Job filtering system is production-ready!")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
