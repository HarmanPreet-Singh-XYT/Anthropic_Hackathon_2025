"""
backend/drafting_engine/content_selector.py
Ranks and selects student experiences by relevance to scholarship priorities
"""

import json
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
        
        system_prompt = """
        You are an expert scholarship evaluator.
        Rate how well student experiences demonstrate specific values and priorities.
        Be objective and evidence-based in your scoring.
        Return only valid JSON.
        """
        
        story_text = story.get('text', story.get('description', str(story)))
        
        user_message = f"""
        Rate how well this experience demonstrates {priority}.
        
        EXPERIENCE:
        {story_text}
        
        SCHOLARSHIP CONTEXT:
        Name: {scholarship_profile.get('name', 'N/A')}
        Mission: {scholarship_profile.get('mission', 'N/A')}
        What they value in {priority}: {scholarship_profile.get('value_descriptions', {}).get(priority, 'N/A')}
        
        EVALUATION CRITERIA:
        1. **Direct Evidence**: Does the experience directly demonstrate {priority}?
        2. **Impact/Outcomes**: Are there measurable results or meaningful outcomes?
        3. **Specificity**: Is the experience described with concrete details?
        4. **Authenticity**: Does it feel genuine and personal?
        5. **Alignment**: Does it match what this scholarship values in {priority}?
        
        Provide scoring as JSON:
        {{
            "raw_score": 0-10 (how well it demonstrates {priority}),
            "evidence_score": 0-10,
            "impact_score": 0-10,
            "specificity_score": 0-10,
            "authenticity_score": 0-10,
            "alignment_score": 0-10,
            "reasoning": "Brief explanation of score",
            "key_strengths": ["strength 1", "strength 2"],
            "key_weaknesses": ["weakness 1"] or []
        }}
        """
        
        try:
            score_json = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            score_data = json.loads(score_json)
            raw_score = score_data.get('raw_score', 5.0)
            
            # Apply priority weight
            weighted_score = float(raw_score) * weight
            
            return weighted_score
            
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: try simple numeric extraction
            print(f"Error parsing relevance score: {e}")
            return 5.0 * weight  # Default to middle score
    
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
        
        system_prompt = """
        You are an expert scholarship essay strategist.
        Analyze how student experiences can be positioned for maximum impact.
        Return only valid JSON.
        """
        
        story_text = story.get('text', story.get('description', str(story)))
        
        user_message = f"""
        Analyze how this experience can be positioned for this scholarship essay.
        
        EXPERIENCE:
        {story_text}
        
        SCHOLARSHIP:
        {json.dumps(scholarship_profile, indent=2)}
        
        Provide strategic analysis as JSON:
        {{
            "fit_score": 0-10,
            "strongest_angles": ["angle 1", "angle 2", "angle 3"],
            "key_details_to_emphasize": ["detail 1", "detail 2"],
            "key_details_to_downplay": ["detail 1"] or [],
            "suggested_framing": "How to position this story",
            "vocabulary_to_use": ["term 1", "term 2"],
            "potential_hooks": ["hook option 1", "hook option 2"],
            "connection_to_values": {{
                "priority_1": "How it connects",
                "priority_2": "How it connects"
            }}
        }}
        """
        
        analysis_json = await self.llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return json.loads(analysis_json)
    
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
        
        system_prompt = """
        You are an expert scholarship advisor.
        Compare student experiences and recommend which to feature in an essay.
        Return only valid JSON.
        """
        
        story_summaries = []
        for i, story in enumerate(stories[:5], 1):  # Limit to top 5
            story_text = story.get('story', {}).get('text', str(story.get('story', '')))
            story_summaries.append(f"Story {i}: {story_text[:300]}...")
        
        user_message = f"""
        Compare these student experiences for a scholarship essay and recommend the best choice.
        
        SCHOLARSHIP: {scholarship_profile.get('name', 'N/A')}
        Values: {scholarship_profile.get('priorities', [])}
        
        STORY OPTIONS:
        {chr(10).join(story_summaries)}
        
        Provide comparison as JSON:
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
        }}
        """
        
        comparison_json = await self.llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return json.loads(comparison_json)
    
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
        
        system_prompt = """
        You are an expert scholarship advisor.
        Identify gaps in essay content and suggest what's missing.
        Return only a JSON array of suggestions.
        """
        
        user_message = f"""
        Review the selected content and identify what's missing for this scholarship.
        
        SCHOLARSHIP PRIORITIES:
        {json.dumps(scholarship_profile.get('priorities', []), indent=2)}
        
        SELECTED CONTENT:
        Primary Story: {selected_content.get('primary_story', {}).get('story', {}).get('text', 'N/A')[:200]}
        Supporting Stories: {len(selected_content.get('supporting_stories', []))} stories selected
        
        Identify gaps as JSON array:
        [
            "Missing: specific examples of [priority]",
            "Could strengthen: quantifiable outcomes",
            "Consider adding: personal connection to [value]"
        ]
        """
        
        suggestions_json = await self.llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return json.loads(suggestions_json)