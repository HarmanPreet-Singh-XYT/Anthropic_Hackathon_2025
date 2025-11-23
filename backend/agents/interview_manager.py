"""
Multi-Turn Interview Manager
Handles intelligent gap-based interviewing with confidence tracking
"""

from typing import Dict, Any, List, Optional, Tuple
from utils.llm_client import LLMClient
from utils.vector_store import VectorStore
import json


class InterviewManager:
    """
    Manages multi-turn interview sessions with confidence tracking.
    
    Capabilities:
    - Prioritize gaps by weight
    - Generate contextual questions
    - Score answers for confidence (0.0-1.0)
    - Determine when to move to next gap
    - Synthesize final bridge story
    """
    
    def __init__(self, llm_client: LLMClient, vector_store: VectorStore):
        """
        Initialize Interview Manager
        
        Args:
            llm_client: LLM client for question generation and scoring
            vector_store: Vector store for resume context
        """
        self.llm = llm_client
        self.vector_store = vector_store
        self.confidence_threshold = 0.80  # Increased threshold for higher quality
        self.max_questions = 8  # Hard limit on questions
    
    async def start_session(
        self,
        gaps: List[str],
        weighted_keywords: Dict[str, float],
        resume_text: str,
        matchmaker_evidence: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initialize interview session with first question
        
        Args:
            gaps: List of identified gaps from matchmaker
            weighted_keywords: Keyword importance weights
            resume_text: Full resume text for context
            matchmaker_evidence: Optional existing evidence from matchmaker
        
        Returns:
            {
                "first_question": str,
                "target_gap": str,
                "gap_confidences": Dict[str, float],
                "prioritized_gaps": List[str]
            }
        """
        # Prioritize gaps by weight (highest first)
        prioritized_gaps = sorted(
            gaps,
            key=lambda g: weighted_keywords.get(g, 0.0),
            reverse=True
        )
        
        # Initialize confidence tracking
        gap_confidences = {gap: 0.0 for gap in gaps}
        
        # Generate first question for highest-priority gap
        first_gap = prioritized_gaps[0]
        first_question = await self._generate_opening_question(
            gap=first_gap,
            weight=weighted_keywords.get(first_gap, 0.0),
            resume_text=resume_text
        )
        
        return {
            "first_question": first_question,
            "target_gap": first_gap,
            "gap_confidences": gap_confidences,
            "prioritized_gaps": prioritized_gaps
        }
    
    async def process_answer(
        self,
        answer: str,
        target_gap: str,
        current_confidence: float,
        gap_weight: float,
        conversation_history: List[Dict[str, str]],
        all_gaps: List[str],
        gap_confidences: Dict[str, float],
        weighted_keywords: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Process user's answer and determine next action
        
        Args:
            answer: User's response
            target_gap: Current gap being addressed
            current_confidence: Current confidence for this gap
            gap_weight: Weight/importance of this gap
            conversation_history: Full conversation so far
            all_gaps: All identified gaps
            gap_confidences: Current confidence for all gaps
            weighted_keywords: Keyword weights
        
        Returns:
            {
                "response": str,  # AI's next question or acknowledgment
                "confidence_update": float,  # New confidence for target gap
                "evidence_extracted": str,  # What was learned from answer
                "next_target": Optional[str],  # Next gap to address (if moving on)
                "is_complete": bool,  # Whether interview is done
                "gap_status": Dict[str, str]  # Status of each gap
            }
        """
        # Score the answer
        new_confidence = await self._score_answer(
            answer=answer,
            gap=target_gap,
            weight=gap_weight,
            current_confidence=current_confidence
        )
        
        # Extract evidence/key points from answer
        evidence = await self._extract_evidence(answer, target_gap)
        
        # Update confidence
        gap_confidences[target_gap] = new_confidence
        
        # Determine next action
        should_continue, next_gap = await self._should_continue_interview(
            gap_confidences=gap_confidences,
            current_target=target_gap,
            all_gaps=all_gaps,
            weighted_keywords=weighted_keywords,
            conversation_history=conversation_history
        )
        
        # Generate response
        if new_confidence >= self.confidence_threshold:
            if next_gap:
                # Move to next gap
                response = await self._generate_transition_response(
                    completed_gap=target_gap,
                    next_gap=next_gap,
                    gap_weight=weighted_keywords.get(next_gap, 0.0)
                )
            else:
                # All gaps complete
                response = await self._generate_completion_response()
        else:
            # Ask follow-up for same gap
            response = await self._generate_followup_question(
                gap=target_gap,
                current_confidence=new_confidence,
                previous_answer=answer,
                conversation_history=conversation_history
            )
        
        # Calculate gap statuses
        gap_status = {
            gap: (
                "complete" if conf >= self.confidence_threshold
                else "in_progress" if conf > 0
                else "not_started"
            )
            for gap, conf in gap_confidences.items()
        }
        
        return {
            "response": response,
            "confidence_update": new_confidence,
            "evidence_extracted": evidence,
            "next_target": next_gap,
            "is_complete": not should_continue,
            "gap_status": gap_status
        }
    
    async def synthesize_bridge_story(
        self,
        conversation_history: List[Dict[str, str]],
        gaps_addressed: Dict[str, float],
        weighted_keywords: Dict[str, float]
    ) -> str:
        """
        Create cohesive narrative from all collected stories
        
        Args:
            conversation_history: Full interview conversation
            gaps_addressed: Final confidence scores for each gap
            weighted_keywords: Keyword weights
        
        Returns:
            Synthesized bridge story as cohesive narrative
        """
        # Extract all user responses
        user_responses = [
            msg["content"] for msg in conversation_history
            if msg["role"] == "user"
        ]
        
        prompt = f"""
You are synthesizing a cohesive "bridge story" from a student interview.

The student was asked about gaps in their resume for a scholarship application.

**Gaps addressed:**
{json.dumps(gaps_addressed, indent=2)}

**Keyword priorities:**
{json.dumps(weighted_keywords, indent=2)}

**Student's responses during interview:**
{chr(10).join(f'- {response}' for response in user_responses)}

**Task:**
Create a cohesive, first-person narrative (2-3 paragraphs) that:
1. Integrates the student's experiences naturally
2. Emphasizes high-weight keywords
3. Flows like a personal story, not a list
4. Maintains the student's authentic voice
5. Bridges the gaps identified in their resume

Write ONLY the narrative, no preamble or meta-commentary.
"""
        
        bridge_story = await self.llm.call(
            system_prompt="You are a skilled essay coach helping students tell their authentic stories.",
            user_message=prompt
        )
        
        return bridge_story.strip()
    
    # ==================== Private Helper Methods ====================
    
    async def _generate_opening_question(
        self,
        gap: str,
        weight: float,
        resume_text: str
    ) -> str:
        """Generate contextual opening question for a gap"""
        
        prompt = f"""
You are an empathetic interview coach helping a student prepare a scholarship application.

**Gap to address:** {gap} (priority weight: {weight:.0%})

**Student's resume context:**
{resume_text[:800]}...

**Task:**
Generate a warm, conversational opening question that:
1. Acknowledges what you see in their resume
2. Asks about experiences related to "{gap}"
3. Feels natural, not interrogative
4. Encourages storytelling, not yes/no answers

Write ONLY the question, nothing else.
"""
        
        question = await self.llm.call(
            system_prompt="You are an empathetic scholarship interview coach.",
            user_message=prompt
        )
        
        return question.strip()
    
    async def _score_answer(
        self,
        answer: str,
        gap: str,
        weight: float,
        current_confidence: float
    ) -> float:
        """
        Score answer quality for the target gap
        
        Returns confidence score 0.0-1.0
        """
        
        prompt = f"""
Evaluate this student's answer for a scholarship gap analysis.

**Gap being addressed:** {gap} (weight: {weight:.0%})
**Current confidence:** {current_confidence:.0%}
**Student's answer:** {answer}

**Scoring rubric:**
- 0.0-0.3: Vague, off-topic, or minimal relevance
- 0.4-0.6: Mentions the topic but lacks specific examples or depth
- 0.7-0.8: Strong example with context, but missing metrics/impact
- 0.9-1.0: Exceptional - specific example with measurable impact or vivid details

**Important:**
- Increase confidence by 0.2-0.4 for good answers
- Don't give perfect scores too easily
- Consider cumulative progress from multiple answers

Return ONLY a single number between 0.0 and 1.0, nothing else.
"""
        
        try:
            response = await self.llm.call(
                system_prompt="You are an objective evaluator of student interview responses.",
                user_message=prompt
            )
            
            # Extract number from response
            score_str = response.strip()
            # Try to parse as float
            score = float(score_str)
            
            # Clamp to valid range
            score = max(0.0, min(1.0, score))
            
            # Ensure we don't decrease confidence
            return max(current_confidence, score)
            
        except (ValueError, AttributeError):
            # Fallback if LLM doesn't return valid number
            # Assume moderate improvement
            return min(1.0, current_confidence + 0.2)
    
    async def _extract_evidence(self, answer: str, gap: str) -> str:
        """Extract key evidence/points from answer"""
        
        if len(answer) < 50:
            return answer
        
        prompt = f"""
Extract the key evidence from this answer about "{gap}".

Student's answer: {answer}

Return a brief summary (1-2 sentences) of what they shared. Be specific.
"""
        
        evidence = await self.llm.call(
            system_prompt="You are extracting key points from interview responses.",
            user_message=prompt
        )
        
        return evidence.strip()
    
    async def _should_continue_interview(
        self,
        gap_confidences: Dict[str, float],
        current_target: str,
        all_gaps: List[str],
        weighted_keywords: Dict[str, float],
        conversation_history: List[Dict[str, str]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if interview should continue and what gap to address next
        
        Returns:
            (should_continue, next_gap_name)
        """
        # Check max questions constraint
        # Each turn has a user message and an assistant message (usually). 
        # We count user messages as "answers" provided.
        user_answers = len([m for m in conversation_history if m["role"] == "user"])
        
        if user_answers >= self.max_questions:
            print(f"  🛑 Max questions ({self.max_questions}) reached. Stopping interview.")
            return (False, None)

        # Check if current gap is satisfied
        current_satisfied = gap_confidences[current_target] >= self.confidence_threshold
        
        if not current_satisfied:
            # Keep working on current gap
            return (True, None)
        
        # Find next unsatisfied gap (prioritized by weight)
        unsatisfied_gaps = [
            gap for gap in all_gaps
            if gap_confidences[gap] < self.confidence_threshold
        ]
        
        if not unsatisfied_gaps:
            # All gaps are satisfied!
            return (False, None)
        
        # Get highest-weight unsatisfied gap
        next_gap = max(
            unsatisfied_gaps,
            key=lambda g: weighted_keywords.get(g, 0.0)
        )
        
        return (True, next_gap)
    
    async def _generate_followup_question(
        self,
        gap: str,
        current_confidence: float,
        previous_answer: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Generate follow-up question for same gap"""
        
        # Determine what to probe for based on confidence level
        if current_confidence < 0.4:
            focus = "Ask for a specific example or story"
        elif current_confidence < 0.7:
            focus = "Ask for measurable impact, outcomes, or duration"
        else:
            focus = "Ask for additional context or challenges faced"
        
        prompt = f"""
You are continuing an interview about "{gap}".

**Current confidence:** {current_confidence:.0%}
**Student's last answer:** {previous_answer}

**Goal for follow-up:** {focus}

Generate a natural follow-up question that:
1. Acknowledges their previous answer positively
2. Probes for more depth/specifics
3. Feels conversational, not repetitive

Write ONLY the question.
"""
        
        question = await self.llm.call(
            system_prompt="You are an empathetic interview coach.",
            user_message=prompt
        )
        
        return question.strip()
    
    async def _generate_transition_response(
        self,
        completed_gap: str,
        next_gap: str,
        gap_weight: float
    ) -> str:
        """Generate transition from one gap to another"""
        
        prompt = f"""
You just finished discussing "{completed_gap}" with a student.

Now transition to asking about "{next_gap}" (priority: {gap_weight:.0%}).

Generate a response that:
1. Briefly acknowledges their previous answer positively
2. Smoothly transitions to the new topic
3. Asks an opening question about "{next_gap}"
4. Stays warm and encouraging

Write the full transition + question.
"""
        
        response = await self.llm.call(
            system_prompt="You are an empathetic interview coach.",
            user_message=prompt
        )
        
        return response.strip()
    
    async def _generate_completion_response(self) -> str:
        """Generate final response when interview is complete"""
        
        return (
            "That's wonderful! I have all the information I need to create "
            "an amazing application for you. Your experiences really demonstrate "
            "the scholarship's values. Let me compile everything and we'll move "
            "to the next step."
        )
