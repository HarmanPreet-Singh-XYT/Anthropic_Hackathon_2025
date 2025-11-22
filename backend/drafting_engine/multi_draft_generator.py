"""
backend/drafting_engine/multi_draft_generator.py
Generates multiple essay drafts with different strategic emphases
"""

import json
import re
from typing import Dict, Any, List, Literal, Optional
from utils.llm_client import create_llm_client


EmphasisType = Literal["primary_priority", "balanced", "storytelling"]


class MultiDraftGenerator:
    """
    Generates multiple essay versions with varied strategic approaches
    """
    
    def __init__(self, temperature: float = 0.7):
        """
        Initialize MultiDraftGenerator with LLM client
        
        Args:
            temperature: Default sampling temperature for creative writing
        """
        self.llm = create_llm_client(temperature=temperature)
        self.transition_llm = create_llm_client(temperature=0.5)  # Lower temp for coherent transitions
    
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
    
    async def generate_drafts(
        self,
        outline: Dict[str, Any],
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any],
        num_drafts: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple essay versions with different emphasis
        
        Args:
            outline: Essay structure from NarrativeArchitect
            content_selection: Selected stories/experiences
            scholarship_profile: Scholarship details and values
            num_drafts: Number of draft variations to generate
        
        Returns:
            List of draft dictionaries with version, emphasis, text, and rationale
        """
        
        drafts = []
        emphasis_options: List[EmphasisType] = ["primary_priority", "balanced", "storytelling"]
        
        for i in range(num_drafts):
            # Determine emphasis strategy for this draft
            emphasis = emphasis_options[i % len(emphasis_options)]
            
            print(f"    ✍️  Generating draft {i+1}/{num_drafts} (emphasis: {emphasis})...")
            
            # Generate the draft
            draft_text = await self.generate_single_draft(
                outline=outline,
                content=content_selection,
                scholarship=scholarship_profile,
                emphasis=emphasis
            )
            
            # Get explanation of approach
            rationale = await self.explain_approach(emphasis, scholarship_profile)
            
            word_count = len(draft_text.split())
            target = outline.get('total_word_limit', 650)
            
            print(f"       Draft {i+1} complete: {word_count}/{target} words")
            
            drafts.append({
                "version": i + 1,
                "emphasis": emphasis,
                "draft": draft_text,
                "rationale": rationale,
                "word_count": word_count,
                "target_word_count": target
            })
        
        return drafts
    
    async def generate_single_draft(
        self,
        outline: Dict[str, Any],
        content: Dict[str, Any],
        scholarship: Dict[str, Any],
        emphasis: EmphasisType
    ) -> str:
        """
        Generate one complete essay draft
        
        Args:
            outline: Essay structure with sections
            content: Selected content to incorporate
            scholarship: Scholarship profile
            emphasis: Strategic emphasis for this draft
        
        Returns:
            Complete essay text
        """
        
        # Build section-by-section with detailed prompts
        essay_sections = {}
        sections = outline.get('sections', {})
        
        for section_name, section_data in sections.items():
            try:
                section_text = await self._generate_section(
                    section_name=section_name,
                    section_data=section_data,
                    content=content,
                    scholarship=scholarship,
                    emphasis=emphasis,
                    outline=outline
                )
                essay_sections[section_name] = section_text
            except Exception as e:
                print(f"       [ERROR] Failed to generate {section_name} section: {e}")
                # Use fallback content
                essay_sections[section_name] = self._get_fallback_section(section_name, section_data)
        
        # Combine sections with smooth transitions
        full_essay = await self.weave_sections(essay_sections, outline)
        
        return full_essay
    
    def _get_fallback_section(self, section_name: str, section_data: Dict[str, Any]) -> str:
        """
        Generate basic fallback content for a section
        """
        return f"[{section_name.title()} section: {section_data.get('description', 'Content goes here')}]"
    
    async def _generate_section(
        self,
        section_name: str,
        section_data: Dict[str, Any],
        content: Dict[str, Any],
        scholarship: Dict[str, Any],
        emphasis: EmphasisType,
        outline: Dict[str, Any]
    ) -> str:
        """
        Generate content for a single essay section
        
        Args:
            section_name: Name of the section (hook, challenge, etc.)
            section_data: Section metadata (word count, purpose, etc.)
            content: Available content to use
            scholarship: Scholarship profile
            emphasis: Strategic emphasis
            outline: Full outline for context
        
        Returns:
            Section text
        """
        
        system_prompt = """You are an expert scholarship essay writer. Write compelling, authentic essay sections that showcase student achievements while maintaining natural voice and avoiding clichés. Return only the section content with no meta-commentary, labels, or markdown formatting."""
        
        # Get emphasis-specific instructions
        emphasis_guidance = self._get_emphasis_guidance(emphasis, scholarship)
        
        # Get relevant content for this section
        relevant_content = self.get_relevant_content(section_name, content)
        
        # Simplify scholarship context
        priorities = scholarship.get('priorities', [])
        top_priorities = ', '.join(priorities[:3]) if priorities else 'scholarship values'
        mission = scholarship.get('mission', 'N/A')
        if len(mission) > 200:
            mission = mission[:200] + "..."
        
        user_message = f"""Write the {section_name.upper()} section of a scholarship essay.

SECTION PURPOSE:
{section_data.get('description', 'N/A')}
Goal: {section_data.get('purpose', 'N/A')}

SCHOLARSHIP CONTEXT:
Name: {scholarship.get('name', 'N/A')}
Key Values: {top_priorities}
Mission: {mission}

CONTENT TO USE:
{relevant_content[:500]}...

STRATEGIC EMPHASIS:
{emphasis_guidance}

CONSTRAINTS:
- Target: ~{section_data.get('target_words', 100)} words
- Range: {section_data.get('word_range', {}).get('min', 80)}-{section_data.get('word_range', {}).get('max', 120)} words
- Include specific details and concrete examples
- Use active voice and strong verbs
- Avoid generic openings like "Throughout my life..."
- Include quantifiable impact (numbers, percentages)

STYLE:
- Authentic student voice (not overly formal)
- Specific, not general
- Show, don't just tell (vivid details)
- Connect to scholarship's mission

Write ONLY the section content. No labels, preamble, or explanation."""
        
        try:
            section_text = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            if not section_text or not section_text.strip():
                print(f"       [WARNING] Empty response for {section_name} section")
                return self._get_fallback_section(section_name, section_data)
            
            # Clean any markdown or labels
            section_text = re.sub(r'^\*\*.*?\*\*:?\s*', '', section_text, flags=re.MULTILINE)
            section_text = re.sub(r'^#{1,6}\s+.*$', '', section_text, flags=re.MULTILINE)
            section_text = re.sub(r'^$$.*?$$:?\s*', '', section_text, flags=re.MULTILINE)
            
            return section_text.strip()
            
        except Exception as e:
            print(f"       [ERROR] Failed to generate {section_name}: {e}")
            return self._get_fallback_section(section_name, section_data)
    
    def _get_emphasis_guidance(
        self,
        emphasis: EmphasisType,
        scholarship: Dict[str, Any]
    ) -> str:
        """
        Get strategic guidance based on emphasis type
        
        Args:
            emphasis: Type of emphasis for this draft
            scholarship: Scholarship profile
        
        Returns:
            Specific guidance text
        """
        
        priorities = scholarship.get('priorities', [])
        top_priority = priorities[0] if priorities else "scholarship values"
        
        if emphasis == "primary_priority":
            return f"""FOCUS HEAVILY on demonstrating: {top_priority}
- Every example should tie back to this value
- Use vocabulary related to this priority
- Make this the central theme"""
        
        elif emphasis == "balanced":
            top_three = ', '.join(priorities[:3]) if len(priorities) >= 3 else top_priority
            return f"""DISTRIBUTE ATTENTION across: {top_three}
- Show how you embody multiple scholarship priorities
- Balance different aspects of your experience
- Demonstrate well-rounded alignment"""
        
        else:  # storytelling
            return """PRIORITIZE NARRATIVE FLOW and compelling storytelling
- Focus on creating an engaging, memorable narrative
- Use vivid details and emotional resonance
- Let the story naturally reveal alignment with values
- Emphasize personal voice and authenticity"""
    
    def get_relevant_content(
        self,
        section_name: str,
        content: Dict[str, Any]
    ) -> str:
        """
        Extract relevant content for specific section
        
        Args:
            section_name: Name of the section
            content: Full content selection
        
        Returns:
            Formatted relevant content
        """
        
        # Get primary story
        primary_story = content.get('primary_story', {})
        if primary_story:
            story_data = primary_story.get('story', {})
            story_text = story_data.get('text', str(story_data))
            
            # Return truncated story text as relevant content
            if len(story_text) > 500:
                return story_text[:500] + "..."
            return story_text
        
        # Fallback
        return "Use student's experiences to demonstrate relevant skills and values"
    
    async def weave_sections(
        self,
        sections: Dict[str, str],
        outline: Dict[str, Any]
    ) -> str:
        """
        Combine sections with smooth transitions
        
        Args:
            sections: Dictionary mapping section names to text
            outline: Essay outline with section order
        
        Returns:
            Complete essay with transitions
        """
        
        # Get section order from outline
        section_order = list(outline.get('sections', {}).keys())
        
        essay_parts = []
        
        for i, section_name in enumerate(section_order):
            # Add the section content
            if section_name in sections:
                essay_parts.append(sections[section_name])
                
                # Add transition to next section (except for last)
                if i < len(section_order) - 1:
                    next_section_name = section_order[i + 1]
                    if next_section_name in sections:
                        transition = await self.generate_transition(
                            sections[section_name],
                            sections[next_section_name]
                        )
                        # Only add transition if it's substantive
                        if transition and len(transition.split()) > 3:
                            essay_parts.append(transition)
        
        return "\n\n".join(essay_parts)
    
    async def generate_transition(
        self,
        current_section: str,
        next_section: str
    ) -> str:
        """
        Create smooth transition sentence between sections
        
        Args:
            current_section: Text of current section
            next_section: Text of next section
        
        Returns:
            Transition sentence (or empty string if not needed)
        """
        
        system_prompt = """You are an expert at creating smooth transitions in essays. Create brief, natural transition sentences that connect ideas seamlessly. If sections already flow well, return "NONE"."""
        
        # Get end of current and start of next section
        current_end = current_section[-300:] if len(current_section) > 300 else current_section
        next_start = next_section[:300] if len(next_section) > 300 else next_section
        
        user_message = f"""Create a brief transition between these sections. Return "NONE" if they already flow well.

Current section ends with:
...{current_end}

Next section begins with:
{next_start}...

Requirements:
- Maximum 15 words
- Natural and conversational
- Avoid "Additionally" or "Furthermore"
- Return "NONE" if sections connect smoothly

Transition (or NONE):"""
        
        try:
            transition = await self.transition_llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            transition = transition.strip()
            
            # Don't use transition if model said none needed
            if "NONE" in transition.upper() or len(transition.split()) > 20:
                return ""
            
            return transition
            
        except Exception as e:
            print(f"       [WARNING] Transition generation failed: {e}")
            return ""  # Skip transition on error
    
    async def explain_approach(
        self,
        emphasis: EmphasisType,
        scholarship_profile: Dict[str, Any]
    ) -> str:
        """
        Explain why this emphasis strategy was chosen
        
        Args:
            emphasis: Strategic emphasis used
            scholarship_profile: Scholarship details
        
        Returns:
            Explanation of approach
        """
        
        system_prompt = """You are an expert scholarship strategist. Explain essay writing strategies in clear, actionable terms for students."""
        
        priorities = scholarship_profile.get('priorities', [])
        top_values = ', '.join(priorities[:3]) if priorities else 'scholarship values'
        
        user_message = f"""Explain why the "{emphasis}" emphasis strategy is effective for this scholarship in 2-3 sentences.

SCHOLARSHIP: {scholarship_profile.get('name', 'N/A')}
Top Values: {top_values}

EMPHASIS: {emphasis}

Cover:
- What this approach prioritizes
- Why it's effective for this scholarship
- What makes this version unique

Keep it conversational and helpful."""
        
        try:
            rationale = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            return rationale.strip() if rationale else f"This draft emphasizes {emphasis} to align with scholarship values."
            
        except Exception as e:
            print(f"       [WARNING] Rationale generation failed: {e}")
            return f"This draft uses a {emphasis} approach to showcase relevant experiences."
    
    async def compare_drafts(
        self,
        drafts: List[Dict[str, Any]],
        scholarship_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze differences between drafts and recommend best option
        
        Args:
            drafts: List of generated drafts
            scholarship_profile: Scholarship details
        
        Returns:
            Comparison analysis with recommendation
        """
        
        system_prompt = """You are an expert scholarship reviewer. Compare essay drafts objectively and provide actionable recommendations. Return ONLY valid JSON with no markdown."""
        
        # Truncate drafts for comparison
        draft_summaries = {}
        for d in drafts:
            draft_text = d['draft']
            if len(draft_text) > 500:
                draft_text = draft_text[:500] + "..."
            draft_summaries[d['version']] = {
                "emphasis": d['emphasis'],
                "preview": draft_text,
                "word_count": d['word_count']
            }
        
        user_message = f"""Compare these scholarship essay drafts and recommend the strongest.

SCHOLARSHIP: {scholarship_profile.get('name', 'N/A')}
Values: {scholarship_profile.get('priorities', [])}

DRAFTS:
{json.dumps(draft_summaries, indent=2)}

Return ONLY valid JSON (no markdown):
{{
    "recommended_version": 1,
    "reasoning": "Why this draft is strongest",
    "draft_comparisons": [
        {{
            "version": 1,
            "strengths": ["strength 1", "strength 2"],
            "weaknesses": ["weakness 1"],
            "score": 8.5
        }}
    ],
    "hybrid_suggestion": "Consider combining X with Y"
}}"""
        
        try:
            comparison_json = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            cleaned_json = self._clean_json_response(comparison_json)
            return json.loads(cleaned_json)
            
        except Exception as e:
            print(f"       [ERROR] Draft comparison failed: {e}")
            # Return default comparison
            return {
                "recommended_version": 1,
                "reasoning": "Unable to perform comparison",
                "draft_comparisons": [
                    {
                        "version": d['version'],
                        "strengths": [f"{d['emphasis']} emphasis"],
                        "weaknesses": [],
                        "score": 7.0
                    }
                    for d in drafts
                ],
                "hybrid_suggestion": "Review drafts manually to identify best elements from each version"
            }