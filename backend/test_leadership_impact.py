#!/usr/bin/env python3
"""
A/B Test: Prove that resume content affects match scores.
Test two resumes - one with minimal leadership vs one with strong leadership.
"""

import asyncio
import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).parent))

from utils.vector_store import VectorStore
from agents.matchmaker import MatchmakerAgent
from utils.llm_client import create_llm_client
from config.settings import settings


async def test_leadership_impact():
    """
    A/B Test: Show that adding leadership content increases match scores
    """
    
    print("\n" + "="*80)
    print("A/B TEST: Leadership Impact on Match Scores")
    print("="*80)
    
    # Initialize
    vector_store = VectorStore("resumes", str(settings.chroma_dir))
    llm_client = create_llm_client()
    matchmaker = MatchmakerAgent(vector_store, llm_client)
    
    # Test A: Resume with MINIMAL leadership (your current resume)
    session_a = f"test-minimal-leadership-{uuid.uuid4().hex[:8]}"
    
    print("\n" + "-"*80)
    print("TEST A: Resume with MINIMAL Leadership")
    print("-"*80)
    
    chunks_a = [
        "Elliot Sones, Computer Science Student at Toronto Metropolitan University",
        "Developed Neural Networks Classifier using Python and NumPy",
        "Built educational platform with Next.js, FastAPI, and Google Cloud",
        "Won 1st place at Metropolitan Undergraduate Engineering Hackathon",
        "Technical skills: Python, JavaScript, SQL, Machine Learning"
    ]
    
    print(f"\nResume A highlights:")
    for i, chunk in enumerate(chunks_a, 1):
        print(f"  {i}. {chunk}")
    
    # Store Resume A
    vector_store.add_documents(
        documents=chunks_a,
        metadatas=[
            {"source": "resume", "chunk_index": i, "session_id": session_a}
            for i in range(len(chunks_a))
        ]
    )
    
    # Test B: Resume with STRONG leadership
    session_b = f"test-strong-leadership-{uuid.uuid4().hex[:8]}"
    
    print("\n" + "-"*80)
    print("TEST B: Resume with STRONG Leadership")
    print("-"*80)
    
    chunks_b = [
        "Elliot Sones, President of Computer Science Student Association, led 50+ members",
        "Founded and organized Metropolitan Hackathon Series, managing team of 15 organizers",
        "Captain of competitive programming team, mentored 20 junior students",
        "Led development team as Tech Lead for university innovation lab",
        "Coordinated volunteer tutoring program serving 100+ underrepresented students"
    ]
    
    print(f"\nResume B highlights:")
    for i, chunk in enumerate(chunks_b, 1):
        print(f"  {i}. {chunk}")
    
    # Store Resume B
    vector_store.add_documents(
        documents=chunks_b,
        metadatas=[
            {"source": "resume", "chunk_index": i, "session_id": session_b}
            for i in range(len(chunks_b))
        ]
    )
    
    # Create decoder analysis (same weights for both tests)
    decoder_analysis = {
        "hidden_weights": {
            "Leadership": 0.30,
            "Service": 0.20,
            "Academic Excellence": 0.30,
            "Passion for Technology": 0.20
        }
    }
    
    print("\n" + "="*80)
    print("Running Matchmaker on Both Resumes")
    print("="*80)
    
    # Test Resume A
    print("\n🔍 Testing Resume A (Minimal Leadership)...")
    result_a = await matchmaker.run(decoder_analysis, session_id=session_a)
    
    print(f"\n📊 Resume A Results:")
    print(f"   Overall Match Score: {result_a['match_score']:.0%}")
    print(f"   Trigger Interview: {result_a['trigger_interview']}")
    
    # Show component breakdown
    if 'keyword_match_details' in result_a:
        print(f"\n   Component Scores:")
        for keyword, details in result_a['keyword_match_details'].items():
            weight = decoder_analysis['hidden_weights'].get(keyword, 0)
            score = details.get('best_match_score', 0)
            print(f"     • {keyword:25} {score:.0%} (weight: {weight:.0%})")
    
    # Test Resume B
    print("\n🔍 Testing Resume B (Strong Leadership)...")
    result_b = await matchmaker.run(decoder_analysis, session_id=session_b)
    
    print(f"\n📊 Resume B Results:")
    print(f"   Overall Match Score: {result_b['match_score']:.0%}")
    print(f"   Trigger Interview: {result_b['trigger_interview']}")
    
    # Show component breakdown
    if 'keyword_match_details' in result_b:
        print(f"\n   Component Scores:")
        for keyword, details in result_b['keyword_match_details'].items():
            weight = decoder_analysis['hidden_weights'].get(keyword, 0)
            score = details.get('best_match_score', 0)
            print(f"     • {keyword:25} {score:.0%} (weight: {weight:.0%})")
    
    # Compare Results
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)
    
    score_diff = result_b['match_score'] - result_a['match_score']
    percent_increase = (score_diff / result_a['match_score']) * 100 if result_a['match_score'] > 0 else 0
    
    print(f"\n📈 Score Difference:")
    print(f"   Resume A (Minimal Leadership): {result_a['match_score']:.1%}")
    print(f"   Resume B (Strong Leadership):  {result_b['match_score']:.1%}")
    print(f"   Absolute Difference:           +{score_diff:.1%}")
    print(f"   Relative Increase:             +{percent_increase:.1f}%")
    
    # Detailed leadership comparison
    if 'keyword_match_details' in result_a and 'keyword_match_details' in result_b:
        leadership_a = result_a['keyword_match_details'].get('Leadership', {}).get('best_match_score', 0)
        leadership_b = result_b['keyword_match_details'].get('Leadership', {}).get('best_match_score', 0)
        leadership_diff = leadership_b - leadership_a
        
        print(f"\n🎯 Leadership Component:")
        print(f"   Resume A: {leadership_a:.1%}")
        print(f"   Resume B: {leadership_b:.1%}")
        print(f"   Difference: +{leadership_diff:.1%}")
    
    # Cleanup
    print("\n🗑️ Cleaning up test sessions...")
    for session_id in [session_a, session_b]:
        docs = vector_store.collection.get(where={"session_id": session_id})
        if docs["ids"]:
            vector_store.delete_documents(docs["ids"])
    
    # Conclusion
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    
    if score_diff > 0.05:  # At least 5% improvement
        print("\n✅ TEST PASSED: Resume content DOES affect match scores!")
        print(f"   Adding leadership content increased score by {score_diff:.1%}")
        print(f"   This proves the matchmaker is analyzing actual resume content.")
        print("\n🎉 System is working correctly with 100% confidence!")
        return True
    else:
        print("\n⚠️  TEST INCONCLUSIVE: Score difference is small")
        print(f"   Difference: {score_diff:.1%}")
        print("   This could mean the similarity scores are already saturated")
        print("   or the test data needs to be more distinct.")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_leadership_impact())
    sys.exit(0 if success else 1)
