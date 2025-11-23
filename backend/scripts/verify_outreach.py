import asyncio
from unittest.mock import AsyncMock, MagicMock
from agents.ghostwriter import GhostwriterAgent

async def test_outreach():
    print("Testing Outreach Feature...")
    
    # Mock LLM Client
    mock_llm = AsyncMock()
    mock_llm.call.return_value = """
    {
        "subject": "Inquiry regarding Future Leaders Scholarship - John Doe",
        "body": "Dear Scholarship Committee,\\n\\nI am writing to express my sincere interest..."
    }
    """
    
    agent = GhostwriterAgent(mock_llm)
    
    # Test Data
    result = await agent.draft_outreach_email(
        scholarship_name="Future Leaders Scholarship",
        organization="Tech Foundation",
        contact_name="Ms. Smith",
        gaps=["Leadership experience in non-profit sector"],
        student_context="Computer Science student with 3.8 GPA and hackathon experience."
    )
    
    print("\nResult:")
    print(f"Subject: {result.get('subject')}")
    print(f"Body: {result.get('body')[:50]}...")
    
    if result.get("subject") and result.get("body"):
        print("\n✅ Verification Passed!")
    else:
        print("\n❌ Verification Failed!")

if __name__ == "__main__":
    asyncio.run(test_outreach())
