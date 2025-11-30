import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, ResumeSession, WorkflowSession, Application
from workflows.db_operations import ResumeSessionOperations, WorkflowSessionOperations, ApplicationOperations

# Setup in-memory SQLite database
engine = create_engine('sqlite:///:memory:')
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_resume_session_user_id(db):
    """Test creating resume session with user_id"""
    resume = ResumeSessionOperations.create(
        db=db,
        session_id="test_resume_1",
        filename="test.pdf",
        file_size_bytes=1000,
        chunks_stored=10,
        user_id="user_123"
    )
    
    assert resume.user_id == "user_123"
    
    # Verify retrieval
    fetched = ResumeSessionOperations.get(db, "test_resume_1")
    assert fetched.user_id == "user_123"
    
    # Verify filtering
    all_sessions = ResumeSessionOperations.get_all(db, user_id="user_123")
    assert len(all_sessions) == 1
    assert all_sessions[0].id == "test_resume_1"
    
    # Verify filtering mismatch
    other_sessions = ResumeSessionOperations.get_all(db, user_id="other_user")
    assert len(other_sessions) == 0

def test_workflow_session_user_id(db):
    """Test creating workflow session with user_id"""
    workflow = WorkflowSessionOperations.create(
        db=db,
        session_id="test_workflow_1",
        scholarship_url="http://example.com",
        resume_session_id="test_resume_1",
        user_id="user_123"
    )
    
    assert workflow.user_id == "user_123"
    
    # Verify retrieval
    fetched = WorkflowSessionOperations.get(db, "test_workflow_1")
    assert fetched.user_id == "user_123"
    
    # Verify filtering
    all_workflows = WorkflowSessionOperations.get_all(db, user_id="user_123")
    assert len(all_workflows) == 1
    assert all_workflows[0].id == "test_workflow_1"

def test_application_user_id(db):
    """Test creating application with user_id"""
    app = ApplicationOperations.create(
        db=db,
        workflow_session_id="test_workflow_1",
        resume_session_id="test_resume_1",
        scholarship_url="http://example.com",
        user_id="user_123"
    )
    
    assert app.user_id == "user_123"
    
    # Verify retrieval
    fetched = ApplicationOperations.get(db, app.id)
    assert fetched.user_id == "user_123"
    
    # Verify filtering
    all_apps = ApplicationOperations.get_all(db, user_id="user_123")
    assert len(all_apps) == 1
    assert all_apps[0].id == app.id
