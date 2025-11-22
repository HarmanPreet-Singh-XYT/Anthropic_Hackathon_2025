"""
Agent E: The Interviewer
Generates contextual questions to extract bridge stories when gaps detected
"""

from typing import Dict, Any, Optional
import json
from pathlib import Path

from utils.llm_client import LLMClient
from utils.prompt_loader import load_prompt


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
        return "interviewer"

    async def _extract_resume_highlights(self, resume_text: str) -> str:
        """
        Extract 2-3 concrete experiences from resume for context
        
        Returns:
            Formatted string with specific experiences
        """
        system_prompt = """Extract 2-3 specific, concrete experiences from this resume.
Focus on experiences with clear roles, organizations, or achievements.
Return as a brief bulleted list (max 3 items, 15 words each).
Output ONLY the bullet points, no additional text."""

        user_prompt = f"""Resume:\n{resume_text[:2000]}\n\nExtract top 3 specific experiences:"""
        
        try:
            response = await self.llm_client.call(
                system_prompt=system_prompt,
                user_message=user_prompt
            )
            highlights = response.strip()
            
            # Validate we got something useful
            if len(highlights) < 20 or not any(char in highlights for char in ['-', '•', '*']):
                # Fallback: extract lines with action verbs
                print("  [Interviewer] LLM extraction failed, using fallback method")
                return self._extract_highlights_fallback(resume_text)
            
            return highlights
            
        except Exception as e:
            print(f"  [Interviewer] Error extracting highlights: {e}")
            return self._extract_highlights_fallback(resume_text)

    def _extract_highlights_fallback(self, resume_text: str) -> str:
        """Fallback method to extract highlights using pattern matching"""
        lines = resume_text.split('\n')
        highlights = []
        
        action_verbs = [
            'led', 'managed', 'developed', 'founded', 'organized', 'created',
            'built', 'designed', 'implemented', 'achieved', 'increased', 'improved'
        ]
        
        for line in lines:
            line_lower = line.lower()
            if any(verb in line_lower for verb in action_verbs) and len(line.strip()) > 30:
                # Clean up the line
                clean_line = line.strip()
                if clean_line and not clean_line.startswith('#'):
                    highlights.append(clean_line)
                    if len(highlights) >= 3:
                        break
        
        if not highlights:
            return "your resume experiences"
        
        return '\n'.join(f"- {h[:100]}" for h in highlights)

    async def _identify_resume_strengths(self, resume_text: str) -> str:
        """
        Identify what areas the resume DOES emphasize
        
        Returns:
            String describing resume's current focus (e.g., "technical projects and research")
        """
        system_prompt = """Analyze this resume and identify its PRIMARY focus area in 3-5 words.
Examples: "technical projects and research", "community organizing and advocacy", "athletic leadership".
Output ONLY the focus description, no additional text."""

        user_prompt = f"""Resume:\n{resume_text[:1500]}\n\nPrimary focus:"""
        
        try:
            response = await self.llm_client.call(
                system_prompt=system_prompt,
                user_message=user_prompt
            )
            focus = response.strip()
            
            # Validate response
            if len(focus) > 50 or len(focus) < 5:
                return "academic and extracurricular activities"
            
            return focus
            
        except Exception as e:
            print(f"  [Interviewer] Error identifying strengths: {e}")
            return "academic and extracurricular activities"

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
        print(f"  → Resume summary length: {len(resume_summary)}")
        print(f"  → Resume focus: {resume_focus}")

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
            system_instruction = """You are a helpful mentor conducting a warm, conversational interview.
Generate a single, specific question that references the student's actual experiences.
DO NOT use placeholders like [briefly highlight...] or [mention experience].
Output ONLY the question, no preamble."""
            
            response_text = await self.llm_client.call(
                system_prompt=system_instruction,
                user_message=full_prompt
            )

            # Clean up response
            question = response_text.strip()
            if question.startswith('"') and question.endswith('"'):
                question = question[1:-1]
            
            # Validate question doesn't contain placeholders
            placeholder_patterns = [
                '[briefly', '[mention', '[specific', '[relevant',
                '[highlight', '[describe', '[share'
            ]
            
            has_placeholder = any(pattern in question.lower() for pattern in placeholder_patterns)
            
            if has_placeholder:
                print(f"  ⚠ Detected placeholder in question, regenerating...")
                # Generate a simpler, direct question
                question = await self._generate_simple_question(target_gap, resume_summary)
            
            print(f"  ✓ Question generated: {question[:80]}...")
            return question

        except Exception as e:
            print(f"  ⚠ Question generation failed: {e}")
            return f"Can you tell me about a time you demonstrated {target_gap}?"

    async def _generate_simple_question(self, target_gap: str, resume_summary: str) -> str:
        """Generate a simple, direct question without placeholders"""
        
        # Extract first concrete thing from resume summary
        lines = resume_summary.split('\n')
        first_experience = None
        
        for line in lines:
            if line.strip() and len(line.strip()) > 20:
                first_experience = line.strip().lstrip('-•* ')
                break
        
        if first_experience and len(first_experience) < 100:
            return f"I noticed you have experience with {first_experience}. Can you tell me about a specific time when you demonstrated {target_gap} in that role or a similar situation?"
        else:
            return f"Can you share a specific story about a time when you demonstrated {target_gap}? Please include details about the situation, what you did, and what the outcome was."

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
        print("\n👤 Interviewer Agent Running...")
        print(f"  → Resume text length: {len(resume_text)}")
        print(f"  → Gaps to address: {gaps}")
        
        if not gaps:
            return {"question": None, "target_gap": None}
        
        # Target the highest weighted gap
        target_gap = gaps[0]
        gap_weight = weights.get(target_gap, 0.0)
        
        print(f"  → Targeting gap: {target_gap} (weight: {gap_weight:.0%})")
        
        # Extract resume highlights
        print("  → Extracting resume highlights...")
        resume_summary = await self._extract_resume_highlights(resume_text)
        
        # Identify resume strengths
        print("  → Identifying resume strengths...")
        resume_focus = await self._identify_resume_strengths(resume_text)
        
        # Generate question
        question = await self.generate_question(
            resume_summary=resume_summary,
            target_gap=target_gap,
            gap_weight=gap_weight,
            resume_focus=resume_focus
        )
        
        print(f"  ✓ Interviewer complete")
        
        return {
            "question": question,
            "target_gap": target_gap
        }

    async def parse_student_response(self, response: str) -> Dict[str, Any]:
        """
        Process and structure student's answer using LLM extraction

        Args:
            response: Student's written answer to question

        Returns:
            Dict containing:
                - raw_response: Original answer
                - extracted_story: Structured story elements
                - keywords_addressed: Which gaps this fills
        """
        print(f"  → Analyzing student response ({len(response)} chars)...")
        
        system_prompt = """
You are an expert narrative analyst. Extract the core story elements from the student's response.
Return ONLY valid JSON.
"""
        
        user_prompt = f"""
ANALYZE THIS STUDENT RESPONSE:
"{response}"

TASK:
1. Extract the "STAR" components (Situation, Task, Action, Result).
2. Identify which values/skills are demonstrated.
3. Assess the emotional tone.

SCHEMA:
{{
  "star_structure": {{
    "situation": "string",
    "action": "string",
    "result": "string"
  }},
  "demonstrated_values": ["list", "of", "values"],
  "tone": "string",
  "clarity_score": float (0-1)
}}

Output ONLY the JSON, no markdown fences.
"""
        try:
            response_text = await self.llm_client.call(
                system_prompt=system_prompt,
                user_message=user_prompt
            )
            
            # Clean and parse JSON
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            analysis = json.loads(cleaned.strip())
            
            return {
                "raw_response": response,
                "extracted_story": analysis.get("star_structure", {}),
                "keywords_addressed": analysis.get("demonstrated_values", []),
                "analysis": analysis
            }
            
        except Exception as e:
            print(f"  ⚠ Response parsing failed: {e}")
            # Fallback structure
            return {
                "raw_response": response,
                "extracted_story": {"action": response},
                "keywords_addressed": [],
                "analysis": {}
            }