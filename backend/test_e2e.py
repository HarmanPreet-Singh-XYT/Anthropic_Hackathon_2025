"""
End-to-End Test for Scholarship Workflow
Tests the full workflow from start to matchmaker page
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflows.scholarship_graph import ScholarshipWorkflow
from agents.scout import ScoutAgent
from agents.profiler import ProfilerAgent
from agents.decoder import DecoderAgent
from agents.matchmaker import MatchmakerAgent
from agents.interviewer import InterviewerAgent
from agents.optimizer import OptimizerAgent
from agents.ghostwriter import GhostwriterAgent
from utils.llm_client import create_llm_client
from utils.vector_store import VectorStore
from dotenv import load_dotenv

# Load env
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, '.env'))

async def test_workflow():
    print("=" * 60)
    print("🧪 Testing End-to-End Scholarship Workflow")
    print("=" * 60)
    
    # Initialize agents
    print("\n[1/5] Initializing agents...")
    llm_client = create_llm_client(temperature=0.3)
    vector_store = VectorStore()
    
    agents = {
        "scout": ScoutAgent(),
        "profiler": ProfilerAgent(vector_store),
        "decoder": DecoderAgent(llm_client),
        "matchmaker": MatchmakerAgent(vector_store, llm_client),
        "interviewer": InterviewerAgent(llm_client),
        "optimizer": OptimizerAgent(llm_client),
        "ghostwriter": GhostwriterAgent(llm_client)
    }
    print("✓ Agents initialized")
    
    # Initialize workflow
    print("\n[2/5] Initializing workflow...")
    workflow = ScholarshipWorkflow(agents)
    print("✓ Workflow ready")
    
    # Test inputs
    scholarship_url = "https://www.coca-colascholarsfoundation.org/apply/"
    resume_path = "data/sample_resume.pdf"  # Assumes a sample resume exists
    
    print(f"\n[3/5] Running workflow...")
    print(f"  Scholarship: {scholarship_url}")
    print(f"  Resume: {resume_path}")
    
    try:
        final_state = await workflow.run(
            scholarship_url=scholarship_url,
            resume_pdf_path=resume_path
        )
        
        print("\n[4/5] Workflow completed!")
        print(f"  Status: {final_state.get('current_phase', 'unknown')}")
        
        # Check critical fields
        print("\n[5/5] Validating results...")
        
        checks = {
            "scholarship_intelligence": final_state.get("scholarship_intelligence") is not None,
            "decoder_analysis": final_state.get("decoder_analysis") is not None,
            "match_score": final_state.get("match_score") is not None,
            "matchmaker_results": final_state.get("matchmaker_results") is not None,
            "interview_question": final_state.get("interview_question") is not None,
        }
        
        print("\nValidation Results:")
        for check, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check}: {passed}")
        
        # Critical check: matchmaker_results must exist
        if not checks["matchmaker_results"]:
            print("\n❌ CRITICAL FAILURE: matchmaker_results is missing!")
            print("   This will cause the frontend to get stuck on 'Analyzing your match...'")
            return False
        
        # Verify matchmaker_results structure
        mr = final_state.get("matchmaker_results", {})
        required_fields = ["match_score", "weighted_values", "keyword_match_details", "gaps"]
        missing = [f for f in required_fields if f not in mr]
        
        if missing:
            print(f"\n❌ FAILURE: matchmaker_results missing fields: {missing}")
            return False
        
        print("\n✅ ALL TESTS PASSED!")
        print(f"\n📊 Match Score: {mr['match_score'] * 100:.0f}%")
        print(f"📋 Gaps: {', '.join(mr['gaps'])}")
        print(f"❓ Interview Question: {final_state.get('interview_question', 'N/A')[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_workflow())
    sys.exit(0 if success else 1)
