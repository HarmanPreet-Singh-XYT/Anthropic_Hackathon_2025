"""
Agent G: The Ghostwriter
Drafts scholarship essay using bridge story, weights, and resume context
"""

from typing import Dict, Any, Optional
from pathlib import Path

from ..utils.llm_client import LLMClient
from ..utils.prompt_loader import load_prompt


class GhostwriterAgent:
    """
    Agent G: The Ghostwriter
    Drafts scholarship essay using bridge story, weights, and resume context.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Ghostwriter Agent

        Args:
            llm_client: Configured LLMClient instance
        """
        self.llm_client = llm_client
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """
        Load ghostwriter system prompt from prompts/ghostwriter.md

        Returns:
            System prompt text template
        """
        return "ghostwriter"

    async def draft_essay(
        self,
        scholarship_values: List[str],
        hidden_weights: Dict[str, float],
        tone: str,
        resume_context: str,
        bridge_story: Optional[str] = None,
        word_limit: int = 500
    ) -> Dict[str, Any]:
        """
        Generate essay draft and strategy note

        Args:
            scholarship_values: Primary values
            hidden_weights: Value weights
            tone: Required tone
            resume_context: Relevant resume text
            bridge_story: Optional story from interview
            word_limit: Max words

        Returns:
            Dict containing 'essay', 'strategy_note', 'word_count'
        """
        print("  → Ghostwriter drafting essay...")

        try:
            # Format weights for prompt
            weights_str = ", ".join([f"{k}: {v:.2f}" for k, v in hidden_weights.items()])
            values_str = ", ".join(scholarship_values)
            
            # Load and populate the prompt
            full_prompt = load_prompt(
                self.system_prompt, 
                {
                    "primary_values": values_str,
                    "hidden_weights": weights_str,
                    "tone": tone,
                    "bridge_story": bridge_story or "No specific bridge story provided. Focus on resume highlights.",
                    "resume_context": resume_context[:3000],  # Limit context size
                    "word_limit": word_limit
                }
            )
            
            # Call LLM
            system_instruction = "You are an expert essay writer. Output valid JSON only."
            
            response_text = await self.llm_client.call(
                system_prompt=system_instruction,
                user_message=full_prompt
            )

            # Parse JSON
            cleaned_response = response_text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            result = json.loads(cleaned_response.strip())
            
            print(f"  ✓ Essay generated ({result.get('word_count', 0)} words)")
            return result

        except Exception as e:
            print(f"  ⚠ Essay generation failed: {e}")
            return {
                "essay": "Error generating essay. Please try again.",
                "strategy_note": f"Generation failed: {str(e)}",
                "word_count": 0
            }

    async def run(
        self,
        decoder_output: Dict[str, Any],
        resume_text: str,
        bridge_story: Optional[str] = None,
        word_limit: int = 500
    ) -> Dict[str, Any]:
        """
        Execute Ghostwriter Agent workflow

        Args:
            decoder_output: Scholarship analysis
            resume_text: Student's resume information
            bridge_story: Story from interview (optional)
            word_limit: Essay length limit

        Returns:
            Dict containing essay and strategy
        """
        primary_values = decoder_output.get("primary_values", [])
        hidden_weights = decoder_output.get("hidden_weights", {})
        tone = decoder_output.get("tone", "Professional")
        
        return await self.draft_essay(
            scholarship_values=primary_values,
            hidden_weights=hidden_weights,
            tone=tone,
            resume_context=resume_text,
            bridge_story=bridge_story,
            word_limit=word_limit
        )
