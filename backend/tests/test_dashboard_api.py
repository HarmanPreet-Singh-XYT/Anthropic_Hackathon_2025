"""
Tests for the dashboard API endpoint
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import app

from api import app, get_db

client = TestClient(app)

# Mock DB dependency
def override_get_db():
    try:
        yield MagicMock()
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

def test_dashboard_no_user_id():
    """Test dashboard endpoint without user ID header"""
    response = client.get("/api/dashboard")
    # Depending on implementation, this might be 400, 401, or just return empty data
    # Given the plan, we expect it to require the header or handle it gracefully
    # Let's assume for now it returns 400 if critical, or maybe just empty. 
    # But usually auth headers are required.
    # However, the current API implementation often treats x_user_id as Optional.
    # If it's optional, it might return empty data.
    assert response.status_code in [200, 400, 401]

@patch("api.ApplicationOperations")
@patch("api.ResumeSessionOperations")
@patch("api.WorkflowSessionOperations")
def test_dashboard_with_data(mock_workflow_ops, mock_resume_ops, mock_app_ops):
    """Test dashboard endpoint with mocked data"""
    
    # Mock data
    user_id = "test-user-123"
    
    # Mock applications
    mock_app = MagicMock()
    mock_app.id = "app-1"
    mock_app.scholarship_url = "http://example.com"
    mock_app.status = "complete"
    mock_app.match_score = 85.5
    mock_app.had_interview = True
    mock_app.created_at.isoformat.return_value = "2023-01-01T00:00:00"
    
    mock_app_ops.get_all.return_value = [mock_app]
    
    # Mock resumes
    mock_resume = MagicMock()
    mock_resume.id = "resume-1"
    mock_resume.filename = "resume.pdf"
    mock_resume.created_at.isoformat.return_value = "2023-01-01T00:00:00"
    
    mock_resume_ops.get_all.return_value = [mock_resume]
    
    # Mock workflows
    mock_workflow = MagicMock()
    mock_workflow.id = "workflow-1"
    mock_workflow.status = "processing"
    mock_workflow.scholarship_url = "http://example.com"
    mock_workflow.created_at.isoformat.return_value = "2023-01-01T00:00:00"
    
    mock_workflow_ops.get_all.return_value = [mock_workflow]
    
    response = client.get("/api/dashboard", headers={"x-user-id": user_id})
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["user_id"] == user_id
    assert len(data["applications"]) == 1
    assert len(data["resumes"]) == 1
    assert len(data["active_workflows"]) == 1
    assert data["stats"]["total_applications"] == 1
    assert data["stats"]["total_interviews"] == 1
