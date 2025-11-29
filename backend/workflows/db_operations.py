"""
Database CRUD operations for ScholarFit AI
Provides high-level database operations for all models
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .database import (
    WorkflowSession, 
    ResumeSession, 
    InterviewSession, 
    Application
)


class WorkflowSessionOperations:
    """CRUD operations for workflow sessions"""
    
    @staticmethod
    def create(
        db: Session,
        session_id: str,
        scholarship_url: str,
        resume_session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> WorkflowSession:
        """
        Create a new workflow session
        
        Args:
            db: Database session
            session_id: Unique workflow session ID
            scholarship_url: URL of the scholarship
            resume_session_id: Optional link to resume session
            
        Returns:
            Created WorkflowSession object
        """
        workflow = WorkflowSession(
            id=session_id,
            resume_session_id=resume_session_id,
            user_id=user_id,
            status="processing",
            scholarship_url=scholarship_url
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        return workflow
    
    @staticmethod
    def get(db: Session, session_id: str) -> Optional[WorkflowSession]:
        """
        Get workflow session by ID
        
        Args:
            db: Database session
            session_id: Workflow session ID
            
        Returns:
            WorkflowSession object or None if not found
        """
        return db.query(WorkflowSession).filter(WorkflowSession.id == session_id).first()
    
    @staticmethod
    def get_all(db: Session, limit: int = 100, offset: int = 0, user_id: Optional[str] = None) -> List[WorkflowSession]:
        """
        Get all workflow sessions with pagination
        
        Args:
            db: Database session
            limit: Maximum number of results
            offset: Number of results to skip
            user_id: Optional user ID filter
            
        Returns:
            List of WorkflowSession objects
        """
        query = db.query(WorkflowSession)
        if user_id:
            query = query.filter(WorkflowSession.user_id == user_id)
            
        return query\
            .order_by(desc(WorkflowSession.created_at))\
            .limit(limit)\
            .offset(offset)\
            .all()
    
    @staticmethod
    def get_by_resume_session(
        db: Session,
        resume_session_id: str,
        limit: int = 100
    ) -> List[WorkflowSession]:
        """
        Get all workflows for a specific resume session
        
        Args:
            db: Database session
            resume_session_id: Resume session ID
            limit: Maximum number of results
            
        Returns:
            List of WorkflowSession objects
        """
        return db.query(WorkflowSession)\
            .filter(WorkflowSession.resume_session_id == resume_session_id)\
            .order_by(desc(WorkflowSession.created_at))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_by_status(
        db: Session,
        status: str,
        limit: int = 100
    ) -> List[WorkflowSession]:
        """
        Get workflows by status
        
        Args:
            db: Database session
            status: Status to filter by (processing, complete, error, etc.)
            limit: Maximum number of results
            
        Returns:
            List of WorkflowSession objects
        """
        return db.query(WorkflowSession)\
            .filter(WorkflowSession.status == status)\
            .order_by(desc(WorkflowSession.created_at))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def update_status(
        db: Session,
        session_id: str,
        status: str,
        error_message: Optional[str] = None
    ):
        """
        Update workflow session status
        
        Args:
            db: Database session
            session_id: Workflow session ID
            status: New status
            error_message: Optional error message if status is 'error'
        """
        workflow = db.query(WorkflowSession).filter(WorkflowSession.id == session_id).first()
        if workflow:
            workflow.status = status
            workflow.updated_at = datetime.utcnow()
            if error_message:
                workflow.error_message = error_message
            if status == "complete":
                workflow.completed_at = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def update_results(
        db: Session,
        session_id: str,
        results: Dict[str, Any]
    ):
        """
        Update workflow results
        
        Args:
            db: Database session
            session_id: Workflow session ID
            results: Dictionary containing result fields
        """
        workflow = db.query(WorkflowSession).filter(WorkflowSession.id == session_id).first()
        if workflow:
            # Update individual fields from results dict
            if "matchmaker_results" in results:
                workflow.matchmaker_results = results["matchmaker_results"]
            if "essay_draft" in results:
                workflow.essay_draft = results["essay_draft"]
            if "resume_optimizations" in results:
                workflow.resume_optimizations = results["resume_optimizations"]
            if "optimized_resume_markdown" in results:
                workflow.optimized_resume_markdown = results["optimized_resume_markdown"]
            if "strategy_note" in results:
                workflow.strategy_note = results["strategy_note"]
            if "match_score" in results:
                workflow.match_score = results["match_score"]
            if "gaps" in results:
                workflow.gaps = results["gaps"]
            if "scholarship_intelligence" in results:
                workflow.scholarship_intelligence = results["scholarship_intelligence"]
            
            workflow.updated_at = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def update_checkpoint(
        db: Session,
        session_id: str,
        state: Dict[str, Any]
    ):
        """
        Update workflow state checkpoint for recovery
        
        Args:
            db: Database session
            session_id: Workflow session ID
            state: Full workflow state dictionary
        """
        workflow = db.query(WorkflowSession).filter(WorkflowSession.id == session_id).first()
        if workflow:
            workflow.state_checkpoint = state
            workflow.updated_at = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def complete(
        db: Session,
        session_id: str,
        results: Dict[str, Any]
    ):
        """
        Mark workflow as complete with final results
        
        Args:
            db: Database session
            session_id: Workflow session ID
            results: Final results dictionary
        """
        workflow = db.query(WorkflowSession).filter(WorkflowSession.id == session_id).first()
        if workflow:
            workflow.status = "complete"
            workflow.completed_at = datetime.utcnow()
            workflow.updated_at = datetime.utcnow()
            # Update all result fields
            WorkflowSessionOperations.update_results(db, session_id, results)
    
    @staticmethod
    def delete(db: Session, session_id: str) -> bool:
        """
        Delete a workflow session
        
        Args:
            db: Database session
            session_id: Workflow session ID
            
        Returns:
            True if deleted, False if not found
        """
        workflow = db.query(WorkflowSession).filter(WorkflowSession.id == session_id).first()
        if workflow:
            db.delete(workflow)
            db.commit()
            return True
        return False


class ResumeSessionOperations:
    """CRUD operations for resume sessions"""
    
    @staticmethod
    def create(
        db: Session,
        session_id: str,
        filename: str,
        file_size_bytes: int,
        chunks_stored: int,
        text_preview: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ResumeSession:
        """
        Create a new resume session
        
        Args:
            db: Database session
            session_id: Unique resume session ID
            filename: Original filename
            file_size_bytes: File size in bytes
            chunks_stored: Number of chunks stored in vector DB
            text_preview: Optional preview of resume text
            
        Returns:
            Created ResumeSession object
        """
        resume = ResumeSession(
            id=session_id,
            user_id=user_id,
            filename=filename,
            file_size_bytes=file_size_bytes,
            chunks_stored=chunks_stored,
            text_preview=text_preview
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
    
    @staticmethod
    def get(db: Session, session_id: str) -> Optional[ResumeSession]:
        """
        Get resume session by ID
        
        Args:
            db: Database session
            session_id: Resume session ID
            
        Returns:
            ResumeSession object or None if not found
        """
        return db.query(ResumeSession).filter(ResumeSession.id == session_id).first()
    
    @staticmethod
    def get_all(db: Session, limit: int = 100, offset: int = 0, user_id: Optional[str] = None) -> List[ResumeSession]:
        """
        Get all resume sessions with pagination
        
        Args:
            db: Database session
            limit: Maximum number of results
            offset: Number of results to skip
            user_id: Optional user ID filter
            
        Returns:
            List of ResumeSession objects
        """
        query = db.query(ResumeSession)
        if user_id:
            query = query.filter(ResumeSession.user_id == user_id)
            
        return query\
            .order_by(desc(ResumeSession.created_at))\
            .limit(limit)\
            .offset(offset)\
            .all()
    
    @staticmethod
    def update(
        db: Session,
        session_id: str,
        **kwargs
    ):
        """
        Update resume session fields
        
        Args:
            db: Database session
            session_id: Resume session ID
            **kwargs: Fields to update
        """
        resume = db.query(ResumeSession).filter(ResumeSession.id == session_id).first()
        if resume:
            for key, value in kwargs.items():
                if hasattr(resume, key):
                    setattr(resume, key, value)
            db.commit()
    
    @staticmethod
    def delete(db: Session, session_id: str) -> bool:
        """
        Delete a resume session
        
        Args:
            db: Database session
            session_id: Resume session ID
            
        Returns:
            True if deleted, False if not found
        """
        resume = db.query(ResumeSession).filter(ResumeSession.id == session_id).first()
        if resume:
            db.delete(resume)
            db.commit()
            return True
        return False


class InterviewSessionOperations:
    """CRUD operations for interview sessions"""
    
    @staticmethod
    def create(
        db: Session,
        interview_id: str,
        workflow_session_id: str,
        gaps: List[str],
        weighted_keywords: Dict[str, float],
        gap_confidences: Dict[str, float],
        prioritized_gaps: List[str],
        current_target: str
    ) -> InterviewSession:
        """
        Create a new interview session
        
        Args:
            db: Database session
            interview_id: Unique interview session ID
            workflow_session_id: Parent workflow session ID
            gaps: List of gap keywords
            weighted_keywords: Dictionary of keyword weights
            gap_confidences: Initial confidence scores
            prioritized_gaps: Ordered list of gaps to address
            current_target: Current gap being addressed
            
        Returns:
            Created InterviewSession object
        """
        interview = InterviewSession(
            id=interview_id,
            workflow_session_id=workflow_session_id,
            gaps=gaps,
            weighted_keywords=weighted_keywords,
            gap_confidences=gap_confidences,
            prioritized_gaps=prioritized_gaps,
            current_target=current_target,
            conversation_history=[],
            collected_evidence={}
        )
        db.add(interview)
        db.commit()
        db.refresh(interview)
        return interview
    
    @staticmethod
    def get(db: Session, interview_id: str) -> Optional[InterviewSession]:
        """
        Get interview session by ID
        
        Args:
            db: Database session
            interview_id: Interview session ID
            
        Returns:
            InterviewSession object or None if not found
        """
        return db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
    
    @staticmethod
    def get_by_workflow(db: Session, workflow_session_id: str) -> Optional[InterviewSession]:
        """
        Get interview session by workflow session ID
        
        Args:
            db: Database session
            workflow_session_id: Workflow session ID
            
        Returns:
            InterviewSession object or None if not found
        """
        return db.query(InterviewSession)\
            .filter(InterviewSession.workflow_session_id == workflow_session_id)\
            .order_by(desc(InterviewSession.created_at))\
            .first()
    
    @staticmethod
    def add_message(
        db: Session,
        interview_id: str,
        role: str,
        content: str
    ):
        """
        Add a message to conversation history
        
        Args:
            db: Database session
            interview_id: Interview session ID
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        interview = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if interview:
            history = interview.conversation_history or []
            history.append({"role": role, "content": content})
            interview.conversation_history = history
            db.commit()
    
    @staticmethod
    def update_confidences(
        db: Session,
        interview_id: str,
        gap_confidences: Dict[str, float],
        current_target: str
    ):
        """
        Update gap confidences and current target
        
        Args:
            db: Database session
            interview_id: Interview session ID
            gap_confidences: Updated confidence scores
            current_target: Current gap being addressed
        """
        interview = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if interview:
            interview.gap_confidences = gap_confidences
            interview.current_target = current_target
            db.commit()
    
    @staticmethod
    def add_evidence(
        db: Session,
        interview_id: str,
        gap: str,
        evidence: str
    ):
        """
        Add evidence for a specific gap
        
        Args:
            db: Database session
            interview_id: Interview session ID
            gap: Gap keyword
            evidence: Evidence text
        """
        interview = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if interview:
            evidence_dict = interview.collected_evidence or {}
            if gap not in evidence_dict:
                evidence_dict[gap] = []
            evidence_dict[gap].append(evidence)
            interview.collected_evidence = evidence_dict
            db.commit()
    
    @staticmethod
    def complete(
        db: Session,
        interview_id: str,
        bridge_story: str
    ):
        """
        Mark interview as complete with bridge story
        
        Args:
            db: Database session
            interview_id: Interview session ID
            bridge_story: Synthesized bridge story
        """
        interview = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if interview:
            interview.bridge_story = bridge_story
            interview.completed_at = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def delete(db: Session, interview_id: str) -> bool:
        """
        Delete an interview session
        
        Args:
            db: Database session
            interview_id: Interview session ID
            
        Returns:
            True if deleted, False if not found
        """
        interview = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if interview:
            db.delete(interview)
            db.commit()
            return True
        return False


class ApplicationOperations:
    """CRUD operations for applications"""
    
    @staticmethod
    def create(
        db: Session,
        workflow_session_id: str,
        resume_session_id: str,
        scholarship_url: str,
        match_score: Optional[float] = None,
        had_interview: bool = False,
        user_id: Optional[str] = None
    ) -> Application:
        """
        Create a new application record
        
        Args:
            db: Database session
            workflow_session_id: Workflow session ID
            resume_session_id: Resume session ID
            scholarship_url: Scholarship URL
            match_score: Match score (0.0 to 1.0)
            had_interview: Whether interview was conducted
            
        Returns:
            Created Application object
        """
        app = Application(
            workflow_session_id=workflow_session_id,
            resume_session_id=resume_session_id,
            user_id=user_id,
            scholarship_url=scholarship_url,
            status="complete",
            match_score=match_score,
            had_interview=had_interview
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        return app
    
    @staticmethod
    def get(db: Session, application_id: str) -> Optional[Application]:
        """
        Get application by ID
        
        Args:
            db: Database session
            application_id: Application ID
            
        Returns:
            Application object or None if not found
        """
        return db.query(Application).filter(Application.id == application_id).first()
    
    @staticmethod
    def get_all(db: Session, limit: int = 100, offset: int = 0, user_id: Optional[str] = None) -> List[Application]:
        """
        Get all applications with pagination
        
        Args:
            db: Database session
            limit: Maximum number of results
            offset: Number of results to skip
            user_id: Optional user ID filter
            
        Returns:
            List of Application objects
        """
        query = db.query(Application)
        if user_id:
            query = query.filter(Application.user_id == user_id)
            
        return query\
            .order_by(desc(Application.created_at))\
            .limit(limit)\
            .offset(offset)\
            .all()
    
    @staticmethod
    def get_by_resume_session(
        db: Session,
        resume_session_id: str
    ) -> List[Application]:
        """
        Get all applications for a resume session
        
        Args:
            db: Database session
            resume_session_id: Resume session ID
            
        Returns:
            List of Application objects
        """
        return db.query(Application)\
            .filter(Application.resume_session_id == resume_session_id)\
            .order_by(desc(Application.created_at))\
            .all()
    
    @staticmethod
    def get_by_workflow_session(
        db: Session,
        workflow_session_id: str
    ) -> Optional[Application]:
        """
        Get application by workflow session ID
        
        Args:
            db: Database session
            workflow_session_id: Workflow session ID
            
        Returns:
            Application object or None if not found
        """
        return db.query(Application)\
            .filter(Application.workflow_session_id == workflow_session_id)\
            .first()
    
    @staticmethod
    def update_status(
        db: Session,
        application_id: str,
        status: str
    ):
        """
        Update application status
        
        Args:
            db: Database session
            application_id: Application ID
            status: New status
        """
        app = db.query(Application).filter(Application.id == application_id).first()
        if app:
            app.status = status
            db.commit()
    
    @staticmethod
    def delete(db: Session, application_id: str) -> bool:
        """
        Delete an application
        
        Args:
            db: Database session
            application_id: Application ID
            
        Returns:
            True if deleted, False if not found
        """
        app = db.query(Application).filter(Application.id == application_id).first()
        if app:
            db.delete(app)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_statistics(db: Session) -> Dict[str, Any]:
        """
        Get application statistics
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with statistics
        """
        from sqlalchemy import func
        
        total = db.query(func.count(Application.id)).scalar()
        with_interview = db.query(func.count(Application.id))\
            .filter(Application.had_interview == True)\
            .scalar()
        avg_score = db.query(func.avg(Application.match_score))\
            .filter(Application.match_score != None)\
            .scalar()
        
        return {
            "total_applications": total or 0,
            "with_interview": with_interview or 0,
            "without_interview": (total or 0) - (with_interview or 0),
            "average_match_score": float(avg_score) if avg_score else 0.0
        }