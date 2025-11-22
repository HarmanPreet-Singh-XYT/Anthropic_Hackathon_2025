
import asyncio
import os
import sys
sys.path.append(os.getcwd())

from backend.utils.vector_store import VectorStore
from backend.agents.profiler import ProfilerAgent
from backend.agents.matchmaker import MatchmakerAgent
from backend.utils.llm_client import create_llm_client

async def debug():
    print("Initializing Vector Store...")
    vs = VectorStore()
    vs.clear_collection() # Start fresh
    
    print("Initializing Profiler...")
    profiler = ProfilerAgent(vs)
    
    pdf_path = "backend/data/sample_resume.pdf"
    print(f"Running Profiler on {pdf_path}...")
    res = await profiler.run(pdf_path)
    print(f"Profiler Result: {res}")
    
    print("Checking Vector Store stats...")
    stats = vs.get_collection_stats()
    print(f"Stats: {stats}")
    
    print("Querying Vector Store...")
    results = vs.query("Leadership", n_results=3)
    print(f"Query 'Leadership': {results}")
    
    if not results['documents']:
        print("❌ No documents found for 'Leadership'")
    else:
        print("✅ Documents found!")
        print(f"Distances: {results['distances']}")

if __name__ == "__main__":
    asyncio.run(debug())
