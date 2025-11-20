"""
backend/drafting_engine/style_matcher.py
Analyzes and matches writing style to scholarship preferences
"""

import json
from typing import Dict, Any
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
        
        system_prompt = """
        You are an expert in rhetorical analysis and writing style assessment.
        Analyze scholarship materials to identify distinctive stylistic patterns.
        Return only valid JSON, no additional text.
        """
        
        user_message = f"""
        Analyze the writing style and tone of this scholarship:
        
        Description: {scholarship_profile.get('description', 'N/A')}
        Winner Stories: {scholarship_profile.get('winner_stories', 'N/A')}
        Organization Mission: {scholarship_profile.get('mission', 'N/A')}
        
        Provide a comprehensive style analysis with:
        1. **tone**: Overall tone (formal/casual/inspirational/technical/conversational)
        2. **sentence_structure**: Sentence complexity (simple/complex/varied/compound)
        3. **key_phrases**: List of phrases that appear multiple times or seem significant
        4. **emotional_vs_rational**: Balance between emotional appeal and logical reasoning (0-100 scale, 0=pure logic, 100=pure emotion)
        5. **person_perspective**: Use of first person vs. third person vs. second person
        6. **opening_style**: Typical opening patterns (question/statement/story/statistic)
        7. **closing_style**: Typical closing patterns (call-to-action/reflection/forward-looking)
        8. **vocabulary_level**: Complexity of vocabulary (accessible/moderate/advanced/technical)
        9. **storytelling_approach**: Narrative vs. expository style
        
        Format as JSON with these exact keys:
        {{
            "tone": "...",
            "sentence_structure": "...",
            "key_phrases": ["phrase1", "phrase2", ...],
            "emotional_vs_rational": 50,
            "person_perspective": "...",
            "opening_style": "...",
            "closing_style": "...",
            "vocabulary_level": "...",
            "storytelling_approach": "..."
        }}
        """
        
        style_json = await self.llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return json.loads(style_json)
    
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
        
        system_prompt = """
        You are an expert essay editor specializing in style adaptation.
        Your task is to rewrite essays to match specific style profiles while 
        preserving all factual content, achievements, and authentic voice.
        """
        
        user_message = f"""
        Rewrite this essay to match the target style profile while keeping the core content intact.
        
        ORIGINAL ESSAY:
        {draft}
        
        TARGET STYLE PROFILE:
        - Tone: {style_profile.get('tone', 'professional')}
        - Sentence structure: {style_profile.get('sentence_structure', 'varied')}
        - Key phrases to incorporate naturally: {', '.join(style_profile.get('key_phrases', [])[:5])}
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
        
        Return ONLY the rewritten essay text, no preamble or explanation.
        """
        
        rewritten_essay = await self.llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return rewritten_essay.strip()
    
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
        
        system_prompt = """
        You are an expert in writing assessment and style analysis.
        Compare an essay's style against a target profile and provide actionable feedback.
        Return only valid JSON.
        """
        
        user_message = f"""
        Evaluate how well this essay matches the target style profile:
        
        ESSAY:
        {essay}
        
        TARGET STYLE:
        {json.dumps(style_profile, indent=2)}
        
        Provide assessment as JSON:
        {{
            "overall_alignment_score": 0-100,
            "tone_match": 0-100,
            "structure_match": 0-100,
            "vocabulary_match": 0-100,
            "strengths": ["what matches well"],
            "gaps": ["what needs adjustment"],
            "specific_recommendations": [
                "concrete suggestion 1",
                "concrete suggestion 2"
            ]
        }}
        """
        
        alignment_json = await self.llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return json.loads(alignment_json)