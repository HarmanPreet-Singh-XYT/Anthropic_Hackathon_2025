"""
backend/drafting_engine/content_selector.py
Ranks and selects student experiences by relevance to scholarship priorities
"""

import json
import re
from typing import Dict, Any, List, Optional
from utils.llm_client import create_llm_client


class ContentSelector:
    """
    Intelligently selects and ranks student experiences for scholarship essays
    """
    
    def __init__(self, temperature: float = 0.3):
        """
        Initialize ContentSelector with LLM client
        
        Args:
            temperature: Sampling temperature (lower for consistent scoring)
        """
        self.llm = create_llm_client(temperature=temperature)
    
    async def select_content(
        self,
        scholarship_profile: Dict[str, Any],
        student_kb: Any,  # Vector DB or knowledge base interface
        strategy: Optional[str] = "weighted"
    ) -> Dict[str, Any]:
        """
        Rank student experiences by relevance to scholarship
        
        Args:
            scholarship_profile: Scholarship priorities and values
            student_kb: Student knowledge base (vector DB or similar)
            strategy: Selection strategy ("weighted", "diverse", "focused")
        
        Returns:
            Dictionary with primary story, supporting stories, and stories to avoid
        """
        
        # Get scholarship priorities with weights
        priorities = scholarship_profile.get('weighted_priorities', {})
        # Example: {"leadership": 0.35, "innovation": 0.30, "community": 0.25, "academic": 0.10}
        
        if not priorities:
            # Fallback to unweighted priorities
            priority_list = scholarship_profile.get('priorities', [])
            priorities = {p: 1.0 / len(priority_list) for p in priority_list}
        
        # Query vector DB for relevant experiences
        candidate_stories = []
        seen_story_ids = set()
        
        for priority, weight in priorities.items():
            # Query KB for experiences related to this priority
            stories = student_kb.query(priority, top_k=5)
            
            for story in stories:
                # Avoid duplicate stories
                story_id = story.get('id') or hash(str(story.get('text', '')))
                if story_id in seen_story_ids:
                    continue
                seen_story_ids.add(story_id)
                
                # Calculate relevance score using LLM
                relevance_score = await self.calculate_relevance(
                    story=story,
                    priority=priority,
                    weight=weight,
                    scholarship_profile=scholarship_profile
                )
                
                candidate_stories.append({
                    "story": story,
                    "priority": priority,
                    "score": relevance_score,
                    "weight": weight,
                    "story_id": story_id
                })
        
        # Rank stories based on strategy
        if strategy == "diverse":
            ranked_stories = self._diverse_ranking(candidate_stories, priorities)
        elif strategy == "focused":
            ranked_stories = self._focused_ranking(candidate_stories, priorities)
        else:  # weighted (default)
            ranked_stories = sorted(candidate_stories, key=lambda x: x['score'], reverse=True)
        
        # Get detailed analysis of top story
        if ranked_stories:
            primary_analysis = await self._analyze_story_fit(
                ranked_stories[0]['story'],
                scholarship_profile
            )
        else:
            primary_analysis = {}
        
        return {
            "primary_story": {
                **ranked_stories[0],
                "analysis": primary_analysis
            } if ranked_stories else None,
            "supporting_stories": ranked_stories[1:4] if len(ranked_stories) > 1 else [],
            "avoid_stories": ranked_stories[-3:] if len(ranked_stories) > 3 else [],
            "all_candidates": ranked_stories,
            "selection_strategy": strategy,
            "total_candidates_evaluated": len(candidate_stories)
        }
    
    async def calculate_relevance(
        self,
        story: Dict[str, Any],
        priority: str,
        weight: float,
        scholarship_profile: Dict[str, Any]
    ) -> float:
        """
        Score story relevance using LLM evaluation
        
        Args:
            story: Student experience/story
            priority: Scholarship priority being evaluated
            weight: Priority weight in overall scoring
            scholarship_profile: Full scholarship context
        
        Returns:
            Weighted relevance score (0.0-10.0)
        """
        
        system_prompt = """You are an expert scholarship evaluator. Rate how well student experiences demonstrate specific values and priorities. Be objective and evidence-based in your scoring. You must return ONLY valid JSON with no additional text or markdown."""
        
        story_text = story.get('text', story.get('description', str(story)))
        value_desc = scholarship_profile.get('value_descriptions', {}).get(priority, 'Not specified')
        
        user_message = f"""Rate how well this experience demonstrates {priority}.

EXPERIENCE:
{story_text}

SCHOLARSHIP CONTEXT:
Name: {scholarship_profile.get('name', 'N/A')}
Mission: {scholarship_profile.get('mission', 'N/A')}
What they value in {priority}: {value_desc}

EVALUATION CRITERIA:
1. Direct Evidence: Does the experience directly demonstrate {priority}?
2. Impact/Outcomes: Are there measurable results or meaningful outcomes?
3. Specificity: Is the experience described with concrete details?
4. Authenticity: Does it feel genuine and personal?
5. Alignment: Does it match what this scholarship values in {priority}?

Return ONLY this JSON structure (no markdown, no code blocks):
{{
    "raw_score": 8.5,
    "evidence_score": 9.0,
    "impact_score": 8.0,
    "specificity_score": 8.5,
    "authenticity_score": 9.0,
    "alignment_score": 8.0,
    "reasoning": "Brief explanation of score",
    "key_strengths": ["strength 1", "strength 2"],
    "key_weaknesses": ["weakness 1"]
}}"""
        
        try:
            score_json = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            # Debug: Print raw response
            print(f"\n[DEBUG] Raw LLM response for {priority}:")
            print(f"Response length: {len(score_json) if score_json else 0}")
            print(f"First 200 chars: {score_json[:200] if score_json else 'EMPTY'}")
            
            if not score_json or not score_json.strip():
                print(f"[WARNING] Empty response from LLM for {priority}")
                return 5.0 * weight
            
            # Clean response - remove markdown code blocks if present
            cleaned_json = self._clean_json_response(score_json)
            
            # Parse JSON
            score_data = json.loads(cleaned_json)
            raw_score = score_data.get('raw_score', 5.0)
            
            # Validate score is numeric
            if not isinstance(raw_score, (int, float)):
                print(f"[WARNING] Invalid raw_score type: {type(raw_score)}")
                raw_score = 5.0
            
            # Apply priority weight
            weighted_score = float(raw_score) * weight
            
            print(f"[DEBUG] Parsed score: raw={raw_score}, weighted={weighted_score:.2f}")
            
            return weighted_score
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parsing failed for {priority}: {e}")
            print(f"[ERROR] Raw response: {score_json[:500] if score_json else 'EMPTY'}")
            
            # Try to extract numeric score as fallback
            fallback_score = self._extract_numeric_score(score_json)
            if fallback_score is not None:
                print(f"[FALLBACK] Extracted numeric score: {fallback_score}")
                return fallback_score * weight
            
            return 5.0 * weight  # Default to middle score
            
        except Exception as e:
            print(f"[ERROR] Unexpected error in calculate_relevance: {e}")
            return 5.0 * weight
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean LLM response to extract pure JSON
        
        Handles:
        - Markdown code blocks (```json ... ```)
        - Leading/trailing whitespace
        - Text before/after JSON
        """
        if not response:
            return "{}"
        
        # Remove markdown code blocks
        response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'^```\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'\s*```$', '', response, flags=re.MULTILINE)
        
        # Try to find JSON object
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return response.strip()
    
    def _extract_numeric_score(self, text: str) -> Optional[float]:
        """
        Extract a numeric score from text as fallback
        
        Looks for patterns like:
        - "raw_score": 8.5
        - score: 7.0
        - 8.5/10
        """
        if not text:
            return None
        
        # Try to find raw_score in text
        score_match = re.search(r'"?raw_score"?\s*:\s*([0-9.]+)', text)
        if score_match:
            try:
                return float(score_match.group(1))
            except ValueError:
                pass
        
        # Try to find any score pattern
        score_match = re.search(r'score["\']?\s*:\s*([0-9.]+)', text, re.IGNORECASE)
        if score_match:
            try:
                return float(score_match.group(1))
            except ValueError:
                pass
        
        # Try to find X/10 pattern
        score_match = re.search(r'([0-9.]+)\s*/\s*10', text)
        if score_match:
            try:
                return float(score_match.group(1))
            except ValueError:
                pass
        
        return None
    
    async def _analyze_story_fit(
        self,
        story: Dict[str, Any],
        scholarship_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deep analysis of how well primary story fits scholarship
        
        Args:
            story: Student story to analyze
            scholarship_profile: Scholarship details
        
        Returns:
            Detailed analysis with suggestions
        """
        
        system_prompt = """You are an expert scholarship essay strategist. Analyze how student experiences can be positioned for maximum impact. Return ONLY valid JSON with no markdown or code blocks."""
        
        story_text = story.get('text', story.get('description', str(story)))
        
        user_message = f"""Analyze how this experience can be positioned for this scholarship essay.

EXPERIENCE:
{story_text}

SCHOLARSHIP:
{json.dumps(scholarship_profile, indent=2)}

Return ONLY this JSON structure (no markdown):
{{
    "fit_score": 8.5,
    "strongest_angles": ["angle 1", "angle 2", "angle 3"],
    "key_details_to_emphasize": ["detail 1", "detail 2"],
    "key_details_to_downplay": ["detail 1"],
    "suggested_framing": "How to position this story",
    "vocabulary_to_use": ["term 1", "term 2"],
    "potential_hooks": ["hook option 1", "hook option 2"],
    "connection_to_values": {{
        "leadership": "How it connects",
        "community_service": "How it connects"
    }}
}}"""
        
        try:
            analysis_json = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            cleaned_json = self._clean_json_response(analysis_json)
            return json.loads(cleaned_json)
            
        except Exception as e:
            print(f"[ERROR] Failed to analyze story fit: {e}")
            # Return minimal valid structure
            return {
                "fit_score": 7.0,
                "strongest_angles": ["Experience demonstrates relevant skills"],
                "key_details_to_emphasize": ["Impact and outcomes"],
                "key_details_to_downplay": [],
                "suggested_framing": "Focus on personal growth and impact",
                "vocabulary_to_use": ["leadership", "impact", "community"],
                "potential_hooks": ["Personal experience", "Meaningful impact"],
                "connection_to_values": {}
            }
    
    def _diverse_ranking(
        self,
        stories: List[Dict[str, Any]],
        priorities: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Rank stories to ensure diverse coverage of priorities
        
        Args:
            stories: Candidate stories with scores
            priorities: Scholarship priorities
        
        Returns:
            Ranked stories with diverse priority coverage
        """
        
        ranked = []
        used_priorities = set()
        remaining_stories = stories.copy()
        
        # First pass: select top story from each priority
        for priority in priorities.keys():
            priority_stories = [s for s in remaining_stories if s['priority'] == priority]
            if priority_stories:
                best = max(priority_stories, key=lambda x: x['score'])
                ranked.append(best)
                remaining_stories.remove(best)
                used_priorities.add(priority)
        
        # Second pass: add remaining stories by score
        remaining_sorted = sorted(remaining_stories, key=lambda x: x['score'], reverse=True)
        ranked.extend(remaining_sorted)
        
        return ranked
    
    def _focused_ranking(
        self,
        stories: List[Dict[str, Any]],
        priorities: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Rank stories focusing heavily on top priority
        
        Args:
            stories: Candidate stories with scores
            priorities: Scholarship priorities
        
        Returns:
            Ranked stories emphasizing top priority
        """
        
        # Get top priority
        top_priority = max(priorities.items(), key=lambda x: x[1])[0]
        
        # Boost scores for stories matching top priority
        boosted_stories = []
        for story in stories:
            boosted_story = story.copy()
            if story['priority'] == top_priority:
                boosted_story['score'] = story['score'] * 1.5  # 50% boost
            boosted_stories.append(boosted_story)
        
        return sorted(boosted_stories, key=lambda x: x['score'], reverse=True)
    
    async def compare_story_options(
        self,
        stories: List[Dict[str, Any]],
        scholarship_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare multiple story options and recommend best choice
        
        Args:
            stories: List of candidate stories
            scholarship_profile: Scholarship details
        
        Returns:
            Comparative analysis with recommendation
        """
        
        system_prompt = """You are an expert scholarship advisor. Compare student experiences and recommend which to feature in an essay. Return ONLY valid JSON."""
        
        story_summaries = []
        for i, story in enumerate(stories[:5], 1):  # Limit to top 5
            story_text = story.get('story', {}).get('text', str(story.get('story', '')))
            story_summaries.append(f"Story {i}: {story_text[:300]}...")
        
        user_message = f"""Compare these student experiences for a scholarship essay and recommend the best choice.

SCHOLARSHIP: {scholarship_profile.get('name', 'N/A')}
Values: {scholarship_profile.get('priorities', [])}

STORY OPTIONS:
{chr(10).join(story_summaries)}

Return ONLY valid JSON (no markdown):
{{
    "recommended_story": 1,
    "reasoning": "Why this story is strongest",
    "story_comparisons": [
        {{
            "story_number": 1,
            "strengths": ["strength 1", "strength 2"],
            "weaknesses": ["weakness 1"],
            "fit_score": 8.5,
            "uniqueness_score": 7.0
        }}
    ],
    "alternative_approach": "Consider this if primary doesn't work well"
}}"""
        
        try:
            comparison_json = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            cleaned_json = self._clean_json_response(comparison_json)
            return json.loads(cleaned_json)
            
        except Exception as e:
            print(f"[ERROR] Story comparison failed: {e}")
            return {
                "recommended_story": 1,
                "reasoning": "Unable to perform comparison",
                "story_comparisons": [],
                "alternative_approach": "Review stories manually"
            }
    
    async def suggest_missing_content(
        self,
        selected_content: Dict[str, Any],
        scholarship_profile: Dict[str, Any]
    ) -> List[str]:
        """
        Identify gaps in selected content relative to scholarship needs
        
        Args:
            selected_content: Currently selected stories
            scholarship_profile: Scholarship requirements
        
        Returns:
            List of content gaps and suggestions
        """
        
        system_prompt = """You are an expert scholarship advisor. Identify gaps in essay content and suggest what's missing. Return ONLY a JSON array of strings."""
        
        user_message = f"""Review the selected content and identify what's missing for this scholarship.

SCHOLARSHIP PRIORITIES:
{json.dumps(scholarship_profile.get('priorities', []), indent=2)}

SELECTED CONTENT:
Primary Story: {selected_content.get('primary_story', {}).get('story', {}).get('text', 'N/A')[:200]}
Supporting Stories: {len(selected_content.get('supporting_stories', []))} stories selected

Return ONLY a JSON array (no markdown):
[
    "Missing: specific examples of X",
    "Could strengthen: quantifiable outcomes",
    "Consider adding: personal connection to Y"
]"""
        
        try:
            suggestions_json = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            cleaned_json = self._clean_json_response(suggestions_json)
            return json.loads(cleaned_json)
            
        except Exception as e:
            print(f"[ERROR] Missing content analysis failed: {e}")
            return ["Unable to analyze content gaps"]