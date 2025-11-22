"""
Test Interview Flow End-to-End
Tests the new interview API endpoints and InterviewManager
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.interview_manager import InterviewManager
from utils.llm_client import create_llm_client
from utils.vector_store import VectorStore
from dotenv import load_dotenv

# Load env
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, '.env'))


async def test_interview_manager():
    """Test the InterviewManager class directly"""
    print("=" * 60)
    print("🧪 Testing Interview Manager")
    print("=" * 60)
    
    # Initialize
    print("\n[1/6] Initializing components...")
    llm_client = create_llm_client(temperature=0.7)
    vector_store = VectorStore()
    interview_manager = InterviewManager(llm_client, vector_store)
    print("✓ Components initialized")
    
    # Mock data
    gaps = ["Community Service", "Leadership"]
    weighted_keywords = {
        "Community Service": 0.6,
        "Leadership": 0.4
    }
    resume_text = """
    John Doe
    Education: MIT, Computer Science
    Experience: Software Engineer Intern at Google
    Skills: Python, JavaScript, Machine Learning
    """
    
    # Test 1: Start session
    print("\n[2/6] Testing session start...")
    try:
        session_data = await interview_manager.start_session(
            gaps=gaps,
            weighted_keywords=weighted_keywords,
            resume_text=resume_text
        )
        
        print(f"✓ Session started")
        print(f"  Target gap: {session_data['target_gap']}")
        print(f"  First question: {session_data['first_question'][:80]}...")
        
        assert session_data['target_gap'] == "Community Service", "Should prioritize highest weight gap"
        assert len(session_data['first_question']) > 0, "Should generate question"
        
    except Exception as e:
        print(f"✗ Session start failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Process first answer
    print("\n[3/6] Testing answer processing...")
    try:
        answer = "I volunteered at a local food bank for 2 years, helping distribute food to 500+ families monthly."
        
        result = await interview_manager.process_answer(
            answer=answer,
            target_gap="Community Service",
            current_confidence=0.0,
            gap_weight=0.6,
            conversation_history=[
                {"role": "assistant", "content": session_data['first_question']},
                {"role": "user", "content": answer}
            ],
            all_gaps=gaps,
            gap_confidences={"Community Service": 0.0, "Leadership": 0.0},
            weighted_keywords=weighted_keywords
        )
        
        print(f"✓ Answer processed")
        print(f"  New confidence: {result['confidence_update']:.2f}")
        print(f"  Evidence: {result['evidence_extracted'][:60]}...")
        print(f"  Response: {result['response'][:80]}...")
        
        assert result['confidence_update'] > 0.0, "Confidence should increase"
        assert result['evidence_extracted'], "Should extract evidence"
        
    except Exception as e:
        print(f"✗ Answer processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Process second answer (to reach threshold)
    print("\n[4/6] Testing follow-up answer...")
    try:
        answer2 = "I also organized fundraising events that raised $10,000 for the food bank and recruited 20 volunteers."
        
        result2 = await interview_manager.process_answer(
            answer=answer2,
            target_gap="Community Service",
            current_confidence=result['confidence_update'],
            gap_weight=0.6,
            conversation_history=[
                {"role": "assistant", "content": session_data['first_question']},
                {"role": "user", "content": answer},
                {"role": "assistant", "content": result['response']},
                {"role": "user", "content": answer2}
            ],
            all_gaps=gaps,
            gap_confidences={"Community Service": result['confidence_update'], "Leadership": 0.0},
            weighted_keywords=weighted_keywords
        )
        
        print(f"✓ Follow-up processed")
        print(f"  New confidence: {result2['confidence_update']:.2f}")
        print(f"  Next target: {result2['next_target']}")
        print(f"  Is complete: {result2['is_complete']}")
        
        # Should move to next gap if confidence is high enough
        if result2['confidence_update'] >= 0.75:
            assert result2['next_target'] == "Leadership", "Should move to next gap"
        
    except Exception as e:
        print(f"✗ Follow-up processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Answer for second gap
    print("\n[5/6] Testing second gap...")
    try:
        answer3 = "I was president of the Computer Science club, leading a team of 30 students and organizing hackathons."
        
        result3 = await interview_manager.process_answer(
            answer=answer3,
            target_gap="Leadership",
            current_confidence=0.0,
            gap_weight=0.4,
            conversation_history=[],
            all_gaps=gaps,
            gap_confidences={"Community Service": result2['confidence_update'], "Leadership": 0.0},
            weighted_keywords=weighted_keywords
        )
        
        print(f"✓ Second gap processed")
        print(f"  Confidence: {result3['confidence_update']:.2f}")
        
    except Exception as e:
        print(f"✗ Second gap processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Synthesize bridge story
    print("\n[6/6] Testing bridge story synthesis...")
    try:
        conversation_history = [
            {"role": "assistant", "content": session_data['first_question']},
            {"role": "user", "content": answer},
            {"role": "assistant", "content": result['response']},
            {"role": "user", "content": answer2},
            {"role": "user", "content": answer3}
        ]
        
        bridge_story = await interview_manager.synthesize_bridge_story(
            conversation_history=conversation_history,
            gaps_addressed={"Community Service": result2['confidence_update'], "Leadership": result3['confidence_update']},
            weighted_keywords=weighted_keywords
        )
        
        print(f"✓ Bridge story synthesized")
        print(f"  Length: {len(bridge_story)} characters")
        print(f"  Preview: {bridge_story[:150]}...")
        
        assert len(bridge_story) > 100, "Bridge story should be substantial"
        
    except Exception as e:
        print(f"✗ Bridge story synthesis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL INTERVIEW MANAGER TESTS PASSED!")
    print("=" * 60)
    return True


async def test_api_endpoints():
    """Test the API endpoints with curl"""
    print("\n" + "=" * 60)
    print("🧪 Testing API Endpoints")
    print("=" * 60)
    
    import subprocess
    import json
    
    # Note: This requires a valid workflow session to exist
    # For now, we'll just test that the endpoints are accessible
    
    print("\n[1/3] Testing /api/health...")
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8000/api/health"],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)
        assert data['status'] == 'ok', "Health check should pass"
        print("✓ Health check passed")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    print("\n[2/3] Checking API is running...")
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8000/"],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)
        assert 'name' in data, "Root endpoint should return API info"
        print("✓ API is running")
    except Exception as e:
        print(f"✗ API check failed: {e}")
        return False
    
    print("\n[3/3] Verifying interview endpoints exist...")
    # Just check that the server doesn't return 404 for these paths
    endpoints = [
        "/api/interview/start",
        "/api/interview/message", 
        "/api/interview/complete"
    ]
    
    for endpoint in endpoints:
        try:
            # POST without data will fail validation, but shouldn't 404
            result = subprocess.run(
                ["curl", "-s", "-w", "%{http_code}", "-o", "/dev/null", 
                 "-X", "POST", f"http://localhost:8000{endpoint}"],
                capture_output=True,
                text=True
            )
            status_code = int(result.stdout)
            # 422 (validation error) or 400 is expected without data
            # 404 would mean endpoint doesn't exist
            assert status_code != 404, f"Endpoint {endpoint} not found"
            print(f"✓ {endpoint} exists (status: {status_code})")
        except Exception as e:
            print(f"✗ {endpoint} check failed: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("✅ ALL API ENDPOINT TESTS PASSED!")
    print("=" * 60)
    return True


async def main():
    """Run all tests"""
    print("\n" + "🚀 " * 20)
    print("INTERVIEW FLOW COMPREHENSIVE TEST SUITE")
    print("🚀 " * 20 + "\n")
    
    # Test 1: Interview Manager
    manager_passed = await test_interview_manager()
    
    # Test 2: API Endpoints
    api_passed = await test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Interview Manager: {'✅ PASSED' if manager_passed else '❌ FAILED'}")
    print(f"API Endpoints:     {'✅ PASSED' if api_passed else '❌ FAILED'}")
    print("=" * 60)
    
    if manager_passed and api_passed:
        print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
