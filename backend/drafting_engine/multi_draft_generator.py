"""
backend/drafting_engine/multi_draft_generator.py
Generates multiple essay drafts with different strategic emphases
"""

import json
from typing import Dict, Any, List, Literal
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
            
            # Generate the draft
            draft_text = await self.generate_single_draft(
                outline=outline,
                content=content_selection,
                scholarship=scholarship_profile,
                emphasis=emphasis
            )
            
            # Get explanation of approach
            rationale = await self.explain_approach(emphasis, scholarship_profile)
            
            drafts.append({
                "version": i + 1,
                "emphasis": emphasis,
                "draft": draft_text,
                "rationale": rationale,
                "word_count": len(draft_text.split()),
                "target_word_count": outline.get('total_word_limit', 650)
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
            section_text = await self._generate_section(
                section_name=section_name,
                section_data=section_data,
                content=content,
                scholarship=scholarship,
                emphasis=emphasis,
                outline=outline
            )
            essay_sections[section_name] = section_text
        
        # Combine sections with smooth transitions
        full_essay = await self.weave_sections(essay_sections, outline)
        
        return full_essay
    
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
        
        system_prompt = """
        You are an expert scholarship essay writer.
        Write compelling, authentic essay sections that showcase student achievements
        while maintaining natural voice and avoiding clichés.
        Return only the section content, no meta-commentary or labels.
        """
        
        # Get emphasis-specific instructions
        emphasis_guidance = self._get_emphasis_guidance(emphasis, scholarship)
        
        # Get relevant content for this section
        relevant_content = self.get_relevant_content(section_name, content)
        
        user_message = f"""
        Write the {section_name.upper()} section of a scholarship essay.
        
        SECTION PURPOSE:
        {section_data.get('description', 'N/A')}
        Goal: {section_data.get('purpose', 'N/A')}
        
        SCHOLARSHIP CONTEXT:
        Name: {scholarship.get('name', 'N/A')}
        Key Values: {', '.join(scholarship.get('priorities', [])[:3])}
        Mission: {scholarship.get('mission', 'N/A')}
        Tone: {scholarship.get('tone_profile', 'professional')}
        
        CONTENT TO USE:
        {relevant_content}
        
        STRATEGIC EMPHASIS:
        {emphasis_guidance}
        
        CONSTRAINTS:
        - Target word count: ~{section_data.get('target_words', 100)} words
        - Word range: {section_data.get('word_range', {}).get('min', 80)}-{section_data.get('word_range', {}).get('max', 120)} words
        - Must include specific details and concrete examples
        - Use active voice and strong verbs
        - Avoid generic openings like "Throughout my life..." or "Ever since I was young..."
        - Include quantifiable impact where possible (numbers, percentages, scale)
        
        STYLE REQUIREMENTS:
        - Maintain authentic student voice (not overly formal or artificial)
        - Be specific, not general ("increased membership by 40%" not "improved the club")
        - Show, don't just tell (use vivid details and scenes)
        - Connect naturally to scholarship's mission
        - Start with impact or intrigue, not background
        
        Write ONLY the section content. No section labels, no preamble, no explanation.
        """
        
        section_text = await self.llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return section_text.strip()
    
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
            return f"""
            FOCUS HEAVILY on demonstrating: {top_priority}
            - Every example should tie back to this value
            - Use vocabulary related to this priority
            - Make this the central theme of the section
            """
        
        elif emphasis == "balanced":
            return f"""
            DISTRIBUTE ATTENTION across multiple values: {', '.join(priorities[:3])}
            - Show how you embody multiple scholarship priorities
            - Balance different aspects of your experience
            - Demonstrate well-rounded alignment
            """
        
        else:  # storytelling
            return f"""
            PRIORITIZE NARRATIVE FLOW and compelling storytelling
            - Focus on creating an engaging, memorable narrative
            - Use vivid details and emotional resonance
            - Let the story naturally reveal alignment with values
            - Emphasize personal voice and authenticity over explicit value statements
            """
    
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
        
        # Map section names to content types
        section_content_map = {
            "hook": ["primary_story", "most_impactful_moment"],
            "challenge": ["obstacles", "context", "problem_statement"],
            "action": ["initiatives", "leadership_examples", "projects"],
            "impact": ["outcomes", "results", "metrics"],
            "reflection": ["growth", "learnings", "future_goals"],
            "context": ["background", "motivation"],
            "approach": ["methodology", "innovation", "process"],
            "results": ["outcomes", "metrics", "achievements"],
            "vision": ["future_goals", "aspirations"],
            "empathy": ["personal_connection", "motivation"],
            "commitment": ["ongoing_work", "future_plans"]
        }
        
        # Get relevant content keys for this section
        relevant_keys = section_content_map.get(section_name, [])
        
        # Extract relevant content
        relevant_parts = []
        for key in relevant_keys:
            if key in content:
                relevant_parts.append(f"{key}: {content[key]}")
        
        if not relevant_parts:
            # Fallback to primary story if no specific mapping
            primary = content.get('primary_story', content.get('experiences', {}))
            relevant_parts.append(f"Available content: {json.dumps(primary, indent=2)}")
        
        return "\n".join(relevant_parts)
    
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
        
        system_prompt = """
        You are an expert at creating smooth transitions in essays.
        Create brief, natural transition sentences that connect ideas seamlessly.
        If sections already flow well, return nothing.
        """
        
        # Get end of current and start of next section
        current_end = current_section[-300:] if len(current_section) > 300 else current_section
        next_start = next_section[:300] if len(next_section) > 300 else next_section
        
        user_message = f"""
        Create a brief transition sentence between these two essay sections.
        Only add a transition if needed - if they already flow well, return "NONE".
        
        Current section ends with:
        ...{current_end}
        
        Next section begins with:
        {next_start}...
        
        Requirements:
        - Maximum 15 words
        - Natural and conversational
        - Avoid obvious transitions like "Additionally" or "Furthermore"
        - Should feel like natural progression of thought
        - Return "NONE" if sections already connect smoothly
        
        Transition sentence (or NONE):
        """
        
        transition = await self.transition_llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        transition = transition.strip()
        
        # Don't use transition if model said none needed
        if "NONE" in transition.upper() or len(transition.split()) > 20:
            return ""
        
        return transition
    
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
        
        system_prompt = """
        You are an expert scholarship strategist.
        Explain essay writing strategies in clear, actionable terms for students.
        """
        
        user_message = f"""
        Explain why the "{emphasis}" emphasis strategy is effective for this scholarship.
        
        SCHOLARSHIP:
        Name: {scholarship_profile.get('name', 'N/A')}
        Top Values: {', '.join(scholarship_profile.get('priorities', [])[:3])}
        
        EMPHASIS STRATEGY: {emphasis}
        
        Provide a 2-3 sentence explanation covering:
        - What this approach prioritizes
        - Why it's effective for this specific scholarship
        - What makes this version unique
        
        Keep it conversational and helpful for students comparing drafts.
        """
        
        rationale = await self.llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return rationale.strip()
    
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
        
        system_prompt = """
        You are an expert scholarship reviewer.
        Compare essay drafts objectively and provide actionable recommendations.
        Return only valid JSON.
        """
        
        draft_texts = {d['version']: d['draft'] for d in drafts}
        
        user_message = f"""
        Compare these scholarship essay drafts and recommend the strongest option.
        
        SCHOLARSHIP: {scholarship_profile.get('name', 'N/A')}
        Values: {scholarship_profile.get('priorities', [])}
        
        DRAFTS:
        {json.dumps(draft_texts, indent=2)}
        
        Provide analysis as JSON:
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
            "hybrid_suggestion": "Consider combining X from version 1 with Y from version 2"
        }}
        """
        
        comparison_json = await self.llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return json.loads(comparison_json)