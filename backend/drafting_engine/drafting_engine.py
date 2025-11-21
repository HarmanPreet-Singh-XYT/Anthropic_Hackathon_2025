"""
backend/drafting_engine/drafting_engine.py
Core Drafting Engine - Orchestrates all drafting components to generate tailored essays
"""

from typing import Dict, List, Optional, Any
from .content_selector import ContentSelector
from .narrative_architect import NarrativeArchitect
from .style_matcher import StyleMatcher
from .authenticity_filter import AuthenticityFilter
from .refinement_loop import RefinementLoop
from .multi_draft_generator import MultiDraftGenerator

# Example usage
# # Initialize engine
# engine = DraftingEngine()

# # Full pipeline
# result = await engine.generate_application_materials(
#     scholarship_profile=scholarship_profile,
#     student_kb=vector_db,
#     strategy="weighted",
#     word_limit=650
# )

# # Access results
# print(result['primary_essay'])
# print(f"Final score: {result['generation_metadata']['final_critique_score']}/10")
# print(f"Resume bullets: {len(result['supplementary_materials']['resume_bullets'])}")

# # Quick draft for testing
# quick_essay = await engine.quick_draft(
#     scholarship_profile=scholarship_profile,
#     student_kb=vector_db,
#     word_limit=500,
#     skip_refinement=False
# )

# # Compare strategies
# comparison = await engine.compare_strategies(
#     scholarship_profile=scholarship_profile,
#     student_kb=vector_db,
#     word_limit=650
# )
# for strategy, data in comparison.items():
#     print(f"{strategy}: {data['authenticity_score']}/10, {data['word_count']} words")


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
        student_kb: Any,  # Vector DB or knowledge base
        strategy: Optional[str] = "weighted",
        essay_prompt: Optional[str] = None,
        word_limit: int = 650
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
        7. Supplementary Materials - Generate resume suggestions, short answers
        
        Args:
            scholarship_profile: Scholarship details and values
            student_kb: Student knowledge base (vector DB)
            strategy: Content selection strategy ("weighted", "diverse", "focused")
            essay_prompt: Optional specific essay prompt
            word_limit: Target word count
        
        Returns:
            Complete application package with essay and supplementary materials
        """
        
        print("🎯 Starting Drafting Engine Pipeline...")
        
        # Stage 1: Content Selection
        print("  → Stage 1/7: Selecting optimal content...")
        content_selection = await self.content_selector.select_content(
            scholarship_profile=scholarship_profile,
            student_kb=student_kb,
            strategy=strategy
        )
        
        # Stage 2: Narrative Architecture
        print("  → Stage 2/7: Architecting narrative structure...")
        outline = await self.narrative_architect.create_outline(
            content_selection=content_selection,
            scholarship_profile=scholarship_profile,
            word_limit=word_limit
        )
        
        # Stage 3: Multi-Draft Generation
        print("  → Stage 3/7: Generating draft variations...")
        draft_versions = await self.multi_draft_generator.generate_drafts(
            outline=outline,
            content_selection=content_selection,
            scholarship_profile=scholarship_profile,
            num_drafts=3
        )
        
        # Stage 4: Style Matching
        print("  → Stage 4/7: Matching scholarship style...")
        style_profile = await self.style_matcher.analyze_scholarship_style(
            scholarship_profile=scholarship_profile
        )
        
        styled_drafts = []
        for draft_info in draft_versions:
            styled_draft = await self.style_matcher.adjust_draft_style(
                draft=draft_info['draft'],
                style_profile=style_profile,
                scholarship_name=scholarship_profile.get('name', 'this scholarship')
            )
            styled_drafts.append({
                **draft_info,
                "styled_draft": styled_draft
            })
        
        # Stage 5: Authenticity Filtering
        print("  → Stage 5/7: Ensuring authenticity...")
        authenticity_checked = []
        for draft_info in styled_drafts:
            authenticity_check = await self.authenticity_filter.check_authenticity(
                draft=draft_info['styled_draft']
            )
            
            # Humanize if needed
            if authenticity_check['score'] < 7.0:
                print(f"    ⚠️  Draft {draft_info['version']} needs humanization (score: {authenticity_check['score']}/10)")
                humanized = await self.authenticity_filter.humanize_draft(
                    draft=draft_info['styled_draft'],
                    issues=authenticity_check['issues']
                )
                final_draft = humanized
                
                # Re-check authenticity after humanization
                recheck = await self.authenticity_filter.check_authenticity(draft=humanized)
                final_score = recheck['score']
            else:
                final_draft = draft_info['styled_draft']
                final_score = authenticity_check['score']
            
            authenticity_checked.append({
                **draft_info,
                "final_draft": final_draft,
                "authenticity_score": final_score,
                "authenticity_check": authenticity_check
            })
        
        # Stage 6: Refinement Loop
        print("  → Stage 6/7: Refining best draft...")
        best_draft = max(authenticity_checked, key=lambda x: x['authenticity_score'])
        
        print(f"    🏆 Selected draft {best_draft['version']} for refinement (authenticity: {best_draft['authenticity_score']}/10)")
        
        refined_result = await self.refinement_loop.refine_draft(
            draft=best_draft['final_draft'],
            scholarship_profile=scholarship_profile,
            max_iterations=3,
            target_score=8.5
        )
        
        # Stage 7: Supplementary Materials
        print("  → Stage 7/7: Generating supplementary materials...")
        supplementary = await self._generate_supplementary_materials(
            content_selection=content_selection,
            scholarship_profile=scholarship_profile,
            strategy=strategy
        )
        
        print("✅ Drafting Engine Pipeline Complete!")
        
        # Calculate final word count
        final_word_count = len(refined_result['final_draft'].split())
        word_count_status = "✓" if abs(final_word_count - word_limit) <= 50 else "⚠️"
        print(f"   {word_count_status} Final word count: {final_word_count}/{word_limit}")
        
        return {
            "primary_essay": refined_result['final_draft'],
            "alternative_versions": authenticity_checked,
            "refinement_history": refined_result['iterations'],
            "improvement_metrics": refined_result['improvement_trajectory'],
            "supplementary_materials": supplementary,
            "generation_metadata": {
                "narrative_style": outline.get('narrative_style'),
                "content_strategy": strategy,
                "style_profile": style_profile,
                "outline": outline,
                "word_count": final_word_count,
                "target_word_count": word_limit,
                "word_count_variance": final_word_count - word_limit,
                "best_draft_version": best_draft['version'],
                "best_draft_emphasis": best_draft['emphasis'],
                "authenticity_score": best_draft['authenticity_score'],
                "final_critique_score": refined_result.get('improvement_trajectory', {}).get('final_score'),
                "total_refinement_iterations": refined_result.get('total_iterations', 0)
            }
        }
    
    async def _generate_supplementary_materials(
        self,
        content_selection: Dict[str, Any],
        scholarship_profile: Dict[str, Any],
        strategy: str
    ) -> Dict[str, Any]:
        """
        Generate resume bullets, cover letters, and short answers
        
        Args:
            content_selection: Selected content from ContentSelector
            scholarship_profile: Scholarship details
            strategy: Content selection strategy used
        
        Returns:
            Dictionary of supplementary materials
        """
        
        from .supplementary_generator import SupplementaryGenerator
        
        generator = SupplementaryGenerator()
        
        materials = {
            "resume_bullets": await generator.generate_resume_bullets(
                content_selection=content_selection,
                scholarship_profile=scholarship_profile
            ),
            "cover_letter_template": await generator.generate_cover_letter(
                content_selection=content_selection,
                scholarship_profile=scholarship_profile
            )
        }
        
        # Add short answers if prompts exist
        short_answer_prompts = scholarship_profile.get('short_answer_prompts')
        if short_answer_prompts:
            # Check if SupplementaryGenerator has this method
            if hasattr(generator, 'generate_short_answers'):
                materials['short_answers'] = await generator.generate_short_answers(
                    prompts=short_answer_prompts,
                    content_selection=content_selection,
                    scholarship_profile=scholarship_profile
                )
            else:
                materials['short_answers'] = {
                    "note": "Short answer generation not yet implemented"
                }
        
        return materials
    
    async def quick_draft(
        self,
        scholarship_profile: Dict[str, Any],
        student_kb: Any,
        word_limit: int = 650,
        skip_refinement: bool = False
    ) -> str:
        """
        Generate a single draft quickly without full pipeline
        
        Args:
            scholarship_profile: Scholarship details
            student_kb: Student knowledge base
            word_limit: Target word count
            skip_refinement: If True, skip the refinement loop
        
        Returns:
            Single essay draft
        """
        
        print("⚡ Quick Draft Mode...")
        
        # Content selection
        content_selection = await self.content_selector.select_content(
            scholarship_profile=scholarship_profile,
            student_kb=student_kb,
            strategy="weighted"
        )
        
        # Create outline
        outline = await self.narrative_architect.create_outline(
            content_selection=content_selection,
            scholarship_profile=scholarship_profile,
            word_limit=word_limit
        )
        
        # Generate single draft
        draft_versions = await self.multi_draft_generator.generate_drafts(
            outline=outline,
            content_selection=content_selection,
            scholarship_profile=scholarship_profile,
            num_drafts=1
        )
        
        draft = draft_versions[0]['draft']
        
        # Optional refinement
        if not skip_refinement:
            refined_result = await self.refinement_loop.refine_draft(
                draft=draft,
                scholarship_profile=scholarship_profile,
                max_iterations=1,
                target_score=7.5
            )
            draft = refined_result['final_draft']
        
        print(f"✅ Quick draft complete ({len(draft.split())} words)")
        
        return draft
    
    async def compare_strategies(
        self,
        scholarship_profile: Dict[str, Any],
        student_kb: Any,
        word_limit: int = 650
    ) -> Dict[str, Any]:
        """
        Generate drafts using different strategies and compare
        
        Args:
            scholarship_profile: Scholarship details
            student_kb: Student knowledge base
            word_limit: Target word count
        
        Returns:
            Comparison of different strategy results
        """
        
        print("🔬 Strategy Comparison Mode...")
        
        strategies = ["weighted", "diverse", "focused"]
        results = {}
        
        for strategy in strategies:
            print(f"\n  Testing strategy: {strategy}")
            
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
            
            # Quick authenticity check
            auth_check = await self.authenticity_filter.check_authenticity(
                draft=drafts[0]['draft']
            )
            
            results[strategy] = {
                "draft": drafts[0]['draft'],
                "authenticity_score": auth_check['score'],
                "word_count": len(drafts[0]['draft'].split()),
                "narrative_style": outline.get('narrative_style'),
                "primary_story": content_selection.get('primary_story', {}).get('priority')
            }
        
        print("\n✅ Strategy comparison complete!")
        
        return results
    



