#!/usr/bin/env python3
"""
Test script to demonstrate EXACT data available to Optimizer and Ghostwriter
Shows precise field names and data structures at each stage
"""

import asyncio
import sys
import json
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.vector_store import VectorStore
from utils.llm_client import create_llm_client
from agents.scout import ScoutAgent
from agents.profiler import ProfilerAgent
from agents.decoder import DecoderAgent
from agents.matchmaker import MatchmakerAgent
from agents.optimizer import OptimizerAgent
from agents.ghostwriter import GhostwriterAgent
from config.settings import settings


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


async def main():
    print_section("DATA TRACE: What Optimizer & Ghostwriter Actually Receive")
    
    # Initialize components
    vector_store = VectorStore(
        collection_name="resumes",
        persist_directory=str(settings.chroma_dir)
    )
    llm_client = create_llm_client()
    
    # Create mock session
    session_id = "trace-demo-session-123"
    
    # ====================
    # PHASE 1: RESUME DATA
    # ====================
    print_section("PHASE 1: Resume Processing (Profiler)")
    
    # Simulate resume text (in real flow, this comes from PDF parsing)
    resume_text = """
    JANE DOE
    Email: jane.doe@example.com | LinkedIn: linkedin.com/in/janedoe
    
    EDUCATION
    Bachelor of Science in Community Development, State University (2020-2024)
    GPA: 3.9/4.0
    
    EXPERIENCE
    Volunteer Coordinator, Local Food Bank (2022-Present)
    - Led team of 50 volunteers in weekly food distribution programs
    - Served 200+ families per month through community outreach
    - Increased volunteer retention by 40% through mentorship program
    
    Campus Community Service Leader (2021-2023)
    - Founded campus-wide volunteer initiative with 300+ student participants
    - Organized 12 community service events annually
    - Partnered with 5 local nonprofits for sustainable impact
    
    SKILLS
    Leadership, Community Organizing, Volunteer Management, Public Speaking
    """
    
    print("Resume text stored in state:")
    print(f"  state['resume_text'] = '''")
    print(f"{resume_text[:300]}...")
    print(f"  '''")
    print(f"\n  Length: {len(resume_text)} characters")
    
    # Store chunks in vector DB (this is what Profiler does)
    chunks = [
        "Jane Doe - Community Development graduate with extensive volunteer coordination experience",
        "Led team of 50 volunteers at Local Food Bank serving 200+ families monthly",
        "Founded campus volunteer initiative engaging 300+ students in community service",
        "Partnered with 5 local nonprofits for sustainable community impact projects",
        "Expertise in leadership, community organizing, and volunteer management"
    ]
    
    vector_store.add_documents(
        documents=chunks,
        metadatas=[
            {"source": "resume", "chunk_index": i, "session_id": session_id}
            for i in range(len(chunks))
        ]
    )
    print(f"\n  ✓ Stored {len(chunks)} chunks in ChromaDB with session_id filter")
    
    # ====================
    # PHASE 2: SCOUT DATA
    # ====================
    print_section("PHASE 2: Scholarship Intelligence (Scout)")
    
    # Simulate Scout output (in real flow, this comes from web scraping)
    scholarship_intelligence = {
        "official": {
            "scholarship_name": "Gates Millennium Scholarship",
            "organization": "Bill & Melinda Gates Foundation",
            "primary_values": ["Leadership", "Community Service", "Academic Excellence"],
            "implicit_values": ["Perseverance", "Social Justice", "Innovation"],
            "tone_indicators": "Inspirational and personal, emphasizing transformation",
            "keywords": ["leadership", "community", "service", "impact", "achievement"],
            "eligibility_criteria": {
                "gpa_requirement": 3.3,
                "grade_levels": ["High School Senior", "College Undergraduate"],
                "citizenship": ["U.S. Citizen", "Legal Permanent Resident"]
            },
            "award_amount": "$10,000 per year",
            "deadline": "March 15, 2025"
        },
        "past_winner_context": {
            "item": [
                {
                    "title": "2023 Winner Essay - Maria Rodriguez",
                    "key_takeaways": [
                        "Led grassroots initiative serving immigrant community",
                        "Emphasized personal growth arc from challenges to leadership",
                        "Quantified impact: 500+ families served over 2 years"
                    ],
                    "validation_score": 0.92
                },
                {
                    "title": "Winner Profile - James Chen",
                    "key_takeaways": [
                        "Founded nonprofit addressing food insecurity",
                        "Connected personal story to community values",
                        "Demonstrated sustained 4-year commitment"
                    ],
                    "validation_score": 0.88
                }
            ],
            "data": [
                {
                    "type": "tip",
                    "content": "Successful applicants emphasize measurable community impact and long-term commitment",
                    "credibility": "PrepScholar Guide",
                    "validation_score": 0.85
                },
                {
                    "type": "insight",
                    "content": "Selection committee values authentic personal narratives over generic accomplishment lists",
                    "credibility": "Past Winner Interview (Reddit)",
                    "validation_score": 0.78
                }
            ],
            "search_summary": {
                "total_items_found": 15,
                "items_after_validation": 2
            }
        },
        "combined_text": "# Gates Millennium Scholarship\n## Primary Values\nLeadership, Community Service, Academic Excellence\n\n## Past Winner Examples\n### 2023 Winner - Grassroots initiative serving 500+ families\n- Key Takeaways: Quantified impact, Personal growth arc...\n\n## Winning Strategies & Tips\n- Emphasize measurable community impact and long-term commitment"
    }
    
    print("Scholarship intelligence stored in state:")
    print(f"  state['scholarship_intelligence'] = {{")
    print(f"    'official': {{")
    print(f"      'scholarship_name': '{scholarship_intelligence['official']['scholarship_name']}'")
    print(f"      'primary_values': {scholarship_intelligence['official']['primary_values']}")
    print(f"      'tone_indicators': '{scholarship_intelligence['official']['tone_indicators']}'")
    print(f"      ... (full official data)")
    print(f"    }},")
    print(f"    'past_winner_context': {{")
    print(f"      'item': [{len(scholarship_intelligence['past_winner_context']['item'])} winner examples],")
    print(f"      'data': [{len(scholarship_intelligence['past_winner_context']['data'])} insights/tips]")
    print(f"    }},")
    print(f"    'combined_text': '# Gates Millennium... (markdown summary)'")
    print(f"  }}")
    
    # ====================
    # PHASE 3: DECODER ANALYSIS
    # ====================
    print_section("PHASE 3: Decoder Analysis (Weights & Values)")
    
    # Simulate Decoder output (extracted from Scout intelligence)
    decoder_analysis = {
        "primary_values": ["Leadership", "Community Service", "Academic Excellence", "Social Impact"],
        "hidden_weights": {
            "Community Service": 0.40,  # Highest priority from Scout analysis
            "Leadership": 0.30,
            "Social Impact": 0.20,
            "Academic Excellence": 0.10
        },
        "tone": "Inspirational and personal, emphasizing transformation and authentic narratives",
        "missing_evidence_query": "Tell me about a time when you demonstrated leadership in community service"
    }
    
    print("Decoder output stored in state:")
    print(f"  state['decoder_analysis'] = {{")
    print(f"    'primary_values': {decoder_analysis['primary_values']}")
    print(f"    'hidden_weights': {{")
    for key, weight in decoder_analysis['hidden_weights'].items():
        print(f"      '{key}': {weight:.2f} ({weight*100:.0f}%)")
    print(f"    }},")
    print(f"    'tone': '{decoder_analysis['tone']}'")
    print(f"  }}")
    
    # ====================
    # PHASE 4: MATCHMAKER (uses Decoder + Vector DB)
    # ====================
    print_section("PHASE 4: Matchmaker (Gap Detection)")
    
    matchmaker = MatchmakerAgent(vector_store, llm_client)
    matchmaker_result = await matchmaker.run(decoder_analysis, session_id=session_id)
    
    print(f"Matchmaker result stored in state:")
    print(f"  state['match_score'] = {matchmaker_result['match_score']:.2f}")
    print(f"  state['trigger_interview'] = {matchmaker_result['trigger_interview']}")
    print(f"  state['identified_gaps'] = {matchmaker_result['gaps']}")
    
    # ====================
    # PHASE 5: INTERVIEW (OPTIONAL - Bridge Story)
    # ====================
    print_section("PHASE 5: Interview Bridge Story (If Triggered)")
    
    # Simulate bridge story (from interview synthesis)
    bridge_story = """My journey in community service began when I witnessed food insecurity firsthand in my neighborhood. I started volunteering at our local food bank, and what began as simple meal distribution evolved into a leadership opportunity. Over two years, I've grown from a single volunteer to coordinating a team of 50 people serving over 200 families each month."""
    
    print("Interview synthesis stored in state:")
    print(f"  state['bridge_story'] = '{bridge_story[:150]}...'")
    print(f"\n  (Note: This is OPTIONAL - only if interview was triggered)")
    
    # ====================
    # PHASE 6: OPTIMIZER INPUT
    # ====================
    print_section("PHASE 6: OPTIMIZER - Exact Input Data")
    
    print("When Optimizer.run() is called:")
    print(f"\nOptimizer.run(resume_text, decoder_output)") 
    print(f"\nParameter 1 - resume_text:")
    print(f"  = state['resume_text']")
    print(f"  Type: str")
    print(f"  Value: '{resume_text[:100]}...'")
    
    print(f"\nParameter 2 - decoder_output:")
    print(f"  = state['decoder_analysis']")
    print(f"  Type: Dict")
    print(f"  Keys: {list(decoder_analysis.keys())}")
    print(f"\n  decoder_output['primary_values'] = {decoder_analysis['primary_values']}")
    print(f"  decoder_output['hidden_weights'] = {decoder_analysis['hidden_weights']}")
    print(f"  decoder_output['tone'] = '{decoder_analysis['tone']}'")
    
    # ====================
    # PHASE 7: GHOSTWRITER INPUT
    # ====================
    print_section("PHASE 7: GHOSTWRITER - Exact Input Data")
    
    print("When Ghostwriter.run() is called:")
    print(f"\nGhostwriter.run(decoder_output, resume_text, bridge_story)")
    
    print(f"\nParameter 1 - decoder_output:")
    print(f"  = state['decoder_analysis']  (Same as Optimizer)")
    
    print(f"\nParameter 2 - resume_text:")
    print(f"  = state['resume_text']  (Same as Optimizer)") 
    
    print(f"\nParameter 3 - bridge_story:")
    print(f"  = state.get('bridge_story')  (May be None)")
    print(f"  Value: '{bridge_story[:100]}...'")
    
    print("\n✅ SUMMARY:")
    print("Optimizer has: resume + weights + values + tone")
    print("Ghostwriter has: resume + weights + values + tone + bridge_story")
    
    # Cleanup
    print_section("Cleanup")
    all_docs = vector_store.collection.get(where={"session_id": session_id})
    if all_docs["ids"]:
        vector_store.delete_documents(all_docs["ids"])
        print(f"✓ Deleted {len(all_docs['ids'])} test chunks")


if __name__ == "__main__":
    asyncio.run(main())
