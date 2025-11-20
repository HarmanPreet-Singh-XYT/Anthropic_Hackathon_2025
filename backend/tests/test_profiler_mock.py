import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock chromadb before importing agents
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()

from agents.profiler import ProfilerAgent

@pytest.mark.asyncio
async def test_profiler_run_success():
    # Mock dependencies
    mock_vector_store = MagicMock()
    
    # Create agent
    agent = ProfilerAgent(vector_store=mock_vector_store)
    
    # Mock pdf_parser functions
    with patch('utils.pdf_parser.validate_pdf', return_value=(True, None)) as mock_validate, \
         patch('utils.pdf_parser.parse_pdf', return_value="This is a sample resume text. It has multiple sentences.") as mock_parse:
        
        # Run agent
        result = await agent.run("dummy_resume.pdf")
        
        # Verify results
        assert result["success"] is True
        assert result["chunks_stored"] > 0
        assert result["resume_text"] == "This is a sample resume text. It has multiple sentences."
        
        # Verify calls
        mock_validate.assert_called_once_with("dummy_resume.pdf")
        mock_parse.assert_called_once_with("dummy_resume.pdf")
        mock_vector_store.add_documents.assert_called_once()

@pytest.mark.asyncio
async def test_profiler_invalid_pdf():
    # Mock dependencies
    mock_vector_store = MagicMock()
    
    # Create agent
    agent = ProfilerAgent(vector_store=mock_vector_store)
    
    # Mock pdf_parser functions
    with patch('utils.pdf_parser.validate_pdf', return_value=(False, "File not found")) as mock_validate:
        
        # Run agent
        result = await agent.run("invalid.pdf")
        
        # Verify results
        assert result["success"] is False
        assert "Invalid PDF" in result["error"]
        
        # Verify calls
        mock_validate.assert_called_once_with("invalid.pdf")
        mock_vector_store.add_documents.assert_not_called()

@pytest.mark.asyncio
async def test_chunk_text():
    mock_vector_store = MagicMock()
    agent = ProfilerAgent(vector_store=mock_vector_store)
    
    text = "Sentence one. Sentence two. Sentence three."
    chunks = agent.chunk_text(text, chunk_size=20)
    
    assert len(chunks) > 1
    assert "Sentence one." in chunks[0]
