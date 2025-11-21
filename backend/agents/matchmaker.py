"""
Agent D: The Matchmaker
RAG comparison between resume and scholarship values with decision gate
"""

import json
from typing import Dict, Any, List


class MatchmakerAgent:
    """
    Responsible for gap analysis:
    - Generate weighted values from scholarship intelligence
    - Query resume vector store using weighted keywords
    - Calculate match score
    - Decide whether to trigger interview mode

    Decision Gate: match_score > 0.8 → proceed, < 0.8 → interview
    """

    def __init__(self, vector_store, llm_client):
        """
        Initialize Matchmaker Agent

        Args:
            vector_store: ChromaDB vector store instance
            llm_client: LLMClient instance for reasoning
        """
        self.vector_store = vector_store
        self.llm_client = llm_client
        self.threshold = 0.8  # Match score threshold
        self.gap_threshold = 0.5  # Individual keyword gap threshold

    async def _generate_weighted_values(self, scout_intelligence: Dict) -> Dict[str, float]:
        """
        Generate weighted importance scores using LLM analysis of Scout data
        
        Args:
            scout_intelligence: Full Scout intelligence output
            
        Returns:
            Dict of value: weight (weights sum to ~1.0)
        """
        # Extract Scout data
        official = scout_intelligence["official"]
        context = scout_intelligence["past_winner_context"]
        
        # Build analysis text
        analysis_text = f"""
Scholarship: {official.get("scholarship_name", "Unknown")}

Official Values: {', '.join(official.get("primary_values", []))}
Implicit Values: {', '.join(official.get("implicit_values", []))}

Selection Emphasis:
- Leadership: {official.get("selection_emphasis", {}).get("leadership_weight", "Not specified")}
- Academic: {official.get("selection_emphasis", {}).get("academic_weight", "Not specified")}
- Service: {official.get("selection_emphasis", {}).get("service_weight", "Not specified")}

Past Winner Patterns: {len(context.get("item", []))} examples analyzed
Community Insights: {len(context.get("data", []))} data points found

Based on this analysis, determine which values matter MOST for winning this scholarship.
"""

        system_prompt = """
You are an expert scholarship analyst. Determine the RELATIVE IMPORTANCE of different values for winning this scholarship.

Based on the official requirements, selection emphasis, and past winner patterns, assign percentage weights to each value.

Rules:
1. Weights MUST sum to 1.0 (100%)
2. Higher weight = more important for winning
3. Return 4-7 most important values only
4. Return ONLY valid JSON mapping value names to float weights (no markdown, no explanations)

Example Output:
{
  "Leadership": 0.35,
  "Community Service": 0.30,
  "Academic Excellence": 0.20,
  "Innovation": 0.15
}
"""

        try:
            # Call LLM
            response_text = await self.llm_client.call(
                system_prompt=system_prompt,
                user_message=analysis_text
            )
            
            # Clean markdown fences if present
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
                
            # Parse JSON
            weights = json.loads(cleaned_text.strip())
            
            # Normalize to ensure sum = 1.0
            total = sum(weights.values())
            if total > 0:
                normalized = {k: v / total for k, v in weights.items()}
            else:
                # Fallback: equal weights
                primary_values = official.get("primary_values", ["Unknown"])
                normalized = {val: 1.0 / len(primary_values) for val in primary_values}
                
            print(f"  ✓ Generated weighted values: {', '.join(f'{k}: {v:.0%}' for k, v in normalized.items())}")
            return normalized
            
        except Exception as e:
            print(f"  ⚠ Weight generation failed: {e}")
            # Fallback: equal weights from primary values
            primary_values = official.get("primary_values", ["Unknown"])
            return {val: 1.0 / len(primary_values) for val in primary_values}

    async def _query_resume_for_keywords(self, weighted_values: Dict[str, float]) -> Dict[str, Dict]:
        """
        Query resume vector store for each weighted keyword
        
        Args:
            weighted_values: Dict mapping keywords to their importance weights
            
        Returns:
            Dict mapping each keyword to its match data:
                - best_match_score: float (0-1, higher is better)
                - matching_chunks: List[str] (top matching resume sections)
                - weight: float (importance weight)
        """
        results = {}
        
        for keyword, weight in weighted_values.items():
            # Query ChromaDB for this keyword
            query_result = self.vector_store.query(
                query_text=keyword,
                n_results=3  # Top 3 matching chunks
            )
            
            # Convert distance to similarity score
            # ChromaDB returns distances where 0 = perfect match, higher = worse
            # We convert to 0-1 scale where 1 = perfect match
            if query_result["distances"] and len(query_result["distances"]) > 0:
                best_distance = min(query_result["distances"])
                # Conversion formula: score = 1 / (1 + distance)
                # This maps: distance=0 → score=1.0, distance=1 → score=0.5, distance=inf → score=0.0
                best_match_score = 1.0 / (1.0 + best_distance)
            else:
                best_match_score = 0.0
            
            results[keyword] = {
                "best_match_score": best_match_score,
                "matching_chunks": query_result.get("documents", [])[:2],  # Top 2 chunks only
                "weight": weight
            }
            
            print(f"  → {keyword}: {best_match_score:.0%} match (weight: {weight:.0%})")
        
        return results

    def _calculate_overall_score(self, keyword_results: Dict[str, Dict]) -> float:
        """
        Calculate weighted average match score
        
        Args:
            keyword_results: Results from _query_resume_for_keywords
            
        Returns:
            Overall match score (0.0-1.0)
        """
        total_score = 0.0
        
        for keyword, data in keyword_results.items():
            match_score = data["best_match_score"]
            weight = data["weight"]
            contribution = match_score * weight
            total_score += contribution
        
        return total_score

    def _identify_gaps(self, keyword_results: Dict[str, Dict]) -> List[str]:
        """
        Identify keywords with low match scores (gaps to address)
        
        Args:
            keyword_results: Results from _query_resume_for_keywords
            
        Returns:
            List of keyword names with match scores below gap threshold,
            sorted by importance (weight) descending
        """
        gaps = []
        
        # Sort by weight (importance) descending
        sorted_keywords = sorted(
            keyword_results.items(),
            key=lambda x: x[1]["weight"],
            reverse=True
        )
        
        for keyword, data in sorted_keywords:
            if data["best_match_score"] < self.gap_threshold:
                gaps.append(keyword)
        
        return gaps

    async def run(self, scout_intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Matchmaker Agent workflow
        
        Args:
            scout_intelligence: Full Scout intelligence output
            
        Returns:
            Dict containing:
                - match_score: float (0.0-1.0)
                - trigger_interview: bool (True if score < 0.8)
                - gaps: List[str] (missing/weak keywords)
                - weighted_values: Dict[str, float] (generated weights)
                - keyword_match_details: Dict (full match data for debugging)
        """
        print("\n" + "=" * 60)
        print("🎯 Matchmaker Agent: Starting gap analysis...")
        print("=" * 60)
        
        # STEP 1: Generate weighted values
        print("\n[STEP 1] Analyzing scholarship importance weights...")
        weighted_values = await self._generate_weighted_values(scout_intelligence)
        
        # STEP 2: Query resume for each keyword
        print("\n[STEP 2] Querying resume for keyword matches...")
        keyword_results = await self._query_resume_for_keywords(weighted_values)
        
        # STEP 3: Calculate overall match score
        print("\n[STEP 3] Calculating overall match score...")
        overall_score = self._calculate_overall_score(keyword_results)
        print(f"  ✓ Overall Match Score: {overall_score:.0%}")
        
        # STEP 4: Identify gaps
        gaps = self._identify_gaps(keyword_results)
        
        # STEP 5: Decision gate
        trigger_interview = overall_score < self.threshold
        
        print("\n" + "=" * 60)
        if trigger_interview:
            print(f"⚠️  Match Score ({overall_score:.0%}) below threshold ({self.threshold:.0%})")
            print(f"→ INTERVIEW TRIGGERED")
            print(f"→ Gaps detected: {', '.join(gaps)}")
        else:
            print(f"✅ Match Score ({overall_score:.0%}) above threshold ({self.threshold:.0%})")
            print(f"→ Proceeding to generation")
        print("=" * 60)
        
        # Return complete result
        return {
            "match_score": overall_score,
            "trigger_interview": trigger_interview,
            "gaps": gaps,
            "weighted_values": weighted_values,
            "keyword_match_details": keyword_results
        }
