"""
Agent E: The Interviewer
Generates contextual questions to extract bridge stories when gaps detected
"""

from typing import Dict, Any
from typing import Dict, Any, Optional
from pathlib import Path

from ..utils.llm_client import LLMClient
from ..utils.prompt_loader import load_prompt


class InterviewerAgent:
    """
    Agent E: The Interviewer
    Generates contextual questions to help students uncover missing stories.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Interviewer Agent

        Args:
            llm_client: Configured LLMClient instance
        """
        self.llm_client = llm_client
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """
        Load interviewer system prompt from prompts/interviewer.md

        Returns:
            System prompt text template
        """
        # Similar to Decoder, we return the template name for runtime loading
        return "interviewer"

    async def generate_question(
        self,
        resume_summary: str,
        target_gap: str,
        gap_weight: float,
        resume_focus: str = "other areas"
    ) -> str:
        """
        Generate a specific interview question

        Args:
            resume_summary: Brief summary of student's current resume
            target_gap: The missing value/keyword to ask about
            gap_weight: Importance of this missing value
            resume_focus: What the resume currently emphasizes

        Returns:
            Conversational question string
        """
        print(f"  → Interviewer generating question for gap: '{target_gap}'...")

        try:
            # Load and populate the prompt
            full_prompt = load_prompt(
                self.system_prompt, 
                {
                    "resume_summary": resume_summary,
                    "target_gap": target_gap,
                    "gap_weight": f"{gap_weight:.0%}",
                    "resume_focus": resume_focus
                }
            )
            
            # Call LLM
            # The prompt file asks for a single conversational question.
            system_instruction = "You are a helpful mentor. Generate a single conversational question."
            
            response_text = await self.llm_client.call(
                system_prompt=system_instruction,
                user_message=full_prompt
            )

            # Clean up response (remove quotes if present)
            question = response_text.strip()
            if question.startswith('"') and question.endswith('"'):
                question = question[1:-1]
            
            print(f"  ✓ Question generated: {question[:50]}...")
            return question

        except Exception as e:
            print(f"  ⚠ Question generation failed: {e}")
            return f"Can you tell me about a time you demonstrated {target_gap}?"

    async def run(
        self,
        resume_text: str,
        gaps: list[str],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Execute Interviewer Agent workflow

        Args:
            resume_text: Full resume text (to be summarized)
            gaps: List of identified gaps
            weights: Criteria weights

        Returns:
            Dict containing:
                - question: str
                - target_gap: str
        """
        if not gaps:
            return {"question": None, "target_gap": None}
            
        # Target the highest weighted gap
        # Gaps are already sorted by Matchmaker, but let's be safe
        target_gap = gaps[0]
        gap_weight = weights.get(target_gap, 0.0)
        
        # Simple resume summary (first 500 chars or so for context)
        # In a real scenario, we might want a better summary from Profiler
        resume_summary = resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text
        
        question = await self.generate_question(
            resume_summary=resume_summary,
            target_gap=target_gap,
            gap_weight=gap_weight
        )
        
        return {
            "question": question,
            "target_gap": target_gap
        }

    def parse_student_response(self, response: str) -> Dict[str, Any]:
        """
        Process and structure student's answer

        Args:
            response: Student's written answer to question

        Returns:
            Dict containing:
                - raw_response: Original answer
                - extracted_story: Structured story elements
                - keywords_addressed: Which gaps this fills
        """
        # TODO: Implement response parsing
        # TODO: Extract key story elements
        """
        Execute Interviewer Agent workflow

        Args:
            matchmaker_output: Gap analysis from Matchmaker

        Returns:
            Dict containing:
                - question: str - Question to ask student
                - target_gap: str - Which keyword this addresses
                - context: str - Why this question matters
        """
        # TODO: Implement full Interviewer workflow
        # 1. Identify highest-priority gap
        # 2. Generate contextual question
        # 3. Return question with metadata
        # Note: Actual student response handled by workflow state
        pass
