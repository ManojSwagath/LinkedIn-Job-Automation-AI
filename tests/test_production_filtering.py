"""
Comprehensive Test Suite for Production Job Filtering System
============================================================
Tests the complete LinkedIn-aligned filtering pipeline
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from matching.job_filter_production import (
    hard_filter_job,
    detect_filled_job,
    validate_job_freshness,
    filter_job_complete,
    filter_jobs_batch,
    ROLE_TAXONOMY,
    FILLED_JOB_SIGNALS
)
from datetime import datetime, timedelta


# ============================================================================
# TEST DATA - Realistic Job Scenarios
# ============================================================================

# ✅ VALID AI Engineer Jobs (Should PASS)
VALID_AI_ENGINEER_JOBS = [
    {
        "title": "AI Engineer",
        "description": "We're looking for an AI Engineer with experience in machine learning and artificial intelligence. You'll work on deep learning models, natural language processing, and computer vision projects using PyTorch and TensorFlow.",
        "company": "Google",
        "location": "Mountain View, CA",
        "posted_date": datetime.now() - timedelta(days=5),
        "applicant_count": 50,
        "apply_button_present": True,
        "job_id": "1"
    },
    {
        "title": "Machine Learning Engineer - AI/ML Team",
        "description": "Join our artificial intelligence team to build LLM applications. Required: machine learning experience, artificial intelligence background, familiarity with GPT, BERT, and transformers.",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "posted_date": datetime.now() - timedelta(days=10),
        "applicant_count": 100,
        "apply_button_present": True,
        "job_id": "2"
    },
    {
        "title": "Artificial Intelligence Engineer",
        "description": "Build cutting-edge machine learning systems. Work on artificial intelligence projects including NLP, computer vision, and neural networks. PyTorch and deep learning experience required.",
        "company": "Meta",
        "location": "Menlo Park, CA",
        "posted_date": datetime.now() - timedelta(days=3),
        "applicant_count": 75,
        "apply_button_present": True,
        "job_id": "3"
    }
]

# ❌ INVALID Jobs (Should be REJECTED - These are the problematic ones from screenshot)
INVALID_JOBS_FOR_AI_ENGINEER = [
    {
        "title": "MCAL Developer",
        "description": "MCAL (Microcontroller Abstraction Layer) developer for automotive embedded systems. Work on AUTOSAR classic stack, embedded C programming, hardware abstraction layers.",
        "company": "Bosch",
        "location": "Stuttgart, Germany",
        "posted_date": datetime.now() - timedelta(days=2),
        "applicant_count": 30,
        "apply_button_present": True,
        "job_id": "bad1"
    },
    {
        "title": "Documentum Developer",
        "description": "Documentum platform developer for enterprise content management. ECM experience, Documentum platform administration, DQL queries, content services.",
        "company": "Dell",
        "location": "Austin, TX",
        "posted_date": datetime.now() - timedelta(days=5),
        "applicant_count": 20,
        "apply_button_present": True,
        "job_id": "bad2"
    },
    {
        "title": "Application Developer L4",
        "description": "Senior application developer for enterprise applications. Java, Spring Boot, SQL Server, REST APIs. No machine learning required.",
        "company": "Infosys",
        "location": "Bangalore, India",
        "posted_date": datetime.now() - timedelta(days=7),
        "applicant_count": 150,
        "apply_button_present": True,
        "job_id": "bad3"
    },
    {
        "title": "Embedded Systems Engineer",
        "description": "Embedded systems development for automotive industry. C/C++, firmware development, hardware debugging, JTAG, oscilloscope experience.",
        "company": "Continental",
        "location": "Munich, Germany",
        "posted_date": datetime.now() - timedelta(days=4),
        "applicant_count": 40,
        "apply_button_present": True,
        "job_id": "bad4"
    },
    {
        "title": "Software Developer - AutoCAD Team",
        "description": "AutoCAD plugin development. C++, CAD software, 3D graphics, mechanical engineering background preferred.",
        "company": "Autodesk",
        "location": "San Rafael, CA",
        "posted_date": datetime.now() - timedelta(days=6),
        "applicant_count": 60,
        "apply_button_present": True,
        "job_id": "bad5"
    },
    {
        "title": "AI/ML Intern",
        "description": "Internship position for students interested in machine learning and artificial intelligence. Deep learning, computer vision, NLP projects.",
        "company": "Microsoft",
        "location": "Redmond, WA",
        "posted_date": datetime.now() - timedelta(days=2),
        "applicant_count": 300,
        "apply_button_present": True,
        "job_id": "bad6"
    }
]

# ❌ FILLED Jobs (Should be REJECTED)
FILLED_JOBS = [
    {
        "title": "AI Engineer",
        "description": "Machine learning and artificial intelligence position. Note: This position has been filled.",
        "company": "Amazon",
        "location": "Seattle, WA",
        "posted_date": datetime.now() - timedelta(days=10),
        "applicant_count": 600,
        "apply_button_present": True,
        "job_id": "filled1"
    },
    {
        "title": "Machine Learning Engineer",
        "description": "We are no longer accepting applications for this artificial intelligence role.",
        "company": "Apple",
        "location": "Cupertino, CA",
        "posted_date": datetime.now() - timedelta(days=15),
        "applicant_count": 550,
        "apply_button_present": False,
        "job_id": "filled2"
    },
    {
        "title": "AI Engineer",
        "description": "Great machine learning opportunity. Artificial intelligence experience required.",
        "company": "Netflix",
        "location": "Los Gatos, CA",
        "posted_date": datetime.now() - timedelta(days=5),
        "applicant_count": 700,  # High count indicates filled
        "apply_button_present": True,
        "job_id": "filled3"
    }
]

# ❌ STALE Jobs (Should be REJECTED)
STALE_JOBS = [
    {
        "title": "AI Engineer",
        "description": "Machine learning and artificial intelligence role with great benefits.",
        "company": "Tesla",
        "location": "Palo Alto, CA",
        "posted_date": datetime.now() - timedelta(days=45),  # Too old
        "applicant_count": 100,
        "apply_button_present": True,
        "job_id": "stale1"
    }
]


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_hard_filter_valid_jobs():
    """Test that valid AI Engineer jobs pass hard filters"""
    print("\n" + "="*80)
    print("TEST 1: Valid AI Engineer Jobs (Should PASS)")
    print("="*80)
    
    passed = 0
    for job in VALID_AI_ENGINEER_JOBS:
        result, reason = hard_filter_job(job, "ai_engineer")
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {job['title']}")
        if result:
            passed += 1
        else:
            print(f"   Rejection reason: {reason}")
    
    print(f"\n📊 Result: {passed}/{len(VALID_AI_ENGINEER_JOBS)} valid jobs passed")
    assert passed == len(VALID_AI_ENGINEER_JOBS), f"Expected all valid jobs to pass, but only {passed} passed"
    print("✅ TEST PASSED\n")


def test_hard_filter_invalid_jobs():
    """Test that invalid jobs (MCAL, Documentum, etc.) are rejected"""
    print("\n" + "="*80)
    print("TEST 2: Invalid Jobs for AI Engineer (Should FAIL)")
    print("="*80)
    
    rejected = 0
    for job in INVALID_JOBS_FOR_AI_ENGINEER:
        result, reason = hard_filter_job(job, "ai_engineer")
        status = "❌ REJECT" if not result else "✅ PASS (ERROR!)"
        print(f"{status}: {job['title']}")
        print(f"   Reason: {reason}")
        if not result:
            rejected += 1
    
    print(f"\n📊 Result: {rejected}/{len(INVALID_JOBS_FOR_AI_ENGINEER)} invalid jobs rejected")
    assert rejected == len(INVALID_JOBS_FOR_AI_ENGINEER), f"Expected all invalid jobs to be rejected, but only {rejected} were rejected"
    print("✅ TEST PASSED\n")


def test_filled_job_detection():
    """Test detection of filled jobs"""
    print("\n" + "="*80)
    print("TEST 3: Filled Job Detection (Should Detect as FILLED)")
    print("="*80)
    
    detected = 0
    for job in FILLED_JOBS:
        is_filled, reason = detect_filled_job(job)
        status = "✅ DETECTED" if is_filled else "❌ MISSED"
        print(f"{status}: {job['title']}")
        print(f"   Reason: {reason}")
        if is_filled:
            detected += 1
    
    print(f"\n📊 Result: {detected}/{len(FILLED_JOBS)} filled jobs detected")
    assert detected == len(FILLED_JOBS), f"Expected all filled jobs to be detected, but only {detected} were detected"
    print("✅ TEST PASSED\n")


def test_freshness_validation():
    """Test freshness validation"""
    print("\n" + "="*80)
    print("TEST 4: Freshness Validation (Stale jobs should FAIL)")
    print("="*80)
    
    rejected = 0
    for job in STALE_JOBS:
        is_fresh, reason = validate_job_freshness(job, max_days=30)
        status = "❌ REJECT" if not is_fresh else "✅ PASS (ERROR!)"
        print(f"{status}: {job['title']}")
        print(f"   Reason: {reason}")
        if not is_fresh:
            rejected += 1
    
    print(f"\n📊 Result: {rejected}/{len(STALE_JOBS)} stale jobs rejected")
    assert rejected == len(STALE_JOBS), f"Expected all stale jobs to be rejected, but only {rejected} were rejected"
    print("✅ TEST PASSED\n")


def test_complete_pipeline():
    """Test complete filtering pipeline"""
    print("\n" + "="*80)
    print("TEST 5: Complete Pipeline (ALL filters)")
    print("="*80)
    
    all_jobs = (
        VALID_AI_ENGINEER_JOBS +
        INVALID_JOBS_FOR_AI_ENGINEER +
        FILLED_JOBS +
        STALE_JOBS
    )
    
    print(f"📥 Input: {len(all_jobs)} total jobs")
    print(f"   - {len(VALID_AI_ENGINEER_JOBS)} valid AI Engineer jobs")
    print(f"   - {len(INVALID_JOBS_FOR_AI_ENGINEER)} invalid role jobs")
    print(f"   - {len(FILLED_JOBS)} filled jobs")
    print(f"   - {len(STALE_JOBS)} stale jobs")
    
    filtered_jobs = filter_jobs_batch(
        jobs=all_jobs,
        role_key="ai_engineer",
        skip_freshness=False
    )
    
    print(f"\n📤 Output: {len(filtered_jobs)} jobs passed all filters")
    print("\nJobs that passed:")
    for job in filtered_jobs:
        print(f"   ✅ {job['title']} - {job['company']}")
    
    # Should only have the valid AI Engineer jobs
    expected_pass = len(VALID_AI_ENGINEER_JOBS)
    assert len(filtered_jobs) == expected_pass, f"Expected {expected_pass} jobs to pass, but {len(filtered_jobs)} passed"
    print(f"\n✅ TEST PASSED: Only valid AI Engineer jobs passed!\n")


def test_role_taxonomy_coverage():
    """Test that all roles have proper taxonomy"""
    print("\n" + "="*80)
    print("TEST 6: Role Taxonomy Coverage")
    print("="*80)
    
    for role_key, config in ROLE_TAXONOMY.items():
        print(f"\n📋 Role: {role_key}")
        print(f"   Must-have titles: {len(config['must_have_titles'])} defined")
        print(f"   Must-have skills: {len(config['must_have_skills'])} defined")
        print(f"   Optional skills: {len(config['optional_skills'])} defined")
        print(f"   Exclude titles: {len(config['exclude_titles'])} defined")
        
        # Validate each role has minimum required fields
        assert len(config['must_have_titles']) > 0, f"{role_key}: No must_have_titles defined"
        assert len(config['must_have_skills']) > 0, f"{role_key}: No must_have_skills defined"
        assert len(config['optional_skills']) >= 2, f"{role_key}: Need at least 2 optional_skills"
        assert len(config['exclude_titles']) > 0, f"{role_key}: No exclude_titles defined"
    
    print(f"\n✅ TEST PASSED: All {len(ROLE_TAXONOMY)} roles have proper taxonomy!\n")


def test_exact_screenshot_scenarios():
    """
    Test the EXACT scenarios from the user's screenshot
    These are the jobs that were wrongly recommended for AI Engineer
    """
    print("\n" + "="*80)
    print("TEST 7: EXACT SCREENSHOT SCENARIOS (Critical Test!)")
    print("="*80)
    print("These are the exact jobs from the user's LinkedIn screenshot")
    print("that should NOT appear for AI Engineer role:\n")
    
    # Jobs from the user's screenshot
    screenshot_jobs = [
        {
            "title": "MCAL Developer",
            "description": "MCAL automotive embedded systems development",
            "company": "Robert Bosch",
            "location": "Bangalore",
            "posted_date": datetime.now() - timedelta(days=2),
            "applicant_count": 50,
            "apply_button_present": True,
            "job_id": "screenshot1"
        },
        {
            "title": "Documentum Developer",
            "description": "Documentum ECM platform development",
            "company": "Tech Company",
            "location": "India",
            "posted_date": datetime.now() - timedelta(days=3),
            "applicant_count": 30,
            "apply_button_present": True,
            "job_id": "screenshot2"
        },
        {
            "title": "Application Developer",
            "description": "Enterprise application development with Java",
            "company": "IT Services",
            "location": "Bangalore",
            "posted_date": datetime.now() - timedelta(days=1),
            "applicant_count": 100,
            "apply_button_present": True,
            "job_id": "screenshot3"
        },
        {
            "title": "Developer L4",
            "description": "Senior developer position for enterprise software",
            "company": "Accenture",
            "location": "Multiple Locations",
            "posted_date": datetime.now() - timedelta(days=4),
            "applicant_count": 200,
            "apply_button_present": True,
            "job_id": "screenshot4"
        }
    ]
    
    rejected = 0
    for job in screenshot_jobs:
        result, reason = hard_filter_job(job, "ai_engineer")
        status = "✅ REJECTED" if not result else "❌ PASSED (BUG!)"
        print(f"{status}: {job['title']}")
        if not result:
            print(f"   ✓ Correctly rejected: {reason}")
            rejected += 1
        else:
            print(f"   ✗ ERROR: This job should have been rejected!")
    
    print(f"\n📊 Result: {rejected}/{len(screenshot_jobs)} problematic jobs correctly rejected")
    assert rejected == len(screenshot_jobs), "CRITICAL: Some screenshot jobs were not rejected!"
    print("\n🎉 CRITICAL TEST PASSED: All problematic jobs from screenshot are now rejected!\n")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run complete test suite"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "PRODUCTION FILTER TEST SUITE" + " "*25 + "║")
    print("╚" + "="*78 + "╝")
    
    tests = [
        ("Valid AI Engineer Jobs", test_hard_filter_valid_jobs),
        ("Invalid Jobs Rejection", test_hard_filter_invalid_jobs),
        ("Filled Job Detection", test_filled_job_detection),
        ("Freshness Validation", test_freshness_validation),
        ("Complete Pipeline", test_complete_pipeline),
        ("Role Taxonomy Coverage", test_role_taxonomy_coverage),
        ("Screenshot Scenarios", test_exact_screenshot_scenarios),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ TEST FAILED: {test_name}")
            print(f"   Error: {str(e)}\n")
            failed += 1
        except Exception as e:
            print(f"❌ TEST ERROR: {test_name}")
            print(f"   Exception: {str(e)}\n")
            failed += 1
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"✅ Passed: {passed}/{len(tests)} tests")
    print(f"❌ Failed: {failed}/{len(tests)} tests")
    
    if failed == 0:
        print("\n🎉🎉🎉 ALL TESTS PASSED! Production filtering system is ready! 🎉🎉🎉")
        print("\nThe system will now:")
        print("   ✓ Reject MCAL Developer jobs")
        print("   ✓ Reject Documentum Developer jobs")
        print("   ✓ Reject Application Developer L4 jobs")
        print("   ✓ Reject Embedded Systems jobs")
        print("   ✓ Reject AutoCAD/PLM/ERP jobs")
        print("   ✓ Reject Intern positions")
        print("   ✓ Reject filled jobs")
        print("   ✓ Reject stale jobs")
        print("   ✓ Only show REAL AI Engineer positions")
        return True
    else:
        print("\n⚠️  Some tests failed. Please fix issues before deploying.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
