"""
FastAPI server for ScholarFit AI backend
Handles resume upload, processing, and ChromaDB integration
"""

import os
from datetime import datetime
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, File, UploadFile, HTTPException, status, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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


# ==================== Pydantic Models ====================

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    vector_store_ready: bool
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


# ==================== FastAPI Application ====================

app = FastAPI(
    title="ScholarFit AI API",
    description="Backend API for scholarship application optimization",
    version="1.0.0",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",  # Frontend dev server
        "http://localhost:3000",  # Alternative frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Global State ====================

# Vector store instance (initialized on startup)
vector_store: Optional[VectorStore] = None

# Workflow orchestrator
workflow_orchestrator: Optional[ScholarshipWorkflow] = None

# Uploads directory
UPLOADS_DIR = Path(__file__).parent / "uploads"

# Session storage for Scout workflows (in-memory)
workflow_sessions: Dict[str, Dict[str, Any]] = {}

# Interview session storage (in-memory)
interview_sessions: Dict[str, Dict[str, Any]] = {}

# Application history storage (in-memory) - maps resume_session_id to list of applications
application_history: Dict[str, List[Dict[str, Any]]] = {}

UPLOADS_DIR.mkdir(exist_ok=True)


# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global vector_store
    
    try:
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
        
        # Initialize Workflow
        global workflow_orchestrator
        workflow_orchestrator = ScholarshipWorkflow(agents)
        print("✓ Workflow orchestrator ready")
        
    except Exception as e:
        print(f"✗ Error initializing services: {e}")
        # Continue anyway - will be caught in health check


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
async def health_check():
    """
    Health check endpoint
    Returns server status and vector store readiness
    """
    if vector_store is None:
        return HealthResponse(
            status="degraded",
            vector_store_ready=False,
            collection_stats=None
        )
    
    try:
        stats = vector_store.get_collection_stats()
        return HealthResponse(
            status="ok",
            vector_store_ready=True,
            collection_stats=stats
        )
    except Exception as e:
        return HealthResponse(
            status="degraded",
            vector_store_ready=False,
            collection_stats={"error": str(e)}
        )


@app.post("/api/upload-resume", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and process a resume PDF
    
    - Validates file type (PDF only)
    - Validates file size (max 5MB)
    - Processes PDF through ProfilerAgent
    - Stores chunks in ChromaDB
    - Cleans up temporary file
    """
    
    # Check vector store is ready
    if vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not initialized"
        )
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only PDF files are supported. Got: {file.filename}"
        )
    
    # Validate file size (5MB limit)
    MAX_SIZE = 5 * 1024 * 1024  # 5MB in bytes
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: 5MB. Got: {file_size / 1024 / 1024:.2f}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )
    
    # Save file temporarily
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = UPLOADS_DIR / temp_filename
    
    
    # Generate unique session ID for this resume
    session_id = str(uuid.uuid4())
    print(f"🆔 [API] Generated session_id: {session_id} for resume upload")
    
    try:
        # Write file to disk
        with open(temp_path, "wb") as f:
            f.write(file_content)
        
        # Optional: Clean up any old data for this session (if re-uploading)
        # This prevents accumulation if the same session_id is reused
        try:
            all_docs = vector_store.collection.get(
                where={"session_id": session_id}
            )
            if all_docs["ids"]:
                print(f"🗑️ [API] Cleaning {len(all_docs['ids'])} old chunks for session: {session_id}")
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
        
        print(f"✓ [API] Resume processed successfully for session: {session_id}")
        
        # Build response
        return UploadResponse(
            success=True,
            message="Resume processed successfully",
            chunks_stored=result.get("chunks_stored", 0),
            metadata={
                "session_id": session_id,  # Return to frontend
                "filename": file.filename,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / 1024 / 1024, 2),
                "text_preview": result.get("resume_text", "")[:200] + "..." 
                    if result.get("resume_text") else None
            }
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Catch any other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error processing resume: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_path.exists():
            temp_path.unlink()


@app.get("/api/resume-stats")
async def get_resume_stats():
    """
    Get ChromaDB collection statistics
    Returns document count and collection info
    """
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
        )


@app.delete("/api/resume")
async def clear_resume():
    """
    Clear all resume data from ChromaDB
    Useful for testing and resetting state
    """
    if vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not initialized"
        )
    
    try:
        # Get count before clearing
        stats_before = vector_store.get_collection_stats()
        count_before = stats_before.get("count", 0)
        
        # Clear collection
        vector_store.clear_collection()
        
        # Get count after
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
async def delete_session_data(session_id: str):
    """
    Delete resume data for a specific session
    
    Args:
        session_id: Session ID from resume upload
        
    Returns:
        Success status and number of documents deleted
    """
    if vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not initialized"
        )
    
    try:
        print(f"🗑️ [API] Deleting resume data for session: {session_id}")
        
        # Get all documents for this session
        all_docs = vector_store.collection.get(
            where={"session_id": session_id}
        )
        
        if not all_docs["ids"]:
            print(f"   ℹ️ No documents found for session: {session_id}")
            return {
                "success": True,
                "message": "No documents found for this session",
                "documents_deleted": 0,
                "session_id": session_id
            }
        
        # Delete the documents
        vector_store.delete_documents(all_docs["ids"])
        deleted_count = len(all_docs["ids"])
        
        print(f"   ✓ Deleted {deleted_count} documents for session: {session_id}")
        
        return {
            "success": True,
            "message": f"Session data deleted successfully",
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
async def validate_resume_session(session_id: str):
    """
    Validate that a resume session exists and has data
    
    Args:
        session_id: Session ID from resume upload
        
    Returns:
        Validation status, chunk count, and metadata
    """
    if vector_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector store not initialized"
        )
    
    try:
        print(f"✓ [API] Validating resume session: {session_id}")
        
        # Query for documents with this session_id
        all_docs = vector_store.collection.get(
            where={"session_id": session_id}
        )
        
        if not all_docs["ids"]:
            print(f"   ℹ️ No documents found for session: {session_id}")
            return {
                "valid": False,
                "session_id": session_id,
                "chunks_count": 0,
                "message": "No resume data found for this session"
            }
        
        # Session exists and has data
        chunks_count = len(all_docs["ids"])
        print(f"   ✓ Found {chunks_count} chunks for session: {session_id}")
        
        # Extract metadata from first chunk
        metadata = all_docs["metadatas"][0] if all_docs["metadatas"] else {}
        
        return {
            "valid": True,
            "session_id": session_id,
            "chunks_count": chunks_count,
            "metadata": metadata,
            "message": "Resume session is valid"
        }
    
    except Exception as e:
        print(f"   ❌ Error validating session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating session: {str(e)}"
        )


@app.get("/api/applications/history/{resume_session_id}")
async def get_application_history(resume_session_id: str):
    """
    Get all applications submitted for a resume session
    
    Args:
        resume_session_id: Resume session ID
        
    Returns:
        List of applications with basic info (workflow_session_id, scholarship_url, status, created_at)
    """
    try:
        print(f"📋 [API] Fetching application history for resume session: {resume_session_id}")
        
        # Get all applications for this resume session
        applications = application_history.get(resume_session_id, [])
        
        print(f"   ✓ Found {len(applications)} applications")
        
        return {
            "success": True,
            "resume_session_id": resume_session_id,
            "applications": applications,
            "count": len(applications)
        }
    
    except Exception as e:
        print(f"   ❌ Error fetching application history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching application history: {str(e)}"
        )


# ==================== Scout Workflow Endpoints ====================

@app.post("/api/scout/start")
async def start_scout_workflow(
    background_tasks: BackgroundTasks,
    scholarship_url: str = Form(...)
):
    """
    Start Scout agent workflow in background
    
    Args:
        scholarship_url: URL of scholarship to analyze
        
    Returns:
        session_id for polling status
    """
    from agents.scout import ScoutAgent
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Initialize session
    workflow_sessions[session_id] = {
        "session_id": session_id,
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
        "scholarship_url": scholarship_url,
        "result": None,
        "error": None
    }
    
    # Background task to run Scout
    async def run_scout_background():
        try:
            print(f"[Scout Background Task] Starting for session {session_id}")
            scout = ScoutAgent()
            result = await scout.run(scholarship_url, debug=False)
            
            workflow_sessions[session_id]["status"] = "complete"
            workflow_sessions[session_id]["result"] = result
            print(f"[Scout Background Task] Completed for session {session_id}")
            
        except Exception as e:
            print(f"[Scout Background Task] Error for session {session_id}: {e}")
            workflow_sessions[session_id]["status"] = "error"
            workflow_sessions[session_id]["error"] = str(e)
    
    # Add background task
    background_tasks.add_task(run_scout_background)
    
    return {
        "session_id": session_id,
        "status": "processing",
        "message": "Scout workflow started"
    }


@app.get("/api/scout/status/{session_id}")
async def get_scout_status(session_id: str):
    """
    Check Scout workflow status
    
    Args:
        session_id: Session ID from start_scout_workflow
        
    Returns:
        Current status and results (if complete)
    """
    if session_id not in workflow_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session = workflow_sessions[session_id]
    
    return {
        "session_id": session_id,
        "status": session["status"],
        "result": session.get("result"),
        "error": session.get("error")
    }


# ==================== Full Workflow Endpoints ====================

@app.post("/api/workflow/start")
async def start_workflow(
    background_tasks: BackgroundTasks,
    scholarship_url: str = Form(...),
    resume_session_id: str = Form(...),  # Session ID from resume upload
    resume_file: Optional[UploadFile] = File(None),
    resume_path: Optional[str] = Form(None)
):
    """
    Start the full ScholarFit AI workflow
    
    Args:
        scholarship_url: URL of scholarship
        resume_session_id: Session ID from resume upload (for vector DB filtering)
        resume_file: Uploaded PDF resume (optional)
        resume_path: Path to already uploaded resume (optional)
    """
    if workflow_orchestrator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Workflow system not initialized"
        )
        
    # Handle resume source
    target_resume_path = resume_path
    
    # If resume_file is provided, save it temporarily
    if resume_file:
        # Process uploaded file similar to upload_resume
        temp_filename = f"{uuid.uuid4()}_{resume_file.filename}"
        temp_path = UPLOADS_DIR / temp_filename
        content = await resume_file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        target_resume_path = str(temp_path)
    
    # For session-based workflow, we don't need resume_path
    # The resume was already uploaded and processed via /api/upload-resume
    # We just need the session_id to query the vector DB
    if not target_resume_path and not resume_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either resume_file, resume_path, or resume_session_id"
        )
    
    # Use a dummy path if we're using session-based approach
    if not target_resume_path:
        target_resume_path = "session_based"  # Placeholder - not actually used
        
    print(f"🆔 [API] Starting workflow with resume session: {resume_session_id}")
    
    # Generate workflow session ID (different from resume session_id)
    workflow_session_id = str(uuid.uuid4())
    
    # Initialize workflow session
    workflow_sessions[workflow_session_id] = {
        "session_id": workflow_session_id,
        "resume_session_id": resume_session_id,  # Track resume session
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
        "scholarship_url": scholarship_url,
        "result": None,
        "error": None,
        "state": None  # To store intermediate state
    }
    
    # Background task wrapper
    async def run_workflow_background():
        try:
            print(f"[Workflow Task] Starting for workflow session {workflow_session_id}")
            print(f"[Workflow Task] Using resume session: {resume_session_id}")
            
            # Get scholarship URL from session (avoid closure issues)
            session_scholarship_url = workflow_sessions[workflow_session_id]["scholarship_url"]
            
            # Run workflow with resume session ID
            final_state = await workflow_orchestrator.run(
                scholarship_url=session_scholarship_url,
                resume_pdf_path=target_resume_path,
                session_id=resume_session_id  # Pass resume session for vector queries
            )
            
            # Check for interrupt (Matchmaker complete or Interview needed)
            # If we have matchmaker results but no essay, we are paused
            if final_state.get("matchmaker_results") and not final_state.get("essay_draft"):
                workflow_sessions[workflow_session_id]["status"] = "waiting_for_input"
                workflow_sessions[workflow_session_id]["result"] = {
                    "matchmaker_results": final_state.get("matchmaker_results"),
                    "context": "Review match results before proceeding",
                    # Include gaps if any for the frontend to decide on interview
                    "gaps": final_state.get("identified_gaps"),
                    "trigger_interview": final_state.get("trigger_interview")
                }
                workflow_sessions[workflow_session_id]["state"] = final_state
            else:
                workflow_sessions[workflow_session_id]["status"] = "complete"
                # Explicitly structure the result to match frontend expectations
                # and avoid sending the entire state (which can be huge)
                workflow_sessions[workflow_session_id]["result"] = {
                    "matchmaker_results": final_state.get("matchmaker_results"),
                    "essay_draft": final_state.get("essay_draft"),
                    "strategy_note": final_state.get("strategy_note"),
                    "match_score": final_state.get("match_score"),
                    "gaps": final_state.get("identified_gaps"),
                    "scholarship_intelligence": final_state.get("scholarship_intelligence"),
                    "resume_text": final_state.get("resume_text")
                }
                
                # Track completed application in history
                app_scholarship_url = workflow_sessions[workflow_session_id].get("scholarship_url", "Unknown")
                if resume_session_id not in application_history:
                    application_history[resume_session_id] = []
                
                application_history[resume_session_id].append({
                    "workflow_session_id": workflow_session_id,
                    "scholarship_url": app_scholarship_url,
                    "status": "complete",
                    "created_at": workflow_sessions[workflow_session_id].get("created_at"),
                    "match_score": final_state.get("match_score"),
                    "had_interview": False
                })
                print(f"[Workflow Task] Added application to history for resume session {resume_session_id}")
                
            print(f"[Workflow Task] Finished step for workflow session {workflow_session_id}")
            
        except Exception as e:
            print(f"[Workflow Task] Error for workflow session {workflow_session_id}: {e}")
            workflow_sessions[workflow_session_id]["status"] = "error"
            workflow_sessions[workflow_session_id]["error"] = str(e)
            
    background_tasks.add_task(run_workflow_background)
    
    return {
        "session_id": workflow_session_id,
        "status": "processing",
        "message": "Scholarship workflow started"
    }


@app.post("/api/workflow/resume")
async def resume_workflow(
    background_tasks: BackgroundTasks,
    session_id: str = Form(...),
    bridge_story: Optional[str] = Form(None)
):
    """
    Resume workflow with student's bridge story (optional)
    """
    if workflow_orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
        
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session = workflow_sessions[session_id]
    if session["status"] != "waiting_for_input":
        raise HTTPException(status_code=400, detail=f"Session is not waiting for input (status: {session['status']})")
        
    # Update status
    session["status"] = "processing_resume"
    checkpoint_state = session["state"]
    
    async def run_resume_background():
        try:
            print(f"[Workflow Task] Resuming session {session_id}")
            
            final_state = await workflow_orchestrator.resume_after_interview(
                bridge_story=bridge_story,
                checkpoint_state=checkpoint_state
            )
            print(final_state.get("resume_markdown"))
            session["status"] = "complete"
            session["result"] = {
                "matchmaker_results": final_state.get("matchmaker_results"),
                "essay_draft": final_state.get("essay_draft"),
                "resume_optimizations": final_state.get("resume_optimizations"),
                "optimized_resume_markdown": final_state.get("resume_markdown"),  # Map resume_markdown to optimized_resume_markdown for frontend
                "strategy_note": final_state.get("strategy_note"),
                "match_score": final_state.get("match_score"),
                "gaps": final_state.get("identified_gaps"),
                "scholarship_intelligence": final_state.get("scholarship_intelligence"),
                "resume_text": final_state.get("resume_text")
            }
            
            # Track completed application with interview in history  
            resume_session_id = session.get("resume_session_id")
            app_scholarship_url = session.get("scholarship_url", "Unknown")
            if resume_session_id:
                if resume_session_id not in application_history:
                    application_history[resume_session_id] = []
                
                application_history[resume_session_id].append({
                    "workflow_session_id": session_id,
                    "scholarship_url": app_scholarship_url,
                    "status": "complete",
                    "created_at": session.get("created_at"),
                    "match_score": final_state.get("match_score"),
                    "had_interview": True
                })
                print(f"[Workflow Task] Added application with interview to history for resume session {resume_session_id}")
            
            print(f"[Workflow Task] Completed session {session_id}")
            
        except Exception as e:
            print(f"[Workflow Task] Error resuming session {session_id}: {e}")
            session["status"] = "error"
            session["error"] = str(e)
            
    background_tasks.add_task(run_resume_background)
    
    return {
        "session_id": session_id,
        "status": "processing_resume",
        "message": "Workflow resumed with bridge story"
    }


@app.get("/api/workflow/status/{session_id}")
async def get_workflow_status(session_id: str):
    """Get workflow status"""
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session = workflow_sessions[session_id]
    
    # Clean up state from response to avoid huge payload
    response = {
        "session_id": session_id,
        "status": session["status"],
        "result": session.get("result"),
        "error": session.get("error")
    }
    
    return response


@app.post("/api/interview/start")
async def start_interview_session(session_id: str = Form(...)):
    """
    Initialize multi-turn interview session
    
    Args:
        session_id: Workflow session ID from matchmaker
        
    Returns:
        interview_id, gaps with weights, first question
    """
    # Get workflow session
    if session_id not in workflow_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow session not found"
        )
    
    workflow_session = workflow_sessions[session_id]
    
    # Check if workflow has matchmaker results
    if workflow_session["status"] != "waiting_for_input":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow not ready for interview (status: {workflow_session['status']})"
        )
    
    result = workflow_session.get("result", {})
    matchmaker_results = result.get("matchmaker_results", {})
    
    if not matchmaker_results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Matchmaker results not available"
        )
    
    # Extract data
    gaps = matchmaker_results.get("gaps", [])
    weighted_keywords = matchmaker_results.get("weighted_values", {})
    
    if not gaps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No gaps detected - interview not needed"
        )
    
    # Get resume text from state
    state = workflow_session.get("state", {})
    resume_text = state.get("resume_text", "")
    
    # Initialize interview manager
    llm_client = create_llm_client()
    interview_manager = InterviewManager(llm_client, vector_store)
    
    # Start session
    try:
        session_data = await interview_manager.start_session(
            gaps=gaps,
            weighted_keywords=weighted_keywords,
            resume_text=resume_text,
            matchmaker_evidence=matchmaker_results.get("evidence", {})
        )
        
        # Create interview session
        interview_id = str(uuid.uuid4())
        interview_sessions[interview_id] = {
            "interview_id": interview_id,
            "session_id": session_id,
            "gaps": gaps,
            "weighted_keywords": weighted_keywords,
            "gap_confidences": session_data["gap_confidences"],
            "prioritized_gaps": session_data["prioritized_gaps"],
            "current_target": session_data["target_gap"],
            "conversation_history": [],
            "collected_evidence": {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Format response
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting interview: {str(e)}"
        )


# ==================== Outreach Endpoints ====================

class GenerateOutreachRequest(BaseModel):
    session_id: str


@app.post("/api/outreach/generate")
async def generate_outreach_email(request: GenerateOutreachRequest):
    """
    Generate an outreach email using session data
    """
    session_id = request.session_id
    
    if session_id not in workflow_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session = workflow_sessions[session_id]
    result_data = session.get("result", {})
    
    if not result_data:
        raise HTTPException(status_code=400, detail="Workflow not complete, no data available")
        
    # Extract data from session result
    intelligence = result_data.get("scholarship_intelligence", {})
    official = intelligence.get("official", {})
    
    scholarship_name = official.get("scholarship_name", "Scholarship")
    organization = official.get("organization", "Organization")
    contact_email = official.get("contact_email")
    contact_name = official.get("contact_name")
    
    gaps = result_data.get("gaps", [])
    resume_text = result_data.get("resume_text", "")
    
    try:
        # Initialize agent
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating email: {str(e)}"
        )



@app.post("/api/interview/message")
async def process_interview_message(
    interview_id: str = Form(...),
    message: str = Form(...)
):
    """
    Process user's answer and generate next question
    
    Args:
        interview_id: Interview session ID
        message: User's answer
        
    Returns:
        AI response, updated confidences, completion status
    """
    if interview_id not in interview_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    session = interview_sessions[interview_id]
    
    # Add user message to history
    session["conversation_history"].append({
        "role": "user",
        "content": message
    })
    
    # Initialize interview manager
    llm_client = create_llm_client()
    interview_manager = InterviewManager(llm_client, vector_store)
    
    try:
        # Process answer
        result = await interview_manager.process_answer(
            answer=message,
            target_gap=session["current_target"],
            current_confidence=session["gap_confidences"][session["current_target"]],
            gap_weight=session["weighted_keywords"].get(session["current_target"], 0.0),
            conversation_history=session["conversation_history"],
            all_gaps=session["gaps"],
            gap_confidences=session["gap_confidences"],
            weighted_keywords=session["weighted_keywords"]
        )
        
        # Update session state
        session["gap_confidences"][session["current_target"]] = result["confidence_update"]
        
        # Store evidence
        if session["current_target"] not in session["collected_evidence"]:
            session["collected_evidence"][session["current_target"]] = []
        session["collected_evidence"][session["current_target"]].append(
            result["evidence_extracted"]
        )
        
        # Update current target if moved to next gap
        if result["next_target"]:
            session["current_target"] = result["next_target"]
        
        # Add AI response to history
        session["conversation_history"].append({
            "role": "assistant",
            "content": result["response"]
        })
        
        # Build gap updates for frontend
        gap_updates = {}
        for gap in session["gaps"]:
            conf = session["gap_confidences"][gap]
            gap_updates[gap] = {
                "confidence": conf,
                "status": result["gap_status"][gap],
                "evidence_collected": session["collected_evidence"].get(gap, [])
            }
        
        return {
            "response": result["response"],
            "gap_updates": gap_updates,
            "keyword_alignment": session["gap_confidences"],
            "is_complete": result["is_complete"],
            "next_target": result["next_target"] or session["current_target"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@app.post("/api/interview/complete")
async def complete_interview(interview_id: str = Form(...)):
    """
    Finalize interview and synthesize bridge story
    
    Args:
        interview_id: Interview session ID
        
    Returns:
        Synthesized bridge story and final alignment scores
    """
    if interview_id not in interview_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    session = interview_sessions[interview_id]
    
    # Initialize interview manager
    llm_client = create_llm_client()
    interview_manager = InterviewManager(llm_client, vector_store)
    
    try:
        # Synthesize bridge story
        bridge_story = await interview_manager.synthesize_bridge_story(
            conversation_history=session["conversation_history"],
            gaps_addressed=session["gap_confidences"],
            weighted_keywords=session["weighted_keywords"]
        )
        
        # Store bridge story in session
        session["bridge_story"] = bridge_story
        session["completed_at"] = datetime.utcnow().isoformat()
        
        return {
            "bridge_story": bridge_story,
            "final_alignment": session["gap_confidences"],
            "ready_for_generation": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing interview: {str(e)}"
        )

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
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )