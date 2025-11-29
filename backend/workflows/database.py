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
    user_id = Column(String, nullable=True, index=True)
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
    user_id = Column(String, nullable=True, index=True)
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
    user_id = Column(String, nullable=True, index=True)
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


class User(Base):
    """User account"""
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # Matches auth provider ID
    email = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    wallet = relationship("UserWallet", back_populates="user", uselist=False)
    transactions = relationship("WalletTransaction", back_populates="user")
    usage_records = relationship("UsageRecord", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")


class UserWallet(Base):
    """User token wallet"""
    __tablename__ = "user_wallets"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    balance_tokens = Column(Integer, default=0)  # Changed to Integer for BigInt compatibility in Python
    currency = Column(String(10), default='TOK')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="wallet")


class WalletTransaction(Base):
    """Wallet transaction history"""
    __tablename__ = "wallet_transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # BigInt
    balance_after = Column(Integer, nullable=False)  # BigInt
    kind = Column(String, nullable=False)  # deduction, grant, purchase
    reference_id = Column(String, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)  # 'metadata' is reserved in SQLAlchemy Base
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")


class UsageRecord(Base):
    """Resource usage tracking"""
    __tablename__ = "usage_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    tokens_used = Column(Integer, nullable=False)  # BigInt
    cost_cents = Column(Integer, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="usage_records")


class BillingPlan(Base):
    """Subscription billing plans"""
    __tablename__ = "billing_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    price_cents = Column(Integer, nullable=False)
    interval = Column(String, nullable=False)  # month, year
    tokens_per_period = Column(Integer, nullable=False)  # BigInt
    features = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """User subscriptions"""
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan_id = Column(String, ForeignKey("billing_plans.id"), nullable=False)
    status = Column(String, nullable=False)  # active, canceled, past_due
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    trial_end = Column(DateTime, nullable=True)
    external_subscription_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("BillingPlan", back_populates="subscriptions")
    payments = relationship("SubscriptionPayment", back_populates="subscription")


class SubscriptionPayment(Base):
    """Subscription payment history"""
    __tablename__ = "subscription_payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(10), default='USD')
    status = Column(String, nullable=False)
    external_payment_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", back_populates="payments")


class Invoice(Base):
    """Invoices"""
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount_cents = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="invoices")


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