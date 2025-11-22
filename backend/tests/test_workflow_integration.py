import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from workflows.scholarship_graph import ScholarshipWorkflow, ScholarshipState

@pytest.mark.asyncio
async def test_scholarship_workflow_integration():
    # Mock agents
    mock_scout = AsyncMock()
    mock_scout.run.return_value = {
        "scholarship_intelligence": {
            "official": {"scholarship_name": "Test Scholarship"},
            "past_winner_context": {},
            "combined_text": "Combined text"
        }
    }

    mock_profiler = AsyncMock()
    mock_profiler.run.return_value = {
        "success": True,
        "text": "Resume text content"
    }

    mock_decoder = AsyncMock()
    mock_decoder.run.return_value = {
        "primary_values": ["Leadership"],
        "hidden_weights": {"Leadership": 1.0},
        "tone": "Professional"
    }

    mock_matchmaker = AsyncMock()
    # Simulate match > threshold
    mock_matchmaker.run.return_value = {
        "match_score": 0.9,
        "trigger_interview": False,
        "gaps": []
    }

    mock_interviewer = AsyncMock()
    mock_optimizer = AsyncMock()
    mock_optimizer.run.return_value = {"optimizations": []}

    mock_ghostwriter = AsyncMock()
    mock_ghostwriter.run.return_value = {
        "essay": "Draft essay",
        "strategy_note": "Strategy"
    }

    agents = {
        "scout": mock_scout,
        "profiler": mock_profiler,
        "decoder": mock_decoder,
        "matchmaker": mock_matchmaker,
        "interviewer": mock_interviewer,
        "optimizer": mock_optimizer,
        "ghostwriter": mock_ghostwriter
    }

    workflow = ScholarshipWorkflow(agents)

    # Test run
    result = await workflow.run("http://example.com", "resume.pdf")

    # Verify flow
    assert result["current_phase"] == "complete"
    assert result["essay_draft"] == "Draft essay"
    
    # Verify agent calls
    mock_scout.run.assert_called_once()
    mock_profiler.run.assert_called_once()
    mock_decoder.run.assert_called_once()
    mock_matchmaker.run.assert_called_once()
    mock_optimizer.run.assert_called_once()
    mock_ghostwriter.run.assert_called_once()
    mock_interviewer.run.assert_not_called()

@pytest.mark.asyncio
async def test_scholarship_workflow_interview_trigger():
    # Mock agents for interview path
    mock_scout = AsyncMock()
    mock_scout.run.return_value = {"scholarship_intelligence": {}}
    mock_profiler = AsyncMock()
    mock_profiler.run.return_value = {"text": "Resume"}
    mock_decoder = AsyncMock()
    mock_decoder.run.return_value = {"hidden_weights": {}}
    
    mock_matchmaker = AsyncMock()
    # Simulate match < threshold
    mock_matchmaker.run.return_value = {
        "match_score": 0.5,
        "trigger_interview": True,
        "gaps": ["Leadership"]
    }

    mock_interviewer = AsyncMock()
    mock_interviewer.run.return_value = {"question": "Tell me about leadership."}

    agents = {
        "scout": mock_scout,
        "profiler": mock_profiler,
        "decoder": mock_decoder,
        "matchmaker": mock_matchmaker,
        "interviewer": mock_interviewer,
        "optimizer": AsyncMock(),
        "ghostwriter": AsyncMock()
    }

    workflow = ScholarshipWorkflow(agents)

    # Test run
    result = await workflow.run("http://example.com", "resume.pdf")

    # Verify interrupt
    assert result["current_phase"] == "interview"
    assert result["interview_question"] == "Tell me about leadership."
    
    mock_interviewer.run.assert_called_once()
