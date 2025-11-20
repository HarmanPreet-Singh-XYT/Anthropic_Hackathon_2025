"""
backend/drafting_engine/refinement_loop.py
Iteratively refines essay drafts using critic-revision cycle
"""

import json
from typing import Dict, Any, List, Optional
from utils.llm_client import create_llm_client


class RefinementLoop:
    """
    Implements iterative refinement with critic and revision agents
    """
    
    def __init__(self, temperature: float = 0.6):
        """
        Initialize RefinementLoop with LLM clients
        
        Args:
            temperature: Default sampling temperature (can be overridden per agent)
        """
        self.critic_llm = create_llm_client(temperature=0.3)  # Lower temp for consistent critique
        self.revision_llm = create_llm_client(temperature=0.6)  # Higher temp for creative revision
    
    async def refine_draft(
        self,
        draft: str,
        scholarship_profile: Dict[str, Any],
        max_iterations: int = 3,
        target_score: float = 8.5
    ) -> Dict[str, Any]:
        """
        Iteratively improve draft with critic feedback
        
        Args:
            draft: Initial essay draft
            scholarship_profile: Scholarship details and criteria
            max_iterations: Maximum refinement cycles
            target_score: Stop when overall score reaches this threshold
        
        Returns:
            Dictionary with final draft, iteration history, and improvement metrics
        """
        
        current_draft = draft
        iteration_history = []
        
        for i in range(max_iterations):
            # Critic agent evaluates current draft
            critique = await self.critic_agent(current_draft, scholarship_profile)
            
            # If score is good enough, stop iterating
            if critique['overall_score'] >= target_score:
                iteration_history.append({
                    "iteration": i + 1,
                    "critique": critique,
                    "improvements": [],
                    "draft": current_draft,
                    "status": "target_reached"
                })
                break
            
            # Generate improvement suggestions
            improvements = self.generate_improvements(critique)
            
            # Revise draft based on critique
            revised_draft = await self.revision_agent(
                current_draft,
                critique,
                improvements,
                scholarship_profile
            )
            
            iteration_history.append({
                "iteration": i + 1,
                "critique": critique,
                "improvements": improvements,
                "draft": revised_draft,
                "status": "revised"
            })
            
            current_draft = revised_draft
        
        return {
            "final_draft": current_draft,
            "iterations": iteration_history,
            "improvement_trajectory": self.calculate_improvement(iteration_history),
            "total_iterations": len(iteration_history)
        }
    
    async def critic_agent(
        self,
        draft: str,
        scholarship_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Multi-dimensional critique of draft
        
        Args:
            draft: Essay text to critique
            scholarship_profile: Scholarship criteria and values
        
        Returns:
            Structured critique with scores and suggestions
        """
        
        system_prompt = """
        You are an expert scholarship reviewer with years of experience evaluating applications.
        Provide thorough, constructive criticism that helps improve essays while maintaining authenticity.
        Return only valid JSON, no additional text.
        """
        
        user_message = f"""
        Evaluate this scholarship essay draft against the scholarship criteria.
        
        SCHOLARSHIP PROFILE:
        - Name: {scholarship_profile.get('name', 'N/A')}
        - Values: {json.dumps(scholarship_profile.get('priorities', []), indent=2)}
        - Mission: {scholarship_profile.get('mission', 'N/A')}
        - Tone preference: {scholarship_profile.get('tone_profile', 'professional')}
        
        ESSAY DRAFT:
        {draft}
        
        EVALUATE ON THESE DIMENSIONS (score 1-10 for each):
        
        1. **ALIGNMENT**: How well does it address scholarship's values?
        2. **SPECIFICITY**: Are examples concrete and detailed?
        3. **IMPACT**: Does it show meaningful outcomes/results?
        4. **AUTHENTICITY**: Does it sound genuine (not generic)?
        5. **NARRATIVE_FLOW**: Is the story compelling and coherent?
        6. **TONE_MATCH**: Does writing style match scholarship's voice?
        7. **HOOK_STRENGTH**: Does opening grab attention?
        8. **CONCLUSION**: Does ending leave lasting impression?
        9. **WORD_EFFICIENCY**: Is every sentence necessary?
        10. **DIFFERENTIATION**: Does it stand out from typical essays?
        
        For each dimension provide:
        - score: 1-10 (integer)
        - evidence: Specific quote or example from the text
        - suggestion: Concrete improvement recommendation
        
        Also provide:
        - overall_score: Average of dimension scores (1-10, can be decimal)
        - top_strengths: Array of 3 specific strengths with examples
        - top_weaknesses: Array of 3 specific weaknesses with examples
        - line_edits: Array of specific text changes with before/after
        
        Format as JSON:
        {{
            "dimensions": {{
                "ALIGNMENT": {{
                    "score": 8,
                    "evidence": "Quote from essay",
                    "suggestion": "Specific improvement"
                }},
                ...
            }},
            "overall_score": 7.5,
            "top_strengths": [
                "Strength 1 with specific example",
                "Strength 2 with specific example",
                "Strength 3 with specific example"
            ],
            "top_weaknesses": [
                "Weakness 1 with specific example",
                "Weakness 2 with specific example",
                "Weakness 3 with specific example"
            ],
            "line_edits": [
                {{
                    "original": "Text to change",
                    "revised": "Improved version",
                    "reason": "Why this change helps"
                }}
            ]
        }}
        """
        
        critique_json = await self.critic_llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return json.loads(critique_json)
    
    async def revision_agent(
        self,
        draft: str,
        critique: Dict[str, Any],
        improvements: List[Dict[str, Any]],
        scholarship_profile: Dict[str, Any]
    ) -> str:
        """
        Apply specific improvements to draft based on critique
        
        Args:
            draft: Original essay text
            critique: Structured critique from critic_agent
            improvements: Prioritized improvement actions
            scholarship_profile: Scholarship context
        
        Returns:
            Revised essay text
        """
        
        system_prompt = """
        You are an expert essay editor specializing in scholarship applications.
        Revise essays based on critique while preserving authenticity and core narrative.
        Return only the revised essay text, no preamble or explanation.
        """
        
        user_message = f"""
        Revise this scholarship essay based on expert critique.
        
        ORIGINAL DRAFT:
        {draft}
        
        CRITIQUE SUMMARY:
        Overall Score: {critique.get('overall_score', 'N/A')}/10
        
        Top Strengths (PRESERVE THESE):
        {self._format_list(critique.get('top_strengths', []))}
        
        Top Weaknesses (ADDRESS THESE):
        {self._format_list(critique.get('top_weaknesses', []))}
        
        SPECIFIC IMPROVEMENTS NEEDED:
        {self._format_improvements(improvements)}
        
        LINE-LEVEL EDITS:
        {self._format_line_edits(critique.get('line_edits', []))}
        
        SCHOLARSHIP CONTEXT:
        This essay is for: {scholarship_profile.get('name', 'this scholarship')}
        Key values to emphasize: {', '.join(scholarship_profile.get('priorities', [])[:3])}
        
        REVISION INSTRUCTIONS:
        1. Address each weakness mentioned in the critique
        2. Implement suggested improvements systematically
        3. Apply line-level edits where specified
        4. Preserve what's working well (the strengths listed above)
        5. Maintain the same core story, facts, and achievements
        6. Keep word count similar (±50 words from original)
        7. Ensure the student's authentic voice remains intact
        
        CRITICAL RULES:
        - DO NOT change the fundamental narrative or story arc
        - DO NOT remove specific achievements, numbers, or facts
        - DO NOT make it more generic or less personal
        - DO NOT lose the student's unique voice and personality
        - DO add more specific details where the critique noted vagueness
        - DO strengthen alignment with scholarship values
        - DO improve clarity and impact of key points
        
        OUTPUT: Return ONLY the complete revised essay, no explanations or notes.
        """
        
        revised_essay = await self.revision_llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return revised_essay.strip()
    
    def generate_improvements(
        self,
        critique: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Convert critique scores into actionable improvements
        
        Args:
            critique: Structured critique from critic_agent
        
        Returns:
            Prioritized list of improvement actions
        """
        
        improvements = []
        dimensions = critique.get('dimensions', {})
        
        # Prioritize dimensions with lowest scores
        sorted_dimensions = sorted(
            dimensions.items(),
            key=lambda x: x[1].get('score', 10)
        )
        
        for dimension, details in sorted_dimensions[:5]:  # Top 5 priorities
            score = details.get('score', 10)
            if score < 7:
                improvements.append({
                    "dimension": dimension,
                    "current_score": score,
                    "issue": details.get('evidence', 'No evidence provided'),
                    "action": details.get('suggestion', 'No suggestion provided'),
                    "priority": "high" if score < 5 else "medium"
                })
        
        return improvements
    
    def calculate_improvement(
        self,
        iteration_history: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Track improvement across iterations
        
        Args:
            iteration_history: List of iteration results
        
        Returns:
            Improvement metrics or None if no history
        """
        
        if not iteration_history:
            return None
        
        scores = [
            it['critique'].get('overall_score', 0)
            for it in iteration_history
        ]
        
        return {
            "initial_score": scores[0],
            "final_score": scores[-1],
            "improvement": scores[-1] - scores[0],
            "improvement_percentage": ((scores[-1] - scores[0]) / scores[0] * 100) if scores[0] > 0 else 0,
            "iterations_needed": len(scores),
            "score_trajectory": scores,
            "consistent_improvement": all(
                scores[i] <= scores[i+1] for i in range(len(scores)-1)
            )
        }
    
    # Helper methods for formatting
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items with bullet points"""
        if not items:
            return "None specified"
        return "\n".join(f"- {item}" for item in items)
    
    def _format_improvements(self, improvements: List[Dict[str, Any]]) -> str:
        """Format improvement actions for prompt"""
        if not improvements:
            return "No specific improvements needed"
        
        formatted = []
        for imp in improvements:
            formatted.append(
                f"[{imp['priority'].upper()}] {imp['dimension']}: "
                f"{imp['action']} (Current score: {imp['current_score']}/10)"
            )
        return "\n".join(formatted)
    
    def _format_line_edits(self, line_edits: List[Dict[str, Any]]) -> str:
        """Format line-level edits for prompt"""
        if not line_edits:
            return "No specific line edits needed"
        
        formatted = []
        for i, edit in enumerate(line_edits, 1):
            formatted.append(
                f"{i}. Change: \"{edit.get('original', '')}\" "
                f"→ \"{edit.get('revised', '')}\" "
                f"(Reason: {edit.get('reason', 'N/A')})"
            )
        return "\n".join(formatted)
    
    async def quick_critique(
        self,
        draft: str,
        scholarship_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get a single critique without refinement (useful for testing)
        
        Args:
            draft: Essay to critique
            scholarship_profile: Scholarship details
        
        Returns:
            Critique results
        """
        return await self.critic_agent(draft, scholarship_profile)