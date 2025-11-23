#!/usr/bin/env python3
"""
Test session isolation in ChromaDB vector store.
Verifies that queries only return results from the correct session.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.vector_store import VectorStore
from agents.profiler import ProfilerAgent
from agents.matchmaker import MatchmakerAgent
from utils.llm_client import create_llm_client
from config.settings import settings


async def test_session_isolation():
    """
    Test that session isolation works correctly:
    1. Upload two different resumes with different session IDs
    2. Query each session
    3. Verify no cross-contamination
    """
    
    print("\n" + "="*70)
    print("SESSION ISOLATION TEST")
    print("="*70)
    
    # Initialize vector store
    vector_store = VectorStore(
        collection_name="resumes",
        persist_directory=str(settings.chroma_dir)
    )
    
    # Clear any existing data
    print("\n📊 Clearing existing data...")
    initial_stats = vector_store.get_collection_stats()
    print(f"   Documents before: {initial_stats['count']}")
    vector_store.clear_collection()
    print(f"   ✓ Collection cleared")
    
    # Create two mock resumes with distinct content
    session_a = "session-test-alice-001"
    session_b = "session-test-bob-002"
    
    chunks_a = [
        "Alice Johnson, Software Engineer with expertise in Python and machine learning",
        "Led development of AI-powered recommendation system at TechCorp",
        "Published research on neural networks at top-tier conferences"
    ]
    
    chunks_b = [
        "Bob Smith, Marketing Manager with 10 years of brand strategy experience",
        "Increased customer engagement by 200% through social media campaigns",
        "Expert in market research and consumer behavior analysis"
    ]
    
    # Store Session A
    print(f"\n📝 Storing Session A: {session_a}")
    vector_store.add_documents(
        documents=chunks_a,
        metadatas=[
            {"source": "resume", "chunk_index": i, "session_id": session_a}
            for i in range(len(chunks_a))
        ]
    )
    print(f"   ✓ Stored {len(chunks_a)} chunks for Session A")
    
    # Store Session B
    print(f"\n📝 Storing Session B: {session_b}")
    vector_store.add_documents(
        documents=chunks_b,
        metadatas=[
            {"source": "resume", "chunk_index": i, "session_id": session_b}
            for i in range(len(chunks_b))
        ]
    )
    print(f"   ✓ Stored {len(chunks_b)} chunks for Session B")
    
    # Verify total count
    stats = vector_store.get_collection_stats()
    total_expected = len(chunks_a) + len(chunks_b)
    print(f"\n📊 Total documents in DB: {stats['count']} (expected: {total_expected})")
    
    if stats['count'] != total_expected:
        print(f"❌ ERROR: Expected {total_expected} documents but found {stats['count']}")
        return False
    
    # Test Query 1: Query Session A for "machine learning"
    print(f"\n🔍 TEST 1: Query Session A for 'machine learning'")
    results_a = vector_store.query_with_filter(
        query_text="machine learning",
        filter_dict={"session_id": session_a},
        n_results=3
    )
    
    print(f"   Results found: {len(results_a['documents'])}")
    for i, (doc, dist) in enumerate(zip(results_a['documents'], results_a['distances'])):
        print(f"   [{i+1}] {doc[:60]}... (distance: {dist:.3f})")
    
    # Verify all results are from Session A (Alice's resume, not Bob's)
    session_a_test_passed = True
    for doc in results_a['documents']:
        # Check that results don't contain Bob's content
        if "bob" in doc.lower() or "marketing" in doc.lower() or "brand strategy" in doc.lower():
            print(f"   ❌ CONTAMINATION: Found Bob's data in Alice's results: {doc}")
            session_a_test_passed = False
        else:
            # Results are from Alice's resume (correct session)
            print(f"   ✓ Correct session data: {doc[:80]}...")
    
    if session_a_test_passed and len(results_a['documents']) > 0:
        print("   ✅ Session A isolation: PASSED")
    else:
        print("   ❌ Session A isolation: FAILED")
        return False
    
    # Test Query 2: Query Session B for "marketing"
    print(f"\n🔍 TEST 2: Query Session B for 'marketing'")
    results_b = vector_store.query_with_filter(
        query_text="marketing strategy",
        filter_dict={"session_id": session_b},
        n_results=3
    )
    
    print(f"   Results found: {len(results_b['documents'])}")
    for i, (doc, dist) in enumerate(zip(results_b['documents'], results_b['distances'])):
        print(f"   [{i+1}] {doc[:60]}... (distance: {dist:.3f})")
    
    # Verify all results are from Session B (Bob's resume, not Alice's)
    session_b_test_passed = True
    for doc in results_b['documents']:
        # Check that results don't contain Alice's content
        if "alice" in doc.lower() or "python" in doc.lower() or "machine learning" in doc.lower() or "neural" in doc.lower():
            print(f"   ❌ CONTAMINATION: Found Alice's data in Bob's results: {doc}")
            session_b_test_passed = False
        else:
            # Results are from Bob's resume (correct session)
            print(f"   ✓ Correct session data: {doc[:80]}...")
    
    if session_b_test_passed and len(results_b['documents']) > 0:
        print("   ✅ Session B isolation: PASSED")
    else:
        print("   ❌ Session B isolation: FAILED")
        return False
    
    # Test Query 3: Verify Session A doesn't get Session B results
    print(f"\n🔍 TEST 3: Query Session A for 'marketing' (should find nothing relevant)")
    results_cross = vector_store.query_with_filter(
        query_text="marketing strategy",
        filter_dict={"session_id": session_a},  # Query A for B's content
        n_results=3
    )
    
    print(f"   Results found: {len(results_cross['documents'])}")
    
    # These results should be from Alice's resume (poor match for 'marketing')
    cross_contamination = False
    for doc in results_cross['documents']:
        if "bob" in doc.lower() or "brand" in doc.lower() or "customer engagement" in doc.lower():
            print(f"   ❌ CROSS-CONTAMINATION DETECTED: {doc}")
            cross_contamination = True
    
    if not cross_contamination:
        print("   ✅ Cross-contamination test: PASSED (no Bob's data in Alice's results)")
    else:
        print("   ❌ Cross-contamination test: FAILED")
        return False
    
    # Clean up test data
    print(f"\n🗑️ Cleaning up test data...")
    all_docs = vector_store.collection.get()
    test_ids = [
        doc_id for doc_id, meta in zip(all_docs["ids"], all_docs["metadatas"])
        if meta.get("session_id") in [session_a, session_b]
    ]
    
    if test_ids:
        vector_store.delete_documents(test_ids)
        print(f"   ✓ Deleted {len(test_ids)} test documents")
    
    final_stats = vector_store.get_collection_stats()
    print(f"   Final document count: {final_stats['count']}")
    
    # Overall result
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - Session isolation is working correctly!")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_session_isolation())
    sys.exit(0 if success else 1)
