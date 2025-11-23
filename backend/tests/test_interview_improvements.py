import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.agents.interviewer import InterviewerAgent
from backend.agents.interview_manager import InterviewManager
from backend.utils.llm_client import LLMClient

@pytest.fixture
def mock_llm_client():
    client = AsyncMock(spec=LLMClient)
    client.call.return_value = "Mocked response"
    return client

@pytest.fixture
def mock_vector_store():
    return MagicMock()

@pytest.mark.asyncio
async def test_interviewer_tool_usage(mock_llm_client):
    """Test that InterviewerAgent uses Google Search tool"""
    agent = InterviewerAgent(mock_llm_client)
    
    # Mock search tool
    agent.search_tool = MagicMock()
    agent.search_tool.service = True
    agent.search_tool.tool_definition = {"name": "google_search"}
    agent.search_tool.execute = AsyncMock(return_value="Search results")
    
    # Mock LLM response to trigger tool use first, then answer
    # First call returns tool use
    tool_block = MagicMock(type="tool_use")
    tool_block.name = "google_search"
    tool_block.input = {"query": "test query"}
    
    tool_use_response = {
        "type": "tool_use",
        "content": [tool_block],
        "stop_reason": "tool_use"
    }  
    
    # Second call returns final question
    final_response = "Final interview question?"
    
    mock_llm_client.call.side_effect = [tool_use_response, final_response]
    
    question = await agent.generate_question(
        resume_summary="Summary",
        target_gap="Leadership",
        gap_weight=0.8
    )
    
    # Verify tool was executed
    agent.search_tool.execute.assert_called_once_with(query="test query")
    
    # Verify final question
    assert question == "Final interview question?"

@pytest.mark.asyncio
async def test_max_questions_constraint(mock_llm_client, mock_vector_store):
    """Test that interview stops after max questions"""
    manager = InterviewManager(mock_llm_client, mock_vector_store)
    manager.max_questions = 3  # Set low limit for testing
    
    # Mock dependencies
    manager._score_answer = AsyncMock(return_value=0.5) # Low confidence
    manager._extract_evidence = AsyncMock(return_value="Evidence")
    manager._generate_followup_question = AsyncMock(return_value="Follow up?")
    
    # Simulate conversation history with 3 user answers
    history = [
        {"role": "assistant", "content": "Q1"},
        {"role": "user", "content": "A1"},
        {"role": "assistant", "content": "Q2"},
        {"role": "user", "content": "A2"},
        {"role": "assistant", "content": "Q3"},
        {"role": "user", "content": "A3"},
    ]
    
    gap_confidences = {"Leadership": 0.5}
    
    result = await manager.process_answer(
        answer="A3",
        target_gap="Leadership",
        current_confidence=0.5,
        gap_weight=0.8,
        conversation_history=history,
        all_gaps=["Leadership"],
        gap_confidences=gap_confidences,
        weighted_keywords={"Leadership": 0.8}
    )
    
    # Should be complete because max questions reached
    assert result["is_complete"] is True
    assert result["next_target"] is None

@pytest.mark.asyncio
async def test_confidence_threshold(mock_llm_client, mock_vector_store):
    """Test that interview continues until confidence threshold met"""
    manager = InterviewManager(mock_llm_client, mock_vector_store)
    manager.confidence_threshold = 0.8
    
    # Mock dependencies
    manager._score_answer = AsyncMock(return_value=0.7) # Below threshold
    manager._extract_evidence = AsyncMock(return_value="Evidence")
    manager._generate_followup_question = AsyncMock(return_value="Follow up?")
    
    history = [{"role": "assistant", "content": "Q1"}]
    gap_confidences = {"Leadership": 0.0}
    
    result = await manager.process_answer(
        answer="A1",
        target_gap="Leadership",
        current_confidence=0.0,
        gap_weight=0.8,
        conversation_history=history,
        all_gaps=["Leadership"],
        gap_confidences=gap_confidences,
        weighted_keywords={"Leadership": 0.8}
    )
    
    # Should NOT be complete
    assert result["is_complete"] is False
    assert result["confidence_update"] == 0.7
