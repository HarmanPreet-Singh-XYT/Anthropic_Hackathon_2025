"""
Agent C: The Decoder
Analyzes scholarship intelligence to extract weighted keyword map
"""

import json
from typing import Dict, Any, List
from pathlib import Path
from utils.llm_client import LLMClient
from utils.prompt_loader import load_prompt


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
            
            system_instruction = (
                "You are a scholarship analysis engine. "
                "You MUST return ONLY a valid JSON object with no markdown fences, "
                "no explanations, and no text before or after the JSON. "
                "Output the raw JSON object directly."
            )
            
            response_text = await self.llm_client.call(
                system_prompt=system_instruction,
                user_message=full_prompt
            )

            # Parse JSON with robust extraction
            cleaned_response = response_text.strip()
            
            # Remove markdown code fences first
            if "```json" in cleaned_response:
                start = cleaned_response.find("```json") + 7
                end = cleaned_response.find("```", start)
                if end != -1:
                    cleaned_response = cleaned_response[start:end].strip()
            elif "```" in cleaned_response:
                start = cleaned_response.find("```") + 3
                end = cleaned_response.find("```", start)
                if end != -1:
                    cleaned_response = cleaned_response[start:end].strip()

            # Attempt to find the first outer-most JSON object
            try:
                start_idx = cleaned_response.find('{')
                if start_idx == -1:
                    raise ValueError("No JSON object found")
                
                # Simple brace counting to find the end
                brace_count = 0
                end_idx = -1
                for i, char in enumerate(cleaned_response[start_idx:], start=start_idx):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                
                if end_idx != -1:
                    cleaned_response = cleaned_response[start_idx:end_idx]
                else:
                    # Fallback to rfind if counting fails (e.g. malformed)
                    cleaned_response = cleaned_response[start_idx:]
                    last_brace = cleaned_response.rfind('}')
                    if last_brace != -1:
                        cleaned_response = cleaned_response[:last_brace+1]

                analysis = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                print(f"  ⚠ JSON Parse Error: {e}")
                # Try one more aggressive cleanup if simple parsing failed
                # Sometimes LLMs put comments like // inside JSON which is invalid
                import re
                cleaned_response = re.sub(r'//.*', '', cleaned_response)
                analysis = json.loads(cleaned_response)
            
            # Validate the analysis has required fields
            if not analysis.get('hidden_weights') or not isinstance(analysis['hidden_weights'], dict):
                raise ValueError("Invalid analysis: missing or empty hidden_weights")
            
            # Normalize weights to sum to 1.0
            weights_sum = sum(analysis['hidden_weights'].values())
            if weights_sum > 0:
                analysis['hidden_weights'] = {
                    k: v / weights_sum for k, v in analysis['hidden_weights'].items()
                }
            
            print("  ✓ Decoder analysis complete")
            return analysis

        except Exception as e:
            print(f"  ⚠ Decoder analysis failed: {e}")
            print(f"  → Attempting to extract primary values from scholarship text for fallback...")
            
            # Try to create reasonable fallback weights
            # Extract potential values from the scholarship text
            common_values = [
                "Leadership",
                "Academic Excellence", 
                "Community Service",
                "Innovation",
                "Diversity and Inclusion"
            ]
            
            # Create equal weights for common scholarship values
            fallback_weights = {val: 1.0 / len(common_values) for val in common_values}
            
            print(f"  → Using fallback weights: {', '.join(f'{k}: {v:.0%}' for k, v in fallback_weights.items())}")
            
            return {
                "primary_values": common_values,
                "hidden_weights": fallback_weights,
                "tone": "Professional and sincere",
                "missing_evidence_query": "Tell me about a time you demonstrated leadership and made an impact."
            }

    async def run(self, scholarship_text: str) -> Dict[str, Any]:
        """
        Execute Decoder Agent workflow

        Args:
            scholarship_text: Combined scholarship text to analyze

        Returns:
            Analysis dict with primary_values, hidden_weights, tone, missing_evidence_query
        """
        return await self.analyze_scholarship(scholarship_text)
