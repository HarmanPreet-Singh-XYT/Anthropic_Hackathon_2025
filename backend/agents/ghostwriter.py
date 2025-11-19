"""
Agent G: The Ghostwriter
Drafts scholarship essay using bridge story, weights, and resume context
"""

from typing import Dict, Any, Optional
from pathlib import Path


class GhostwriterAgent:
    """
    Responsible for essay generation:
    - Use bridge story as narrative hook
    - Align with scholarship weights and tone
    - Incorporate relevant resume context

    Output: Full essay draft + strategy note
    """

    def __init__(self, anthropic_client, prompt_dir: Path):
        """
        Initialize Ghostwriter Agent

        Args:
            anthropic_client: Anthropic API client
            prompt_dir: Directory containing prompt templates
        """
        self.client = anthropic_client
        self.prompt_dir = prompt_dir
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """
        Load ghostwriter system prompt from prompts/ghostwriter.md

        Returns:
            System prompt text
        """
        # TODO: Implement prompt loading from markdown file
        pass

    async def draft_essay(
        self,
        bridge_story: Optional[str],
        scholarship_analysis: Dict[str, Any],
        resume_context: str,
        word_limit: int = 500
    ) -> str:
        """
        Generate essay draft

        Args:
            bridge_story: Story from Interviewer (if gaps existed)
            scholarship_analysis: Weights, tone from Decoder
            resume_context: Relevant sections from resume
            word_limit: Maximum words for essay

        Returns:
            Full essay draft
        """
        # TODO: Implement essay generation using ghostwriter prompt
        # TODO: Use bridge story as hook if available
        # TODO: Align with tone and weight priorities
        # TODO: Respect word limit
        pass

    def generate_strategy_note(
        self,
        scholarship_analysis: Dict[str, Any],
        bridge_story: Optional[str]
    ) -> str:
        """
        Explain why this narrative approach was chosen

        Args:
            scholarship_analysis: Decoder output
            bridge_story: Story used (if any)

        Returns:
            Strategy explanation for student
        """
        # TODO: Implement strategy note generation
        # TODO: Explain narrative choices
        # TODO: Connect to scholarship values
        pass

    async def run(
        self,
        decoder_output: Dict[str, Any],
        resume_context: str,
        bridge_story: Optional[str] = None,
        word_limit: int = 500
    ) -> Dict[str, Any]:
        """
        Execute Ghostwriter Agent workflow

        Args:
            decoder_output: Scholarship analysis
            resume_context: Student's resume information
            bridge_story: Story from interview (optional)
            word_limit: Essay length limit

        Returns:
            Dict containing:
                - essay: Full essay draft
                - strategy_note: Explanation of narrative approach
                - word_count: Actual essay length
        """
        # TODO: Implement full Ghostwriter workflow
        # 1. Draft essay using all inputs
        # 2. Generate strategy note
        # 3. Validate word count
        # 4. Return complete package
        pass
