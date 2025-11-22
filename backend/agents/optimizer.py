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
        self.llm_client = llm_client
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        return "optimizer"

    def _extract_bullets_from_resume(self, resume_text: str) -> List[str]:
        """
        Extract individual bullet points/experiences from resume text
        
        Returns:
            List of achievement bullets
        """
        bullets = []
        
        # Method 1: Explicit bullet points
        bullet_chars = ['-', '*', '•', '▪', '‣', '⁃']
        
        for line in resume_text.split('\n'):
            line = line.strip()
            if not line or len(line) < 20:  # Skip empty or very short lines
                continue
            
                        # Check if line starts with bullet character
            if any(line.startswith(char) for char in bullet_chars):
                bullet_text = line.lstrip(''.join(bullet_chars)).strip()
                if bullet_text:
                    bullets.append(bullet_text)
            # Or if line contains action verbs (likely an achievement)
            elif any(verb in line.lower() for verb in [
                'led', 'managed', 'developed', 'created', 'increased', 'improved',
                'designed', 'implemented', 'organized', 'founded', 'built',
                'achieved', 'delivered', 'coordinated', 'launched', 'established'
            ]):
                bullets.append(line)
        
        # If we found very few bullets, try a more aggressive extraction
        if len(bullets) < 3:
            print(f"  [Optimizer] Only found {len(bullets)} bullets, trying alternative extraction...")
            bullets = self._extract_bullets_aggressive(resume_text)
        
        print(f"  [Optimizer] Extracted {len(bullets)} bullet points from resume")
        return bullets

    def _extract_bullets_aggressive(self, resume_text: str) -> List[str]:
        """Fallback: Extract any substantial sentence that looks like an achievement"""
        bullets = []
        
        for line in resume_text.split('\n'):
            line = line.strip()
            # Skip headers (usually short or start with #)
            if len(line) < 30 or line.startswith('#'):
                continue
            # Skip lines that look like contact info or dates
            if any(pattern in line.lower() for pattern in ['@', 'phone', 'email', 'linkedin']):
                continue
            if line.count('/') >= 2 or line.count('-') >= 2:  # Likely a date range
                continue
            
            # Keep lines that look like descriptions
            if len(line) > 30 and any(c.isalpha() for c in line):
                bullets.append(line)
        
        return bullets[:15]  # Limit to 15 most substantial lines

    async def optimize_bullets(
        self,
        student_experiences: str,
        scholarship_values: List[str],
        weighted_priorities: Dict[str, float],
        tone: str
    ) -> List[Dict[str, Any]]:
        """Generate optimized resume bullets"""
        print("  → Optimizer rewriting bullets...")
        print(f"  → Input length: {len(student_experiences)} chars")
        print(f"  → Scholarship values: {scholarship_values}")

        try:
            weights_str = ", ".join([f"{k}: {v:.2f}" for k, v in weighted_priorities.items()])
            values_str = ", ".join(scholarship_values)

            full_prompt = load_prompt(
                self.system_prompt, 
                {
                    "student_experiences": student_experiences,
                    "scholarship_values": values_str,
                    "weighted_priorities": weights_str,
                    "tone": tone
                }
            )
            
            system_instruction = """You are a resume expert. 
You MUST return ONLY a valid JSON array of objects with no markdown fences.
Each object must have: original, optimized, rationale, priority.
Output the raw JSON array directly."""
            
            response_text = await self.llm_client.call(
                system_prompt=system_instruction,
                user_message=full_prompt
            )

            cleaned_response = response_text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
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

    async def generate_full_resume(
        self,
        original_resume: str,
        optimizations: List[Dict[str, Any]],
        scholarship_values: List[str],
        tone: str
    ) -> str:
        """Generate a complete rewritten resume in markdown format"""
        print("  → Generating full optimized resume...")

        try:
            opt_summary = "\n".join([
                f"- Original: {o.get('original', '')}\n  Improved: {o.get('optimized', o.get('improved', ''))}"
                for o in optimizations
            ])

            prompt = f"""Based on the following original resume and optimizations, generate a complete, 
professionally formatted resume in Markdown.

ORIGINAL RESUME:
{original_resume[:3000]}

OPTIMIZATIONS MADE:
{opt_summary}

SCHOLARSHIP VALUES TO EMPHASIZE:
{', '.join(scholarship_values)}

DESIRED TONE: {tone}

Instructions:
1. Incorporate all the optimized bullets into the appropriate sections
2. Ensure consistent formatting throughout
3. Use proper Markdown structure (headers, bullet points, bold for emphasis)
4. Maintain professional resume conventions
5. Keep sections organized: Contact Info, Summary/Objective, Experience, Education, Skills, etc.
6. Ensure the resume flows naturally and tells a cohesive story
7. Keep the student's original structure but enhance the content

Output the complete resume in Markdown format only, no additional commentary.
NO code fences, just raw markdown."""

            response = await self.llm_client.call(
                system_prompt="You are an expert resume writer. Output clean Markdown only, no code fences.",
                user_message=prompt
            )

            cleaned = response.strip()
            if cleaned.startswith("```markdown"):
                cleaned = cleaned[11:]
            elif cleaned.startswith("```md"):
                cleaned = cleaned[5:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()
            
            # Validate markdown structure
            if not cleaned:
                print("  ⚠ Empty markdown generated, using original resume")
                return original_resume
            
            # Check for basic markdown headers
            has_headers = any(line.startswith('#') for line in cleaned.split('\n'))
            if not has_headers:
                print("  ⚠ No markdown headers found, adding structure...")
                cleaned = f"# Resume\n\n{cleaned}"
            
            # Check minimum length
            if len(cleaned) < 200:
                print(f"  ⚠ Markdown too short ({len(cleaned)} chars), using original")
                return original_resume

            print(f"  ✓ Full resume generated ({len(cleaned)} chars, {cleaned.count('#')} sections)")
            return cleaned

        except Exception as e:
            print(f"  ⚠ Full resume generation failed: {e}")
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

        Returns:
            Dict containing:
                - optimizations: List of before/after bullets with rationale
                - full_resume_markdown: Complete rewritten resume in markdown
        """
        print("\n🔧 Optimizer Agent Running...")
        print(f"  → Resume text length: {len(resume_text)} chars")

        # Validate inputs
        if not resume_text or len(resume_text) < 100:
            print(f"  ⚠ ERROR: Resume text is empty or too short ({len(resume_text)} chars)")
            return {
                "optimizations": [],
                "full_resume_markdown": ""
            }

        primary_values = decoder_output.get("primary_values", [])
        hidden_weights = decoder_output.get("hidden_weights", {})
        tone = decoder_output.get("tone", "Professional")

        print(f"  → Primary values: {primary_values}")
        print(f"  → Hidden weights: {list(hidden_weights.keys())}")
        print(f"  → Tone: {tone}")

        # Extract structured bullet points
        print("  → Extracting resume bullets...")
        resume_bullets = self._extract_bullets_from_resume(resume_text)
        
        if not resume_bullets:
            print("  ⚠ WARNING: No bullets extracted from resume")
            structured_experiences = resume_text
        else:
            structured_experiences = "\n".join([f"- {bullet}" for bullet in resume_bullets])
            print(f"  → Structured {len(resume_bullets)} bullets")

        # Generate optimizations
        raw_optimizations = await self.optimize_bullets(
            student_experiences=structured_experiences,
            scholarship_values=primary_values,
            weighted_priorities=hidden_weights,
            tone=tone
        )

        # Format optimizations
        priority_weight_map = {"high": 0.9, "medium": 0.6, "low": 0.3}
        formatted_optimizations = []
        
        for opt in raw_optimizations:
            weight = priority_weight_map.get(opt.get("priority", "medium"), 0.6)
            formatted_optimizations.append({
                "original": opt.get("original", ""),
                "optimized": opt.get("improved", opt.get("optimized", "")),
                "rationale": opt.get("rationale", ""),
                "weight": weight
            })

        # Generate the full rewritten resume in markdown
        full_resume_md = await self.generate_full_resume(
            original_resume=resume_text,
            optimizations=formatted_optimizations,
            scholarship_values=primary_values,
            tone=tone
        )

        print(f"  ✓ Optimizer complete: {len(formatted_optimizations)} bullets optimized")
        print(f"  ✓ Full resume markdown: {len(full_resume_md)} chars")
        
        return {
            "optimizations": formatted_optimizations,
            "full_resume_markdown": full_resume_md
        }