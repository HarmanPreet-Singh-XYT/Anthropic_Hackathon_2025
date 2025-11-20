"""
backend/drafting_engine/supplementary_generator.py
Generates resume bullets, cover letters, and short answer responses
"""

from typing import Dict, List, Any, Optional, Tuple
import json
from utils.llm_client import create_llm_client
from utils.prompt_loader import load_prompt


class SupplementaryGenerator:
    """
    Generates supplementary application materials beyond the main essay
    """
    
    def __init__(self, temperature: float = 0.6):
        self.llm = create_llm_client(temperature=temperature)
    
    async def generate_resume_bullets(
        self,
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate 5-7 optimized resume bullet points tailored to scholarship
        
        Args:
            content_selection: Selected stories/experiences from ContentSelector
            scholarship_profile: Scholarship values and priorities
        
        Returns:
            List of bullet point suggestions with original, improved, rationale
        """
        
        prompt = load_prompt("resume_optimizer", {
            "scholarship_values": json.dumps(scholarship_profile['priorities'], indent=2),
            "weighted_priorities": json.dumps(scholarship_profile['weighted_priorities'], indent=2),
            "student_experiences": json.dumps(content_selection, indent=2),
            "tone": scholarship_profile.get('tone_profile', 'professional')
        })
        
        bullets_json = await self.llm.call(
            system_prompt=prompt,
            user_message="""
            Suggest 5-7 resume bullet point optimizations.
            
            For each bullet:
            1. Identify which existing experience to optimize
            2. Provide original version (if modifying existing)
            3. Provide improved version optimized for this scholarship
            4. Explain why this change aligns with scholarship values
            5. Specify which resume section it belongs to
            
            Format as JSON array:
            [
                {
                    "section": "Experience" | "Projects" | "Leadership" | "Volunteer",
                    "original": "Original bullet text (if modifying existing)",
                    "improved": "Optimized bullet text with scholarship vocabulary",
                    "rationale": "Why this change matters for this specific scholarship",
                    "impact_metrics": "Quantifiable outcomes if applicable",
                    "priority": "high" | "medium" | "low"
                }
            ]
            
            Requirements:
            - Use action verbs from scholarship description
            - Incorporate scholarship's value keywords naturally
            - Add quantifiable metrics where possible
            - Maintain authenticity (no exaggeration)
            - Target 1-2 lines per bullet (15-25 words)
            """
        )
        
        bullets = json.loads(bullets_json)
        return bullets
    
    async def generate_cover_letter(
        self,
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any]
    ) -> str:
        """
        Generate professional cover letter template
        
        Args:
            content_selection: Selected stories and achievements
            scholarship_profile: Scholarship information
        
        Returns:
            Cover letter template with [CUSTOMIZATION] placeholders
        """
        
        prompt = f"""
        Generate a professional cover letter template for this scholarship application.
        
        SCHOLARSHIP DETAILS:
        Name: {scholarship_profile.get('name', 'This Scholarship')}
        Organization: {scholarship_profile.get('organization', '[Organization Name]')}
        Values: {scholarship_profile['priorities']}
        Mission: {scholarship_profile.get('mission', 'Supporting students in their educational journey')}
        
        STUDENT HIGHLIGHTS:
        {json.dumps(content_selection.get('primary_story', {}), indent=2)}
        
        STRUCTURE:
        
        [Opening Paragraph]
        - Express genuine interest in the scholarship
        - Brief statement of why student is excellent fit
        - Hook that connects to scholarship's mission
        
        [Body Paragraph 1]
        - Highlight key experience #1 that aligns with their values
        - Include specific achievement or impact
        - Connect to scholarship's priorities explicitly
        
        [Body Paragraph 2]
        - Highlight key experience #2 (different dimension)
        - Show growth, leadership, or unique perspective
        - Demonstrate understanding of scholarship's mission
        
        [Closing Paragraph]
        - Express enthusiasm and gratitude
        - Forward-looking statement about impact
        - Professional closing
        
        REQUIREMENTS:
        - Tone: Professional but personable, matching {scholarship_profile.get('tone_profile', 'formal')}
        - Length: ~300-350 words (3-4 paragraphs)
        - Use [BRACKETS] for parts student should customize with specific details
        - Include scholarship name and organization explicitly
        - Avoid generic phrases ("I am writing to apply...")
        - Start with engaging opening, not boilerplate
        
        Format: Complete letter with proper business letter structure.
        """
        
        cover_letter = await self.llm.call(
            system_prompt="You are an expert in professional correspondence and scholarship applications.",
            user_message=prompt
        )
        
        return cover_letter
    
    async def generate_short_answers(
        self,
        prompts: List[Tuple[str, int]],
        content_selection: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate responses to short answer questions
        
        Args:
            prompts: List of (question_text, word_limit) tuples
            content_selection: Available student stories
            strategy: Strategic approach for application
        
        Returns:
            List of short answer responses with metadata
        """
        
        answers = []
        
        for question, word_limit in prompts:
            answer_data = await self._generate_single_short_answer(
                question=question,
                word_limit=word_limit,
                content_selection=content_selection,
                strategy=strategy
            )
            
            answers.append(answer_data)
        
        return answers
    
    async def _generate_single_short_answer(
        self,
        question: str,
        word_limit: int,
        content_selection: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate one short answer response
        """
        
        prompt = f"""
        Answer this scholarship short answer question with a compelling, specific response.
        
        QUESTION: {question}
        
        WORD LIMIT: {word_limit} words (strict)
        
        AVAILABLE STUDENT CONTENT:
        {json.dumps(content_selection, indent=2)}
        
        STRATEGIC CONTEXT:
        {json.dumps(strategy, indent=2)}
        
        REQUIREMENTS:
        1. Be specific and concrete (no generic statements)
        2. Include quantifiable impact if question allows
        3. Stay WITHIN word limit (±5 words acceptable)
        4. Match scholarship's values from strategy
        5. Use authentic student voice (not overly formal)
        6. Answer the question directly (don't be tangential)
        7. Include a specific example or story if space allows
        
        STRUCTURE GUIDANCE:
        - If word limit < 100: One focused point with specific example
        - If word limit 100-200: Main point + supporting detail + brief impact
        - If word limit 200+: Mini-essay with intro, body, conclusion
        
        Return ONLY the answer text, no meta-commentary.
        """
        
        answer = await self.llm.call(
            system_prompt="You are an expert at crafting concise, impactful scholarship responses.",
            user_message=prompt
        )
        
        # Validate word count
        actual_word_count = len(answer.split())
        word_count_status = "✓" if abs(actual_word_count - word_limit) <= 5 else "⚠"
        
        return {
            "question": question,
            "answer": answer,
            "word_count": actual_word_count,
            "word_limit": word_limit,
            "word_count_status": word_count_status,
            "within_limit": abs(actual_word_count - word_limit) <= 5
        }
    
    async def generate_additional_materials(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any],
        student_kb: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate any additional requested materials
        
        Args:
            scholarship_profile: Scholarship information
            content_selection: Selected content
            student_kb: Full student knowledge base
        
        Returns:
            Dictionary of additional materials
        """
        
        materials = {}
        
        # Personal statement (if different from main essay)
        if scholarship_profile.get('requires_personal_statement'):
            materials['personal_statement'] = await self._generate_personal_statement(
                scholarship_profile,
                content_selection,
                student_kb
            )
        
        # Recommendation letter talking points
        materials['recommendation_talking_points'] = await self._generate_rec_letter_guidance(
            scholarship_profile,
            content_selection
        )
        
        # Interview preparation (if scholarship has interview stage)
        if scholarship_profile.get('has_interview_stage'):
            materials['interview_prep'] = await self._generate_interview_prep(
                scholarship_profile,
                content_selection
            )
        
        # Portfolio/work samples guidance
        if scholarship_profile.get('accepts_portfolio'):
            materials['portfolio_guidance'] = await self._generate_portfolio_guidance(
                scholarship_profile,
                content_selection
            )
        
        return materials
    
    async def _generate_personal_statement(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any],
        student_kb: Dict[str, Any]
    ) -> str:
        """
        Generate broader personal statement (different from essay)
        """
        
        prompt = f"""
        Write a personal statement for this scholarship application.
        This is DIFFERENT from the main essay - it should provide broader context
        about the student's background, motivations, and goals.
        
        SCHOLARSHIP CONTEXT:
        {json.dumps(scholarship_profile, indent=2)}
        
        STUDENT BACKGROUND:
        {json.dumps(student_kb.get('structured_data', {}), indent=2)}
        
        KEY STORIES TO INCORPORATE:
        {json.dumps(content_selection, indent=2)}
        
        STRUCTURE:
        1. Background: Where you come from, formative experiences
        2. Motivations: Why you're pursuing this field/goal
        3. Journey: Key experiences that shaped your path
        4. Aspirations: Long-term vision and impact goals
        5. Fit: Why this scholarship aligns with your mission
        
        LENGTH: 500-700 words
        TONE: Reflective, authentic, forward-looking
        
        Make it personal, specific, and aligned with scholarship values.
        """
        
        statement = await self.llm.call(
            system_prompt="You are an expert at helping students articulate their personal journey and aspirations.",
            user_message=prompt
        )
        
        return statement
    
    async def _generate_rec_letter_guidance(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Generate talking points for recommendation letters
        """
        
        prompt = f"""
        Create guidance for recommendation letter writers for this scholarship.
        
        SCHOLARSHIP VALUES:
        {scholarship_profile['priorities']}
        
        SCHOLARSHIP PRIORITIES:
        {scholarship_profile['weighted_priorities']}
        
        STUDENT'S KEY STORIES:
        {json.dumps(content_selection, indent=2)}
        
        Provide:
        1. Key qualities the scholarship is looking for
        2. Specific examples/projects recommenders should mention
        3. Suggested talking points that align with scholarship values
        4. What NOT to emphasize (lower-priority attributes)
        
        Format as JSON:
        {{
            "key_qualities": ["quality1", "quality2", ...],
            "examples_to_mention": ["example1", "example2", ...],
            "talking_points": ["point1", "point2", ...],
            "avoid_emphasizing": ["attribute1", "attribute2", ...]
        }}
        """
        
        guidance_json = await self.llm.call(
            system_prompt="You are an expert at coaching recommendation letter strategy.",
            user_message=prompt
        )
        
        return json.loads(guidance_json)
    
    async def _generate_interview_prep(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Generate interview preparation materials
        """
        
        prompt = f"""
        Prepare interview guidance for this scholarship.
        
        SCHOLARSHIP:
        {json.dumps(scholarship_profile, indent=2)}
        
        STUDENT'S STRONGEST STORIES:
        {json.dumps(content_selection, indent=2)}
        
        Generate:
        1. Likely interview questions (10-15)
        2. Key messages to weave into answers
        3. Stories to have ready for different question types
        4. Questions student should ask interviewers
        
        Format as JSON:
        {{
            "likely_questions": [
                {{"question": "...", "strategy": "...", "story_to_use": "..."}}
            ],
            "key_messages": ["message1", "message2", ...],
            "question_types": {{
                "behavioral": ["story1", "story2"],
                "motivational": ["story3", "story4"],
                "technical": ["story5"]
            }},
            "questions_to_ask": ["question1", "question2", ...]
        }}
        """
        
        prep_json = await self.llm.call(
            system_prompt="You are an expert interview coach for scholarship applications.",
            user_message=prompt
        )
        
        return json.loads(prep_json)
    
    async def _generate_portfolio_guidance(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate portfolio/work sample selection guidance
        """
        
        prompt = f"""
        Provide guidance on portfolio/work samples for this scholarship.
        
        SCHOLARSHIP VALUES:
        {scholarship_profile['priorities']}
        
        STUDENT'S PROJECTS:
        {json.dumps(content_selection.get('supporting_stories', []), indent=2)}
        
        Recommend:
        1. Which projects/works to include (top 3-5)
        2. How to present each piece (what to emphasize)
        3. Order of presentation
        4. Descriptions/captions that align with scholarship values
        
        Format as JSON:
        {{
            "recommended_pieces": [
                {{
                    "title": "...",
                    "why_include": "...",
                    "how_to_present": "...",
                    "caption_suggestion": "..."
                }}
            ],
            "presentation_order": ["piece1", "piece2", ...],
            "overall_narrative": "How portfolio tells cohesive story"
        }}
        """
        
        guidance_json = await self.llm.call(
            system_prompt="You are an expert at portfolio curation for scholarship applications.",
            user_message=prompt
        )
        
        return json.loads(guidance_json)


# Export for use in other modules
__all__ = ['SupplementaryGenerator']