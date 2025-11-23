
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.vector_store import VectorStore
from agents.profiler import ProfilerAgent
from agents.matchmaker import MatchmakerAgent
from utils.llm_client import create_llm_client

async def debug():
    print("Initializing Vector Store...")
    # Use absolute path for chroma_db to be safe
    root_dir = Path(__file__).parent.parent.parent
    chroma_dir = root_dir / "chroma_db"
    
    vs = VectorStore(persist_directory=str(chroma_dir))
    vs.clear_collection() # Start fresh
    
    print("Initializing Profiler...")
    profiler = ProfilerAgent(vs)
    
    # Use absolute path for sample resume
    pdf_path = root_dir / "backend" / "data" / "sample_resume.pdf"
    
    if not pdf_path.exists():
        print(f"❌ Sample resume not found at {pdf_path}")
        print("Run 'python backend/scripts/create_dummy_pdf.py' first.")
        return

    print(f"Running Profiler on {pdf_path}...")
    res = await profiler.run(str(pdf_path))
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
