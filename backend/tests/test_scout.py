"""
Test script for Scout Agent
Tests Firecrawl integration with real scholarship URL
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.scout import ScoutAgent


async def test_scout_agent():
    """Test Scout Agent with real scholarship URL"""

    # Load environment variables
    load_dotenv()

    # Test URL - Coca-Cola Scholars Program
    test_url = "https://www.coca-colascholarsfoundation.org/apply/"

    print("=" * 70)
    print("SCOUT AGENT TEST")
    print("=" * 70)
    print(f"\nTest URL: {test_url}")
    print(f"Firecrawl API Key: {'✓ Found' if os.getenv('FIRECRAWL_API_KEY') else '✗ Missing'}")
    print("\n" + "=" * 70)

    try:
        # Initialize Scout Agent
        scout = ScoutAgent()

        # Run Scout workflow with debug enabled
        result = await scout.run(test_url, debug=True)

        # Display results
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)

        # Official data
        official = result['scholarship_intelligence']['official']
        print(f"\n📋 Scholarship Name: {official['scholarship_name']}")
        print(f"🎯 Primary Values: {', '.join(official['primary_values'])}")
        print(f"📊 Tone: {official['tone_indicators']}")

        # Past winner items
        items = result['scholarship_intelligence']['past_winner_context']['item']
        print(f"\n📝 Past Winner Items Found: {len(items)}")
        if items:
            for i, item in enumerate(items[:3], 1):
                print(f"  {i}. {item['title']} (Score: {item['validation_score']:.0%})")
                print(f"     URL: {item['url'][:80]}...")

        # Community insights
        insights = result['scholarship_intelligence']['past_winner_context']['data']
        print(f"\n💡 Community Insights Found: {len(insights)}")
        if insights:
            for i, insight in enumerate(insights[:3], 1):
                print(f"  {i}. [{insight['source'].upper()}] {insight['type']}")
                print(f"     {insight['content'][:100]}...")
                print(f"     Score: {insight['validation_score']:.0%}")

        # Summary
        summary = result['scholarship_intelligence']['past_winner_context']['search_summary']
        print(f"\n📊 Search Summary:")
        print(f"  - Total items found: {summary['total_items_found']}")
        print(f"  - Items after validation: {summary['items_after_validation']}")
        print(f"  - Total insights found: {summary['total_data_points_found']}")
        print(f"  - Insights after validation: {summary['data_after_validation']}")
        print(f"  - Average validation score: {summary['average_validation_score']:.0%}")

        # Combined text preview
        print(f"\n📄 Combined Intelligence (preview):")
        print("-" * 70)
        print(result['combined_text'][:500] + "...")
        print("-" * 70)

        # Save full output to JSON
        output_file = Path(__file__).parent / "test_output.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n💾 Full output saved to: {output_file}")

        print("\n" + "=" * 70)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ TEST FAILED")
        print("=" * 70)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_scout_agent())
