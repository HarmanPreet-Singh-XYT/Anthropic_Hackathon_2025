"""
backend/drafting_engine/drafting_engine.py
Core Drafting Engine - Orchestrates all drafting components to generate tailored essays
"""

from typing import Dict, List, Optional, Any
import traceback
from .content_selector import ContentSelector
from .narrative_architect import NarrativeArchitect
from .style_matcher import StyleMatcher
from .authenticity_filter import AuthenticityFilter
from .refinement_loop import RefinementLoop
from .multi_draft_generator import MultiDraftGenerator


class DraftingEngine:
    """
    Master orchestrator for essay generation pipeline
    """
    
    def __init__(self):
        """Initialize all pipeline components"""
        self.content_selector = ContentSelector()
        self.narrative_architect = NarrativeArchitect()
        self.multi_draft_generator = MultiDraftGenerator()
        self.style_matcher = StyleMatcher()
        self.authenticity_filter = AuthenticityFilter()
        self.refinement_loop = RefinementLoop()
    
    async def generate_application_materials(
        self,
        scholarship_profile: Dict[str, Any],
        student_kb: Any,
        strategy: Optional[str] = "weighted",
        essay_prompt: Optional[str] = None,
        word_limit: int = 650,
        include_latex_resume: bool = True,
        latex_template_style: str = "modern"
    ) -> Dict[str, Any]:
        """
        Main pipeline: Generate complete application package
        
        Pipeline stages:
        1. Content Selection - Choose which stories to emphasize
        2. Narrative Architecture - Structure essay for maximum impact
        3. Multi-Draft Generation - Create 3 versions with different emphasis
        4. Style Matching - Align with scholarship's linguistic style
        5. Authenticity Filtering - Ensure human-sounding output
        6. Refinement Loop - Iteratively improve best draft
        7. Supplementary Materials - Generate resume, LaTeX resume, cover letter, short answers
        
        Args:
            scholarship_profile: Scholarship details and values
            student_kb: Student knowledge base (vector DB)
            strategy: Content selection strategy ("weighted", "diverse", "focused")
            essay_prompt: Optional specific essay prompt
            word_limit: Target word count
            include_latex_resume: Whether to generate LaTeX resume (default True)
            latex_template_style: "modern", "classic", or "minimal"
        
        Returns:
            Complete application package with essay and supplementary materials
        """
        
        print("\n" + "="*80)
        print("🎯 DRAFTING ENGINE PIPELINE")
        print("="*80)
        print(f"Scholarship: {scholarship_profile.get('name', 'Unknown')}")
        print(f"Strategy: {strategy}")
        print(f"Word Limit: {word_limit}")
        print(f"LaTeX Resume: {'Yes' if include_latex_resume else 'No'}")
        print("="*80 + "\n")
        
        pipeline_errors = []
        warnings = []
        
        # Stage 1: Content Selection
        try:
            print("  → Stage 1/7: Selecting optimal content...")
            content_selection = await self.content_selector.select_content(
                scholarship_profile=scholarship_profile,
                student_kb=student_kb,
                strategy=strategy
            )
            print("    ✅ Content selection complete")
        except Exception as e:
            error_msg = f"Content selection failed: {str(e)}"
            print(f"    ❌ {error_msg}")
            pipeline_errors.append({"stage": 1, "error": error_msg})
            # Return early with error
            return self._create_error_response(pipeline_errors, scholarship_profile)
        
        # Stage 2: Narrative Architecture
        try:
            print("  → Stage 2/7: Architecting narrative structure...")
            outline = await self.narrative_architect.create_outline(
                content_selection=content_selection,
                scholarship_profile=scholarship_profile,
                word_limit=word_limit
            )
            print("    ✅ Narrative architecture complete")
        except Exception as e:
            error_msg = f"Narrative architecture failed: {str(e)}"
            print(f"    ❌ {error_msg}")
            pipeline_errors.append({"stage": 2, "error": error_msg})
            return self._create_error_response(pipeline_errors, scholarship_profile)
        
        # Stage 3: Multi-Draft Generation
        try:
            print("  → Stage 3/7: Generating draft variations...")
            draft_versions = await self.multi_draft_generator.generate_drafts(
                outline=outline,
                content_selection=content_selection,
                scholarship_profile=scholarship_profile,
                num_drafts=3
            )
            print("    ✅ Draft generation complete")
        except Exception as e:
            error_msg = f"Draft generation failed: {str(e)}"
            print(f"    ❌ {error_msg}")
            pipeline_errors.append({"stage": 3, "error": error_msg})
            return self._create_error_response(pipeline_errors, scholarship_profile)
        
        # Stage 4: Style Matching
        try:
            print("  → Stage 4/7: Matching scholarship style...")
            style_profile = await self.style_matcher.analyze_scholarship_style(
                scholarship_profile=scholarship_profile
            )
            
            styled_drafts = []
            for i, draft_info in enumerate(draft_versions, 1):
                try:
                    styled_draft = await self.style_matcher.adjust_draft_style(
                        draft=draft_info['draft'],
                        style_profile=style_profile,
                        scholarship_name=scholarship_profile.get('name', 'this scholarship')
                    )
                    styled_drafts.append({**draft_info, "styled_draft": styled_draft})
                except Exception as e:
                    warning = f"Style matching failed for draft {i}, using original"
                    print(f"    ⚠️  {warning}")
                    warnings.append(warning)
                    styled_drafts.append({**draft_info, "styled_draft": draft_info['draft']})
            
            print("    ✅ Style matching complete")
        except Exception as e:
            error_msg = f"Style matching failed: {str(e)}"
            print(f"    ⚠️  {error_msg} - Using original drafts")
            warnings.append(error_msg)
            styled_drafts = [{**d, "styled_draft": d['draft']} for d in draft_versions]
            style_profile = {"tone": "professional", "note": "Default style used"}
        
        # Stage 5: Authenticity Filtering
        try:
            print("  → Stage 5/7: Ensuring authenticity...")
            authenticity_checked = []
            for draft_info in styled_drafts:
                try:
                    authenticity_check = await self.authenticity_filter.check_authenticity(
                        draft=draft_info['styled_draft']
                    )
                    
                    if authenticity_check['score'] < 7.0:
                        print(f"    ⚠️  Draft {draft_info['version']} needs humanization (score: {authenticity_check['score']:.1f}/10)")
                        try:
                            humanized = await self.authenticity_filter.humanize_draft(
                                draft=draft_info['styled_draft'],
                                issues=authenticity_check
                            )
                            final_draft = humanized
                            recheck = await self.authenticity_filter.check_authenticity(draft=humanized)
                            final_score = recheck['score']
                            print(f"       After humanization: {final_score:.1f}/10")
                        except Exception as e:
                            print(f"       Humanization failed, using original")
                            final_draft = draft_info['styled_draft']
                            final_score = authenticity_check['score']
                    else:
                        print(f"    ✓ Draft {draft_info['version']} authentic (score: {authenticity_check['score']:.1f}/10)")
                        final_draft = draft_info['styled_draft']
                        final_score = authenticity_check['score']
                    
                    authenticity_checked.append({
                        **draft_info,
                        "final_draft": final_draft,
                        "authenticity_score": final_score,
                        "authenticity_check": authenticity_check
                    })
                except Exception as e:
                    print(f"    ⚠️  Authenticity check failed for draft {draft_info['version']}")
                    authenticity_checked.append({
                        **draft_info,
                        "final_draft": draft_info['styled_draft'],
                        "authenticity_score": 7.0,
                        "authenticity_check": {"score": 7.0, "note": "Default score"}
                    })
            
            print("    ✅ Authenticity filtering complete")
        except Exception as e:
            error_msg = f"Authenticity filtering failed: {str(e)}"
            print(f"    ⚠️  {error_msg}")
            warnings.append(error_msg)
            authenticity_checked = styled_drafts
        
        # Stage 6: Refinement Loop
        try:
            print("  → Stage 6/7: Refining best draft...")
            if authenticity_checked:
                best_draft = max(authenticity_checked, key=lambda x: x.get('authenticity_score', 0))
                print(f"    🏆 Selected draft {best_draft['version']} for refinement (authenticity: {best_draft.get('authenticity_score', 0):.1f}/10)")
                
                refined_result = await self.refinement_loop.refine_draft(
                    draft=best_draft.get('final_draft', best_draft.get('styled_draft', best_draft.get('draft', ''))),
                    scholarship_profile=scholarship_profile,
                    max_iterations=3,
                    target_score=8.5
                )
                print("    ✅ Refinement complete")
            else:
                raise ValueError("No drafts available for refinement")
        except Exception as e:
            error_msg = f"Refinement failed: {str(e)}"
            print(f"    ⚠️  {error_msg} - Using best unrefined draft")
            warnings.append(error_msg)
            best_draft = authenticity_checked[0] if authenticity_checked else styled_drafts[0]
            refined_result = {
                'final_draft': best_draft.get('final_draft', best_draft.get('styled_draft', best_draft.get('draft', ''))),
                'iterations': [],
                'improvement_trajectory': {'final_score': 7.0},
                'total_iterations': 0
            }
        
        # Stage 7: Supplementary Materials
        try:
            print("  → Stage 7/7: Generating supplementary materials...")
            supplementary = await self._generate_supplementary_materials(
                content_selection=content_selection,
                scholarship_profile=scholarship_profile,
                strategy=strategy,
                student_kb=student_kb,
                include_latex_resume=include_latex_resume,
                latex_template_style=latex_template_style
            )
            print("    ✅ Supplementary materials complete")
        except Exception as e:
            error_msg = f"Supplementary materials generation failed: {str(e)}"
            print(f"    ⚠️  {error_msg}")
            warnings.append(error_msg)
            supplementary = {"note": "Supplementary materials unavailable", "error": str(e)}
        
        # Final output
        print("\n" + "="*80)
        print("✅ DRAFTING ENGINE PIPELINE COMPLETE")
        print("="*80)
        
        final_word_count = len(refined_result['final_draft'].split())
        word_count_status = "✓" if abs(final_word_count - word_limit) <= 50 else "⚠️"
        print(f"   {word_count_status} Final word count: {final_word_count}/{word_limit}")
        
        if include_latex_resume and 'latex_resume' in supplementary:
            print(f"   📄 LaTeX resume: Generated ({latex_template_style} template)")
        
        if warnings:
            print(f"   ⚠️  {len(warnings)} warnings during generation")
        
        print("="*80 + "\n")
        
        return {
            "success": True,
            "primary_essay": refined_result['final_draft'],
            "alternative_versions": authenticity_checked,
            "refinement_history": refined_result.get('iterations', []),
            "improvement_metrics": refined_result.get('improvement_trajectory', {}),
            "supplementary_materials": supplementary,
            "generation_metadata": {
                "narrative_style": outline.get('narrative_style'),
                "content_strategy": strategy,
                "style_profile": style_profile,
                "outline": outline,
                "word_count": final_word_count,
                "target_word_count": word_limit,
                "word_count_variance": final_word_count - word_limit,
                "best_draft_version": best_draft.get('version', 1),
                "best_draft_emphasis": best_draft.get('emphasis', 'balanced'),
                "authenticity_score": best_draft.get('authenticity_score', 7.0),
                "final_critique_score": refined_result.get('improvement_trajectory', {}).get('final_score'),
                "total_refinement_iterations": refined_result.get('total_iterations', 0),
                "latex_resume_included": include_latex_resume,
                "latex_template_style": latex_template_style if include_latex_resume else None,
                "warnings": warnings,
                "pipeline_status": "completed_with_warnings" if warnings else "completed_successfully"
            }
        }
    
    def _create_error_response(
        self,
        errors: List[Dict[str, Any]],
        scholarship_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create error response when pipeline fails early"""
        return {
            "success": False,
            "error": "Pipeline failed",
            "errors": errors,
            "primary_essay": "[Essay generation failed. Please try again or contact support.]",
            "alternative_versions": [],
            "refinement_history": [],
            "improvement_metrics": {},
            "supplementary_materials": {},
            "generation_metadata": {
                "scholarship_name": scholarship_profile.get('name', 'Unknown'),
                "pipeline_status": "failed",
                "errors": errors
            }
        }
    
    async def _generate_supplementary_materials(
        self,
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any],
        strategy: str,
        student_kb: Any = None,
        include_latex_resume: bool = True,
        latex_template_style: str = "modern"
    ) -> Dict[str, Any]:
        """
        Generate resume bullets, LaTeX resume, cover letters, and short answers
        
        Args:
            content_selection: Selected content from ContentSelector
            scholarship_profile: Scholarship details
            strategy: Content selection strategy used
            student_kb: Student knowledge base for additional context
            include_latex_resume: Whether to generate LaTeX resume
            latex_template_style: Style for LaTeX resume
        
        Returns:
            Dictionary of supplementary materials
        """
        
        from .supplementary_generator import SupplementaryGenerator
        
        generator = SupplementaryGenerator()
        materials = {}
        
        # Resume bullets
        try:
            materials["resume_bullets"] = await generator.generate_resume_bullets(
                content_selection=content_selection,
                scholarship_profile=scholarship_profile
            )
        except Exception as e:
            print(f"       ⚠️  Resume bullets failed: {e}")
            materials["resume_bullets"] = []
        
        # Cover letter
        try:
            materials["cover_letter_template"] = await generator.generate_cover_letter(
                content_selection=content_selection,
                scholarship_profile=scholarship_profile
            )
        except Exception as e:
            print(f"       ⚠️  Cover letter failed: {e}")
            materials["cover_letter_template"] = "[Cover letter template unavailable]"
        
        # LaTeX resume
        if include_latex_resume:
            try:
                print("    📝 Generating LaTeX resume...")
                student_kb_dict = None
                if student_kb and hasattr(student_kb, 'get_structured_data'):
                    student_kb_dict = {"structured_data": student_kb.get_structured_data()}
                elif isinstance(student_kb, dict):
                    student_kb_dict = student_kb
                
                materials['latex_resume'] = await generator.generate_latex_resume(
                    content_selection=content_selection,
                    scholarship_profile=scholarship_profile,
                    student_kb=student_kb_dict,
                    template_style=latex_template_style
                )
            except Exception as e:
                print(f"       ⚠️  LaTeX resume failed: {e}")
                materials['latex_resume'] = {"error": str(e), "latex_code": "% LaTeX generation failed"}
        
        # Short answers
        short_answer_prompts = scholarship_profile.get('short_answer_prompts')
        if short_answer_prompts:
            try:
                materials['short_answers'] = await generator.generate_short_answers(
                    prompts=short_answer_prompts,
                    content_selection=content_selection,
                    scholarship_profile=scholarship_profile
                )
            except Exception as e:
                print(f"       ⚠️  Short answers failed: {e}")
                materials['short_answers'] = {"error": str(e)}
        
        return materials
    
    async def quick_draft(
        self,
        scholarship_profile: Dict[str, Any],
        student_kb: Any,
        word_limit: int = 650,
        skip_refinement: bool = False
    ) -> str:
        """Generate a single draft quickly without full pipeline"""
        
        print("\n⚡ QUICK DRAFT MODE")
        print("="*80)
        
        try:
            content_selection = await self.content_selector.select_content(
                scholarship_profile=scholarship_profile,
                student_kb=student_kb,
                strategy="weighted"
            )
            
            outline = await self.narrative_architect.create_outline(
                content_selection=content_selection,
                scholarship_profile=scholarship_profile,
                word_limit=word_limit
            )
            
            draft_versions = await self.multi_draft_generator.generate_drafts(
                outline=outline,
                content_selection=content_selection,
                scholarship_profile=scholarship_profile,
                num_drafts=1
            )
            
            draft = draft_versions[0]['draft']
            
            if not skip_refinement:
                refined_result = await self.refinement_loop.refine_draft(
                    draft=draft,
                    scholarship_profile=scholarship_profile,
                    max_iterations=1,
                    target_score=7.5
                )
                draft = refined_result['final_draft']
            
            word_count = len(draft.split())
            print(f"✅ Quick draft complete: {word_count}/{word_limit} words")
            print("="*80 + "\n")
            return draft
            
        except Exception as e:
            print(f"❌ Quick draft failed: {str(e)}")
            print("="*80 + "\n")
            return f"[Quick draft generation failed: {str(e)}]"
    
    async def generate_latex_resume_only(
        self,
        scholarship_profile: Dict[str, Any],
        student_kb: Any,
        template_style: str = "modern"
    ) -> Dict[str, Any]:
        """
        Generate only the LaTeX resume without full pipeline
        
        Args:
            scholarship_profile: Scholarship details
            student_kb: Student knowledge base
            template_style: "modern", "classic", or "minimal"
        
        Returns:
            LaTeX resume package with code and instructions
        """
        
        print("\n📄 LATEX RESUME GENERATION")
        print("="*80)
        
        try:
            content_selection = await self.content_selector.select_content(
                scholarship_profile=scholarship_profile,
                student_kb=student_kb,
                strategy="weighted"
            )
            
            from .supplementary_generator import SupplementaryGenerator
            generator = SupplementaryGenerator()
            
            student_kb_dict = None
            if student_kb and hasattr(student_kb, 'get_structured_data'):
                student_kb_dict = {"structured_data": student_kb.get_structured_data()}
            elif isinstance(student_kb, dict):
                student_kb_dict = student_kb
            
            latex_resume = await generator.generate_latex_resume(
                content_selection=content_selection,
                scholarship_profile=scholarship_profile,
                student_kb=student_kb_dict,
                template_style=template_style
            )
            
            print(f"✅ LaTeX resume generated ({template_style} template)")
            print("="*80 + "\n")
            return latex_resume
            
        except Exception as e:
            print(f"❌ LaTeX resume generation failed: {str(e)}")
            print("="*80 + "\n")
            return {
                "error": str(e),
                "latex_code": "% LaTeX generation failed",
                "template_style": template_style
            }
    
    async def compare_strategies(
        self,
        scholarship_profile: Dict[str, Any],
        student_kb: Any,
        word_limit: int = 650
    ) -> Dict[str, Any]:
        """Generate drafts using different strategies and compare"""
        
        print("\n🔬 STRATEGY COMPARISON MODE")
        print("="*80)
        
        strategies = ["weighted", "diverse", "focused"]
        results = {}
        
        for strategy in strategies:
            print(f"\n  Testing strategy: {strategy}")
            
            try:
                content_selection = await self.content_selector.select_content(
                    scholarship_profile=scholarship_profile,
                    student_kb=student_kb,
                    strategy=strategy
                )
                
                outline = await self.narrative_architect.create_outline(
                    content_selection=content_selection,
                    scholarship_profile=scholarship_profile,
                    word_limit=word_limit
                )
                
                drafts = await self.multi_draft_generator.generate_drafts(
                    outline=outline,
                    content_selection=content_selection,
                    scholarship_profile=scholarship_profile,
                    num_drafts=1
                )
                
                auth_check = await self.authenticity_filter.check_authenticity(
                                        draft=drafts[0]['draft']
                )
                
                results[strategy] = {
                    "draft": drafts[0]['draft'],
                    "authenticity_score": auth_check['score'],
                    "word_count": len(drafts[0]['draft'].split()),
                    "narrative_style": outline.get('narrative_style'),
                    "primary_story": content_selection.get('primary_story', {}).get('priority', 'N/A'),
                    "emphasis": drafts[0].get('emphasis', 'balanced')
                }
                
                print(f"     ✓ {strategy}: {auth_check['score']:.1f}/10 authenticity, {len(drafts[0]['draft'].split())} words")
                
            except Exception as e:
                print(f"     ✗ {strategy} failed: {str(e)}")
                results[strategy] = {
                    "error": str(e),
                    "draft": None,
                    "authenticity_score": 0,
                    "word_count": 0
                }
        
        print("\n✅ Strategy comparison complete")
        print("="*80 + "\n")
        return results