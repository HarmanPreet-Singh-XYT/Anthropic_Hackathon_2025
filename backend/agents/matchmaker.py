"""
Agent D: The Matchmaker
RAG comparison between resume and scholarship values with decision gate
"""

import json
from typing import Dict, Any, List, Tuple


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
        self.threshold = 0.7  # Match score threshold (raised to ensure high quality)
        self.gap_threshold = 0.65  # Individual keyword gap threshold

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

    async def _query_resume_for_keywords(
        self, 
        weighted_values: Dict[str, float],
        session_id: str
    ) -> Dict[str, Dict]:
        """
        Query resume vector store for each weighted keyword
        
        Args:
            weighted_values: Dict mapping keywords to their importance weights
            session_id: Session identifier to filter queries
            
        Returns:
            Dict mapping each keyword to its match data:
                - best_match_score: float (0-1, higher is better)
                - matching_chunks: List[str] (top matching resume sections)
                - weight: float (importance weight)
        """
        results = {}
        
        print(f"🔍 [MatchmakerAgent] Querying vector DB for session: {session_id}")
        
        for keyword, weight in weighted_values.items():
            # Query ChromaDB for this keyword, filtered by session
            query_result = self.vector_store.query_with_filter(
                query_text=keyword,
                filter_dict={"session_id": session_id},  # Session isolation
                n_results=3  # Top 3 matching chunks
            )
            
            # Convert distance to similarity score
            # ChromaDB returns distances where 0 = perfect match, higher = worse
            # We convert to 0-1 scale where 1 = perfect match
            if query_result["distances"] and len(query_result["distances"]) > 0:
                best_distance = min(query_result["distances"])
                # Conversion formula: score = 1 / (1 + distance * 0.5)
                # This maps: distance=0 → score=1.0, distance=1 → score=0.66, distance=1.5 → score=0.57
                # We use a very flat curve to ensure we get some signal
                best_match_score = 1.0 / (1.0 + best_distance * 0.5)
            else:
                best_match_score = 0.0

            # Extract matching text chunks
            matching_chunks = query_result.get("documents", [[]])[0] if query_result.get("documents") else []

            results[keyword] = {
                "best_match_score": best_match_score,
                "matching_chunks": matching_chunks,
                "weight": weight
            }
            
            raw_dist = best_distance if 'best_distance' in locals() else "N/A"
            print(f"  → {keyword} (weight: {weight:.0%}): match score = {best_match_score:.2f} (dist: {raw_dist}) [session: {session_id}]")

        return results

    async def query_resume(self, criteria: str) -> Tuple[List[str], float]:
        """
        Search resume for evidence of a specific criteria

        Args:
            criteria: Scholarship value or requirement

        Returns:
            Tuple of (evidence_snippets, max_relevance_score)
        """
        # Query vector store
        results = self.vector_store.query(query_text=criteria, n_results=3)
        
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        if not documents:
            return [], 0.0
            
        # Convert distance to similarity score (approximate)
        # ChromaDB default is L2 distance. Lower is better.
        # We'll invert it for a 0-1 similarity score.
        # This is a heuristic; cosine distance would be 0-2.
        # Assuming L2 on normalized vectors, range is 0-2.
        # Similarity = 1 - (distance / 2)
        
        # Let's use a simple inverse distance heuristic for now
        # If distance is 0 (perfect match), score is 1.
        # If distance is large (>1.5), score approaches 0.
        
        best_distance = distances[0] if distances else 1.0
        relevance_score = max(0.0, 1.0 - (best_distance / 2.0))
        
        return documents, relevance_score

    async def calculate_match_score(
        self,
        weights: Dict[str, float],
        evidence_scores: Dict[str, float]
    ) -> float:
        """
        Calculate weighted match score

        Args:
            weights: Criteria weights from Decoder
            evidence_scores: Relevance scores for each criteria

        Returns:
            Weighted average score (0.0 - 1.0)
        """
        total_score = 0.0
        total_weight = 0.0
        
        for category, weight in weights.items():
            score = evidence_scores.get(category, 0.0)
            total_score += score * weight
            total_weight += weight
            
        if total_weight == 0:
            return 0.0
            
        return total_score / total_weight

    async def identify_gaps(
        self,
        weights: Dict[str, float],
        evidence_scores: Dict[str, float],
        threshold: float = 0.4
    ) -> List[str]:
        """
        Identify high-value criteria with low evidence

        Args:
            weights: Criteria weights
            evidence_scores: Evidence relevance scores
            threshold: Score below which is considered a gap

        Returns:
            List of missing criteria names
        """
        gaps = []
        for category, weight in weights.items():
            score = evidence_scores.get(category, 0.0)
            # A gap is significant if it has high weight (>0.1) AND low score
            if weight > 0.1 and score < threshold:
                gaps.append(category)
                
        # Sort gaps by weight (highest priority first)
        gaps.sort(key=lambda x: weights.get(x, 0), reverse=True)
        return gaps

    def _calculate_overall_score(self, keyword_results: Dict[str, Dict]) -> float:
        """
        Calculate weighted overall match score

        Args:
            keyword_results: Results from _query_resume_for_keywords

        Returns:
            Overall weighted match score (0-1)
        """
        total_weighted_score = 0.0
        total_weight = 0.0

        for keyword, data in keyword_results.items():
            score = data["best_match_score"]
            weight = data["weight"]
            total_weighted_score += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return total_weighted_score / total_weight

    def _identify_gaps(self, keyword_results: Dict[str, Dict]) -> List[str]:
        """
        Identify keywords with low match scores relative to their importance

        Args:
            keyword_results: Results from _query_resume_for_keywords

        Returns:
            List of keywords that are gaps (high importance, low match)
        """
        gaps = []

        for keyword, data in keyword_results.items():
            score = data["best_match_score"]
            weight = data["weight"]

            # Gap if high weight (>10% importance) but low score (<threshold)
            if weight > 0.1 and score < self.gap_threshold:
                gaps.append(keyword)

        # Sort by importance (weight)
        gaps.sort(key=lambda k: keyword_results[k]["weight"], reverse=True)
        return gaps

    async def run(
        self,
        decoder_analysis: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute Matchmaker Agent workflow

        Args:
            decoder_analysis: Output from Decoder Agent containing weights
            session_id: Session identifier for filtering vector queries

        Returns:
            Dict containing:
                - match_score: float (0-1 overall match)
                - trigger_interview: bool
                - gaps: List[str] (missing criteria)
                - weighted_values: Dict[str, float]
                - keyword_match_details: Dict
        """
        # STEP 1: Get weighted values from Decoder
        print("\n[STEP 1] Analyzing scholarship importance weights...")
        
        # Use weights directly from Decoder if available
        if "hidden_weights" in decoder_analysis:
            weighted_values = decoder_analysis["hidden_weights"]
            if weighted_values:
                print(f"  ✓ Using weights from Decoder: {', '.join(f'{k}: {v:.0%}' for k, v in weighted_values.items())}")
            else:
                print("  ⚠ Decoder returned empty weights dict")
                weighted_values = {}
        else:
            # Fallback (shouldn't happen in normal flow)
            print("  ⚠ No weights found in Decoder output, using defaults")
            weighted_values = {}

        # STEP 2: Query resume for each keyword
        print("\n[STEP 2] Querying resume for keyword matches...")
        
        if not weighted_values:
            print("  ⚠ No weighted values available - cannot perform keyword matching")
            print("  → This likely means the Decoder failed. Check Decoder logs above.")
            keyword_results = {}
        else:
            keyword_results = await self._query_resume_for_keywords(weighted_values, session_id)
        
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
