"""
PostgreSQL database models and connection setup
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class WorkflowSession(Base):
    """Workflow session tracking"""
    __tablename__ = "workflow_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_session_id = Column(String, ForeignKey("resume_sessions.id"), nullable=True)
    status = Column(String, nullable=False)  # processing, waiting_for_input, complete, error
    scholarship_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Workflow results (stored as JSON)
    matchmaker_results = Column(JSON, nullable=True)
    essay_draft = Column(Text, nullable=True)
    resume_optimizations = Column(JSON, nullable=True)
    optimized_resume_markdown = Column(Text, nullable=True)
    strategy_note = Column(Text, nullable=True)
    match_score = Column(Float, nullable=True)
    gaps = Column(JSON, nullable=True)
    scholarship_intelligence = Column(JSON, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # State checkpoint (for resumable workflows)
    state_checkpoint = Column(JSON, nullable=True)
    
    # Relationships
    resume_session = relationship("ResumeSession", back_populates="workflows")
    interview_sessions = relationship("InterviewSession", back_populates="workflow")
    applications = relationship("Application", back_populates="workflow")


class ResumeSession(Base):
    """Resume upload session tracking"""
    __tablename__ = "resume_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    chunks_stored = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Optional: Store resume text preview
    text_preview = Column(Text, nullable=True)
    
    # Relationships
    workflows = relationship("WorkflowSession", back_populates="resume_session")
    applications = relationship("Application", back_populates="resume_session")


class InterviewSession(Base):
    """Interview session tracking"""
    __tablename__ = "interview_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_session_id = Column(String, ForeignKey("workflow_sessions.id"), nullable=False)
    
    gaps = Column(JSON, nullable=False)  # List of gap keywords
    weighted_keywords = Column(JSON, nullable=False)  # Dict of keyword -> weight
    gap_confidences = Column(JSON, nullable=False)  # Dict of gap -> confidence
    prioritized_gaps = Column(JSON, nullable=False)  # List of prioritized gaps
    
    current_target = Column(String, nullable=True)
    conversation_history = Column(JSON, default=list)  # List of messages
    collected_evidence = Column(JSON, default=dict)  # Dict of gap -> evidence
    bridge_story = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    workflow = relationship("WorkflowSession", back_populates="interview_sessions")


class Application(Base):
    """Application history tracking"""
    __tablename__ = "applications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_session_id = Column(String, ForeignKey("workflow_sessions.id"), nullable=False)
    resume_session_id = Column(String, ForeignKey("resume_sessions.id"), nullable=False)
    
    scholarship_url = Column(String, nullable=False)
    status = Column(String, nullable=False)  # complete, error
    match_score = Column(Float, nullable=True)
    had_interview = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = relationship("WorkflowSession", back_populates="applications")
    resume_session = relationship("ResumeSession", back_populates="applications")


# Database connection and session management
class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self, database_url: str):
        """
        Initialize database connection
        
        Args:
            database_url: PostgreSQL connection string
                Format: postgresql://user:password@host:port/database
        """
        self.engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True  # Verify connections before using
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session (use with context manager)"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)