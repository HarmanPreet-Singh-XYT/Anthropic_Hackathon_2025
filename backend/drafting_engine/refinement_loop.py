"""
backend/drafting_engine/refinement_loop.py
Iteratively refines essay drafts using critic-revision cycle
"""

import json
import re
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
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean LLM response to extract pure JSON
        """
        if not response:
            return "{}"
        
        # Remove markdown code blocks
        response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'^```\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'\s*```$', '', response, flags=re.MULTILINE)
        
        # Try to find JSON object or array
        json_match = re.search(r'[\{$$].*[\}$$]', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return response.strip()
    
    def _get_default_critique(self, score: float = 7.0) -> Dict[str, Any]:
        """
        Return default critique when analysis fails
        """
        return {
            "dimensions": {
                "ALIGNMENT": {"score": 7, "evidence": "N/A", "suggestion": "Review alignment with values"},
                "SPECIFICITY": {"score": 7, "evidence": "N/A", "suggestion": "Add more specific details"},
                "IMPACT": {"score": 7, "evidence": "N/A", "suggestion": "Quantify outcomes"},
                "AUTHENTICITY": {"score": 8, "evidence": "N/A", "suggestion": "Maintain authentic voice"},
                "NARRATIVE_FLOW": {"score": 7, "evidence": "N/A", "suggestion": "Improve transitions"}
            },
            "overall_score": score,
            "top_strengths": [
                "Essay demonstrates relevant experiences",
                "Authentic voice is present",
                "Structure is clear"
            ],
            "top_weaknesses": [
                "Could benefit from more specific details",
                "Impact could be quantified better",
                "Some sections could be more concise"
            ],
            "line_edits": []
        }
    
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
        
        print(f"    🔄 Starting refinement loop (max {max_iterations} iterations, target score: {target_score}/10)...")
        
        current_draft = draft
        iteration_history = []
        
        for i in range(max_iterations):
            print(f"       Iteration {i+1}/{max_iterations}...")
            
            # Critic agent evaluates current draft
            critique = await self.critic_agent(current_draft, scholarship_profile)
            
            current_score = critique.get('overall_score', 0)
            print(f"       Score: {current_score:.1f}/10")
            
            # If score is good enough, stop iterating
            if current_score >= target_score:
                print(f"       ✅ Target score reached!")
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
            print(f"       Found {len(improvements)} areas to improve")
            
            # Revise draft based on critique
            revised_draft = await self.revision_agent(
                current_draft,
                critique,
                improvements,
                scholarship_profile
            )
            
            # Check if revision actually changed anything
            if revised_draft == current_draft:
                print(f"       ⚠️  No changes made in revision")
                iteration_history.append({
                    "iteration": i + 1,
                    "critique": critique,
                    "improvements": improvements,
                    "draft": current_draft,
                    "status": "no_change"
                })
                break
            
            iteration_history.append({
                "iteration": i + 1,
                "critique": critique,
                "improvements": improvements,
                "draft": revised_draft,
                "status": "revised"
            })
            
            current_draft = revised_draft
        
        improvement_trajectory = self.calculate_improvement(iteration_history)
        final_score = improvement_trajectory.get('final_score', 7.0) if improvement_trajectory else 7.0
        
        print(f"    ✅ Refinement complete: {len(iteration_history)} iterations, final score: {final_score:.1f}/10")
        
        return {
            "final_draft": current_draft,
            "iterations": iteration_history,
            "improvement_trajectory": improvement_trajectory,
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
        
        system_prompt = """You are an expert scholarship reviewer with years of experience evaluating applications. Provide thorough, constructive criticism that helps improve essays while maintaining authenticity. Return ONLY valid JSON with no markdown or additional text."""
        
        # Truncate draft if too long
        draft_preview = draft if len(draft) < 2000 else draft[:2000] + "..."
        
        priorities = scholarship_profile.get('priorities', [])
        priorities_str = ', '.join(priorities[:5]) if priorities else 'N/A'
        
        mission = scholarship_profile.get('mission', 'N/A')
        if len(mission) > 300:
            mission = mission[:300] + "..."
        
        user_message = f"""Evaluate this scholarship essay draft against the scholarship criteria.

SCHOLARSHIP PROFILE:
- Name: {scholarship_profile.get('name', 'N/A')}
- Values: {priorities_str}
- Mission: {mission}

ESSAY DRAFT:
{draft_preview}

EVALUATE ON THESE DIMENSIONS (score 1-10 for each):

1. ALIGNMENT: How well does it address scholarship's values?
2. SPECIFICITY: Are examples concrete and detailed?
3. IMPACT: Does it show meaningful outcomes/results?
4. AUTHENTICITY: Does it sound genuine (not generic)?
5. NARRATIVE_FLOW: Is the story compelling and coherent?
6. TONE_MATCH: Does writing style match scholarship's voice?
7. HOOK_STRENGTH: Does opening grab attention?
8. CONCLUSION: Does ending leave lasting impression?
9. WORD_EFFICIENCY: Is every sentence necessary?
10. DIFFERENTIATION: Does it stand out from typical essays?

Return ONLY valid JSON (no markdown):
{{
    "dimensions": {{
        "ALIGNMENT": {{
            "score": 8,
            "evidence": "Quote from essay",
            "suggestion": "Specific improvement"
        }},
        "SPECIFICITY": {{"score": 7, "evidence": "...", "suggestion": "..."}},
        "IMPACT": {{"score": 8, "evidence": "...", "suggestion": "..."}},
        "AUTHENTICITY": {{"score": 9, "evidence": "...", "suggestion": "..."}},
        "NARRATIVE_FLOW": {{"score": 7, "evidence": "...", "suggestion": "..."}}
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
}}"""
        
        try:
            critique_json = await self.critic_llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            print(f"       [DEBUG] Critique response length: {len(critique_json) if critique_json else 0}")
            
            if not critique_json or not critique_json.strip():
                print("       [WARNING] Empty critique response")
                return self._get_default_critique()
            
            cleaned_json = self._clean_json_response(critique_json)
            critique = json.loads(cleaned_json)
            
            # Validate overall_score exists and is numeric
            if 'overall_score' not in critique or not isinstance(critique.get('overall_score'), (int, float)):
                print("       [WARNING] Invalid overall_score, calculating from dimensions")
                dimensions = critique.get('dimensions', {})
                if dimensions:
                    scores = [d.get('score', 7) for d in dimensions.values() if isinstance(d, dict)]
                    critique['overall_score'] = sum(scores) / len(scores) if scores else 7.0
                else:
                    critique['overall_score'] = 7.0
            
            # Ensure required fields exist
            if 'top_strengths' not in critique or not critique['top_strengths']:
                critique['top_strengths'] = ["Essay demonstrates relevant experiences"]
            if 'top_weaknesses' not in critique or not critique['top_weaknesses']:
                critique['top_weaknesses'] = ["Could benefit from more specific details"]
            if 'line_edits' not in critique:
                critique['line_edits'] = []
            
            return critique
            
        except json.JSONDecodeError as e:
            print(f"       [ERROR] Failed to parse critique: {e}")
            print(f"       [ERROR] Response: {critique_json[:300] if critique_json else 'EMPTY'}")
            return self._get_default_critique()
            
        except Exception as e:
            print(f"       [ERROR] Unexpected error in critic_agent: {e}")
            return self._get_default_critique()
    
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
        
        system_prompt = """You are an expert essay editor specializing in scholarship applications. Revise essays based on critique while preserving authenticity and core narrative. Return ONLY the revised essay text with no preamble, explanation, or markdown formatting."""
        
        priorities = scholarship_profile.get('priorities', [])
        priorities_str = ', '.join(priorities[:3]) if priorities else 'scholarship values'
        
        user_message = f"""Revise this scholarship essay based on expert critique.

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

SCHOLARSHIP CONTEXT:
This essay is for: {scholarship_profile.get('name', 'this scholarship')}
Key values to emphasize: {priorities_str}

REVISION INSTRUCTIONS:
1. Address each weakness mentioned in the critique
2. Implement suggested improvements systematically
3. Preserve what's working well (the strengths listed above)
4. Maintain the same core story, facts, and achievements
5. Keep word count similar (±50 words from original)
6. Ensure the student's authentic voice remains intact

CRITICAL RULES:
- DO NOT change the fundamental narrative or story arc
- DO NOT remove specific achievements, numbers, or facts
- DO NOT make it more generic or less personal
- DO add more specific details where the critique noted vagueness
- DO strengthen alignment with scholarship values
- DO improve clarity and impact of key points

OUTPUT: Return ONLY the complete revised essay, no explanations or notes."""
        
        try:
            revised_essay = await self.revision_llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            if not revised_essay or not revised_essay.strip():
                print("       [WARNING] Empty revision response, using original")
                return draft
            
            # Clean any metadata or labels
            revised_essay = re.sub(r'^(REVISED|ESSAY|IMPROVED):\s*', '', revised_essay, flags=re.IGNORECASE)
            revised_essay = re.sub(r'^\*\*.*?\*\*:?\s*', '', revised_essay, flags=re.MULTILINE)
            revised_essay = re.sub(r'^#{1,6}\s+.*$', '', revised_essay, flags=re.MULTILINE)
            
            # Check if revision is substantially different
            if revised_essay.strip() == draft.strip():
                print("       [WARNING] Revision identical to original")
            
            return revised_essay.strip()
            
        except Exception as e:
            print(f"       [ERROR] Revision failed: {e}")
            print("       [FALLBACK] Using original draft")
            return draft
    
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
        
        if not dimensions:
            return improvements
        
        # Prioritize dimensions with lowest scores
        sorted_dimensions = sorted(
            dimensions.items(),
            key=lambda x: x[1].get('score', 10) if isinstance(x[1], dict) else 10
        )
        
        for dimension, details in sorted_dimensions[:5]:  # Top 5 priorities
            if not isinstance(details, dict):
                continue
                
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
        
        scores = []
        for it in iteration_history:
            critique = it.get('critique', {})
            score = critique.get('overall_score', 0)
            if isinstance(score, (int, float)):
                scores.append(float(score))
        
        if not scores:
            return None
        
        initial = scores[0]
        final = scores[-1]
        improvement = final - initial
        
        return {
            "initial_score": initial,
            "final_score": final,
            "improvement": improvement,
            "improvement_percentage": ((improvement / initial) * 100) if initial > 0 else 0,
            "iterations_needed": len(scores),
            "score_trajectory": scores,
            "consistent_improvement": all(
                scores[i] <= scores[i+1] for i in range(len(scores)-1)
            ) if len(scores) > 1 else True
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
                f"[{imp.get('priority', 'medium').upper()}] {imp.get('dimension', 'N/A')}: "
                f"{imp.get('action', 'N/A')} (Current score: {imp.get('current_score', 0)}/10)"
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