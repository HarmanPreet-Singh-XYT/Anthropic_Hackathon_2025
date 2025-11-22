"""
Agent C: The Decoder
Analyzes scholarship intelligence to extract weighted keyword map
"""

from typing import Dict, Any, List
from pathlib import Path


class DecoderAgent:
    """
    Responsible for pattern recognition:
    - Analyze scholarship criteria and winner context
    Agent C: The Decoder
    Analyzes scholarship text to extract implicit values, weights, and tone.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize Decoder Agent

        Args:
            llm_client: Configured LLMClient instance
        """
        self.llm_client = llm_client
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """
        Load decoder system prompt from prompts/decoder.md

        Returns:
            System prompt text template
        """
        # We load the raw template here. Variable substitution happens at runtime.
        # Since load_prompt performs substitution, we'll use a placeholder for now 
        # or better, we just load the file content directly if we want to keep the template 
        # for later substitution, BUT utils.prompt_loader.load_prompt requires variables 
        # if they are in the file.
        #
        # Actually, looking at utils.prompt_loader, it substitutes immediately.
        # So we should probably load the template string manually or adjust how we use it.
        # However, the prompt has {scholarship_text} at the bottom.
        # The system prompt usually shouldn't change per call, but here the input is part of it.
        # Let's check the prompt file again.
        # backend/prompts/decoder.md has {scholarship_text} at the end.
        # This means the "System Prompt" effectively includes the User Input in this design.
        # We will treat the whole thing as the message to send, or split it.
        # For simplicity with the current prompt design, we will load it at runtime.
        return "decoder"

    async def analyze_scholarship(self, scholarship_text: str) -> Dict[str, Any]:
        """
        Analyze scholarship text to extract structured intelligence

        Args:
            scholarship_text: Combined text from Scout (official + insights)

        Returns:
            Dict containing:
                - primary_values: List[str]
                - hidden_weights: Dict[str, float]
                - tone: str
                - missing_evidence_query: str
        """
        print(f"  → Decoder analyzing {len(scholarship_text)} chars of scholarship text...")

        try:
            # Load and populate the prompt
            full_prompt = load_prompt(self.system_prompt, {"scholarship_text": scholarship_text})
            
            # Call LLM
            # Since the prompt file contains the input text, we can use it as the system prompt
            # or user message. The prompt file says "You are an expert...". 
            # Usually we split system instructions and user content.
            # But for this implementation, we'll pass the whole thing.
            # To be cleaner, we could pass the instruction part as system and text as user.
            # But given the prompt file structure, it's a single block.
            # Let's pass it as the system prompt and a simple "Analyze this" as user message,
            # OR just pass the whole thing as the user message if the system prompt is fixed.
            #
            # Let's try to be smart: The prompt file has instructions AND input.
            # We'll send the whole filled template as the User message, 
            # and a generic System prompt to enforce JSON.
            
            system_instruction = "You are a scholarship analysis engine. Output valid JSON only."
            
            response_text = await self.llm_client.call(
                system_prompt=system_instruction,
                user_message=full_prompt
            )

            # Parse JSON
            # Clean up potential markdown code blocks
            cleaned_response = response_text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            analysis = json.loads(cleaned_response.strip())
            
            print("  ✓ Decoder analysis complete")
            return analysis

        except Exception as e:
            print(f"  ⚠ Decoder analysis failed: {e}")
            # Return fallback/empty structure
            return {
                "primary_values": [],
                "hidden_weights": {},
                "tone": "Professional and sincere",
                "missing_evidence_query": "Tell me about a time you demonstrated leadership."
            }

    async def run(self, scholarship_text: str) -> Dict[str, Any]:
        """
        Execute Decoder Agent workflow

        Args:
        pass
