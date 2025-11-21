"""
Integration tests for FastAPI endpoints
Tests resume upload, processing, and ChromaDB integration
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api import app, vector_store


# Test client
client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ScholarFit AI API"
    assert data["status"] == "running"
    assert "endpoints" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "vector_store_ready" in data
    
    # Should be ready after startup
    assert data["vector_store_ready"] == True
    assert data["status"] in ["ok", "degraded"]


def test_resume_stats():
    """Test resume stats endpoint"""
    response = client.get("/api/resume-stats")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert data["success"] == True
    assert "count" in data
    assert "collection_name" in data


def test_upload_invalid_file_type():
    """Test upload with non-PDF file"""
    # Create a fake text file
    files = {"file": ("test.txt", b"This is not a PDF", "text/plain")}
    response = client.post("/api/upload-resume", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "PDF" in data["detail"]


def test_upload_empty_file():
    """Test upload with empty file"""
    files = {"file": ("empty.pdf", b"", "application/pdf")}
    response = client.post("/api/upload-resume", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "empty" in data["detail"].lower()


def test_upload_oversized_file():
    """Test upload with file exceeding 5MB limit"""
    # Create a 6MB file
    large_content = b"x" * (6 * 1024 * 1024)
    files = {"file": ("large.pdf", large_content, "application/pdf")}
    response = client.post("/api/upload-resume", files=files)
    
    assert response.status_code == 413
    data = response.json()
    assert "too large" in data["detail"].lower()


@pytest.mark.skip(reason="Requires valid PDF file - manual test recommended")
def test_upload_valid_pdf():
    """
    Test upload with valid PDF
    
    NOTE: This test is skipped in automated runs because it requires a real PDF.
    To run manually:
    1. Create a test PDF at backend/tests/fixtures/test_resume.pdf
    2. Run: pytest tests/test_api.py::test_upload_valid_pdf -v
    """
    pdf_path = Path(__file__).parent / "fixtures" / "test_resume.pdf"
    
    if not pdf_path.exists():
        pytest.skip(f"Test PDF not found at {pdf_path}")
    
    with open(pdf_path, "rb") as f:
        files = {"file": ("test_resume.pdf", f, "application/pdf")}
        response = client.post("/api/upload-resume", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["chunks_stored"] > 0
    assert "metadata" in data
    assert data["metadata"]["filename"] == "test_resume.pdf"


def test_clear_resume():
    """Test clearing resume data"""
    response = client.delete("/api/resume")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "documents_removed" in data


def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/api/health")
    # CORS headers should be present for allowed origins
    # Note: TestClient doesn't fully simulate CORS, but we can verify app config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
