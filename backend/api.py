"""
FastAPI server for ScholarFit AI backend
Handles resume upload, processing, and ChromaDB integration
"""

import os
from datetime import datetime
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, status, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config.settings import settings
from utils.vector_store import VectorStore
from agents.profiler import ProfilerAgent


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

# Uploads directory
UPLOADS_DIR = Path(__file__).parent / "uploads"

# Session storage for Scout workflows (in-memory)
workflow_sessions: Dict[str, Dict[str, Any]] = {}
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
        
    except Exception as e:
        print(f"✗ Error initializing vector store: {e}")
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
    
    try:
        # Write file to disk
        with open(temp_path, "wb") as f:
            f.write(file_content)
        
        # Process with ProfilerAgent
        profiler = ProfilerAgent(vector_store)
        result = await profiler.run(str(temp_path))
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error during processing")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process PDF: {error_msg}"
            )
        
        # Build response
        return UploadResponse(
            success=True,
            message="Resume processed successfully",
            chunks_stored=result.get("chunks_stored", 0),
            metadata={
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
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


# ==================== Scout Workflow Endpoints ====================

@app.post("/api/scout/start")
async def start_scout_workflow(
    scholarship_url: str = Form(...),
    background_tasks: BackgroundTasks
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
