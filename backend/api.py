"""
FastAPI server for ScholarFit AI backend
Handles resume upload, processing, and ChromaDB integration with PostgreSQL storage
"""

import os
from datetime import datetime
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, File, UploadFile, HTTPException, status, Form, BackgroundTasks, Depends, Header
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
from workflows.database import DatabaseManager
from workflows.db_operations import (
    WorkflowSessionOperations,
    ResumeSessionOperations,
    InterviewSessionOperations,
    ApplicationOperations
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


class DashboardResponse(BaseModel):
    """Dashboard data response model"""
    user_id: Optional[str]
    stats: Dict[str, Any]
    applications: List[Dict[str, Any]]
    resumes: List[Dict[str, Any]]
    active_workflows: List[Dict[str, Any]]


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
    
    if vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not initialized"
        )
    
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
    print(f"🆔 [API] Generated session_id: {session_id} for resume upload")
    
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
        
        # Store resume session in database
        text_preview = result.get("resume_text", "")[:500] if result.get("resume_text") else None
        resume_session = ResumeSessionOperations.create(
            db=db,
            session_id=session_id,
            filename=file.filename,
            file_size_bytes=file_size,
            chunks_stored=result.get("chunks_stored", 0),
            text_preview=text_preview,
            user_id=x_user_id
        )
        
        print(f"✓ [API] Resume processed and stored in DB for session: {session_id}")
        
        return UploadResponse(
            success=True,
            message="Resume processed successfully",
            chunks_stored=result.get("chunks_stored", 0),
            metadata={
                "session_id": session_id,
                "filename": file.filename,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / 1024 / 1024, 2),
                "text_preview": text_preview
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
        print(f"📊 [API] Fetching dashboard data for user: {x_user_id}")
        
        # 1. Get Applications
        applications = ApplicationOperations.get_all(db, user_id=x_user_id)
        app_list = [
            {
                "id": app.id,
                "workflow_session_id": app.workflow_session_id,
                "scholarship_url": app.scholarship_url,
                "status": app.status,
                "match_score": app.match_score,
                "had_interview": app.had_interview,
                "created_at": app.created_at.isoformat()
            }
            for app in applications
        ]
        
        # 2. Get Resumes
        resumes = ResumeSessionOperations.get_all(db, user_id=x_user_id)
        resume_list = [
            {
                "id": resume.id,
                "filename": resume.filename,
                "created_at": resume.created_at.isoformat(),
                "file_size_bytes": resume.file_size_bytes
            }
            for resume in resumes
        ]
        
        # 3. Get Active Workflows (processing or waiting_for_input)
        # We fetch all and filter in memory for simplicity, or could add specific DB query
        all_workflows = WorkflowSessionOperations.get_all(db, user_id=x_user_id)
        active_workflows = [
            {
                "id": wf.id,
                "status": wf.status,
                "scholarship_url": wf.scholarship_url,
                "created_at": wf.created_at.isoformat(),
                "updated_at": wf.updated_at.isoformat() if wf.updated_at else None
            }
            for wf in all_workflows
            if wf.status in ["processing", "waiting_for_input", "processing_resume"]
        ]
        
        # 4. Calculate Stats
        total_apps = len(app_list)
        total_interviews = sum(1 for app in app_list if app.get("had_interview"))
        avg_score = 0
        if total_apps > 0:
            scores = [app.get("match_score") for app in app_list if app.get("match_score") is not None]
            if scores:
                avg_score = sum(scores) / len(scores)
        
        return DashboardResponse(
            user_id=x_user_id,
            stats={
                "total_applications": total_apps,
                "total_interviews": total_interviews,
                "average_match_score": round(avg_score, 1),
                "active_workflows_count": len(active_workflows)
            },
            applications=app_list,
            resumes=resume_list,
            active_workflows=active_workflows
        )
        
    except Exception as e:
        print(f"❌ [API] Error fetching dashboard data: {e}")
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
    
    if workflow_orchestrator is None:
        raise HTTPException(status_code=503, detail="Workflow system not initialized")
    
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
                    "gaps": final_state.get("identified_gaps")
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
        raise HTTPException(status_code=400, detail="Workflow not complete")
    
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )