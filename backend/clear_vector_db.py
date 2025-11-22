#!/usr/bin/env python3
"""
Utility script to clear the ChromaDB vector store
"""

from utils.vector_store import VectorStore
from config.settings import settings

def main():
    print("🗑️  Clearing ChromaDB vector store...")
    
    # Initialize vector store
    vector_store = VectorStore(
        collection_name="resumes",
        persist_directory=str(settings.chroma_dir)
    )
    
    # Get stats before clearing
    stats_before = vector_store.get_collection_stats()
    count_before = stats_before.get("count", 0)
    
    print(f"📊 Documents before: {count_before}")
    
    if count_before == 0:
        print("✓ Collection is already empty")
        return
    
    # Clear the collection
    vector_store.clear_collection()
    
    # Get stats after clearing
    stats_after = vector_store.get_collection_stats()
    count_after = stats_after.get("count", 0)
    
    print(f"📊 Documents after: {count_after}")
    print(f"✓ Removed {count_before - count_after} documents")
    print("✓ Vector store cleared successfully")

if __name__ == "__main__":
    main()
