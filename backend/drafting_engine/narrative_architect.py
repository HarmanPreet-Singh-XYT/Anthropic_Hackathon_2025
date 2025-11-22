"""
backend/drafting_engine/narrative_architect.py
Designs essay structure and narrative arc based on scholarship personality
"""

import json
import re
from typing import Dict, Any, Literal, Optional
from utils.llm_client import create_llm_client


NarrativeStyle = Literal["hero_journey", "achievement_showcase", "community_impact"]


class NarrativeArchitect:
    """
    Creates optimized essay outlines based on scholarship type and values
    """
    
    def __init__(self, temperature: float = 0.4):
        """
        Initialize NarrativeArchitect with LLM client
        
        Args:
            temperature: Sampling temperature (lower for structured outline decisions)
        """
        self.llm = create_llm_client(temperature=temperature)
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean LLM response to extract pure JSON
        
        Handles:
        - Markdown code blocks (```json ... ```)
        - Leading/trailing whitespace
        - Text before/after JSON
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
    
    async def create_outline(
        self,
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any],
        word_limit: int
    ) -> Dict[str, Any]:
        """
        Build essay structure based on scholarship personality
        
        Args:
            content_selection: Selected stories/experiences from ContentSelector
            scholarship_profile: Scholarship values and characteristics
            word_limit: Target word count for essay
        
        Returns:
            Structured outline with sections and word allocations
        """
        
        print("    🏗️  Detecting narrative style...")
        # Determine narrative arc based on scholarship type
        narrative_style = await self.detect_narrative_style(scholarship_profile)
        print(f"    📖 Selected narrative style: {narrative_style}")
        
        # Get base outline template
        outline = self._get_outline_template(narrative_style)
        
        # Allocate word counts to each section
        outline = self._allocate_word_counts(outline, word_limit)
        
        # Add metadata
        outline["narrative_style"] = narrative_style
        outline["total_word_limit"] = word_limit
        outline["scholarship_name"] = scholarship_profile.get('name', 'N/A')
        
        print("    💡 Generating section guidance...")
        # Get AI-powered section guidance
        section_guidance = await self._generate_section_guidance(
            outline,
            content_selection,
            scholarship_profile
        )
        outline["section_guidance"] = section_guidance
        
        return outline
    
    async def detect_narrative_style(
        self,
        scholarship_profile: Dict[str, Any]
    ) -> NarrativeStyle:
        """
        Use LLM to determine best narrative approach
        
        Args:
            scholarship_profile: Scholarship details and values
        
        Returns:
            Optimal narrative style for this scholarship
        """
        
        system_prompt = """You are an expert in scholarship essay strategy and narrative structure. Analyze scholarship characteristics to determine the most effective narrative approach. Respond with ONLY the narrative style name (hero_journey, achievement_showcase, or community_impact), no explanation or additional text."""
        
        user_message = f"""Based on this scholarship's values and language, what narrative style will resonate best?

SCHOLARSHIP DETAILS:
Name: {scholarship_profile.get('name', 'N/A')}
Description: {scholarship_profile.get('description', 'N/A')}
Key Values: {json.dumps(scholarship_profile.get('priorities', []), indent=2)}
Mission: {scholarship_profile.get('mission', 'N/A')}

Choose ONE narrative style:

1. **hero_journey**: Best for scholarships emphasizing:
   - Personal transformation and growth
   - Overcoming significant obstacles
   - Resilience and perseverance
   - Character development
   Example: "Students who have overcome adversity"

2. **achievement_showcase**: Best for scholarships emphasizing:
   - Technical excellence and innovation
   - Academic/professional accomplishments
   - Measurable results and outcomes
   - STEM or merit-based focus
   Example: "Outstanding academic achievement"

3. **community_impact**: Best for scholarships emphasizing:
   - Service and giving back
   - Community engagement
   - Social justice or activism
   Example: "Students committed to serving their communities"

Respond with ONLY one of these exact strings:
- hero_journey
- achievement_showcase
- community_impact"""
        
        try:
            response = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            print(f"    [DEBUG] Narrative style response: {response[:200]}")
            
            # Clean and validate response
            style = response.strip().lower()
            
            # Map to valid style
            if "hero" in style or "journey" in style:
                return "hero_journey"
            elif "achievement" in style or "showcase" in style:
                return "achievement_showcase"
            elif "community" in style or "impact" in style:
                return "community_impact"
            else:
                # Default fallback based on priorities
                priorities = scholarship_profile.get('priorities', [])
                if any(word in str(priorities).lower() for word in ['service', 'community', 'impact']):
                    print("    [FALLBACK] Defaulting to community_impact based on priorities")
                    return "community_impact"
                elif any(word in str(priorities).lower() for word in ['academic', 'achievement', 'excellence']):
                    print("    [FALLBACK] Defaulting to achievement_showcase based on priorities")
                    return "achievement_showcase"
                else:
                    print("    [FALLBACK] Defaulting to hero_journey")
                    return "hero_journey"
                    
        except Exception as e:
            print(f"    [ERROR] Failed to detect narrative style: {e}")
            print("    [FALLBACK] Defaulting to hero_journey")
            return "hero_journey"
    
    def _get_outline_template(self, narrative_style: NarrativeStyle) -> Dict[str, Any]:
        """
        Get base outline template for narrative style
        
        Args:
            narrative_style: Type of narrative arc
        
        Returns:
            Outline structure with sections and percentages
        """
        
        if narrative_style == "hero_journey":
            # For transformative/personal growth scholarships
            return {
                "sections": {
                    "hook": {
                        "description": "Opening scene from primary story that captures transformation",
                        "purpose": "Grab attention with vivid, specific moment",
                        "allocation_percentage": 0.15
                    },
                    "challenge": {
                        "description": "Problem/obstacle faced - the 'before' state",
                        "purpose": "Establish stakes and context for growth",
                        "allocation_percentage": 0.20
                    },
                    "action": {
                        "description": "What you did - leadership/innovation in response",
                        "purpose": "Demonstrate agency, skills, and determination",
                        "allocation_percentage": 0.30
                    },
                    "impact": {
                        "description": "Concrete results and outcomes achieved",
                        "purpose": "Show measurable change and effectiveness",
                        "allocation_percentage": 0.20
                    },
                    "reflection": {
                        "description": "Growth achieved and future vision",
                        "purpose": "Connect to scholarship values and demonstrate maturity",
                        "allocation_percentage": 0.15
                    }
                }
            }
        
        elif narrative_style == "achievement_showcase":
            # For merit/technical scholarships
            return {
                "sections": {
                    "hook": {
                        "description": "Bold statement of achievement or intriguing question",
                        "purpose": "Establish credibility immediately",
                        "allocation_percentage": 0.10
                    },
                    "context": {
                        "description": "The challenge/opportunity that prompted work",
                        "purpose": "Frame the problem space and its significance",
                        "allocation_percentage": 0.20
                    },
                    "approach": {
                        "description": "Your methodology, innovation, and technical execution",
                        "purpose": "Showcase expertise and problem-solving ability",
                        "allocation_percentage": 0.35
                    },
                    "results": {
                        "description": "Quantified outcomes and impact metrics",
                        "purpose": "Prove effectiveness with concrete data",
                        "allocation_percentage": 0.25
                    },
                    "vision": {
                        "description": "Future applications and continued excellence",
                        "purpose": "Show forward-thinking and scholarship ROI",
                        "allocation_percentage": 0.10
                    }
                }
            }
        
        else:  # community_impact
            # For service/community scholarships
            return {
                "sections": {
                    "hook": {
                        "description": "Community need observed - specific scene or statistic",
                        "purpose": "Establish urgency and personal connection",
                        "allocation_percentage": 0.15
                    },
                    "empathy": {
                        "description": "Personal connection to cause and understanding",
                        "purpose": "Show genuine care and motivation",
                        "allocation_percentage": 0.20
                    },
                    "action": {
                        "description": "Initiative taken and community engagement",
                        "purpose": "Demonstrate leadership through service",
                        "allocation_percentage": 0.25
                    },
                    "impact": {
                        "description": "Lives changed - quantified community benefit",
                        "purpose": "Prove meaningful difference with specific examples",
                        "allocation_percentage": 0.25
                    },
                    "commitment": {
                        "description": "Ongoing dedication and future service plans",
                        "purpose": "Show sustained commitment beyond requirement",
                        "allocation_percentage": 0.15
                    }
                }
            }
    
    def _allocate_word_counts(
        self,
        outline: Dict[str, Any],
        word_limit: int
    ) -> Dict[str, Any]:
        """
        Allocate specific word counts to each section
        
        Args:
            outline: Base outline structure
            word_limit: Total word limit
        
        Returns:
            Outline with word counts added
        """
        
        sections = outline["sections"]
        
        for section_name, section_data in sections.items():
            percentage = section_data["allocation_percentage"]
            section_data["target_words"] = int(word_limit * percentage)
            section_data["word_range"] = {
                "min": int(word_limit * percentage * 0.8),  # Allow 20% flexibility
                "max": int(word_limit * percentage * 1.2)
            }
        
        return outline
    
    async def _generate_section_guidance(
        self,
        outline: Dict[str, Any],
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate specific writing guidance for each section
        
        Args:
            outline: Outline structure with sections
            content_selection: Selected content from ContentSelector
            scholarship_profile: Scholarship details
        
        Returns:
            Dictionary mapping section names to specific guidance
        """
        
        system_prompt = """You are an expert essay writing coach specializing in scholarship applications. Provide specific, actionable guidance for each essay section. Return ONLY valid JSON with no markdown or code blocks."""
        
        # Simplify content selection for prompt
        primary_story = content_selection.get('primary_story', {})
        story_text = ""
        if primary_story:
            story_data = primary_story.get('story', {})
            story_text = story_data.get('text', str(story_data))[:300]
        
        user_message = f"""Provide specific writing guidance for each section of this essay outline.

OUTLINE STRUCTURE:
{json.dumps(outline['sections'], indent=2)}

PRIMARY STORY TO USE:
{story_text}...

SCHOLARSHIP FOCUS:
Values: {scholarship_profile.get('priorities', [])}
Mission: {scholarship_profile.get('mission', 'N/A')[:200]}

For each section, provide:
- What specific story/experience to use
- Key points to emphasize
- What to avoid

Return ONLY valid JSON (no markdown):
{{
    "hook": "Specific guidance for hook section...",
    "challenge": "Specific guidance for next section...",
    ...
}}"""
        
        try:
            guidance_json = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            print(f"    [DEBUG] Section guidance response length: {len(guidance_json) if guidance_json else 0}")
            
            if not guidance_json or not guidance_json.strip():
                print("    [WARNING] Empty section guidance response")
                return self._get_default_section_guidance(outline)
            
            cleaned_json = self._clean_json_response(guidance_json)
            return json.loads(cleaned_json)
            
        except json.JSONDecodeError as e:
            print(f"    [ERROR] Failed to parse section guidance: {e}")
            print(f"    [ERROR] Response: {guidance_json[:500] if guidance_json else 'EMPTY'}")
            return self._get_default_section_guidance(outline)
            
        except Exception as e:
            print(f"    [ERROR] Unexpected error in section guidance: {e}")
            return self._get_default_section_guidance(outline)
    
    def _get_default_section_guidance(self, outline: Dict[str, Any]) -> Dict[str, str]:
        """
        Provide default guidance when LLM fails
        
        Args:
            outline: Outline structure
            
        Returns:
            Default guidance for each section
        """
        sections = outline.get('sections', {})
        guidance = {}
        
        for section_name, section_data in sections.items():
            guidance[section_name] = (
                f"{section_data.get('description', 'Write this section')}. "
                f"Purpose: {section_data.get('purpose', 'Support your narrative')}. "
                f"Target {section_data.get('target_words', 100)} words."
            )
        
        return guidance
    
    async def validate_outline_fit(
        self,
        outline: Dict[str, Any],
        scholarship_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that chosen outline structure matches scholarship well
        
        Args:
            outline: Created outline structure
            scholarship_profile: Scholarship details
        
        Returns:
            Validation results with confidence score and suggestions
        """
        
        system_prompt = """You are an expert in scholarship essay strategy. Evaluate whether an outline structure is optimal for a specific scholarship. Return ONLY valid JSON with no markdown."""
        
        user_message = f"""Evaluate this outline for alignment with scholarship characteristics:

OUTLINE:
Narrative Style: {outline.get('narrative_style', 'N/A')}
Sections: {list(outline.get('sections', {}).keys())}

SCHOLARSHIP:
Name: {scholarship_profile.get('name', 'N/A')}
Values: {scholarship_profile.get('priorities', [])}
Mission: {scholarship_profile.get('mission', 'N/A')[:200]}

Provide evaluation as JSON (no markdown):
{{
    "confidence_score": 8.5,
    "strengths": ["strength 1", "strength 2"],
    "concerns": ["concern 1"],
    "alternative_style": null
}}"""
        
        try:
            validation_json = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            cleaned_json = self._clean_json_response(validation_json)
            return json.loads(cleaned_json)
            
        except Exception as e:
            print(f"    [ERROR] Outline validation failed: {e}")
            return {
                "confidence_score": 7.0,
                "strengths": ["Structure follows best practices"],
                "concerns": [],
                "alternative_style": None
            }