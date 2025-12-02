"""
Test script to reproduce the outreach 400 error
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_session
from workflows.db_operations import WorkflowSessionOperations

def test_outreach_data():
    """Check if workflow sessions have scholarship_intelligence"""
    db = next(get_session())
    
    try:
        # Get all workflows
        workflows = WorkflowSessionOperations.get_all(db, limit=10)
        
        print(f"\n📊 Found {len(workflows)} workflow sessions\n")
        
        for wf in workflows:
            print(f"Session ID: {wf.id}")
            print(f"  Status: {wf.status}")
            print(f"  Scholarship URL: {wf.scholarship_url}")
            print(f"  Has scholarship_intelligence: {wf.scholarship_intelligence is not None}")
            
            if wf.state_checkpoint:
                has_in_checkpoint = "scholarship_intelligence" in wf.state_checkpoint
                print(f"  Has scholarship_intelligence in checkpoint: {has_in_checkpoint}")
                
                if has_in_checkpoint and not wf.scholarship_intelligence:
                    print(f"  ⚠️  ISSUE FOUND: scholarship_intelligence in checkpoint but not in DB field!")
            
            print()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_outreach_data()
