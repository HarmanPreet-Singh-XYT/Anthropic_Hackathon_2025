import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.scout import ScoutAgent

# Load env vars from root
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(root_dir, '.env'))

async def test_scout():
    print("Testing Scout Agent...")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    print(f"API Key present: {bool(api_key)}")
    if api_key:
        print(f"API Key starts with: {api_key[:10]}...")
    
    try:
        agent = ScoutAgent()
        print("✓ Agent initialized")
        
        # Test URL (Coca-Cola Scholars is a good test case)
        url = "https://www.coca-colascholarsfoundation.org/apply/"
        print(f"Testing scrape of: {url}")
        
        # Test internal fetch directly first
        markdown = agent._fetch_and_clean(url)
        print(f"✓ Fetch successful. Markdown length: {len(markdown)}")
        print(f"Preview:\n{markdown[:200]}...")
        
        # Test full run
        print("\nRunning full Scout workflow...")
        result = await agent.run(url, debug=True)
        
        print("\n✓ Workflow complete!")
        print(f"Scholarship Name: {result['scholarship_intelligence']['official']['scholarship_name']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scout())
