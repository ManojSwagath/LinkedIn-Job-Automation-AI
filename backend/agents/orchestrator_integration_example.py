"""
Integration Example: Complete AutoAgentHire Workflow
====================================================
Demonstrates how to use the Multi-Agent Orchestrator with existing components.

This script shows:
1. How to initialize all components
2. How to run the autonomous workflow
3. How to check status during execution
4. How to handle results

Usage:
    python backend/agents/orchestrator_integration_example.py
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.agents.multi_agent_orchestrator import MultiAgentOrchestrator
from backend.rag.resume_intelligence import ResumeIntelligence
from backend.agents.autoagenthire_bot import AutoAgentHireBot
from backend.config import settings


async def run_autonomous_workflow():
    """
    Complete autonomous workflow example.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('backend/logs/orchestrator.log')
        ]
    )
    
    logger = logging.getLogger("Example")
    
    logger.info("=" * 70)
    logger.info("AUTO AGENT HIRE - INTEGRATION EXAMPLE")
    logger.info("=" * 70)
    
    # ===========================
    # STEP 1: Initialize Components
    # ===========================
    
    logger.info("\n📦 Step 1: Initializing components...")
    
    # Initialize Resume Intelligence (RAG + Embeddings)
    logger.info("   ✓ Resume Intelligence Module")
    resume_intelligence = ResumeIntelligence(
        openai_api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize Browser Automation
    logger.info("   ✓ Browser Automation (AutoAgentHireBot)")
    bot_config = {
        "linkedin_email": settings.LINKEDIN_EMAIL or os.getenv("LINKEDIN_EMAIL"),
        "linkedin_password": settings.LINKEDIN_PASSWORD or os.getenv("LINKEDIN_PASSWORD"),
        "auto_apply": True,
        "max_results": 50,
        "similarity_threshold": 0.75
    }
    browser_automation = AutoAgentHireBot(config=bot_config)
    
    # ===========================
    # STEP 2: Create Orchestrator
    # ===========================
    
    logger.info("\n🤖 Step 2: Creating Multi-Agent Orchestrator...")
    orchestrator = MultiAgentOrchestrator(
        resume_intelligence=resume_intelligence,
        browser_automation=browser_automation,
        similarity_threshold=0.75  # 75% minimum match score for application
    )
    logger.info("   ✓ Orchestrator initialized with 5 agents")
    
    # ===========================
    # STEP 3: Configure Workflow
    # ===========================
    
    logger.info("\n⚙️  Step 3: Configuring workflow parameters...")
    
    # Workflow parameters
    user_id = "test_user_001"
    resume_file = "data/resumes/sample_resume.pdf"  # Change to your resume
    keywords = "Machine Learning Engineer"
    location = "San Francisco, CA"
    max_jobs = 30
    
    logger.info(f"   User ID: {user_id}")
    logger.info(f"   Resume: {resume_file}")
    logger.info(f"   Keywords: {keywords}")
    logger.info(f"   Location: {location}")
    logger.info(f"   Max Jobs: {max_jobs}")
    
    # Check if resume exists
    if not Path(resume_file).exists():
        logger.error(f"\n❌ Resume file not found: {resume_file}")
        logger.error("   Please update the 'resume_file' variable with a valid path")
        return
    
    # ===========================
    # STEP 4: Run Workflow
    # ===========================
    
    logger.info("\n🚀 Step 4: Starting autonomous workflow...")
    logger.info("   This will:")
    logger.info("   1. Parse your resume with AI")
    logger.info("   2. Search LinkedIn for matching jobs")
    logger.info("   3. Score jobs using semantic similarity")
    logger.info("   4. Auto-apply to top matches")
    logger.info("   5. Generate comprehensive report")
    logger.info("")
    
    try:
        # Run the workflow
        report = await orchestrator.run(
            user_id=user_id,
            resume_file_path=resume_file,
            keywords=keywords,
            location=location,
            max_jobs=max_jobs
        )
        
        # ===========================
        # STEP 5: Process Results
        # ===========================
        
        logger.info("\n✅ Workflow completed successfully!")
        
        # Access results
        summary = report['summary']
        applications = report['applications']
        
        logger.info("\n📊 Final Results:")
        logger.info(f"   Jobs Found: {summary['total_jobs_found']}")
        logger.info(f"   Jobs Matched: {summary['total_jobs_matched']}")
        logger.info(f"   Applications Sent: {summary['applications_successful']}")
        logger.info(f"   Success Rate: {summary['success_rate']}")
        
        # Save report to file
        import json
        report_file = f"reports/orchestrator_report_{report['run_id']}.json"
        Path("reports").mkdir(exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, indent=2, fp=f)
        
        logger.info(f"\n💾 Report saved: {report_file}")
        
        return report
        
    except Exception as e:
        logger.error(f"\n❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Get status to see where it failed
        status = orchestrator.get_status()
        logger.error(f"\nFailed at phase: {status.get('current_phase')}")
        
        return None


async def run_with_status_monitoring():
    """
    Example with real-time status monitoring.
    This shows how to poll status during execution (useful for frontend).
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("StatusMonitor")
    
    # Initialize components
    resume_intelligence = ResumeIntelligence()
    browser = AutoAgentHireBot(config={
        "linkedin_email": os.getenv("LINKEDIN_EMAIL"),
        "linkedin_password": os.getenv("LINKEDIN_PASSWORD")
    })
    
    orchestrator = MultiAgentOrchestrator(
        resume_intelligence=resume_intelligence,
        browser_automation=browser
    )
    
    # Run workflow in background
    workflow_task = asyncio.create_task(
        orchestrator.run(
            user_id="test",
            resume_file_path="data/resumes/sample_resume.pdf",
            keywords="Software Engineer",
            location="Remote"
        )
    )
    
    # Monitor status while running
    logger.info("Monitoring workflow status...")
    
    while not workflow_task.done():
        status = orchestrator.get_status()
        
        logger.info(f"\nCurrent Status:")
        logger.info(f"  Phase: {status.get('current_phase')}")
        logger.info(f"  Jobs Found: {status['metrics']['jobs_found']}")
        logger.info(f"  Jobs Matched: {status['metrics']['jobs_matched']}")
        logger.info(f"  Jobs Applied: {status['metrics']['jobs_applied']}")
        
        # Show agent statuses
        for agent_name, agent_status in status['agents'].items():
            logger.info(f"  {agent_name}: {agent_status['status']}")
        
        await asyncio.sleep(5)  # Poll every 5 seconds
    
    # Get final result
    try:
        report = await workflow_task
        logger.info("\n✅ Workflow completed!")
        return report
    except Exception as e:
        logger.error(f"\n❌ Workflow failed: {e}")
        return None


async def test_individual_agents():
    """
    Test individual agents separately (useful for debugging).
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AgentTest")
    
    # Initialize components
    resume_intelligence = ResumeIntelligence()
    
    # Test Resume Agent
    logger.info("\n🧪 Testing Resume Agent...")
    from backend.agents.multi_agent_orchestrator import ResumeParsingAgent, AgentMessage, OrchestrationState, AgentStatus, WorkflowPhase, AgentExecutionState
    
    resume_agent = ResumeParsingAgent(resume_intelligence)
    
    # Create mock state
    state = OrchestrationState(
        run_id="test_run",
        user_id="test_user",
        status=AgentStatus.RUNNING,
        current_phase=WorkflowPhase.INITIALIZATION,
        agents={"ResumeAgent": AgentExecutionState(name="ResumeAgent", status=AgentStatus.IDLE)}
    )
    
    # Create message
    message = AgentMessage(
        from_agent="Test",
        to_agent="ResumeAgent",
        action="PARSE_RESUME",
        data={
            'resume_file_path': 'data/resumes/sample_resume.pdf',
            'keywords': 'Python Developer',
            'location': 'Remote',
            'max_jobs': 10
        }
    )
    
    try:
        result = await resume_agent.execute(message, state)
        logger.info(f"✅ Resume Agent: {result.action}")
        if state.resume_data:
            logger.info(f"   Name: {state.resume_data.get('name')}")
            logger.info(f"   Skills: {len(state.resume_data.get('skills', []))}")
    except Exception as e:
        logger.error(f"❌ Resume Agent failed: {e}")
    
    logger.info("\n✅ Agent testing complete")


# ===========================
# MAIN
# ===========================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AutoAgentHire Integration Example")
    parser.add_argument(
        '--mode',
        choices=['basic', 'monitor', 'test'],
        default='basic',
        help='Execution mode: basic (default), monitor (with status), test (individual agents)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'basic':
        print("\n🚀 Running basic autonomous workflow...")
        asyncio.run(run_autonomous_workflow())
    
    elif args.mode == 'monitor':
        print("\n📊 Running with status monitoring...")
        asyncio.run(run_with_status_monitoring())
    
    elif args.mode == 'test':
        print("\n🧪 Testing individual agents...")
        asyncio.run(test_individual_agents())
