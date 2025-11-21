"""
backend/drafting_engine/supplementary_generator.py
Generates resume bullets, cover letters, LaTeX resumes, and short answer responses
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
        """
        prompt = load_prompt("optimizer", {
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
            """
        )
        
        bullets = json.loads(bullets_json)
        return bullets
    
    async def generate_latex_resume(
        self,
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any],
        student_kb: Optional[Dict[str, Any]] = None,
        template_style: str = "modern"
    ) -> Dict[str, Any]:
        """
        Generate a complete LaTeX resume tailored to the scholarship
        
        Args:
            content_selection: Selected stories/experiences from ContentSelector
            scholarship_profile: Scholarship values and priorities
            student_kb: Optional full student knowledge base for additional details
            template_style: "modern", "classic", or "minimal"
        
        Returns:
            Dictionary with LaTeX code, compilation instructions, and metadata
        """
        
        # First, get optimized bullet points
        optimized_bullets = await self.generate_resume_bullets(
            content_selection=content_selection,
            scholarship_profile=scholarship_profile
        )
        
        # Extract student info from KB or content selection
        student_info = self._extract_student_info(content_selection, student_kb)
        
        prompt = f"""
        Generate a complete, compilable LaTeX resume tailored for this scholarship application.
        
        SCHOLARSHIP CONTEXT:
        Name: {scholarship_profile.get('name', 'Scholarship')}
        Values: {json.dumps(scholarship_profile.get('priorities', []), indent=2)}
        Weighted Priorities: {json.dumps(scholarship_profile.get('weighted_priorities', {}), indent=2)}
        Tone: {scholarship_profile.get('tone_profile', 'professional')}
        
        STUDENT INFORMATION:
        {json.dumps(student_info, indent=2)}
        
        OPTIMIZED BULLET POINTS TO INCORPORATE:
        {json.dumps(optimized_bullets, indent=2)}
        
        CONTENT/EXPERIENCES TO HIGHLIGHT:
        {json.dumps(content_selection, indent=2)}
        
        TEMPLATE STYLE: {template_style}
        - modern: Clean lines, subtle colors, modern fonts (uses fontawesome icons)
        - classic: Traditional academic style, serif fonts, no colors
        - minimal: Ultra-clean, maximum whitespace, very readable
        
        REQUIREMENTS:
        1. Generate COMPLETE, COMPILABLE LaTeX code (no placeholders except for personal info)
        2. Use standard LaTeX packages available in most distributions
        3. Include proper sectioning: Education, Experience, Projects, Skills, Leadership/Activities
        4. Order sections strategically based on scholarship priorities
        5. Incorporate the optimized bullet points naturally
        6. Use action verbs and quantifiable metrics
        7. Keep to ONE PAGE (use appropriate margins and font sizes)
        8. Include comments for easy customization
        9. Use [YOUR NAME], [YOUR EMAIL], etc. for personal info placeholders
        
        LATEX PACKAGES TO USE:
        - geometry (for margins)
        - enumitem (for custom lists)
        - titlesec (for section formatting)
        - hyperref (for links)
        - xcolor (for colors, if modern style)
        - fontawesome5 (for icons, if modern style)
        
        Return the complete LaTeX document starting with \\documentclass and ending with \\end{{document}}.
        """
        
        latex_code = await self.llm.call(
            system_prompt="""You are an expert LaTeX typesetter specializing in professional resumes. 
            You create clean, ATS-friendly resumes that compile without errors.
            Always generate complete, working LaTeX code.""",
            user_message=prompt
        )
        
        # Clean up the LaTeX code (remove markdown code blocks if present)
        latex_code = self._clean_latex_output(latex_code)
        
        # Generate section order rationale
        section_rationale = await self._generate_section_rationale(
            scholarship_profile=scholarship_profile,
            content_selection=content_selection
        )
        
        return {
            "latex_code": latex_code,
            "template_style": template_style,
            "optimized_bullets": optimized_bullets,
            "section_order_rationale": section_rationale,
            "compilation_instructions": self._get_compilation_instructions(),
            "customization_guide": self._get_customization_guide(),
            "scholarship_alignment": {
                "name": scholarship_profile.get('name'),
                "key_values_emphasized": scholarship_profile.get('priorities', [])[:3],
                "tone_used": scholarship_profile.get('tone_profile', 'professional')
            }
        }
    
    def _extract_student_info(
        self,
        content_selection: Dict[str, Any],
        student_kb: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract structured student information for resume"""
        
        info = {
            "name": "[YOUR NAME]",
            "email": "[YOUR EMAIL]",
            "phone": "[YOUR PHONE]",
            "linkedin": "[YOUR LINKEDIN]",
            "github": "[YOUR GITHUB]",
            "location": "[CITY, STATE]",
            "education": [],
            "experiences": [],
            "projects": [],
            "skills": [],
            "leadership": []
        }
        
        if student_kb:
            structured = student_kb.get('structured_data', {})
            info.update({
                "education": structured.get('education', []),
                "experiences": structured.get('experiences', []),
                "projects": structured.get('projects', []),
                "skills": structured.get('skills', []),
                "leadership": structured.get('leadership', [])
            })
        
        # Extract from content selection
        if content_selection:
            primary = content_selection.get('primary_story', {})
            supporting = content_selection.get('supporting_stories', [])
            
            # Add any experiences not already captured
            all_stories = [primary] + supporting if primary else supporting
            for story in all_stories:
                if story.get('type') == 'experience' and story not in info['experiences']:
                    info['experiences'].append(story)
                elif story.get('type') == 'project' and story not in info['projects']:
                    info['projects'].append(story)
        
        return info
    
    def _clean_latex_output(self, latex_code: str) -> str:
        """Remove markdown formatting from LaTeX output"""
        code = latex_code.strip()
        if code.startswith("```latex"):
            code = code[8:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()
    
    async def _generate_section_rationale(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any]
    ) -> Dict[str, str]:
        """Explain why sections are ordered the way they are"""
        
        prompt = f"""
        Based on this scholarship's priorities, explain the optimal resume section order.
        
        Scholarship Priorities: {scholarship_profile.get('priorities', [])}
        Weighted Priorities: {scholarship_profile.get('weighted_priorities', {{}})}
        
        Return JSON with section names as keys and brief rationale as values:
        {{
            "Education": "Why this section is placed here...",
            "Experience": "Why this section is placed here...",
            ...
        }}
        """
        
        rationale_json = await self.llm.call(
            system_prompt="You are a career advisor explaining resume strategy.",
            user_message=prompt
        )
        
        try:
            return json.loads(rationale_json)
        except json.JSONDecodeError:
            return {"note": "Section order optimized for scholarship priorities"}
    
    def _get_compilation_instructions(self) -> str:
        """Return LaTeX compilation instructions"""
        return """
COMPILATION INSTRUCTIONS:
========================

Option 1: Overleaf (Recommended for beginners)
1. Go to overleaf.com and create a free account
2. Click "New Project" → "Blank Project"
3. Delete the default content and paste this LaTeX code
4. Click "Recompile" to see your resume
5. Download as PDF when satisfied

Option 2: Local LaTeX Installation
1. Install a LaTeX distribution:
   - Windows: MiKTeX (miktex.org)
   - Mac: MacTeX (tug.org/mactex)
   - Linux: TeX Live (sudo apt install texlive-full)
2. Save the code as 'resume.tex'
3. Compile with: pdflatex resume.tex
4. For modern template with icons: xelatex resume.tex

Option 3: Online Compilers
- latex.codecogs.com
- latexbase.com

TROUBLESHOOTING:
- If fontawesome5 errors occur, use 'classic' or 'minimal' template
- For special characters, ensure UTF-8 encoding
- Run pdflatex twice if references don't appear correctly
"""
    
    def _get_customization_guide(self) -> str:
        """Return customization guide for the LaTeX resume"""
        return """
CUSTOMIZATION GUIDE:
===================

PERSONAL INFORMATION:
Replace all [PLACEHOLDER] text with your actual information.

ADDING/REMOVING SECTIONS:
- To add a section: Copy an existing \\section{} block
- To remove: Delete from \\section{} to the next \\section{}

ADJUSTING SPACING:
- Increase space: Add \\vspace{5pt} between items
- Decrease space: Change \\vspace to smaller values or \\vspace{-5pt}

CHANGING COLORS (modern template):
- Find \\definecolor{} commands near the top
- Adjust RGB values or use predefined colors

BULLET POINTS:
- Each \\item is a bullet point
- Keep bullets to 1-2 lines for readability
- Start with strong action verbs

FONTS:
- Classic: Uses default LaTeX fonts
- Modern: May require XeLaTeX for custom fonts

PAGE LENGTH:
- Adjust margins in \\geometry{} command
- Reduce font size: Change 11pt to 10pt in \\documentclass
- Condense sections by reducing \\vspace values
"""

    async def generate_cover_letter(
        self,
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any]
    ) -> str:
        """Generate professional cover letter template"""
        
        prompt = f"""
        Generate a professional cover letter template for this scholarship application.
        
        SCHOLARSHIP DETAILS:
        Name: {scholarship_profile.get('name', 'This Scholarship')}
        Organization: {scholarship_profile.get('organization', '[Organization Name]')}
        Values: {scholarship_profile['priorities']}
        Mission: {scholarship_profile.get('mission', 'Supporting students in their educational journey')}
        
        STUDENT HIGHLIGHTS:
        {json.dumps(content_selection.get('primary_story', {}), indent=2)}
        
        LENGTH: ~300-350 words (3-4 paragraphs)
        TONE: Professional but personable, matching {scholarship_profile.get('tone_profile', 'formal')}
        
        Use [BRACKETS] for parts student should customize.
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
        """Generate responses to short answer questions"""
        
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
        """Generate one short answer response"""
        
        prompt = f"""
        Answer this scholarship short answer question.
        
        QUESTION: {question}
        WORD LIMIT: {word_limit} words (strict)
        
        AVAILABLE STUDENT CONTENT:
        {json.dumps(content_selection, indent=2)}
        
        Return ONLY the answer text.
        """
        
        answer = await self.llm.call(
            system_prompt="You are an expert at crafting concise, impactful scholarship responses.",
            user_message=prompt
        )
        
        actual_word_count = len(answer.split())
        
        return {
            "question": question,
            "answer": answer,
            "word_count": actual_word_count,
            "word_limit": word_limit,
            "within_limit": abs(actual_word_count - word_limit) <= 5
        }
    
    async def generate_additional_materials(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any],
        student_kb: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate any additional requested materials"""
        
        materials = {}
        
        if scholarship_profile.get('requires_personal_statement'):
            materials['personal_statement'] = await self._generate_personal_statement(
                scholarship_profile, content_selection, student_kb
            )
        
        materials['recommendation_talking_points'] = await self._generate_rec_letter_guidance(
            scholarship_profile, content_selection
        )
        
        if scholarship_profile.get('has_interview_stage'):
            materials['interview_prep'] = await self._generate_interview_prep(
                scholarship_profile, content_selection
            )
        
        return materials
    
    async def _generate_personal_statement(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any],
        student_kb: Dict[str, Any]
    ) -> str:
        """Generate broader personal statement"""
        
        prompt = f"""
        Write a personal statement (500-700 words) for this scholarship.
        
        SCHOLARSHIP: {json.dumps(scholarship_profile, indent=2)}
        STUDENT BACKGROUND: {json.dumps(student_kb.get('structured_data', {}), indent=2)}
        KEY STORIES: {json.dumps(content_selection, indent=2)}
        """
        
        return await self.llm.call(
            system_prompt="You help students articulate their personal journey.",
            user_message=prompt
        )
    
    async def _generate_rec_letter_guidance(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate talking points for recommendation letters"""
        
        prompt = f"""
        Create recommendation letter guidance for this scholarship.
        
        SCHOLARSHIP VALUES: {scholarship_profile['priorities']}
        STUDENT'S KEY STORIES: {json.dumps(content_selection, indent=2)}
        
        Return JSON:
        {{
            "key_qualities": [],
            "examples_to_mention": [],
            "talking_points": [],
            "avoid_emphasizing": []
        }}
        """
        
        guidance_json = await self.llm.call(
            system_prompt="You coach recommendation letter strategy.",
            user_message=prompt
        )
        
        return json.loads(guidance_json)
    
    async def _generate_interview_prep(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate interview preparation materials"""
        
        prompt = f"""
        Prepare interview guidance for this scholarship.
        
        SCHOLARSHIP: {json.dumps(scholarship_profile, indent=2)}
        STUDENT'S STORIES: {json.dumps(content_selection, indent=2)}
        
        Return JSON with likely_questions, key_messages, and questions_to_ask.
        """
        
        prep_json = await self.llm.call(
            system_prompt="You are an interview coach for scholarship applications.",
            user_message=prompt
        )
        
        return json.loads(prep_json)


__all__ = ['SupplementaryGenerator']