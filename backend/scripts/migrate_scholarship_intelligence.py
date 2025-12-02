"""
Migration script to fix existing workflows missing scholarship_intelligence
This script copies scholarship_intelligence from state_checkpoint to the DB field
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_session
from workflows.db_operations import WorkflowSessionOperations

def migrate_scholarship_intelligence():
    """
    Fix workflows that have scholarship_intelligence in checkpoint but not in DB field
    """
    db = next(get_session())
    
    try:
        # Get all workflows
        workflows = WorkflowSessionOperations.get_all(db, limit=1000)
        
        fixed_count = 0
        total_count = len(workflows)
        
        print(f"\n🔍 Checking {total_count} workflow sessions...\n")
        
        for wf in workflows:
            # Check if scholarship_intelligence is in checkpoint but not in DB field
            if wf.state_checkpoint and not wf.scholarship_intelligence:
                checkpoint_intel = wf.state_checkpoint.get("scholarship_intelligence")
                
                if checkpoint_intel:
                    print(f"✓ Fixing workflow {wf.id[:8]}... (status: {wf.status})")
                    
                    # Update the DB field
                    WorkflowSessionOperations.update_results(db, wf.id, {
                        "scholarship_intelligence": checkpoint_intel
                    })
                    
                    fixed_count += 1
        
        print(f"\n✅ Migration complete!")
        print(f"   Fixed: {fixed_count} workflows")
        print(f"   Total checked: {total_count}")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_scholarship_intelligence()
