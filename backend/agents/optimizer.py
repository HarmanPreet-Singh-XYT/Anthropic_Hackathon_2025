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
            import traceback
            traceback.print_exc()
            return []

    async def generate_full_optimized_resume(
        self,
        original_resume: str,
        scholarship_values: List[str],
        weighted_priorities: Dict[str, float],
        tone: str,
        optimizations: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a complete optimized resume in Markdown format using LLM

        Args:
            original_resume: Original resume text
            scholarship_values: List of primary values
            weighted_priorities: Dict of value weights
            tone: Desired tone
            optimizations: List of bullet optimizations for reference

        Returns:
            Complete optimized resume in Markdown format
        """
        print("  → Generating full optimized resume via LLM...")

        try:
            # Format the optimizations for context
            optimizations_text = "\n".join([
                f"- Original: {opt.get('original', '')}\n  Optimized: {opt.get('improved', opt.get('optimized', ''))}"
                for opt in optimizations[:10]  # Limit to first 10 for context
            ])

            weights_str = ", ".join([f"{k}: {v:.2f}" for k, v in weighted_priorities.items()])
            values_str = ", ".join(scholarship_values)

            prompt = f"""You are an expert resume writer. Generate a complete, professionally formatted resume in Markdown that incorporates the optimized content below while maintaining the original resume's structure and information.

**Original Resume:**
{original_resume}

**Scholarship Values to Emphasize:**
{values_str}

**Priority Weights:**
{weights_str}

**Tone:**
{tone}

**Sample Optimizations (for reference):**
{optimizations_text}

**Instructions:**
1. Maintain the EXACT structure of the original resume (sections, headers, formatting)
2. Keep ALL contact information, education details, dates, company names exactly as they appear
3. Incorporate the optimized bullet points while preserving the resume's professional format
4. Use proper Markdown formatting:
   - Use # for name/title
   - Use ## for section headers (Experience, Education, Skills, etc.)
   - Use ### for job titles/positions
   - Use - for bullet points
   - Use *italic* for dates or emphasis
   - Maintain proper spacing and structure
5. Ensure the resume highlights the scholarship values: {values_str}
6. Keep the tone {tone}

**OUTPUT ONLY THE COMPLETE MARKDOWN RESUME - NO EXPLANATIONS OR EXTRA TEXT**
"""

            system_instruction = "You are an expert resume writer. Output only the complete Markdown-formatted resume with no additional commentary."
            
            response_text = await self.llm_client.call(
                system_prompt=system_instruction,
                user_message=prompt
            )

            # Clean up the response
            cleaned_response = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_response.startswith("```markdown"):
                cleaned_response = cleaned_response[11:]
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            cleaned_response = cleaned_response.strip()
            
            print(f"  ✓ Generated full optimized resume ({len(cleaned_response)} characters)")
            
            # Validate that we got actual content
            if len(cleaned_response) < 100:
                print("  ⚠ Generated resume seems too short, using original")
                return original_resume
            
            return cleaned_response

        except Exception as e:
            print(f"  ⚠ Failed to generate full resume: {e}")
            import traceback
            traceback.print_exc()
            return original_resume

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
                - optimized_resume_markdown: Complete optimized resume in Markdown format
        """
        print("\n🔧 Optimizer Agent Running...")
        print(f"  → Resume text length: {len(resume_text)} characters")

        # Extract values from decoder output
        primary_values = decoder_output.get("primary_values", [])
        hidden_weights = decoder_output.get("hidden_weights", {})
        tone = decoder_output.get("tone", "Professional")

        # Step 1: Generate optimized bullets
        raw_optimizations = await self.optimize_bullets(
            student_experiences=resume_text,
            scholarship_values=primary_values,
            weighted_priorities=hidden_weights,
            tone=tone
        )

        print(f"  → Received {len(raw_optimizations)} raw optimizations")

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

        # Step 2: Generate complete optimized resume in Markdown using LLM
        optimized_resume_markdown = await self.generate_full_optimized_resume(
            original_resume=resume_text,
            scholarship_values=primary_values,
            weighted_priorities=hidden_weights,
            tone=tone,
            optimizations=raw_optimizations
        )

        print(f"  ✓ Optimizer complete: {len(formatted_optimizations)} bullets optimized")
        print(f"  ✓ Generated resume length: {len(optimized_resume_markdown)} characters")
        
        # Preview the generated resume
        print("\n" + "="*80)
        print("OPTIMIZED RESUME PREVIEW:")
        print("="*80)
        preview_lines = optimized_resume_markdown.split('\n')[:20]
        print('\n'.join(preview_lines))
        if len(optimized_resume_markdown.split('\n')) > 20:
            print("...")
        print("="*80 + "\n")

        return {
            "optimizations": formatted_optimizations,
            "optimized_resume_markdown": optimized_resume_markdown
        }