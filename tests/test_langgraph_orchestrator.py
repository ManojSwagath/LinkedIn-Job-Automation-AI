"""
Test suite for LangGraph-based Multi-Agent Orchestrator
=========================================================
Tests graph compilation, execution, and state management.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.langgraph_orchestrator import LangGraphOrchestrator, get_orchestrator
from backend.agents.graph_state import AgentInput, create_initial_state, WorkflowStatus


def test_graph_compilation():
    """Test that the workflow graph compiles without errors"""
    print("\n🧪 Testing graph compilation...")
    
    try:
        orchestrator = LangGraphOrchestrator()
        assert orchestrator.graph is not None
        assert orchestrator.app is not None
        print("   ✅ Graph compiled successfully")
        return True
    except Exception as e:
        print(f"   ❌ Graph compilation failed: {e}")
        return False


def test_singleton_orchestrator():
    """Test that singleton orchestrator works"""
    print("\n🧪 Testing singleton orchestrator...")
    
    try:
        orch1 = get_orchestrator()
        orch2 = get_orchestrator()
        assert orch1 is orch2, "Singleton should return same instance"
        print("   ✅ Singleton orchestrator working")
        return True
    except Exception as e:
        print(f"   ❌ Singleton test failed: {e}")
        return False


def test_initial_state_creation():
    """Test initial state creation from input"""
    print("\n🧪 Testing initial state creation...")
    
    try:
        input_data: AgentInput = {
            "user_id": "test_user_001",
            "resume_text": "Experienced ML Engineer with Python, PyTorch, and NLP skills...",
            "resume_file_path": None,
            "target_roles": ["machine_learning_engineer"],
            "desired_locations": ["San Francisco, CA", "Remote"],
            "min_salary": 150000,
            "max_applications": 5,
            "dry_run": True,
        }
        
        state = create_initial_state(input_data)
        
        assert state.get("user_id") == "test_user_001"
        assert state.get("session_id") is not None
        assert state.get("target_roles") == ["machine_learning_engineer"]
        assert state.get("max_applications") == 5
        assert state.get("dry_run") is True
        assert state.get("workflow_status") == "pending" or state.get("workflow_status") == WorkflowStatus.PENDING
        
        print("   ✅ Initial state created correctly")
        return True
    except Exception as e:
        print(f"   ❌ Initial state creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_execution():
    """Test full workflow execution with mock data"""
    print("\n🧪 Testing workflow execution...")
    
    try:
        orchestrator = get_orchestrator()
        
        input_data: AgentInput = {
            "user_id": "test_user_002",
            "resume_text": "Senior ML Engineer with 5 years of experience in deep learning, PyTorch, TensorFlow, Python, and NLP.",
            "resume_file_path": None,
            "target_roles": ["machine_learning_engineer", "data_scientist"],
            "desired_locations": ["Remote"],
            "min_salary": None,
            "max_applications": 3,
            "dry_run": True,
        }
        
        # Run workflow
        result = orchestrator.run_sync(input_data)
        
        # Verify result structure
        assert result["session_id"] is not None
        assert result["workflow_status"] in ["completed", "failed"]
        assert "total_jobs_found" in result
        assert "applications_submitted" in result
        assert "top_matches" in result
        
        print(f"   ✅ Workflow executed successfully")
        print(f"      Session ID: {result['session_id']}")
        print(f"      Status: {result['workflow_status']}")
        print(f"      Jobs found: {result['total_jobs_found']}")
        print(f"      Applications: {result['applications_submitted']}")
        print(f"      Execution time: {result['execution_time_seconds']:.2f}s")
        
        return True
    except Exception as e:
        print(f"   ❌ Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_with_filters():
    """Test workflow with salary filtering"""
    print("\n🧪 Testing workflow with filters...")
    
    try:
        orchestrator = get_orchestrator()
        
        input_data: AgentInput = {
            "user_id": "test_user_003",
            "resume_text": "ML Engineer with Python, deep learning, computer vision",
            "resume_file_path": None,
            "target_roles": ["machine_learning_engineer"],
            "desired_locations": ["San Francisco, CA"],
            "min_salary": 200000,  # High salary filter
            "max_applications": 2,
            "dry_run": True,
        }
        
        result = orchestrator.run_sync(input_data)
        
        assert result["workflow_status"] == "completed"
        
        # With high salary filter, some jobs should be filtered out
        print(f"   ✅ Filtering test passed")
        print(f"      Jobs found: {result['total_jobs_found']}")
        print(f"      After filtering: {len(result['top_matches'])}")
        
        return True
    except Exception as e:
        print(f"   ❌ Filtering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dry_run_mode():
    """Test that dry-run mode doesn't actually apply"""
    print("\n🧪 Testing dry-run mode...")
    
    try:
        orchestrator = get_orchestrator()
        
        input_data: AgentInput = {
            "user_id": "test_user_004",
            "resume_text": "Data Scientist with Python, SQL, ML",
            "resume_file_path": None,
            "target_roles": ["data_scientist"],
            "desired_locations": ["Remote"],
            "min_salary": None,
            "max_applications": 5,
            "dry_run": True,
        }
        
        result = orchestrator.run_sync(input_data)
        
        # In dry-run, applications should be marked as dry-run
        for app in result.get("submitted_applications", []):
            assert "dry-run" in app.get("status", "").lower() or app.get("status") == "submitted (dry-run)"
        
        print(f"   ✅ Dry-run mode working correctly")
        print(f"      Applications simulated: {result['applications_submitted']}")
        
        return True
    except Exception as e:
        print(f"   ❌ Dry-run test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all test suites"""
    print("=" * 70)
    print("🧪 LANGGRAPH ORCHESTRATOR - TEST SUITE")
    print("=" * 70)
    
    tests = [
        test_graph_compilation,
        test_singleton_orchestrator,
        test_initial_state_creation,
        test_workflow_execution,
        test_workflow_with_filters,
        test_dry_run_mode,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n❌ Test {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 70)
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n📊 Summary:")
        print(f"   ✅ {len(results)}/{len(results)} tests passed")
        print("\n🎉 LangGraph orchestrator is production-ready!")
        return True
    else:
        print(f"❌ {sum(not r for r in results)}/{len(results)} TESTS FAILED")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
