"""
backend/drafting_engine/style_matcher.py
Analyzes and matches writing style to scholarship preferences
"""

import json
import re
from typing import Dict, Any, Optional
from utils.llm_client import create_llm_client


class StyleMatcher:
    """
    Analyzes scholarship writing style and adjusts drafts to match
    """
    
    def __init__(self, temperature: float = 0.6):
        """
        Initialize StyleMatcher with LLM client
        
        Args:
            temperature: Sampling temperature for LLM calls
        """
        self.llm = create_llm_client(temperature=temperature)
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean LLM response to extract pure JSON
        """
        if not response:
            return "{}"
        
        # Remove markdown code blocks
        response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'^```\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'\s*```$', '', response, flags=re.MULTILINE)
        
        # Try to find JSON object or array
        json_match = re.search(r'[\{$$].*[\}$$]', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return response.strip()
    
    def _get_default_style_profile(self) -> Dict[str, Any]:
        """
        Return default style profile when analysis fails
        """
        return {
            "tone": "professional and authentic",
            "sentence_structure": "varied",
            "key_phrases": ["leadership", "impact", "community", "growth"],
            "emotional_vs_rational": 50,
            "person_perspective": "first person",
            "opening_style": "engaging statement",
            "closing_style": "forward-looking",
            "vocabulary_level": "moderate",
            "storytelling_approach": "narrative with reflection"
        }
    
    async def analyze_scholarship_style(
        self,
        scholarship_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract stylistic patterns from scholarship materials
        
        Args:
            scholarship_profile: Dictionary containing scholarship details
        
        Returns:
            Style profile with tone, structure, and key patterns
        """
        
        print("    🎨 Analyzing scholarship style...")
        
        system_prompt = """You are an expert in rhetorical analysis and writing style assessment. Analyze scholarship materials to identify distinctive stylistic patterns. Return ONLY valid JSON with no markdown or additional text."""
        
        # Gather available text, with safe fallbacks
        description = scholarship_profile.get('description', 'N/A')
        if len(description) > 500:
            description = description[:500] + "..."
        
        mission = scholarship_profile.get('mission', 'N/A')
        if len(mission) > 300:
            mission = mission[:300] + "..."
        
        user_message = f"""Analyze the writing style and tone of this scholarship:

Description: {description}
Organization Mission: {mission}
Key Values: {', '.join(scholarship_profile.get('priorities', [])[:5])}

Provide a comprehensive style analysis as JSON (no markdown):
{{
    "tone": "formal/casual/inspirational/technical/conversational",
    "sentence_structure": "simple/complex/varied/compound",
    "key_phrases": ["phrase1", "phrase2"],
    "emotional_vs_rational": 50,
    "person_perspective": "first/third/second person",
    "opening_style": "question/statement/story/statistic",
    "closing_style": "call-to-action/reflection/forward-looking",
    "vocabulary_level": "accessible/moderate/advanced/technical",
    "storytelling_approach": "narrative/expository/mixed"
}}"""
        
        try:
            style_json = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            print(f"    [DEBUG] Style analysis response length: {len(style_json) if style_json else 0}")
            
            if not style_json or not style_json.strip():
                print("    [WARNING] Empty style analysis response")
                return self._get_default_style_profile()
            
            cleaned_json = self._clean_json_response(style_json)
            style_profile = json.loads(cleaned_json)
            
            # Validate required keys
            required_keys = ["tone", "sentence_structure", "vocabulary_level"]
            for key in required_keys:
                if key not in style_profile:
                    print(f"    [WARNING] Missing key '{key}' in style profile")
                    style_profile[key] = self._get_default_style_profile()[key]
            
            return style_profile
            
        except json.JSONDecodeError as e:
            print(f"    [ERROR] Failed to parse style analysis: {e}")
            print(f"    [ERROR] Response: {style_json[:300] if style_json else 'EMPTY'}")
            return self._get_default_style_profile()
            
        except Exception as e:
            print(f"    [ERROR] Unexpected error in style analysis: {e}")
            return self._get_default_style_profile()
    
    async def adjust_draft_style(
        self,
        draft: str,
        style_profile: Dict[str, Any],
        scholarship_name: str = "this scholarship"
    ) -> str:
        """
        Modify draft to match scholarship's style while preserving content
        
        Args:
            draft: Original essay text
            style_profile: Target style patterns from analyze_scholarship_style
            scholarship_name: Name of scholarship for context
        
        Returns:
            Rewritten essay matching target style
        """
        
        print(f"    ✨ Adjusting style to match {scholarship_name}...")
        
        system_prompt = """You are an expert essay editor specializing in style adaptation. Your task is to rewrite essays to match specific style profiles while preserving all factual content, achievements, and authentic voice. Return ONLY the rewritten essay with no preamble or explanation."""
        
        # Safely get style attributes with defaults
        key_phrases = style_profile.get('key_phrases', [])[:5]
        key_phrases_str = ', '.join(key_phrases) if key_phrases else "N/A"
        
        user_message = f"""Rewrite this essay to match the target style profile while keeping the core content intact.

ORIGINAL ESSAY:
{draft}

TARGET STYLE PROFILE:
- Tone: {style_profile.get('tone', 'professional')}
- Sentence structure: {style_profile.get('sentence_structure', 'varied')}
- Key phrases to incorporate naturally: {key_phrases_str}
- Emotional vs. rational balance: {style_profile.get('emotional_vs_rational', 50)}/100 emotional
- Perspective: {style_profile.get('person_perspective', 'first person')}
- Vocabulary level: {style_profile.get('vocabulary_level', 'moderate')}
- Opening style: {style_profile.get('opening_style', 'engaging statement')}
- Closing style: {style_profile.get('closing_style', 'forward-looking')}

CRITICAL REQUIREMENTS:
- Preserve ALL specific facts, numbers, dates, and achievements exactly
- Keep the same stories, examples, and experiences
- Maintain the student's authentic voice and personality
- Only adjust language choice, sentence structure, and tone
- Don't add information that wasn't in the original
- Don't make it sound artificial or over-polished
- Ensure natural incorporation of key phrases (don't force them)
- Match the approximate length of the original (±10%)

Return ONLY the rewritten essay text, no preamble or explanation."""
        
        try:
            rewritten_essay = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            if not rewritten_essay or not rewritten_essay.strip():
                print("    [WARNING] Empty style adjustment response, using original")
                return draft
            
            # Clean any metadata or labels
            rewritten_essay = re.sub(r'^(REWRITTEN|ESSAY|ADJUSTED):\s*', '', rewritten_essay, flags=re.IGNORECASE)
            rewritten_essay = re.sub(r'^\*\*.*?\*\*:?\s*', '', rewritten_essay, flags=re.MULTILINE)
            
            word_count_diff = abs(len(rewritten_essay.split()) - len(draft.split()))
            if word_count_diff > len(draft.split()) * 0.3:  # More than 30% change
                print(f"    [WARNING] Style adjustment changed length significantly ({word_count_diff} words)")
            
            return rewritten_essay.strip()
            
        except Exception as e:
            print(f"    [ERROR] Style adjustment failed: {e}")
            print("    [FALLBACK] Using original draft")
            return draft
    
    async def compare_style_alignment(
        self,
        essay: str,
        style_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess how well an essay matches the target style profile
        
        Args:
            essay: Essay text to evaluate
            style_profile: Target style profile
        
        Returns:
            Alignment score and specific recommendations
        """
        
        system_prompt = """You are an expert in writing assessment and style analysis. Compare an essay's style against a target profile and provide actionable feedback. Return ONLY valid JSON with no markdown."""
        
        # Truncate essay for analysis
        essay_preview = essay[:1000] if len(essay) > 1000 else essay
        
        user_message = f"""Evaluate how well this essay matches the target style profile:

ESSAY (preview):
{essay_preview}...

TARGET STYLE:
{json.dumps(style_profile, indent=2)}

Provide assessment as JSON (no markdown):
{{
    "overall_alignment_score": 85,
    "tone_match": 90,
    "structure_match": 80,
    "vocabulary_match": 85,
    "strengths": ["what matches well"],
    "gaps": ["what needs adjustment"],
    "specific_recommendations": [
        "concrete suggestion 1",
        "concrete suggestion 2"
    ]
}}"""
        
        try:
            alignment_json = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            cleaned_json = self._clean_json_response(alignment_json)
            alignment = json.loads(cleaned_json)
            
            # Validate scores are numeric
            for score_key in ["overall_alignment_score", "tone_match", "structure_match", "vocabulary_match"]:
                if score_key in alignment and not isinstance(alignment[score_key], (int, float)):
                    alignment[score_key] = 75  # Default score
            
            return alignment
            
        except Exception as e:
            print(f"    [ERROR] Style alignment comparison failed: {e}")
            return {
                "overall_alignment_score": 75,
                "tone_match": 75,
                "structure_match": 75,
                "vocabulary_match": 75,
                "strengths": ["Style analysis unavailable"],
                "gaps": [],
                "specific_recommendations": ["Manual review recommended"]
            }