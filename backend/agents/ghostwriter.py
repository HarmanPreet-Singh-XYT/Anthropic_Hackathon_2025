"""
Agent G: The Ghostwriter
Drafts scholarship essay using bridge story, weights, and resume context
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from utils.llm_client import LLMClient
from utils.prompt_loader import load_prompt


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

            # Robust JSON Parsing & Repair
            cleaned_response = response_text.strip()
            
            # Remove markdown code blocks
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            cleaned_response = cleaned_response.strip()

            def repair_json(json_str):
                import re
                # 1. Remove non-printable control characters (keep \n, \r, \t)
                json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', json_str)
                
                # 2. Escape unescaped newlines inside string values
                # This is tricky with regex, so we use a simple heuristic:
                # If we see a newline that isn't followed by a quote or whitespace+quote/bracket, it might be inside a string.
                # A safer way for essays: The essay is likely a long string. 
                # We'll try standard load first, then fallback to aggressive escaping.
                return json_str

            try:
                # Attempt 1: Standard Load
                result = json.loads(repair_json(cleaned_response))
            except json.JSONDecodeError:
                try:
                    # Attempt 2: Aggressive Newline Escaping for the essay body
                    # This assumes the essay is in a field like "essay": "..."
                    # We manually escape newlines inside the JSON string structure
                    # This is complex, so we'll try a simpler fallback:
                    # Use regex to extract the essay content directly if JSON fails
                    
                    print("  ⚠ JSON parse failed, attempting regex extraction...")
                    
                    essay_match = re.search(r'"essay"\s*:\s*"(.*?)"', cleaned_response, re.DOTALL)
                    strategy_match = re.search(r'"strategy_note"\s*:\s*"(.*?)"', cleaned_response, re.DOTALL)
                    
                    if essay_match:
                        essay_text = essay_match.group(1).replace('\\"', '"').replace('\\n', '\n')
                        strategy_text = strategy_match.group(1).replace('\\"', '"') if strategy_match else "Strategy extracted via regex"
                        
                        result = {
                            "essay": essay_text,
                            "strategy_note": strategy_text,
                            "word_count": len(essay_text.split())
                        }
                    else:
                        # Attempt 3: Python literal eval (sometimes LLMs output Python dicts)
                        import ast
                        result = ast.literal_eval(cleaned_response)
                        
                except Exception as e:
                    print(f"  ⚠ All parsing attempts failed: {e}")
                    # Final Fallback: Treat entire text as essay if it looks like one
                    if len(cleaned_response) > 100:
                        result = {
                            "essay": cleaned_response,
                            "strategy_note": "Parsing failed, raw output returned.",
                            "word_count": len(cleaned_response.split())
                        }
                    else:
                        raise ValueError(f"Could not parse output: {cleaned_response[:100]}...")

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

    async def draft_outreach_email(
        self,
        scholarship_name: str,
        organization: str,
        contact_name: Optional[str],
        gaps: List[str],
        student_context: str
    ) -> Dict[str, str]:
        """
        Draft an outreach email to the scholarship committee
        """
        print("  → Ghostwriter drafting outreach email...")
        
        try:
            full_prompt = load_prompt(
                "outreach",
                {
                    "scholarship_name": scholarship_name,
                    "organization": organization or "Scholarship Committee",
                    "contact_name": contact_name or "Scholarship Committee",
                    "gaps": ", ".join(gaps) if gaps else "general application details",
                    "student_context": student_context[:1000]
                }
            )
            
            system_instruction = "You are an expert communications coach. Output valid JSON only."
            
            response_text = await self.llm_client.call(
                system_prompt=system_instruction,
                user_message=full_prompt
            )
            
            # Robust JSON parsing (same approach as essay generation)
            cleaned = response_text.strip()
            
            # Remove markdown code blocks
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Remove control characters
            import re
            cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
            
            try:
                # Attempt standard JSON parsing
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                print(f"  ⚠ JSON parse error: {e}, attempting extraction...")
                
                # Fallback: Extract fields with regex
                subject_match = re.search(r'"subject"\s*:\s*"(.*?)"', cleaned, re.DOTALL)
                body_match = re.search(r'"body"\s*:\s*"(.*?)"(?=\s*[,}])', cleaned, re.DOTALL)
                
                if subject_match and body_match:
                    return {
                        "subject": subject_match.group(1).replace('\\"', '"'),
                        "body": body_match.group(1).replace('\\"', '"').replace('\\n', '\n')
                    }
                else:
                    raise
            
        except Exception as e:
            print(f"  ⚠ Outreach email generation failed: {e}")
            return {
                "subject": f"Inquiry regarding {scholarship_name}",
                "body": "Error generating email body."
            }
