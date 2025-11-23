import asyncio
import uuid
from api import app, workflow_sessions
from agents.ghostwriter import GhostwriterAgent
from utils.llm_client import create_llm_client

async def verify_outreach_generation():
    print("🧪 Verifying Automated Outreach Generation...")
    
    # 1. Create a mock session with populated data
    session_id = str(uuid.uuid4())
    print(f"  → Created mock session: {session_id}")
    
    workflow_sessions[session_id] = {
        "session_id": session_id,
        "status": "complete",
        "result": {
            "scholarship_intelligence": {
                "official": {
                    "scholarship_name": "Test Scholarship",
                    "organization": "Test Org",
                    "contact_email": "contact@test.org",
                    "contact_name": "Dr. Test"
                }
            },
            "gaps": ["Leadership experience", "Community service"],
            "resume_text": "I am a student with good grades but I need to show more leadership."
        }
    }
    
    # 2. Mock the LLM client to avoid real calls (optional, but good for speed)
    # For now, we'll let it make a real call to verify the prompt works, 
    # assuming the environment is set up. If not, we'll catch the error.
    
    try:
        from api import generate_outreach_email, GenerateOutreachRequest
        
        request = GenerateOutreachRequest(session_id=session_id)
        result = await generate_outreach_email(request)
        
        print("\n✅ Generation Successful!")
        print(f"  Subject: {result['subject']}")
        print(f"  Body length: {len(result['body'])} chars")
        print(f"  Contact: {result['contact_name']} <{result['contact_email']}>")
        
        if result['contact_email'] == "contact@test.org":
            print("  ✓ Contact email correctly retrieved")
        else:
            print("  ❌ Contact email mismatch")
            
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_outreach_generation())
