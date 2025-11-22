"""
Agent F: The Resume Optimizer
Rewrites resume bullets using scholarship vocabulary
"""

from typing import Dict, Any, List
from pathlib import Path
import json

from utils.llm_client import LLMClient
from utils.prompt_loader import load_prompt


class OptimizerAgent:
    """
    Agent F: The Optimizer
    Rewrites resume bullets to align with scholarship vocabulary and values.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Optimizer Agent

        Args:
            llm_client: Configured LLMClient instance
        """
        self.llm_client = llm_client
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """
        Load optimizer system prompt from prompts/optimizer.md

        Returns:
            System prompt text template
        """
        return "optimizer"

    async def optimize_bullets(
        self,
        student_experiences: str,
        scholarship_values: List[str],
        weighted_priorities: Dict[str, float],
        tone: str
    ) -> List[Dict[str, Any]]:
        """
        Generate optimized resume bullets

        Args:
            student_experiences: Relevant resume sections or text
            scholarship_values: List of primary values
            weighted_priorities: Dict of value weights
            tone: Desired tone description

        Returns:
            List of optimized bullet objects
        """
        print("  → Optimizer rewriting bullets...")

        try:
            # Format weights for prompt
            weights_str = ", ".join([f"{k}: {v:.2f}" for k, v in weighted_priorities.items()])
            values_str = ", ".join(scholarship_values)

            # Load and populate the prompt
            full_prompt = load_prompt(
                self.system_prompt, 
                {
                    "student_experiences": student_experiences,
                    "scholarship_values": values_str,
                    "weighted_priorities": weights_str,
                    "tone": tone
                }
            )
            
            # Call LLM
            system_instruction = "You are a resume expert. Output valid JSON array only."
            
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
            
            optimizations = json.loads(cleaned_response.strip())
            
            print(f"  ✓ Generated {len(optimizations)} optimized bullets")
            return optimizations

        except Exception as e:
            print(f"  ⚠ Optimization failed: {e}")
            return []

    async def run(
        self,
        resume_text: str,
        decoder_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Optimizer Agent workflow

        Args:
            resume_text: Student's resume text
            decoder_output: Scholarship analysis from Decoder

        Returns:
            Dict containing:
                - optimizations: List of before/after bullets with rationale
                - summary: Overall optimization strategy
        """
        print("\n🔧 Optimizer Agent Running...")

        # Extract values from decoder output
        primary_values = decoder_output.get("primary_values", [])
        hidden_weights = decoder_output.get("hidden_weights", {})
        tone = decoder_output.get("tone", "Professional")

        # Call the optimization method
        raw_optimizations = await self.optimize_bullets(
            student_experiences=resume_text,
            scholarship_values=primary_values,
            weighted_priorities=hidden_weights,
            tone=tone
        )

        # Transform to frontend format: {original, optimized, weight}
        formatted_optimizations = []
        for opt in raw_optimizations:
            # Map priority to weight value
            priority_weight_map = {"high": 0.9, "medium": 0.6, "low": 0.3}
            weight = priority_weight_map.get(opt.get("priority", "medium"), 0.6)

            formatted_optimizations.append({
                "original": opt.get("original", ""),
                "optimized": opt.get("improved", opt.get("optimized", "")),
                "weight": weight
            })

        print(f"  ✓ Optimizer complete: {len(formatted_optimizations)} bullets optimized")

        return {
            "optimizations": formatted_optimizations
        }
