"""
Database utility scripts for ScholarFit AI
Run with: python db_utils.py [command]
"""

import sys
from database import DatabaseManager
from config.settings import settings


def test_connection():
    """Test database connection"""
    try:
        print("Testing database connection...")
        db_manager = DatabaseManager(settings.database_url)
        db = next(db_manager.get_session())
        print("✓ Database connection successful!")
        db.close()
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        db_manager = DatabaseManager(settings.database_url)
        db_manager.create_tables()
        print("✓ Tables created successfully!")
        return True
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        return False


def drop_tables():
    """Drop all database tables (WARNING: destructive!)"""
    confirm = input("⚠️  WARNING: This will delete ALL data. Type 'DELETE' to confirm: ")
    if confirm != "DELETE":
        print("Cancelled.")
        return False
    
    try:
        print("Dropping all tables...")
        db_manager = DatabaseManager(settings.database_url)
        db_manager.drop_tables()
        print("✓ Tables dropped successfully!")
        return True
    except Exception as e:
        print(f"✗ Failed to drop tables: {e}")
        return False


def reset_database():
    """Reset database (drop and recreate all tables)"""
    print("Resetting database...")
    if drop_tables():
        return create_tables()
    return False


def show_stats():
    """Show database statistics"""
    try:
        from database import (
            WorkflowSessionOperations,
            ResumeSessionOperations,
            InterviewSessionOperations,
            ApplicationOperations
        )
        from sqlalchemy import func
        
        print("Database Statistics:")
        print("-" * 50)
        
        db_manager = DatabaseManager(settings.database_url)
        db = next(db_manager.get_session())
        
        # Count records
        from database import WorkflowSession, ResumeSession, InterviewSession, Application
        
        workflow_count = db.query(func.count(WorkflowSession.id)).scalar()
        resume_count = db.query(func.count(ResumeSession.id)).scalar()
        interview_count = db.query(func.count(InterviewSession.id)).scalar()
        application_count = db.query(func.count(Application.id)).scalar()
        
        print(f"Resume Sessions: {resume_count}")
        print(f"Workflow Sessions: {workflow_count}")
        print(f"Interview Sessions: {interview_count}")
        print(f"Applications: {application_count}")
        print("-" * 50)
        
        # Status breakdown
        from sqlalchemy import distinct
        statuses = db.query(
            WorkflowSession.status,
            func.count(WorkflowSession.id)
        ).group_by(WorkflowSession.status).all()
        
        if statuses:
            print("\nWorkflow Status Breakdown:")
            for status, count in statuses:
                print(f"  {status}: {count}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to get stats: {e}")
        return False


def cleanup_old_sessions():
    """Clean up old incomplete sessions (older than 24 hours)"""
    try:
        from datetime import datetime, timedelta
        from database import WorkflowSession
        
        print("Cleaning up old sessions...")
        
        db_manager = DatabaseManager(settings.database_url)
        db = next(db_manager.get_session())
        
        # Find old incomplete sessions
        cutoff = datetime.utcnow() - timedelta(hours=24)
        old_sessions = db.query(WorkflowSession).filter(
            WorkflowSession.status.in_(["processing", "processing_resume"]),
            WorkflowSession.created_at < cutoff
        ).all()
        
        count = 0
        for session in old_sessions:
            session.status = "error"
            session.error_message = "Session timeout (cleaned up by utility)"
            count += 1
        
        db.commit()
        db.close()
        
        print(f"✓ Cleaned up {count} old sessions")
        return True
        
    except Exception as e:
        print(f"✗ Failed to cleanup: {e}")
        return False


def export_applications():
    """Export all applications to CSV"""
    try:
        import csv
        from datetime import datetime
        from database import Application
        
        print("Exporting applications...")
        
        db_manager = DatabaseManager(settings.database_url)
        db = next(db_manager.get_session())
        
        applications = db.query(Application).all()
        
        filename = f"applications_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID', 'Resume Session', 'Workflow Session',
                'Scholarship URL', 'Status', 'Match Score',
                'Had Interview', 'Created At'
            ])
            
            for app in applications:
                writer.writerow([
                    app.id,
                    app.resume_session_id,
                    app.workflow_session_id,
                    app.scholarship_url,
                    app.status,
                    app.match_score,
                    app.had_interview,
                    app.created_at.isoformat()
                ])
        
        db.close()
        
        print(f"✓ Exported {len(applications)} applications to {filename}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to export: {e}")
        return False


def show_help():
    """Show available commands"""
    print("""
ScholarFit AI Database Utilities

Available commands:
  test           - Test database connection
  create         - Create all database tables
  drop           - Drop all database tables (WARNING: destructive!)
  reset          - Reset database (drop and recreate)
  stats          - Show database statistics
  cleanup        - Clean up old incomplete sessions
  export         - Export applications to CSV
  help           - Show this help message

Usage:
  python db_utils.py [command]

Examples:
  python db_utils.py test
  python db_utils.py stats
  python db_utils.py cleanup
    """)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        'test': test_connection,
        'create': create_tables,
        'drop': drop_tables,
        'reset': reset_database,
        'stats': show_stats,
        'cleanup': cleanup_old_sessions,
        'export': export_applications,
        'help': show_help
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()