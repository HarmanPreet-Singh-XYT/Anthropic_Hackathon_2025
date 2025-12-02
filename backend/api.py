"""
FastAPI server for ScholarFit AI backend
Handles resume upload, processing, and ChromaDB integration with PostgreSQL storage
"""

import os
from datetime import datetime
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, File, UploadFile, HTTPException, status, Form, BackgroundTasks, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config.settings import settings
from utils.vector_store import VectorStore
from utils.llm_client import create_llm_client
from agents.scout import ScoutAgent
from agents.profiler import ProfilerAgent
from agents.decoder import DecoderAgent
from agents.matchmaker import MatchmakerAgent
from agents.interviewer import InterviewerAgent
from agents.optimizer import OptimizerAgent
from agents.ghostwriter import GhostwriterAgent
from agents.interview_manager import InterviewManager
from workflows import ScholarshipWorkflow

# Database imports
from database import DatabaseManager
from workflows.db_operations import (
    WorkflowSessionOperations,
    ResumeSessionOperations,
    InterviewSessionOperations,
    ApplicationOperations,
    UserOperations,
    UsageRecordOperations,
    WalletTransactionOperations
)


# ==================== Pydantic Models ====================

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    vector_store_ready: bool
    database_ready: bool
    collection_stats: Optional[Dict[str, Any]] = None


class UploadResponse(BaseModel):
    """Resume upload response model"""
    success: bool
    message: str
    chunks_stored: int
    metadata: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    details: Optional[str] = None


# --- Dashboard Models ---

class WalletInfo(BaseModel):
    balance_tokens: int
    currency: str
    last_updated: Optional[datetime]


class PlanInfo(BaseModel):
    name: str
    interval: str
    price_cents: int
    tokens_per_period: int
    features: Optional[Dict[str, Any]] = None


class SubscriptionInfo(BaseModel):
    status: str
    plan: PlanInfo
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]


class DashboardApplication(BaseModel):
    id: str
    session_id: str
    scholarship_url: str
    status: str
    match_score: Optional[float]
    had_interview: bool
    created_at: datetime


class DashboardInterview(BaseModel):
    id: str
    current_target: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


class DashboardWorkflow(BaseModel):
    id: str
    scholarship_url: str
    status: str
    match_score: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    applications: List[DashboardApplication]
    interview_session: Optional[DashboardInterview]


class DashboardResume(BaseModel):
    id: str
    filename: str
    file_size_bytes: int
    created_at: datetime
    text_preview: Optional[str]
    workflow_sessions: List[DashboardWorkflow]


class UsageStats(BaseModel):
    queries_today: int
    queries_month: int
    tokens_used_today: int
    tokens_used_month: int


class ActivityItem(BaseModel):
    type: str
    ref_id: str
    description: str
    timestamp: datetime
    amount: Optional[int] = None


class UserInfo(BaseModel):
    id: str
    email: Optional[str] = None


class DashboardResponse(BaseModel):
    """Dashboard data response model"""
    user: UserInfo
    wallet: Optional[WalletInfo]
    subscription: Optional[SubscriptionInfo]
    resume_sessions: List[DashboardResume]
    usage: UsageStats
    recent_activity: List[ActivityItem]


# --- Billing Models ---

class PaymentHistoryItem(BaseModel):
    id: str
    amount_cents: int
    currency: str
    status: str
    date: datetime
    description: str

class TransactionHistoryItem(BaseModel):
    id: str
    amount: int
    type: str  # 'credit' or 'debit'
    balance_after: int
    description: str
    date: datetime

class UsageHistoryItem(BaseModel):
    id: str
    feature: str
    amount: int
    cost_cents: Optional[int]
    date: datetime

class BillingDetailsResponse(BaseModel):
    subscription: Optional[SubscriptionInfo]
    wallet: Optional[WalletInfo]
    payment_history: List[PaymentHistoryItem]
    transaction_history: List[TransactionHistoryItem]
    usage_history: List[UsageHistoryItem]


# ... (FastAPI Application setup remains same) ...


# ==================== FastAPI Application ====================

app = FastAPI(
    title="ScholarFit AI API",
    description="Backend API for scholarship application optimization",
    version="1.0.0",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Global State ====================

# Vector store instance
vector_store: Optional[VectorStore] = None

# Database manager
db_manager: Optional[DatabaseManager] = None

# Workflow orchestrator
workflow_orchestrator: Optional[ScholarshipWorkflow] = None

# Uploads directory
UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


# ==================== Database Dependency ====================

def get_db():
    """Dependency to get database session"""
    db = next(db_manager.get_session())
    try:
        yield db
    finally:
        db.close()


# ==================== Billing Plan Management ====================

def _seed_billing_plans_if_needed():
    """Seed billing plans if they don't exist"""
    from database import BillingPlan
    
    db = next(db_manager.get_session())
    try:
        # Check if plans already exist
        existing = db.query(BillingPlan).count()
        if existing > 0:
            print(f"  ✓ {existing} billing plans already exist")
            return
        
        # Define predefined plans
        plans = [
            BillingPlan(
                slug="free",
                name="Free",
                price_cents=0,
                interval="month",
                tokens_per_period=100,
                features={"max_applications": 5, "support": "community"}
            ),
            BillingPlan(
                slug="starter",
                name="Starter",
                price_cents=999,  # $9.99
                interval="month",
                tokens_per_period=500,
                features={"max_applications": 25, "support": "email", "priority_processing": False}
            ),
            BillingPlan(
                slug="pro",
                name="Pro",
                price_cents=2900,  # $29.00
                interval="month",
                tokens_per_period=2000,
                features={"max_applications": -1, "support": "priority", "priority_processing": True, "advanced_analytics": True}
            ),
            BillingPlan(
                slug="pro-annual",
                name="Pro Annual",
                price_cents=29000,  # $290.00 (save ~17%)
                interval="year",
                tokens_per_period=24000,
                features={"max_applications": -1, "support": "priority", "priority_processing": True, "advanced_analytics": True, "annual_discount": True}
            )
        ]
        
        for plan in plans:
            db.add(plan)
        
        db.commit()
        print(f"  ✓ Created {len(plans)} billing plans")
        
    except Exception as e:
        print(f"  ✗ Error seeding billing plans: {e}")
        db.rollback()
    finally:
        db.close()


def _validate_plan_slug(db: Session, plan_slug: str) -> bool:
    """
    Validate that a plan slug exists in the database
    
    Args:
        db: Database session
        plan_slug: The plan slug to validate
        
    Returns:
        True if valid, raises HTTPException if not
    """
    from database import BillingPlan
    
    plan = db.query(BillingPlan).filter(BillingPlan.slug == plan_slug).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan slug: {plan_slug}. Plan does not exist."
        )
    return True


# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global vector_store, db_manager, workflow_orchestrator
    
    try:
        # Initialize PostgreSQL database
        print("Initializing PostgreSQL database...")
        db_manager = DatabaseManager(settings.database_url)
        db_manager.create_tables()
        print("✓ PostgreSQL database initialized")
        
        # Seed billing plans if they don't exist
        print("Checking billing plans...")
        _seed_billing_plans_if_needed()
        print("✓ Billing plans ready")
        
        # Initialize ChromaDB vector store
        vector_store = VectorStore(
            collection_name="resumes",
            persist_directory=str(settings.chroma_dir)
        )
        print(f"✓ Vector store initialized: {settings.chroma_dir}")
        
        # Get initial stats
        stats = vector_store.get_collection_stats()
        print(f"✓ Collection stats: {stats['count']} documents")
        
        # Initialize LLM Client
        llm_client = create_llm_client()
        print("✓ LLM Client initialized")
        
        # Initialize Agents
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
        
        # Initialize Workflow with database session factory
        workflow_orchestrator = ScholarshipWorkflow(
            agents=agents,
            db_session_factory=db_manager.get_session
        )
        print("✓ Workflow orchestrator ready")
        
    except Exception as e:
        print(f"✗ Error initializing services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down API server...")


# ==================== Helper Functions ====================

def sanitize_user_id(x_user_id: Optional[str]) -> Optional[str]:
    """
    Sanitize user_id from header, converting string 'null'/'undefined' to None
    
    This prevents issues where frontend sends string "null" or "undefined" 
    instead of omitting the header, which would cause database query mismatches.
    
    Args:
        x_user_id: Raw user ID from header
        
    Returns:
        Sanitized user ID or None
    """
    if not x_user_id:
        return None
    
    # Convert string representations of null to actual None
    if x_user_id.lower() in ('null', 'undefined', 'none', ''):
        return None
    
    return x_user_id.strip()


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "ScholarFit AI API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "upload_resume": "/api/upload-resume",
            "resume_stats": "/api/resume-stats",
            "clear_resume": "/api/resume (DELETE)",
        }
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    vector_ready = vector_store is not None
    db_ready = db_manager is not None
    
    stats = None
    if vector_ready:
        try:
            stats = vector_store.get_collection_stats()
        except Exception as e:
            stats = {"error": str(e)}
    
    return HealthResponse(
        status="ok" if (vector_ready and db_ready) else "degraded",
        vector_store_ready=vector_ready,
        database_ready=db_ready,
        collection_stats=stats
    )


@app.post("/api/upload-resume", response_model=UploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    """Upload and process a resume PDF"""
    
    # SANITIZE user_id to prevent string "null" issues
    raw_user_id = x_user_id
    x_user_id = sanitize_user_id(x_user_id)
    
    print(f"📤 [UPLOAD] Raw header x_user_id: {repr(raw_user_id)}")
    print(f"📤 [UPLOAD] Sanitized user_id: {repr(x_user_id)}")
    
    if vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not initialized"
        )
    
    # Handle missing user_id
    if not x_user_id:
        print("⚠️  [API] No x-user-id header provided, using anonymous session")
        x_user_id = None  # Will be stored as NULL in database
    else:
        print(f"✓ [API] Upload for user: {x_user_id}")
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only PDF files are supported."
        )
    
    # Validate file size
    MAX_SIZE = settings.max_upload_size_mb * 1024 * 1024
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {settings.max_upload_size_mb}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )
    
    # Save file temporarily
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = UPLOADS_DIR / temp_filename
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    print(f"🆔 [API] Generated session_id: {session_id} for resume upload (user: {x_user_id or 'anonymous'})")
    
    try:
        # Write file to disk
        with open(temp_path, "wb") as f:
            f.write(file_content)
        
        # Clean up old vector data for this session
        try:
            all_docs = vector_store.collection.get(where={"session_id": session_id})
            if all_docs["ids"]:
                print(f"🗑️ [API] Cleaning {len(all_docs['ids'])} old chunks")
                vector_store.delete_documents(all_docs["ids"])
        except Exception as e:
            print(f"⚠️ [API] Could not clean old session data: {e}")
        
        # Process with ProfilerAgent
        profiler = ProfilerAgent(vector_store)
        result = await profiler.run(str(temp_path), session_id=session_id)
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error during processing")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process PDF: {error_msg}"
            )
        
        # Store resume session in database WITH user_id
        text_preview = result.get("resume_text", "")[:500] if result.get("resume_text") else None
        
        print(f"📝 [API] Creating resume session in database...")
        print(f"   - session_id: {session_id}")
        print(f"   - filename: {file.filename}")
        print(f"   - file_size_bytes: {file_size}")
        print(f"   - chunks_stored: {result.get('chunks_stored', 0)}")
        print(f"   - user_id: {x_user_id or 'NULL'}")
        
        try:
            # Direct database insert with immediate commit
            from database import ResumeSession
            
            resume_session = ResumeSession(
                id=session_id,
                user_id=x_user_id,
                filename=file.filename,
                file_size_bytes=file_size,
                chunks_stored=result.get("chunks_stored", 0),
                text_preview=text_preview
            )
            db.add(resume_session)
            db.commit()
            db.refresh(resume_session)
            
            print(f"✓ [API] Resume session created successfully: {resume_session.id}")
            
            # VERIFY it was actually saved
            verification = db.query(ResumeSession).filter(ResumeSession.id == session_id).first()
            if not verification:
                print(f"❌ [API] CRITICAL: Resume was committed but not found in database!")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Resume was saved but could not be verified in database"
                )
            print(f"✓ [API] Resume session verified in database")
            
        except HTTPException:
            raise
        except Exception as db_error:
            db.rollback()
            print(f"❌ [API] Database error creating resume session: {db_error}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save resume to database: {str(db_error)}"
            )
        
        print(f"✓ [API] Resume processed and stored in DB for session: {session_id} (user: {x_user_id or 'anonymous'})")
        
        return UploadResponse(
            success=True,
            message="Resume processed successfully",
            chunks_stored=result.get("chunks_stored", 0),
            metadata={
                "session_id": session_id,
                "filename": file.filename,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / 1024 / 1024, 2),
                "text_preview": text_preview,
                "user_id": x_user_id  # Include in response so frontend knows
            }
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error processing resume: {str(e)}"
        )
    
    finally:
        if temp_path.exists():
            temp_path.unlink()


@app.post("/api/admin/migrate-user-data")
async def migrate_anonymous_data_to_user(
    target_user_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Migrate all anonymous (NULL user_id) data to a specific user.
    This is useful for claiming existing data after implementing user authentication.
    """
    from database import ResumeSession, WorkflowSession, Application, InterviewSession, UsageRecord
    
    try:
        print(f"🔄 [Migration] Starting data migration to user: {target_user_id}")
        
        # 1. Migrate Resume Sessions
        anonymous_resumes = db.query(ResumeSession).filter(
            ResumeSession.user_id == None
        ).all()
        
        resume_count = 0
        for resume in anonymous_resumes:
            resume.user_id = target_user_id
            resume_count += 1
            print(f"   ✓ Migrated resume: {resume.id}")
        
        # 2. Migrate Workflow Sessions
        anonymous_workflows = db.query(WorkflowSession).filter(
            WorkflowSession.user_id == None
        ).all()
        
        workflow_count = 0
        for workflow in anonymous_workflows:
            workflow.user_id = target_user_id
            workflow_count += 1
            print(f"   ✓ Migrated workflow: {workflow.id}")
        
        # 3. Migrate Applications
        anonymous_applications = db.query(Application).filter(
            Application.user_id == None
        ).all()
        
        application_count = 0
        for app in anonymous_applications:
            app.user_id = target_user_id
            application_count += 1
            print(f"   ✓ Migrated application: {app.id}")
        
        # 4. Migrate Usage Records
        anonymous_usage = db.query(UsageRecord).filter(
            UsageRecord.user_id == None
        ).all()
        
        usage_count = 0
        for usage in anonymous_usage:
            usage.user_id = target_user_id
            usage_count += 1
        
        # Commit all changes
        db.commit()
        
        print(f"✅ [Migration] Migration complete!")
        print(f"   • Resumes: {resume_count}")
        print(f"   • Workflows: {workflow_count}")
        print(f"   • Applications: {application_count}")
        print(f"   • Usage Records: {usage_count}")
        
        return {
            "success": True,
            "message": f"Migrated anonymous data to user {target_user_id}",
            "migrated": {
                "resumes": resume_count,
                "workflows": workflow_count,
                "applications": application_count,
                "usage_records": usage_count
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ [Migration] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@app.get("/api/admin/check-schema")
async def check_database_schema(db: Session = Depends(get_db)):
    """Check database schema and constraints"""
    from database import ResumeSession
    from sqlalchemy import inspect
    
    try:
        inspector = inspect(db.bind)
        
        # Get ResumeSession table info
        columns = inspector.get_columns('resume_sessions')
        indexes = inspector.get_indexes('resume_sessions')
        pk_constraint = inspector.get_pk_constraint('resume_sessions')
        foreign_keys = inspector.get_foreign_keys('resume_sessions')
        
        # Try a test insert and rollback
        test_id = str(uuid.uuid4())
        test_resume = ResumeSession(
            id=test_id,
            user_id="test_user",
            filename="test.pdf",
            file_size_bytes=100,
            chunks_stored=1,
            text_preview="test"
        )
        db.add(test_resume)
        db.flush()  # Flush but don't commit
        
        # Check if it's in the session
        found = db.query(ResumeSession).filter(ResumeSession.id == test_id).first()
        test_passed = found is not None
        
        db.rollback()  # Rollback test insert
        
        return {
            "schema": {
                "columns": [
                    {
                        "name": col['name'],
                        "type": str(col['type']),
                        "nullable": col['nullable'],
                        "default": col.get('default')
                    }
                    for col in columns
                ],
                "primary_key": pk_constraint,
                "indexes": indexes,
                "foreign_keys": foreign_keys
            },
            "test_insert": {
                "passed": test_passed,
                "message": "Test insert successful" if test_passed else "Test insert failed"
            }
        }
    except Exception as e:
        db.rollback()
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@app.get("/api/admin/orphaned-data")
async def check_orphaned_data(db: Session = Depends(get_db)):
    """Check for data without user_id"""
    from database import ResumeSession, WorkflowSession, Application, InterviewSession, UsageRecord
    
    try:
        orphaned_resumes = db.query(ResumeSession).filter(ResumeSession.user_id == None).all()
        orphaned_workflows = db.query(WorkflowSession).filter(WorkflowSession.user_id == None).all()
        orphaned_applications = db.query(Application).filter(Application.user_id == None).all()
        orphaned_usage = db.query(UsageRecord).filter(UsageRecord.user_id == None).all()
        
        return {
            "orphaned_data": {
                "resumes": {
                    "count": len(orphaned_resumes),
                    "items": [
                        {
                            "id": r.id,
                            "filename": r.filename,
                            "created_at": r.created_at.isoformat()
                        }
                        for r in orphaned_resumes
                    ]
                },
                "workflows": {
                    "count": len(orphaned_workflows),
                    "items": [
                        {
                            "id": w.id,
                            "resume_session_id": w.resume_session_id,
                            "status": w.status,
                            "created_at": w.created_at.isoformat()
                        }
                        for w in orphaned_workflows
                    ]
                },
                "applications": {
                    "count": len(orphaned_applications),
                    "items": [
                        {
                            "id": a.id,
                            "workflow_session_id": a.workflow_session_id,
                            "created_at": a.created_at.isoformat()
                        }
                        for a in orphaned_applications
                    ]
                },
                "usage_records": {
                    "count": len(orphaned_usage)
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking orphaned data: {str(e)}"
        )


@app.post("/api/test/create-resume-session")
async def test_create_resume_session(
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    """Test endpoint to verify database write operations"""
    from database import ResumeSession
    
    test_session_id = str(uuid.uuid4())
    
    try:
        print(f"🧪 [TEST] Attempting to create resume session...")
        print(f"   - session_id: {test_session_id}")
        print(f"   - user_id: {x_user_id or 'NULL'}")
        
        # Method 1: Direct SQLAlchemy
        print(f"   Method 1: Direct SQLAlchemy insert...")
        resume_direct = ResumeSession(
            id=test_session_id,
            filename="test_resume.pdf",
            file_size_bytes=12345,
            chunks_stored=10,
            text_preview="This is a test resume",
            user_id=x_user_id
        )
        db.add(resume_direct)
        db.commit()
        db.refresh(resume_direct)
        print(f"   ✓ Direct insert successful: {resume_direct.id}")
        
        # Verify it exists
        check = db.query(ResumeSession).filter(ResumeSession.id == test_session_id).first()
        if check:
            print(f"   ✓ Verification successful: Record exists in database")
        else:
            print(f"   ✗ Verification failed: Record NOT found in database")
        
        # Method 2: Using Operations class
        print(f"   Method 2: Using ResumeSessionOperations...")
        test_session_id_2 = str(uuid.uuid4())
        
        try:
            resume_ops = ResumeSessionOperations.create(
                db=db,
                session_id=test_session_id_2,
                filename="test_resume_2.pdf",
                file_size_bytes=54321,
                chunks_stored=15,
                text_preview="This is another test",
                user_id=x_user_id
            )
            print(f"   ✓ Operations class successful: {resume_ops.id}")
        except Exception as ops_error:
            print(f"   ✗ Operations class failed: {ops_error}")
            import traceback
            traceback.print_exc()
        
        # Count total resumes
        total = db.query(ResumeSession).count()
        print(f"   Total resume sessions in DB: {total}")
        
        return {
            "success": True,
            "test_session_ids": [test_session_id, test_session_id_2],
            "total_resumes": total,
            "message": "Test successful - database writes are working"
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ [TEST] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test failed: {str(e)}"
        )


@app.get("/api/resume-stats")
async def get_resume_stats(db: Session = Depends(get_db)):
    """Get ChromaDB collection statistics"""
    if vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not initialized"
        )
    
    try:
        stats = vector_store.get_collection_stats()
        return {
            "success": True,
            **stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
        )


@app.delete("/api/resume")
async def clear_resume(db: Session = Depends(get_db)):
    """Clear all resume data from ChromaDB"""
    if vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not initialized"
        )
    
    try:
        stats_before = vector_store.get_collection_stats()
        count_before = stats_before.get("count", 0)
        
        vector_store.clear_collection()
        
        stats_after = vector_store.get_collection_stats()
        count_after = stats_after.get("count", 0)
        
        return {
            "success": True,
            "message": "Resume data cleared successfully",
            "documents_removed": count_before - count_after
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing resume data: {str(e)}"
        )


@app.delete("/api/resume/session/{session_id}")
async def delete_session_data(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete resume data for a specific session"""
    if vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not initialized"
        )
    
    try:
        print(f"🗑️ [API] Deleting resume data for session: {session_id}")
        
        # Delete from vector store
        all_docs = vector_store.collection.get(where={"session_id": session_id})
        deleted_count = 0
        
        if all_docs["ids"]:
            vector_store.delete_documents(all_docs["ids"])
            deleted_count = len(all_docs["ids"])
        
        # Delete from database
        ResumeSessionOperations.delete(db, session_id)
        
        print(f"   ✓ Deleted {deleted_count} documents and DB record")
        
        return {
            "success": True,
            "message": "Session data deleted successfully",
            "documents_deleted": deleted_count,
            "session_id": session_id
        }
    
    except Exception as e:
        print(f"   ❌ Error deleting session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session data: {str(e)}"
        )


@app.get("/api/resume/session/{session_id}/validate")
async def validate_resume_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Validate that a resume session exists"""
    if vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not initialized"
        )
    
    try:
        # Check database
        resume_session = ResumeSessionOperations.get(db, session_id)
        
        if not resume_session:
            return {
                "valid": False,
                "session_id": session_id,
                "chunks_count": 0,
                "message": "No resume data found for this session"
            }
        
        # Check vector store
        all_docs = vector_store.collection.get(where={"session_id": session_id})
        chunks_count = len(all_docs["ids"]) if all_docs["ids"] else 0
        
        return {
            "valid": True,
            "session_id": session_id,
            "chunks_count": chunks_count,
            "metadata": {
                "filename": resume_session.filename,
                "file_size_bytes": resume_session.file_size_bytes,
                "created_at": resume_session.created_at.isoformat()
            },
            "message": "Resume session is valid"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating session: {str(e)}"
        )


@app.get("/api/applications/history/{resume_session_id}")
async def get_application_history(
    resume_session_id: str,
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    """Get all applications for a resume session"""
    try:
        print(f"📋 [API] Fetching application history for: {resume_session_id}")
        
        applications = ApplicationOperations.get_by_resume_session(db, resume_session_id)
        
        app_list = [
            {
                "workflow_session_id": app.workflow_session_id,
                "scholarship_url": app.scholarship_url,
                "status": app.status,
                "match_score": app.match_score,
                "had_interview": app.had_interview,
                "created_at": app.created_at.isoformat()
            }
            for app in applications
        ]
        
        print(f"   ✓ Found {len(app_list)} applications")
        
        return {
            "success": True,
            "resume_session_id": resume_session_id,
            "applications": app_list,
            "count": len(app_list)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching application history: {str(e)}"
        )


@app.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    """Get aggregated dashboard data for a user"""
    try:
        # SANITIZE user_id to prevent string "null" issues
        raw_user_id = x_user_id
        x_user_id = sanitize_user_id(x_user_id)
        
        print(f"📊 [DASHBOARD] Raw header x_user_id: {repr(raw_user_id)}")
        print(f"📊 [DASHBOARD] Sanitized user_id: {repr(x_user_id)}")
        
        # Enhanced debugging: Check what user_ids exist in database
        from database import ResumeSession
        
        all_user_ids = db.query(ResumeSession.user_id).distinct().all()
        print(f"📊 [DASHBOARD] All unique user_ids in database: {[uid[0] for uid in all_user_ids]}")
        
        # Check if exact match exists
        if x_user_id:
            exact_match_count = db.query(ResumeSession).filter(ResumeSession.user_id == x_user_id).count()
            print(f"📊 [DASHBOARD] Exact matches for user_id={repr(x_user_id)}: {exact_match_count}")
        
        # For demo purposes, if no user_id after sanitization, use a default test user
        if not x_user_id:
            x_user_id = "test_user_demo"
            print(f"📊 [DASHBOARD] No user_id provided, using demo user: {x_user_id}")
        
        print(f"📊 [DASHBOARD] Fetching dashboard data for user: {x_user_id}")
        
        # 1. Get/Create User & Wallet
        user = UserOperations.create_if_not_exists(db, x_user_id)
        print(f"   ✓ User found: {user.id}")
        
        # 2. Build Wallet Info
        wallet_info = None
        if user.wallet:
            wallet_info = WalletInfo(
                balance_tokens=user.wallet.balance_tokens,
                currency=user.wallet.currency,
                last_updated=user.wallet.updated_at
            )
            print(f"   ✓ Wallet: {user.wallet.balance_tokens} tokens")
            
        # 3. Build Subscription Info
        sub_info = None
        if user.subscriptions:
            # Get active subscription
            active_sub = next((s for s in user.subscriptions if s.status == "active"), None)
            if active_sub and active_sub.plan:
                sub_info = SubscriptionInfo(
                    status=active_sub.status,
                    plan=PlanInfo(
                        name=active_sub.plan.name,
                        interval=active_sub.plan.interval,
                        price_cents=active_sub.plan.price_cents,
                        tokens_per_period=active_sub.plan.tokens_per_period,
                        features=active_sub.plan.features
                    ),
                    current_period_start=active_sub.current_period_start,
                    current_period_end=active_sub.current_period_end
                )
                print(f"   ✓ Subscription: {active_sub.plan.name}")
        
        # 4. Get ALL resume sessions (not just for this user initially, for debugging)
        from database import WorkflowSession, Application, InterviewSession
        
        # Debug: Check total resume sessions in database
        total_resumes = db.query(ResumeSession).count()
        print(f"   📄 Total resume sessions in DB: {total_resumes}")
        
        # Get resumes for this user OR resumes with no user_id (legacy data)
        resumes = db.query(ResumeSession).filter(
            (ResumeSession.user_id == x_user_id) | (ResumeSession.user_id == None)
        ).order_by(ResumeSession.created_at.desc()).all()
        
        print(f"   📄 Resume sessions found for user {x_user_id}: {len(resumes)}")
        
        if len(resumes) == 0:
            print(f"   ⚠️  No resumes found. Checking if any workflows exist without user_id...")
            # Check for orphaned workflows
            orphaned_workflows = db.query(WorkflowSession).filter(
                WorkflowSession.user_id == None
            ).count()
            print(f"   ⚠️  Found {orphaned_workflows} workflows with no user_id")
        
        dashboard_resumes = []
        
        for resume in resumes:
            print(f"   📝 Processing resume: {resume.id} ({resume.filename})")
            
            # Get workflows for this resume - check both with user_id and without
            workflows = db.query(WorkflowSession).filter(
                WorkflowSession.resume_session_id == resume.id
            ).order_by(WorkflowSession.created_at.desc()).all()
            
            print(f"      → Found {len(workflows)} workflows for resume {resume.id}")
            
            dashboard_workflows = []
            
            for wf in workflows:
                print(f"         • Workflow {wf.id}: status={wf.status}, url={wf.scholarship_url[:50] if wf.scholarship_url else 'None'}...")
                
                # Get applications for this workflow
                app = db.query(Application).filter(
                    Application.workflow_session_id == wf.id
                ).first()
                
                dash_apps = []
                if app:
                    print(f"            → Application found: {app.id}")
                    dash_apps.append(DashboardApplication(
                        id=app.id,
                        session_id=app.workflow_session_id,
                        scholarship_url=app.scholarship_url,
                        status=app.status,
                        match_score=app.match_score,
                        had_interview=app.had_interview,
                        created_at=app.created_at
                    ))
                else:
                    print(f"            → No application found")
                
                # Get interview for this workflow
                interview = db.query(InterviewSession).filter(
                    InterviewSession.workflow_session_id == wf.id
                ).first()
                
                dash_interview = None
                if interview:
                    print(f"            → Interview found: {interview.id}")
                    dash_interview = DashboardInterview(
                        id=interview.id,
                        current_target=interview.current_target,
                        created_at=interview.created_at,
                        completed_at=interview.completed_at
                    )
                else:
                    print(f"            → No interview found")
                
                dashboard_workflows.append(DashboardWorkflow(
                    id=wf.id,
                    scholarship_url=wf.scholarship_url,
                    status=wf.status,
                    match_score=wf.match_score,
                    created_at=wf.created_at,
                    updated_at=wf.updated_at,
                    completed_at=wf.completed_at,
                    applications=dash_apps,
                    interview_session=dash_interview
                ))
            
            dashboard_resumes.append(DashboardResume(
                id=resume.id,
                filename=resume.filename,
                file_size_bytes=resume.file_size_bytes,
                created_at=resume.created_at,
                text_preview=resume.text_preview,
                workflow_sessions=dashboard_workflows
            ))
        
        print(f"   ✓ Built {len(dashboard_resumes)} resume items with workflows")
            
        # 5. Get Usage Stats
        usage_stats = UsageRecordOperations.get_stats(db, x_user_id)
        print(f"   ✓ Usage stats: {usage_stats}")
        
        # 6. Get Recent Activity
        activity_items = []
        
        # Add recent transactions
        transactions = WalletTransactionOperations.get_recent(db, x_user_id, limit=5)
        for tx in transactions:
            desc_text = f"{tx.kind.capitalize()} transaction"
            if tx.kind == 'deduction':
                desc_text = f"Used tokens for {tx.reference_id or 'service'}"
            elif tx.kind == 'purchase':
                desc_text = "Purchased tokens"
                
            activity_items.append(ActivityItem(
                type=f"transaction_{tx.kind}",
                ref_id=tx.id,
                description=desc_text,
                timestamp=tx.created_at,
                amount=tx.amount
            ))
        
        # Add recent completed workflows - again check with or without user_id
        recent_workflows = db.query(WorkflowSession).filter(
            (WorkflowSession.user_id == x_user_id) | (WorkflowSession.user_id == None),
            WorkflowSession.status == "complete"
        ).order_by(WorkflowSession.updated_at.desc()).limit(5).all()
        
        for wf in recent_workflows:
            activity_items.append(ActivityItem(
                type="workflow_completed",
                ref_id=wf.id,
                description=f"Completed workflow for scholarship",
                timestamp=wf.completed_at or wf.updated_at
            ))
        
        # Sort combined activity by timestamp desc
        activity_items.sort(key=lambda x: x.timestamp, reverse=True)
        activity_items = activity_items[:10]  # Keep top 10
        
        print(f"   ✓ Built {len(activity_items)} activity items")
        print(f"✅ [API] Dashboard data prepared successfully")
        
        return DashboardResponse(
            user=UserInfo(id=user.id, email=user.email),
            wallet=wallet_info,
            subscription=sub_info,
            resume_sessions=dashboard_resumes,
            usage=UsageStats(**usage_stats),
            recent_activity=activity_items
        )
        
    except Exception as e:
        print(f"❌ [API] Error fetching dashboard data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard data: {str(e)}"
        )


# ==================== Scout Workflow Endpoints ====================

@app.post("/api/scout/start")
async def start_scout_workflow(
    background_tasks: BackgroundTasks,
    scholarship_url: str = Form(...),
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    """Start Scout agent workflow"""
    session_id = str(uuid.uuid4())
    
    # Create workflow session in database
    WorkflowSessionOperations.create(
        db=db,
        session_id=session_id,
        scholarship_url=scholarship_url,
        user_id=x_user_id
    )
    
    async def run_scout_background():
        db_session = next(db_manager.get_session())
        try:
            print(f"[Scout] Starting for session {session_id}")
            scout = ScoutAgent()
            result = await scout.run(scholarship_url, debug=False)
            
            WorkflowSessionOperations.update_status(db_session, session_id, "complete")
            WorkflowSessionOperations.update_results(db_session, session_id, {"scout_result": result})
            
            print(f"[Scout] Completed for session {session_id}")
        except Exception as e:
            print(f"[Scout] Error: {e}")
            WorkflowSessionOperations.update_status(db_session, session_id, "error", str(e))
        finally:
            db_session.close()
    
    background_tasks.add_task(run_scout_background)
    
    return {
        "session_id": session_id,
        "status": "processing",
        "message": "Scout workflow started"
    }


@app.get("/api/scout/status/{session_id}")
async def get_scout_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Check Scout workflow status"""
    workflow = WorkflowSessionOperations.get(db, session_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = None
    if workflow.status == "complete":
        result = {"scout_result": workflow.matchmaker_results}
    
    return {
        "session_id": session_id,
        "status": workflow.status,
        "result": result,
        "error": workflow.error_message
    }


# ==================== Full Workflow Endpoints ====================

@app.post("/api/workflow/start")
async def start_workflow(
    background_tasks: BackgroundTasks,
    scholarship_url: str = Form(...),
    resume_session_id: str = Form(...),
    resume_file: Optional[UploadFile] = File(None),
    resume_path: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    """Start the full ScholarFit AI workflow"""
    
    # SANITIZE user_id to prevent string "null" issues
    raw_user_id = x_user_id
    x_user_id = sanitize_user_id(x_user_id)
    
    print(f"🚀 [WORKFLOW] Raw header x_user_id: {repr(raw_user_id)}")
    print(f"🚀 [WORKFLOW] Sanitized user_id: {repr(x_user_id)}")
    
    if workflow_orchestrator is None:
        raise HTTPException(status_code=503, detail="Workflow system not initialized")
    
    # Check user has sufficient tokens
    WORKFLOW_TOKEN_COST = 50  # Cost to run a workflow
    
    if x_user_id:
        from database import UserWallet, WalletTransaction, UsageRecord
        
        user = UserOperations.create_if_not_exists(db, x_user_id)
        wallet = db.query(UserWallet).filter(UserWallet.user_id == x_user_id).first()
        
        if not wallet or wallet.balance_tokens < WORKFLOW_TOKEN_COST:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient tokens. Required: {WORKFLOW_TOKEN_COST}, Available: {wallet.balance_tokens if wallet else 0}"
            )
        
        # Deduct tokens IMMEDIATELY and commit
        old_balance = wallet.balance_tokens
        wallet.balance_tokens -= WORKFLOW_TOKEN_COST
        wallet.updated_at = datetime.utcnow()
        
        # Create transaction record
        transaction = WalletTransaction(
            user_id=x_user_id,
            amount=-WORKFLOW_TOKEN_COST,
            balance_after=wallet.balance_tokens,
            kind='deduction',
            reference_id=None,  # Will update with workflow_session_id after creation
            metadata_json={'resource_type': 'workflow', 'scholarship_url': scholarship_url}
        )
        db.add(transaction)
        
        # CRITICAL: Commit the wallet deduction BEFORE starting background task
        db.commit()
        
        print(f"💰 [Workflow] Deducted {WORKFLOW_TOKEN_COST} tokens from user {x_user_id}. Balance: {old_balance} → {wallet.balance_tokens}")
    else:
        transaction = None
    
    # Handle resume source
    target_resume_path = resume_path
    
    if resume_file:
        temp_filename = f"{uuid.uuid4()}_{resume_file.filename}"
        temp_path = UPLOADS_DIR / temp_filename
        content = await resume_file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        target_resume_path = str(temp_path)
    
    if not target_resume_path and not resume_session_id:
        raise HTTPException(status_code=400, detail="Must provide resume source")
    
    if not target_resume_path:
        target_resume_path = "session_based"
    
    workflow_session_id = str(uuid.uuid4())
    
    # Create workflow session in database
    WorkflowSessionOperations.create(
        db=db,
        session_id=workflow_session_id,
        scholarship_url=scholarship_url,
        resume_session_id=resume_session_id,
        user_id=x_user_id
    )
    
    # Update transaction reference_id and create usage record
    if x_user_id and transaction:
        transaction.reference_id = workflow_session_id
        
        # Record usage
        usage = UsageRecord(
            user_id=x_user_id,
            resource_type='workflow',
            resource_id=workflow_session_id,
            tokens_used=WORKFLOW_TOKEN_COST,
            metadata_json={'scholarship_url': scholarship_url}
        )
        db.add(usage)
        
        db.commit()
    
    async def run_workflow_background():
        db_session = next(db_manager.get_session())
        try:
            print(f"[Workflow] Starting {workflow_session_id}")
            
            final_state = await workflow_orchestrator.run(
                scholarship_url=scholarship_url,
                resume_pdf_path=target_resume_path,
                session_id=resume_session_id
            )
            
            # Check for pause point
            if final_state.get("matchmaker_results") and not final_state.get("essay_draft"):
                WorkflowSessionOperations.update_status(db_session, workflow_session_id, "waiting_for_input")
                WorkflowSessionOperations.update_checkpoint(db_session, workflow_session_id, final_state)
                WorkflowSessionOperations.update_results(db_session, workflow_session_id, {
                    "matchmaker_results": final_state.get("matchmaker_results"),
                    "gaps": final_state.get("identified_gaps"),
                    "scholarship_intelligence": final_state.get("scholarship_intelligence")
                })
            else:
                # Complete workflow
                results = {
                    "matchmaker_results": final_state.get("matchmaker_results"),
                    "essay_draft": final_state.get("essay_draft"),
                    "strategy_note": final_state.get("strategy_note"),
                    "match_score": final_state.get("match_score"),
                    "gaps": final_state.get("identified_gaps"),
                    "scholarship_intelligence": final_state.get("scholarship_intelligence")
                }
                
                WorkflowSessionOperations.complete(db_session, workflow_session_id, results)
                
                # Track application
                ApplicationOperations.create(
                    db=db_session,
                    workflow_session_id=workflow_session_id,
                    resume_session_id=resume_session_id,
                    scholarship_url=scholarship_url,
                    match_score=final_state.get("match_score"),
                    had_interview=False,
                    user_id=x_user_id
                )
            
            print(f"[Workflow] Completed {workflow_session_id}")
            
        except Exception as e:
            print(f"[Workflow] Error: {e}")
            WorkflowSessionOperations.update_status(db_session, workflow_session_id, "error", str(e))
            
            # REFUND TOKENS ON ERROR
            if x_user_id:
                try:
                    refund_session = next(db_manager.get_session())
                    wallet_refund = refund_session.query(UserWallet).filter(
                        UserWallet.user_id == x_user_id
                    ).first()
                    
                    if wallet_refund:
                        wallet_refund.balance_tokens += WORKFLOW_TOKEN_COST
                        wallet_refund.updated_at = datetime.utcnow()
                        
                        # Create refund transaction
                        refund_tx = WalletTransaction(
                            user_id=x_user_id,
                            amount=WORKFLOW_TOKEN_COST,
                            balance_after=wallet_refund.balance_tokens,
                            kind='grant',
                            reference_id=workflow_session_id,
                            metadata_json={
                                'resource_type': 'workflow_refund',
                                'reason': 'workflow_error',
                                'error': str(e)[:200]
                            }
                        )
                        refund_session.add(refund_tx)
                        refund_session.commit()
                        print(f"💰 [Workflow] Refunded {WORKFLOW_TOKEN_COST} tokens to user {x_user_id}")
                    
                    refund_session.close()
                except Exception as refund_error:
                    print(f"❌ [Workflow] Failed to refund tokens: {refund_error}")
            
        finally:
            db_session.close()
    
    background_tasks.add_task(run_workflow_background)
    
    return {
        "session_id": workflow_session_id,
        "status": "processing",
        "message": "Workflow started"
    }


@app.post("/api/workflow/resume")
async def resume_workflow(
    background_tasks: BackgroundTasks,
    session_id: str = Form(...),
    bridge_story: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    """Resume workflow after interview"""
    
    workflow = WorkflowSessionOperations.get(db, session_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if workflow.status != "waiting_for_input":
        raise HTTPException(status_code=400, detail=f"Invalid status: {workflow.status}")
    
    WorkflowSessionOperations.update_status(db, session_id, "processing_resume")
    
    async def run_resume_background():
        db_session = next(db_manager.get_session())
        try:
            print(f"[Workflow] Resuming {session_id}")
            
            final_state = await workflow_orchestrator.resume_after_interview(
                bridge_story=bridge_story,
                checkpoint_state=workflow.state_checkpoint
            )
            
            results = {
                "matchmaker_results": final_state.get("matchmaker_results"),
                "essay_draft": final_state.get("essay_draft"),
                "resume_optimizations": final_state.get("resume_optimizations"),
                "optimized_resume_markdown": final_state.get("resume_markdown"),
                "strategy_note": final_state.get("strategy_note"),
                "match_score": final_state.get("match_score"),
                "gaps": final_state.get("identified_gaps")
            }
            
            WorkflowSessionOperations.complete(db_session, session_id, results)
            
            # Track application with interview
            ApplicationOperations.create(
                db=db_session,
                workflow_session_id=session_id,
                resume_session_id=workflow.resume_session_id,
                scholarship_url=workflow.scholarship_url,
                match_score=final_state.get("match_score"),
                had_interview=True,
                user_id=x_user_id
            )
            
            print(f"[Workflow] Completed resume {session_id}")
            
        except Exception as e:
            print(f"[Workflow] Error: {e}")
            WorkflowSessionOperations.update_status(db_session, session_id, "error", str(e))
        finally:
            db_session.close()
    
    background_tasks.add_task(run_resume_background)
    
    return {
        "session_id": session_id,
        "status": "processing_resume",
        "message": "Workflow resumed"
    }


@app.get("/api/workflow/status/{session_id}")
async def get_workflow_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get workflow status"""
    
    workflow = WorkflowSessionOperations.get(db, session_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = None
    if workflow.status in ["complete", "waiting_for_input"]:
        result = {
            "matchmaker_results": workflow.matchmaker_results,
            "essay_draft": workflow.essay_draft,
            "resume_optimizations": workflow.resume_optimizations,
            "optimized_resume_markdown": workflow.optimized_resume_markdown,
            "strategy_note": workflow.strategy_note,
            "match_score": workflow.match_score,
            "gaps": workflow.gaps,
            "scholarship_intelligence": workflow.scholarship_intelligence
        }
    
    return {
        "session_id": session_id,
        "status": workflow.status,
        "result": result,
        "error": workflow.error_message
    }


# ==================== Interview Endpoints ====================

@app.post("/api/interview/start")
async def start_interview_session(
    session_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Initialize interview session"""
    
    workflow = WorkflowSessionOperations.get(db, session_id)
    
    if not workflow or workflow.status != "waiting_for_input":
        raise HTTPException(status_code=400, detail="Workflow not ready for interview")
    
    gaps = workflow.gaps or []
    matchmaker_results = workflow.matchmaker_results or {}
    weighted_keywords = matchmaker_results.get("weighted_values", {})
    
    if not gaps:
        raise HTTPException(status_code=400, detail="No gaps detected")
    
    # Get resume text from state
    state = workflow.state_checkpoint or {}
    resume_text = state.get("resume_text", "")
    
    llm_client = create_llm_client()
    interview_manager = InterviewManager(llm_client, vector_store)
    
    try:
        session_data = await interview_manager.start_session(
            gaps=gaps,
            weighted_keywords=weighted_keywords,
            resume_text=resume_text,
            matchmaker_evidence=matchmaker_results.get("evidence", {})
        )
        
        interview_id = str(uuid.uuid4())
        
        # Store in database
        InterviewSessionOperations.create(
            db=db,
            interview_id=interview_id,
            workflow_session_id=session_id,
            gaps=gaps,
            weighted_keywords=weighted_keywords,
            gap_confidences=session_data["gap_confidences"],
            prioritized_gaps=session_data["prioritized_gaps"],
            current_target=session_data["target_gap"]
        )
        
        return {
            "interview_id": interview_id,
            "gaps": [
                {
                    "keyword": gap,
                    "weight": weighted_keywords.get(gap, 0.0),
                    "current_confidence": 0.0,
                    "status": "not_started"
                }
                for gap in gaps
            ],
            "weighted_keywords": weighted_keywords,
            "first_question": session_data["first_question"],
            "target_gap": session_data["target_gap"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting interview: {str(e)}")


@app.post("/api/interview/message")
async def process_interview_message(
    interview_id: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process interview message"""
    
    interview = InterviewSessionOperations.get(db, interview_id)
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Add user message
    InterviewSessionOperations.add_message(db, interview_id, "user", message)
    
    llm_client = create_llm_client()
    interview_manager = InterviewManager(llm_client, vector_store)
    
    try:
        result = await interview_manager.process_answer(
            answer=message,
            target_gap=interview.current_target,
            current_confidence=interview.gap_confidences[interview.current_target],
            gap_weight=interview.weighted_keywords.get(interview.current_target, 0.0),
            conversation_history=interview.conversation_history,
            all_gaps=interview.gaps,
            gap_confidences=interview.gap_confidences,
            weighted_keywords=interview.weighted_keywords
        )
        
        # Update confidences
        new_confidences = interview.gap_confidences.copy()
        new_confidences[interview.current_target] = result["confidence_update"]
        
        new_target = result["next_target"] or interview.current_target
        
        InterviewSessionOperations.update_confidences(db, interview_id, new_confidences, new_target)
        
        # Store evidence
        InterviewSessionOperations.add_evidence(
            db, interview_id, interview.current_target, result["evidence_extracted"]
        )
        
        # Add AI response
        InterviewSessionOperations.add_message(db, interview_id, "assistant", result["response"])
        
        # Build gap updates
        gap_updates = {}
        for gap in interview.gaps:
            conf = new_confidences[gap]
            gap_updates[gap] = {
                "confidence": conf,
                "status": result["gap_status"][gap]
            }
        
        return {
            "response": result["response"],
            "gap_updates": gap_updates,
            "keyword_alignment": new_confidences,
            "is_complete": result["is_complete"],
            "next_target": result["next_target"] or interview.current_target
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.post("/api/interview/complete")
async def complete_interview(
    interview_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Complete interview and synthesize bridge story"""
    
    interview = InterviewSessionOperations.get(db, interview_id)
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    llm_client = create_llm_client()
    interview_manager = InterviewManager(llm_client, vector_store)
    
    try:
        bridge_story = await interview_manager.synthesize_bridge_story(
            conversation_history=interview.conversation_history,
            gaps_addressed=interview.gap_confidences,
            weighted_keywords=interview.weighted_keywords
        )
        
        # Store bridge story
        InterviewSessionOperations.complete(db, interview_id, bridge_story)
        
        return {
            "bridge_story": bridge_story,
            "final_alignment": interview.gap_confidences,
            "ready_for_generation": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing interview: {str(e)}")


# ==================== Outreach Endpoints ====================

class GenerateOutreachRequest(BaseModel):
    session_id: str


@app.post("/api/outreach/generate")
async def generate_outreach_email(
    request: GenerateOutreachRequest,
    db: Session = Depends(get_db)
):
    """Generate outreach email"""
    
    workflow = WorkflowSessionOperations.get(db, request.session_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not workflow.scholarship_intelligence:
        raise HTTPException(
            status_code=400, 
            detail=f"Scholarship intelligence not available. Workflow status: {workflow.status}. Please ensure the workflow has completed the scout phase."
        )
    
    intelligence = workflow.scholarship_intelligence or {}
    official = intelligence.get("official", {})
    
    scholarship_name = official.get("scholarship_name", "Scholarship")
    organization = official.get("organization", "Organization")
    contact_email = official.get("contact_email")
    contact_name = official.get("contact_name")
    
    gaps = workflow.gaps or []
    
    # Get resume text from state
    state = workflow.state_checkpoint or {}
    resume_text = state.get("resume_text", "")
    
    try:
        llm_client = create_llm_client()
        ghostwriter = GhostwriterAgent(llm_client)
        
        email_draft = await ghostwriter.draft_outreach_email(
            scholarship_name=scholarship_name,
            organization=organization,
            contact_name=contact_name,
            gaps=gaps,
            student_context=resume_text
        )
        
        return {
            "subject": email_draft.get("subject"),
            "body": email_draft.get("body"),
            "contact_email": contact_email,
            "contact_name": contact_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating email: {str(e)}")


# ==================== Error Handlers ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "details": str(exc)
        }
    )



# ==================== Stripe/Billing Endpoints ====================

@app.get("/api/billing/plans")
async def get_billing_plans(db: Session = Depends(get_db)):
    """Get available billing plans"""
    try:
        from database import BillingPlan
        
        plans = db.query(BillingPlan).all()
        
        return {
            "plans": [
                {
                    "id": plan.id,
                    "slug": plan.slug,
                    "name": plan.name,
                    "price_cents": plan.price_cents,
                    "interval": plan.interval,
                    "tokens_per_period": plan.tokens_per_period,
                    "features": plan.features
                }
                for plan in plans
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching billing plans: {str(e)}"
        )


@app.post("/api/stripe/create-checkout-session")
async def create_checkout_session(
    plan_slug: str = Form(...),
    success_url: str = Form(...),
    cancel_url: str = Form(...),
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    """Create a Stripe checkout session"""
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )
    
    try:
        # Validate plan slug exists in database (prevent scam attempts)
        _validate_plan_slug(db, plan_slug)
        
        from services.stripe_service import StripeService
        
        session_data = StripeService.create_checkout_session(
            db=db,
            user_id=x_user_id,
            plan_slug=plan_slug,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return session_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating checkout session: {str(e)}"
        )


@app.post("/api/stripe/create-portal-session")
async def create_portal_session(
    return_url: str = Form(...),
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    """Create a Stripe customer portal session"""
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )
    
    try:
        from services.stripe_service import StripeService
        
        portal_url = StripeService.create_portal_session(
            db=db,
            user_id=x_user_id,
            return_url=return_url
        )
        
        return {"url": portal_url}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating portal session: {str(e)}"
        )


@app.post("/api/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    if not sig_header:
        print(f"❌ [Webhook] Missing stripe-signature header")
        print(f"   Available headers: {list(request.headers.keys())}")
        print(f"   Payload size: {len(payload)} bytes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header. Use Stripe CLI for local testing: stripe listen --forward-to localhost:8000/api/stripe/webhook"
        )
    
    try:
        from services.stripe_service import StripeService
        
        print(f"✓ [Webhook] Processing event with signature")
        result = StripeService.handle_webhook_event(
            db=db,
            payload=payload,
            sig_header=sig_header
        )
        
        return result
    except ValueError as e:
        print(f"❌ [Webhook] ValueError: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"❌ [Webhook] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing error: {str(e)}"
        )


@app.post("/api/subscription/cancel")
async def cancel_subscription(
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    """Cancel user's subscription"""
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )
    
    try:
        from database import Subscription
        import stripe
        
        # Get active subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == x_user_id,
            Subscription.status == 'active'
        ).first()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        # Cancel at period end in Stripe
        stripe.Subscription.modify(
            subscription.external_subscription_id,
            cancel_at_period_end=True
        )
        
        subscription.cancel_at_period_end = True
        db.commit()
        
        return {"status": "canceled", "message": "Subscription will be canceled at the end of the period"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error canceling subscription: {str(e)}"
        )


@app.get("/api/billing/details", response_model=BillingDetailsResponse)
async def get_billing_details(
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None)
):
    """Get comprehensive billing and subscription details"""
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )
        
    try:
        from database import Subscription, SubscriptionPayment, BillingPlan
        
        # 1. Get User & Wallet
        user = UserOperations.create_if_not_exists(db, x_user_id)
        
        wallet_info = None
        if user.wallet:
            wallet_info = WalletInfo(
                balance_tokens=user.wallet.balance_tokens,
                currency=user.wallet.currency,
                last_updated=user.wallet.updated_at
            )
            
        # 2. Get Subscription Info
        sub_info = None
        active_sub = None
        if user.subscriptions:
            active_sub = next((s for s in user.subscriptions if s.status == "active"), None)
            if active_sub and active_sub.plan:
                sub_info = SubscriptionInfo(
                    status=active_sub.status,
                    plan=PlanInfo(
                        name=active_sub.plan.name,
                        interval=active_sub.plan.interval,
                        price_cents=active_sub.plan.price_cents,
                        tokens_per_period=active_sub.plan.tokens_per_period,
                        features=active_sub.plan.features
                    ),
                    current_period_start=active_sub.current_period_start,
                    current_period_end=active_sub.current_period_end
                )
                
        # 3. Get Payment History (from SubscriptionPayment)
        payments = []
        if user.subscriptions:
            for sub in user.subscriptions:
                sub_payments = db.query(SubscriptionPayment).filter(
                    SubscriptionPayment.subscription_id == sub.id
                ).order_by(SubscriptionPayment.created_at.desc()).limit(20).all()
                
                for p in sub_payments:
                    # Get plan name for better description
                    plan_name = sub.plan.name if sub.plan else "Subscription"
                    status_emoji = "✓" if p.status == "succeeded" else "✗"
                    
                    description = f"{status_emoji} {plan_name} - {p.status.capitalize()}"
                    if p.status == "succeeded":
                        description = f"Payment for {plan_name} subscription"
                    elif p.status == "failed":
                        description = f"Failed payment for {plan_name}"
                    
                    payments.append(PaymentHistoryItem(
                        id=p.id,
                        amount_cents=p.amount_cents,
                        currency=p.currency,
                        status=p.status,
                        date=p.created_at,
                        description=description
                    ))
        
        # Sort payments by date desc and limit
        payments.sort(key=lambda x: x.date, reverse=True)
        payments = payments[:20]
        
        # 4. Get Transaction History (from WalletTransaction)
        transactions = WalletTransactionOperations.get_recent(db, x_user_id, limit=30)
        tx_history = []
        for tx in transactions:
            tx_type = 'credit' if tx.kind in ['grant', 'purchase', 'bonus'] else 'debit'
            
            # Enhanced descriptions based on transaction kind and metadata
            desc = f"{tx.kind.capitalize()}"
            if tx.kind == 'deduction':
                # Try to get more context from metadata
                if tx.metadata_json and 'resource_type' in tx.metadata_json:
                    desc = f"Used for {tx.metadata_json['resource_type']}"
                else:
                    desc = f"Token usage - {tx.reference_id or 'service'}"
            elif tx.kind == 'grant':
                if tx.metadata_json and 'source' in tx.metadata_json:
                    source = tx.metadata_json['source']
                    if source == 'subscription_start':
                        desc = f"Welcome bonus - {tx.metadata_json.get('plan', 'Subscription')}"
                    elif source == 'subscription_renewal':
                        desc = f"Monthly allowance - {tx.metadata_json.get('plan', 'Subscription')}"
                    else:
                        desc = "Token grant"
                else:
                    desc = "Token grant"
            elif tx.kind == 'purchase':
                desc = "Token purchase"
            elif tx.kind == 'bonus':
                desc = "Bonus tokens"
                
            tx_history.append(TransactionHistoryItem(
                id=tx.id,
                amount=abs(tx.amount),  # Show absolute value
                type=tx_type,
                balance_after=tx.balance_after,
                description=desc,
                date=tx.created_at
            ))
            
        # 5. Get Usage History (from UsageRecord)
        usage_records = UsageRecordOperations.get_recent(db, x_user_id, limit=30)
        usage_history = []
        for rec in usage_records:
            # Map resource_type to user-friendly feature names
            feature_display = rec.resource_type
            if rec.resource_type == 'workflow':
                feature_display = 'Scholarship Application'
            elif rec.resource_type == 'interview':
                feature_display = 'Interview Session'
            elif rec.resource_type == 'resume_upload':
                feature_display = 'Resume Processing'
            elif rec.resource_type == 'essay_generation':
                feature_display = 'Essay Generation'
            
            usage_history.append(UsageHistoryItem(
                id=rec.id,
                feature=feature_display,
                amount=rec.tokens_used,
                cost_cents=rec.cost_cents,
                date=rec.created_at
            ))
            
        return BillingDetailsResponse(
            subscription=sub_info,
            wallet=wallet_info,
            payment_history=payments,
            transaction_history=tx_history,
            usage_history=usage_history
        )
        
    except Exception as e:
        print(f"Error fetching billing details: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching billing details: {str(e)}"
        )


# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )