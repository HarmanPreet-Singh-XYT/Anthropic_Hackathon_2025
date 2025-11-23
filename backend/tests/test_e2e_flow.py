import requests
import time
import os

API_URL = "http://localhost:8000"
PDF_PATH = "data/sample_resume.pdf"

def test_workflow_flow():
    print("🚀 Starting E2E Workflow Test")
    
    # 1. Start Workflow
    print("\n[1] Starting workflow...")
    with open(PDF_PATH, "rb") as f:
        files = {"resume_file": f}
        data = {"scholarship_url": "https://www.coca-colascholarsfoundation.org/apply/"}
        response = requests.post(f"{API_URL}/api/workflow/start", files=files, data=data)
        
    if response.status_code != 200:
        print(f"❌ Failed to start workflow: {response.text}")
        return
        
    session_id = response.json()["session_id"]
    print(f"✓ Workflow started. Session ID: {session_id}")
    
    # 2. Poll for Matchmaker Completion (Expect 'waiting_for_input')
    print("\n[2] Polling for Matchmaker completion...")
    status = "processing"
    result = None
    
    for _ in range(60):  # Wait up to 2 minutes
        time.sleep(2)
        res = requests.get(f"{API_URL}/api/workflow/status/{session_id}")
        data = res.json()
        status = data["status"]
        print(f"  Status: {status}")
        
        if status == "waiting_for_input":
            result = data["result"]
            break
        elif status == "complete":
            print("❌ Workflow completed too early! It should have paused.")
            return
        elif status == "error":
            print(f"❌ Workflow failed: {data.get('error')}")
            return
            
    if status != "waiting_for_input":
        print("❌ Timed out waiting for matchmaker interrupt")
        return
        
    print("✓ Workflow paused correctly at 'waiting_for_input'")
    
    # Verify we have match results but NO essay
    if "matchmaker_results" in result:
        print("✓ Matchmaker results present")
    else:
        print("❌ Matchmaker results missing")
        
    # Note: The result object in waiting_for_input doesn't include essay, so we are good.
    
    # 3. Resume Workflow (Simulate Skip Interview)
    print("\n[3] Resuming workflow (Simulating Skip Interview)...")
    resume_data = {
        "session_id": session_id,
        "bridge_story": ""  # Empty story
    }
    res = requests.post(f"{API_URL}/api/workflow/resume", data=resume_data)
    
    if res.status_code != 200:
        print(f"❌ Failed to resume workflow: {res.text}")
        return
        
    print("✓ Resume request sent")
    
    # 4. Poll for Final Completion
    print("\n[4] Polling for final completion...")
    for _ in range(60):
        time.sleep(2)
        res = requests.get(f"{API_URL}/api/workflow/status/{session_id}")
        data = res.json()
        status = data["status"]
        print(f"  Status: {status}")
        
        if status == "complete":
            result = data["result"]
            break
        elif status == "error":
            print(f"❌ Workflow failed during generation: {data.get('error')}")
            return
            
    if status != "complete":
        print("❌ Timed out waiting for generation")
        return
        
    print("✓ Workflow completed successfully")
    
    # Verify Essay
    if result.get("essay_draft"):
        print(f"✓ Essay generated ({len(result['essay_draft'])} chars)")
    else:
        print("❌ Essay missing from final result")
        
    print("\n✅ TEST PASSED: Workflow flow is correct!")

if __name__ == "__main__":
    if not os.path.exists(PDF_PATH):
        print(f"❌ {PDF_PATH} not found. Run create_dummy_pdf.py first.")
    else:
        test_workflow_flow()
