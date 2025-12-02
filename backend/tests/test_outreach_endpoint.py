"""
Test for outreach endpoint to verify the 400 error fix
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import app
from database import WorkflowSession

# Test client
client = TestClient(app)


def test_outreach_with_missing_scholarship_intelligence():
    """Test that outreach returns proper error when scholarship_intelligence is missing"""
    
    # Mock a workflow without scholarship_intelligence
    mock_workflow = Mock(spec=WorkflowSession)
    mock_workflow.id = "test-session-123"
    mock_workflow.status = "waiting_for_input"
    mock_workflow.scholarship_intelligence = None
    mock_workflow.gaps = []
    mock_workflow.state_checkpoint = {}
    
    with patch('api.WorkflowSessionOperations.get', return_value=mock_workflow):
        response = client.post(
            "/api/outreach/generate",
            json={"session_id": "test-session-123"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "scholarship intelligence not available" in data["detail"].lower()
        assert "waiting_for_input" in data["detail"]


def test_outreach_with_scholarship_intelligence():
    """Test that outreach works when scholarship_intelligence is present"""
    
    # Mock a workflow with scholarship_intelligence
    mock_workflow = Mock(spec=WorkflowSession)
    mock_workflow.id = "test-session-456"
    mock_workflow.status = "waiting_for_input"
    mock_workflow.scholarship_intelligence = {
        "official": {
            "scholarship_name": "Test Scholarship",
            "organization": "Test Org",
            "contact_email": "test@example.com",
            "contact_name": "John Doe"
        }
    }
    mock_workflow.gaps = ["leadership", "community service"]
    mock_workflow.state_checkpoint = {
        "resume_text": "Sample resume text"
    }
    
    # Mock the ghostwriter response
    mock_email = {
        "subject": "Application Inquiry - Test Scholarship",
        "body": "Dear John Doe,\n\nI am writing to express my interest..."
    }
    
    with patch('api.WorkflowSessionOperations.get', return_value=mock_workflow):
        with patch('api.GhostwriterAgent.draft_outreach_email', return_value=mock_email):
            response = client.post(
                "/api/outreach/generate",
                json={"session_id": "test-session-456"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "subject" in data
            assert "body" in data
            assert "contact_email" in data
            assert data["contact_email"] == "test@example.com"


def test_outreach_session_not_found():
    """Test that outreach returns 404 when session doesn't exist"""
    
    with patch('api.WorkflowSessionOperations.get', return_value=None):
        response = client.post(
            "/api/outreach/generate",
            json={"session_id": "nonexistent-session"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "session not found" in data["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
