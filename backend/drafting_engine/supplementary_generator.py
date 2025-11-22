"""
backend/drafting_engine/supplementary_generator.py
Generates resume bullets, cover letters, LaTeX resumes, and short answer responses
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import re
from utils.llm_client import create_llm_client
from utils.prompt_loader import load_prompt


class SupplementaryGenerator:
    """
    Generates supplementary application materials beyond the main essay
    """
    
    def __init__(self, temperature: float = 0.6):
        self.llm = create_llm_client(temperature=temperature)
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean LLM response to extract pure JSON
        Handles both objects {} and arrays []
        """
        if not response:
            return "{}"
        
        # Remove markdown code blocks
        response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE | re.IGNORECASE)
        response = re.sub(r'^```\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'\s*```$', '', response, flags=re.MULTILINE)
        
        # Remove any leading/trailing text explanations
        response = response.strip()
        
        # Try to find JSON object or array
        # Look for arrays first
        array_match = re.search(r'$$.*$$', response, re.DOTALL)
        if array_match:
            potential_json = array_match.group(0)
            # Verify it's valid by checking bracket balance
            if potential_json.count('[') == potential_json.count(']'):
                return potential_json
        
        # Then try objects
        object_match = re.search(r'\{.*\}', response, re.DOTALL)
        if object_match:
            potential_json = object_match.group(0)
            # Verify it's valid by checking brace balance
            if potential_json.count('{') == potential_json.count('}'):
                return potential_json
        
        return response.strip()
    
    async def generate_resume_bullets(
        self,
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate 5-7 optimized resume bullet points tailored to scholarship
        """
        
        print("    📋 Generating optimized resume bullets...")
        
        # Simplify content for prompt
        primary_story = content_selection.get('primary_story', {})
        story_text = ""
        if primary_story:
            story_data = primary_story.get('story', {})
            story_text = story_data.get('text', str(story_data))[:500]
        
        priorities = scholarship_profile.get('priorities', [])[:5]
        priorities_str = ', '.join(priorities) if priorities else 'scholarship values'
        
        system_prompt = """You are an expert resume writer specializing in scholarship applications. Generate optimized resume bullet points that emphasize quantifiable achievements and align with scholarship values. Return ONLY a valid JSON array with no additional text, explanation, or markdown formatting."""
        
        user_message = f"""Generate 5-7 optimized resume bullet points for this scholarship application.

    SCHOLARSHIP VALUES: {priorities_str}

    STUDENT EXPERIENCES:
    {story_text}...

    Requirements:
    - Start each bullet with a strong action verb
    - Include quantifiable metrics (numbers, percentages, scale)
    - Emphasize impact and outcomes
    - Align language with scholarship values
    - Keep bullets to 1-2 lines each

    Return ONLY a JSON array (no markdown, no text before or after):
    [
        {{
            "section": "Experience",
            "original": "Led coding club",
            "improved": "Founded TechBridge coding initiative serving 50+ underrepresented students, securing $5,000 in funding and partnerships with 3 tech companies",
            "rationale": "Emphasizes scale, resourcefulness, and equity",
            "impact_metrics": "50+ students, $5,000 secured, 3 partnerships",
            "priority": "high"
        }},
        {{
            "section": "Leadership",
            "improved": "Developed comprehensive web development curriculum resulting in 15 completed student projects and 3 hackathon awards within 8 months",
            "rationale": "Highlights curriculum design and measurable outcomes",
            "impact_metrics": "15 projects, 3 awards, 8-month timeframe",
            "priority": "high"
        }}
    ]"""
        
        try:
            bullets_json = await self.llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            if not bullets_json or not bullets_json.strip():
                print("    [WARNING] Empty resume bullets response")
                return self._get_default_bullets()
            
            # Debug logging
            print(f"    [DEBUG] Resume bullets response length: {len(bullets_json)}")
            print(f"    [DEBUG] First 100 chars: {bullets_json[:100]}")
            print(f"    [DEBUG] Last 100 chars: {bullets_json[-100:]}")
            
            # Clean the response more aggressively
            cleaned_json = self._clean_json_response(bullets_json)
            
            # Additional cleaning for arrays
            cleaned_json = cleaned_json.strip()
            
            # If it starts with [ and ends with ], extract just that
            if '[' in cleaned_json and ']' in cleaned_json:
                start_idx = cleaned_json.find('[')
                end_idx = cleaned_json.rfind(']')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    cleaned_json = cleaned_json[start_idx:end_idx + 1]
            
            print(f"    [DEBUG] Cleaned JSON length: {len(cleaned_json)}")
            print(f"    [DEBUG] Cleaned first 100 chars: {cleaned_json[:100]}")
            
            bullets = json.loads(cleaned_json)
            
            if not isinstance(bullets, list):
                print("    [WARNING] Resume bullets not a list")
                return self._get_default_bullets()
            
            print(f"    ✅ Generated {len(bullets)} resume bullets")
            return bullets
            
        except json.JSONDecodeError as e:
            print(f"    [ERROR] Failed to parse resume bullets: {e}")
            print(f"    [ERROR] Attempted to parse: {cleaned_json[:500] if 'cleaned_json' in locals() else bullets_json[:500]}")
            
            # Try more aggressive cleaning
            try:
                # Remove everything before first [ and after last ]
                if '[' in bullets_json and ']' in bullets_json:
                    start = bullets_json.find('[')
                    end = bullets_json.rfind(']')
                    extracted = bullets_json[start:end + 1]
                    
                    # Remove any escaped newlines or extra whitespace
                    extracted = extracted.replace('\\n', ' ').replace('\n', ' ')
                    extracted = re.sub(r'\s+', ' ', extracted)
                    
                    print(f"    [RETRY] Attempting to parse extracted array...")
                    bullets = json.loads(extracted)
                    
                    if isinstance(bullets, list):
                        print(f"    ✅ Successfully parsed {len(bullets)} bullets on retry")
                        return bullets
            except Exception as retry_error:
                print(f"    [RETRY FAILED] {retry_error}")
            
            return self._get_default_bullets()
        
        except Exception as e:
            print(f"    [ERROR] Unexpected error generating bullets: {e}")
            import traceback
            print(f"    [TRACEBACK] {traceback.format_exc()}")
            return self._get_default_bullets()
    
    def _get_default_bullets(self) -> List[Dict[str, Any]]:
        """Return default bullet points when generation fails"""
        return [
            {
                "section": "Experience",
                "original": "",
                "improved": "Led initiative resulting in measurable impact on community/organization",
                "rationale": "Demonstrates leadership and impact",
                "impact_metrics": "Quantify results where possible",
                "priority": "high"
            },
            {
                "section": "Leadership",
                "original": "",
                "improved": "Organized team effort to achieve specific goal with measurable outcomes",
                "rationale": "Shows teamwork and results",
                "impact_metrics": "Include numbers and percentages",
                "priority": "medium"
            }
        ]
    
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
        
        print(f"    📄 Generating LaTeX resume ({template_style} template)...")
        
        # First, get optimized bullet points
        optimized_bullets = await self.generate_resume_bullets(
            content_selection=content_selection,
            scholarship_profile=scholarship_profile
        )
        
        # Extract student info from KB or content selection
        student_info = self._extract_student_info(content_selection, student_kb)
        
        # Simplify data for prompt
        priorities = scholarship_profile.get('priorities', [])[:5]
        priorities_str = ', '.join(priorities) if priorities else 'scholarship values'
        
        prompt = f"""Generate a complete, compilable LaTeX resume tailored for this scholarship application.

SCHOLARSHIP CONTEXT:
Name: {scholarship_profile.get('name', 'Scholarship')}
Values: {priorities_str}
Tone: {scholarship_profile.get('tone_profile', 'professional')}

TEMPLATE STYLE: {template_style}
- modern: Clean lines, subtle colors, modern fonts (uses fontawesome icons)
- classic: Traditional academic style, serif fonts, no colors
- minimal: Ultra-clean, maximum whitespace, very readable

STUDENT SECTIONS TO INCLUDE:
Education: {len(student_info.get('education', []))} entries
Experience: {len(student_info.get('experiences', []))} entries
Projects: {len(student_info.get('projects', []))} entries
Skills: {len(student_info.get('skills', []))} categories
Leadership: {len(student_info.get('leadership', []))} entries

REQUIREMENTS:
1. Generate COMPLETE, COMPILABLE LaTeX code (no placeholders except personal info)
2. Use standard LaTeX packages (geometry, enumitem, titlesec, hyperref, xcolor)
3. Include sections: Education, Experience, Projects, Skills, Leadership/Activities
4. Order sections strategically based on scholarship priorities
5. Use action verbs and quantifiable metrics
6. Keep to ONE PAGE
7. Use [YOUR NAME], [YOUR EMAIL], etc. for personal info placeholders

Return the complete LaTeX document starting with \\documentclass and ending with \\end{{document}}."""
        
        try:
            latex_code = await self.llm.call(
                system_prompt="""You are an expert LaTeX typesetter specializing in professional resumes. 
                You create clean, ATS-friendly resumes that compile without errors.
                Always generate complete, working LaTeX code.""",
                user_message=prompt
            )
            
            if not latex_code or not latex_code.strip():
                print("    [WARNING] Empty LaTeX response")
                latex_code = self._get_fallback_latex_template(template_style)
            
            # Clean up the LaTeX code
            latex_code = self._clean_latex_output(latex_code)
            
            # Validate it looks like LaTeX
            if not latex_code.startswith('\\documentclass'):
                print("    [WARNING] LaTeX code doesn't start with \\documentclass")
                latex_code = self._get_fallback_latex_template(template_style)
            
            print("    ✅ LaTeX resume generated")
            
        except Exception as e:
            print(f"    [ERROR] LaTeX generation failed: {e}")
            latex_code = self._get_fallback_latex_template(template_style)
        
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
    
    def _get_fallback_latex_template(self, template_style: str) -> str:
        """Return a basic LaTeX template when generation fails"""
        return r"""
\documentclass[11pt,letterpaper]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{hyperref}

\titleformat{\section}{\Large\bfseries}{}{0pt}{}[\titlerule]
\titlespacing{\section}{0pt}{12pt}{6pt}

\begin{document}

\begin{center}
{\Huge \textbf{[YOUR NAME]}} \\
\vspace{2pt}
[YOUR EMAIL] $|$ [YOUR PHONE] $|$ [YOUR LOCATION]
\end{center}

\section{Education}
\textbf{[Your University]} \hfill [Graduation Date] \\
[Degree] in [Major] \hfill GPA: [X.XX/4.0]

\section{Experience}
\textbf{[Position Title]} \hfill [Start Date] -- [End Date] \\
\textit{[Organization Name]} \hfill [Location]
\begin{itemize}[leftmargin=*,noitemsep,topsep=0pt]
    \item [Achievement with quantifiable impact]
    \item [Leadership example with specific results]
    \item [Innovation or problem-solving example]
\end{itemize}

\section{Projects}
\textbf{[Project Name]} \hfill [Date]
\begin{itemize}[leftmargin=*,noitemsep,topsep=0pt]
    \item [Technical achievement or innovation]
    \item [Impact or results]
\end{itemize}

\section{Skills}
\textbf{Technical:} [Skill 1], [Skill 2], [Skill 3] \\
\textbf{Languages:} [Language 1], [Language 2]

\section{Leadership \& Activities}
\textbf{[Leadership Role]} \hfill [Date] \\
\textit{[Organization]} \\
[Brief description of impact or achievement]

\end{document}
"""
    
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
            if structured:
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
                if not isinstance(story, dict):
                    continue
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
        
        priorities = scholarship_profile.get('priorities', [])[:5]
        priorities_str = ', '.join(priorities) if priorities else 'scholarship values'
        
        prompt = f"""Based on this scholarship's priorities, explain the optimal resume section order.

Scholarship Priorities: {priorities_str}

Return JSON with section names as keys and brief rationale (no markdown):
{{
    "Education": "Why this section is placed here...",
    "Experience": "Why this section is placed here..."
}}"""
        
        try:
            rationale_json = await self.llm.call(
                system_prompt="You are a career advisor explaining resume strategy.",
                user_message=prompt
            )
            
            cleaned_json = self._clean_json_response(rationale_json)
            return json.loads(cleaned_json)
            
        except Exception as e:
            print(f"    [WARNING] Section rationale generation failed: {e}")
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
        
        print("    ✉️  Generating cover letter template...")
        
        # Get primary story for cover letter
        primary_story = content_selection.get('primary_story', {})
        story_text = ""
        if primary_story:
            story_data = primary_story.get('story', {})
            story_text = story_data.get('text', str(story_data))[:400]
        
        priorities = scholarship_profile.get('priorities', [])
        priorities_str = ', '.join(priorities[:3]) if priorities else 'your values'
        
        mission = scholarship_profile.get('mission', 'Supporting students in their educational journey')
        if len(mission) > 200:
            mission = mission[:200] + "..."
        
        prompt = f"""Generate a professional cover letter template for this scholarship application.

SCHOLARSHIP DETAILS:
Name: {scholarship_profile.get('name', 'This Scholarship')}
Organization: {scholarship_profile.get('organization', '[Organization Name]')}
Values: {priorities_str}
Mission: {mission}

STUDENT HIGHLIGHTS:
{story_text}...

LENGTH: ~300-350 words (3-4 paragraphs)
TONE: Professional but personable, matching {scholarship_profile.get('tone_profile', 'formal')}

Use [BRACKETS] for parts student should customize.

Return ONLY the cover letter text, no preamble or explanation."""
        
        try:
            cover_letter = await self.llm.call(
                system_prompt="You are an expert in professional correspondence and scholarship applications. Write clear, compelling cover letters.",
                user_message=prompt
            )
            
            if not cover_letter or not cover_letter.strip():
                print("    [WARNING] Empty cover letter response")
                return self._get_fallback_cover_letter(scholarship_profile)
            
            # Clean any metadata
            cover_letter = re.sub(r'^(COVER LETTER|LETTER):\s*', '', cover_letter, flags=re.IGNORECASE)
            
            print("    ✅ Cover letter generated")
            return cover_letter.strip()
            
        except Exception as e:
            print(f"    [ERROR] Cover letter generation failed: {e}")
            return self._get_fallback_cover_letter(scholarship_profile)
    
    def _get_fallback_cover_letter(self, scholarship_profile: Dict[str, Any]) -> str:
        """Return basic cover letter template when generation fails"""
        scholarship_name = scholarship_profile.get('name', 'this scholarship')
        return f"""[Your Name]
[Your Address]
[City, State ZIP]
[Your Email]
[Your Phone]

[Date]

[Scholarship Committee Name]
{scholarship_name}
[Organization Address]
[City, State ZIP]

Dear {scholarship_name} Selection Committee,

I am writing to express my strong interest in the {scholarship_name}. As a [year] student pursuing [degree] at [university], I am deeply aligned with your organization's commitment to [mention scholarship values].

[Describe your most relevant experience or achievement that demonstrates alignment with scholarship values. Include specific details and outcomes.]

[Explain how this scholarship will help you achieve your goals and how you plan to contribute to the scholarship's mission. Connect your future plans to the organization's values.]

Thank you for considering my application. I would be honored to represent {scholarship_name} and contribute to [organization mission/community].

Sincerely,

[Your Name]
"""
    
    async def generate_short_answers(
        self,
        prompts: List[Tuple[str, int]],
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate responses to short answer questions"""
        
        print(f"    💬 Generating {len(prompts)} short answer responses...")
        
        answers = []
        for i, (question, word_limit) in enumerate(prompts, 1):
            print(f"       Question {i}/{len(prompts)}...")
            answer_data = await self._generate_single_short_answer(
                question=question,
                word_limit=word_limit,
                content_selection=content_selection,
                scholarship_profile=scholarship_profile
            )
            answers.append(answer_data)
        
        print("    ✅ Short answers complete")
        return answers
    
    async def _generate_single_short_answer(
        self,
        question: str,
        word_limit: int,
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate one short answer response"""
        
        # Get relevant content
        primary_story = content_selection.get('primary_story', {})
        story_text = ""
        if primary_story:
            story_data = primary_story.get('story', {})
            story_text = story_data.get('text', str(story_data))[:400]
        
        prompt = f"""Answer this scholarship short answer question.

QUESTION: {question}
WORD LIMIT: {word_limit} words (strict)

SCHOLARSHIP VALUES: {', '.join(scholarship_profile.get('priorities', [])[:3])}

AVAILABLE STUDENT CONTENT:
{story_text}...

REQUIREMENTS:
- Stay within word limit (±5 words maximum)
- Be specific and concrete
- Use first-person voice
- Show, don't just tell
- Connect to scholarship values

Return ONLY the answer text, no preamble or labels."""
        
        try:
            answer = await self.llm.call(
                system_prompt="You are an expert at crafting concise, impactful scholarship responses.",
                user_message=prompt
            )
            
            if not answer or not answer.strip():
                print(f"       [WARNING] Empty answer for question")
                answer = f"[Answer to: {question[:50]}...] (Word limit: {word_limit})"
            
            # Clean any metadata
            answer = re.sub(r'^(ANSWER|RESPONSE):\s*', '', answer, flags=re.IGNORECASE)
            answer = answer.strip()
            
            actual_word_count = len(answer.split())
            
            if abs(actual_word_count - word_limit) > 10:
                print(f"       [WARNING] Answer length off target: {actual_word_count}/{word_limit} words")
            
            return {
                "question": question,
                "answer": answer,
                "word_count": actual_word_count,
                "word_limit": word_limit,
                "within_limit": abs(actual_word_count - word_limit) <= 5
            }
            
        except Exception as e:
            print(f"       [ERROR] Short answer generation failed: {e}")
            return {
                "question": question,
                "answer": f"[Answer to be completed - {word_limit} words]",
                "word_count": 0,
                "word_limit": word_limit,
                "within_limit": False,
                "error": str(e)
            }
    
    async def generate_additional_materials(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any],
        student_kb: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate any additional requested materials"""
        
        print("    📚 Generating additional materials...")
        
        materials = {}
        
        if scholarship_profile.get('requires_personal_statement'):
            print("       - Personal statement")
            materials['personal_statement'] = await self._generate_personal_statement(
                scholarship_profile, content_selection, student_kb
            )
        
        print("       - Recommendation letter guidance")
        materials['recommendation_talking_points'] = await self._generate_rec_letter_guidance(
            scholarship_profile, content_selection
        )
        
        if scholarship_profile.get('has_interview_stage'):
            print("       - Interview preparation")
            materials['interview_prep'] = await self._generate_interview_prep(
                scholarship_profile, content_selection
            )
        
        print("    ✅ Additional materials complete")
        return materials
    
    async def _generate_personal_statement(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any],
        student_kb: Dict[str, Any]
    ) -> str:
        """Generate broader personal statement"""
        
        structured_data = student_kb.get('structured_data', {})
        personal_info = structured_data.get('personal_info', {})
        
        # Get primary story
        primary_story = content_selection.get('primary_story', {})
        story_text = ""
        if primary_story:
            story_data = primary_story.get('story', {})
            story_text = story_data.get('text', str(story_data))[:500]
        
        prompt = f"""Write a personal statement (500-700 words) for this scholarship.

SCHOLARSHIP: {scholarship_profile.get('name', 'Scholarship')}
VALUES: {', '.join(scholarship_profile.get('priorities', [])[:5])}
MISSION: {scholarship_profile.get('mission', 'N/A')[:200]}

STUDENT BACKGROUND:
Name: {personal_info.get('name', '[Student Name]')}
Key Story: {story_text}...

REQUIREMENTS:
- 500-700 words
- Tell a compelling narrative
- Show personal growth and impact
- Connect to scholarship values
- End with future vision

Return ONLY the personal statement text."""
        
        try:
            statement = await self.llm.call(
                system_prompt="You help students articulate their personal journey in compelling personal statements.",
                user_message=prompt
            )
            
            return statement.strip() if statement else "[Personal statement to be completed]"
            
        except Exception as e:
            print(f"       [ERROR] Personal statement generation failed: {e}")
            return "[Personal statement to be completed - 500-700 words]"
    
    async def _generate_rec_letter_guidance(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate talking points for recommendation letters"""
        
        priorities = scholarship_profile.get('priorities', [])[:5]
        priorities_str = ', '.join(priorities) if priorities else 'scholarship values'
        
        # Get primary story
        primary_story = content_selection.get('primary_story', {})
        story_text = ""
        if primary_story:
            story_data = primary_story.get('story', {})
            story_text = story_data.get('text', str(story_data))[:400]
        
        prompt = f"""Create recommendation letter guidance for this scholarship.

SCHOLARSHIP VALUES: {priorities_str}
STUDENT'S KEY STORIES: {story_text}...

Return JSON (no markdown):
{{
    "key_qualities": ["quality 1", "quality 2"],
    "examples_to_mention": ["example 1", "example 2"],
    "talking_points": ["point 1", "point 2"],
    "avoid_emphasizing": ["thing to avoid"]
}}"""
        
        try:
            guidance_json = await self.llm.call(
                system_prompt="You coach recommendation letter strategy for scholarship applications.",
                user_message=prompt
            )
            
            cleaned_json = self._clean_json_response(guidance_json)
            guidance = json.loads(cleaned_json)
            
            # Validate structure
            if not isinstance(guidance, dict):
                print("       [WARNING] Invalid rec letter guidance structure")
                return self._get_default_rec_guidance()
            
            return guidance
            
        except Exception as e:
            print(f"       [ERROR] Rec letter guidance failed: {e}")
            return self._get_default_rec_guidance()
    
    def _get_default_rec_guidance(self) -> Dict[str, List[str]]:
        """Return default recommendation letter guidance"""
        return {
            "key_qualities": [
                "Leadership ability",
                "Academic excellence",
                "Community engagement"
            ],
            "examples_to_mention": [
                "Specific projects or initiatives led",
                "Measurable outcomes and impact",
                "Growth and development over time"
            ],
            "talking_points": [
                "How student demonstrates scholarship values",
                "Specific examples of character and achievement",
                "Potential for future impact"
            ],
            "avoid_emphasizing": [
                "Generic praise without examples",
                "Qualities not relevant to scholarship"
            ]
        }
    
    async def _generate_interview_prep(
        self,
        scholarship_profile: Dict[str, Any],
        content_selection: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate interview preparation materials"""
        
        priorities = scholarship_profile.get('priorities', [])[:5]
        priorities_str = ', '.join(priorities) if priorities else 'scholarship values'
        
        # Get primary story
        primary_story = content_selection.get('primary_story', {})
        story_text = ""
        if primary_story:
            story_data = primary_story.get('story', {})
            story_text = story_data.get('text', str(story_data))[:400]
        
        prompt = f"""Prepare interview guidance for this scholarship.

SCHOLARSHIP: {scholarship_profile.get('name', 'Scholarship')}
VALUES: {priorities_str}
STUDENT'S STORIES: {story_text}...

Return JSON (no markdown):
{{
    "likely_questions": [
        "Question about leadership experience",
        "Question about challenges overcome"
    ],
    "key_messages": [
        "Message to emphasize",
        "Story to tell"
    ],
    "questions_to_ask": [
        "Question about scholarship program",
        "Question about past recipients"
    ],
    "preparation_tips": [
        "Practice tip 1",
        "Practice tip 2"
    ]
}}"""
        
        try:
            prep_json = await self.llm.call(
                system_prompt="You are an interview coach for scholarship applications.",
                user_message=prompt
            )
            
            cleaned_json = self._clean_json_response(prep_json)
            prep = json.loads(cleaned_json)
            
            # Validate structure
            if not isinstance(prep, dict):
                print("       [WARNING] Invalid interview prep structure")
                return self._get_default_interview_prep()
            
            return prep
            
        except Exception as e:
            print(f"       [ERROR] Interview prep generation failed: {e}")
            return self._get_default_interview_prep()
    
    def _get_default_interview_prep(self) -> Dict[str, Any]:
        """Return default interview preparation"""
        return {
            "likely_questions": [
                "Tell us about yourself and why you're applying",
                "Describe a challenge you've overcome",
                "How do you demonstrate our scholarship values?",
                "What are your future goals?",
                "How will this scholarship help you?"
            ],
            "key_messages": [
                "Emphasize alignment with scholarship values",
                "Share specific examples and outcomes",
                "Connect past experiences to future goals",
                "Show genuine passion and commitment"
            ],
            "questions_to_ask": [
                "What qualities do successful recipients share?",
                "Are there opportunities to connect with past recipients?",
                "What is the timeline for the selection process?",
                "How can recipients stay involved with the organization?"
            ],
            "preparation_tips": [
                "Practice STAR method (Situation, Task, Action, Result)",
                "Prepare 2-3 stories that showcase different values",
                "Research the scholarship organization thoroughly",
                "Prepare questions that show genuine interest",
                "Practice with a friend or mentor"
            ]
        }


__all__ = ['SupplementaryGenerator']