"""
Agent E: The Interviewer
Generates contextual questions to extract bridge stories when gaps detected
"""

from typing import Dict, Any
from pathlib import Path


class InterviewerAgent:
    """
    Responsible for human-in-the-loop interaction:
    - Generate specific questions based on narrative gaps
    - Extract authentic student stories
    - Never hallucinate content

    Output: Contextual question to fill highest-priority gap
    """

    def __init__(self, anthropic_client, prompt_dir: Path):
        """
        Initialize Interviewer Agent

        Args:
            anthropic_client: Anthropic API client
            prompt_dir: Directory containing prompt templates
        """
        self.client = anthropic_client
        self.prompt_dir = prompt_dir
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """
        Load interviewer system prompt from prompts/interviewer.md

        Returns:
            System prompt text
        """
        # TODO: Implement prompt loading from markdown file
        pass

    async def generate_question(
        self,
        gaps: list[str],
        scholarship_weights: Dict[str, float],
        resume_summary: str
    ) -> str:
        """
        Generate contextual question to extract bridge story

        Args:
            gaps: Missing keywords from Matchmaker
            scholarship_weights: Importance of each keyword
            resume_summary: Summary of student's current resume

        Returns:
            Specific question to ask the student
        """
        # TODO: Implement question generation using interviewer prompt
        # TODO: Focus on highest-weighted gap
        # TODO: Make question specific and conversational
        pass

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
        pass

    async def run(self, matchmaker_output: Dict[str, Any]) -> Dict[str, Any]:
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
