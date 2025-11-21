"""
tests/test_drafting_engine.py
Comprehensive pytest test suite for the Drafting Engine components
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# Import all components
from drafting_engine.content_selector import ContentSelector
from drafting_engine.narrative_architect import NarrativeArchitect
from drafting_engine.style_matcher import StyleMatcher
from drafting_engine.authenticity_filter import AuthenticityFilter
from drafting_engine.refinement_loop import RefinementLoop
from drafting_engine.multi_draft_generator import MultiDraftGenerator
from drafting_engine.supplementary_generator import SupplementaryGenerator
from drafting_engine.drafting_engine import DraftingEngine


# ============================================================================
# FIXTURES - Shared test data
# ============================================================================

@pytest.fixture
def scholarship_profile() -> Dict[str, Any]:
    """Sample scholarship profile for testing"""
    return {
        "name": "Tech Leaders Scholarship",
        "organization": "Innovation Foundation",
        "description": "Supporting future technology leaders who demonstrate innovation, leadership, and community impact.",
        "mission": "Empowering the next generation of tech innovators",
        "priorities": ["leadership", "innovation", "community", "academic"],
        "weighted_priorities": {
            "leadership": 0.35,
            "innovation": 0.30,
            "community": 0.25,
            "academic": 0.10
        },
        "tone_profile": "professional",
        "winner_stories": "Past winners have led coding bootcamps, developed apps for social good, and mentored underrepresented students in STEM.",
        "winner_patterns": "Strong technical skills combined with community engagement",
        "short_answer_prompts": [
            "Describe a time you demonstrated leadership (150 words)",
            "What innovation are you most proud of? (100 words)"
        ]
    }


@pytest.fixture
def content_selection() -> Dict[str, Any]:
    """Sample content selection output"""
    return {
        "primary_story": {
            "story": {
                "id": "story_001",
                "text": "Led a coding bootcamp for 50 underserved high school students, teaching Python and web development over 12 weeks. Students built 15 functional apps, with 3 winning local hackathon prizes."
            },
            "priority": "leadership",
            "score": 8.5,
            "analysis": {
                "fit_score": 9,
                "strongest_angles": ["youth mentorship", "technical education", "measurable impact"],
                "key_details_to_emphasize": ["50 students", "12 weeks", "15 apps", "hackathon wins"]
            }
        },
        "supporting_stories": [
            {
                "story": {
                    "id": "story_002",
                    "text": "Developed an AI-powered app that helps elderly users navigate public transportation, now used by 200+ seniors in my city."
                },
                "priority": "innovation",
                "score": 7.8
            },
            {
                "story": {
                    "id": "story_003",
                    "text": "Organized monthly tech workshops at local library, reaching 300+ community members over two years."
                },
                "priority": "community",
                "score": 7.2
            }
        ],
        "avoid_stories": [],
        "all_candidates": [],
        "selection_strategy": "weighted",
        "total_candidates_evaluated": 10
    }


@pytest.fixture
def essay_outline() -> Dict[str, Any]:
    """Sample narrative outline"""
    return {
        "narrative_style": "hero_journey",
        "total_word_limit": 650,
        "scholarship_name": "Tech Leaders Scholarship",
        "sections": {
            "hook": {
                "description": "Opening scene from primary story",
                "purpose": "Grab attention with vivid moment",
                "allocation_percentage": 0.15,
                "target_words": 97,
                "word_range": {"min": 78, "max": 117}
            },
            "challenge": {
                "description": "Problem/obstacle faced",
                "purpose": "Establish stakes and context",
                "allocation_percentage": 0.20,
                "target_words": 130,
                "word_range": {"min": 104, "max": 156}
            },
            "action": {
                "description": "What you did - leadership/innovation",
                "purpose": "Demonstrate agency and skills",
                "allocation_percentage": 0.30,
                "target_words": 195,
                "word_range": {"min": 156, "max": 234}
            },
            "impact": {
                "description": "Concrete results achieved",
                "purpose": "Show measurable change",
                "allocation_percentage": 0.20,
                "target_words": 130,
                "word_range": {"min": 104, "max": 156}
            },
            "reflection": {
                "description": "Growth and future vision",
                "purpose": "Connect to scholarship values",
                "allocation_percentage": 0.15,
                "target_words": 97,
                "word_range": {"min": 78, "max": 117}
            }
        },
        "section_guidance": {
            "hook": "Start with the moment you first met your bootcamp students",
            "challenge": "Describe the educational gap you observed",
            "action": "Detail your curriculum design and teaching approach",
            "impact": "Highlight the 15 apps and hackathon wins",
            "reflection": "Connect to your future goals in tech education"
        }
    }


@pytest.fixture
def sample_draft() -> str:
    """Sample essay draft for testing"""
    return """
    The fluorescent lights flickered above as fifty pairs of eyes stared at me expectantly. These high school students from underserved neighborhoods had never written a line of code, yet here they were, trusting me to change that.

    Growing up, I witnessed how the digital divide limited opportunities in my community. While my peers at well-funded schools learned programming, students in under-resourced areas were left behind. This gap wasn't just about technology—it was about futures being decided by zip codes.

    I designed a 12-week curriculum that started with the basics but quickly moved to real-world applications. Instead of abstract exercises, students built apps addressing problems they saw in their own communities. I recruited five volunteer mentors from local tech companies, creating a support network that extended beyond our Saturday sessions. When students struggled, we adapted. When they excelled, we challenged them further.

    The results exceeded my expectations. Fifty students completed the program, creating 15 functional applications. Three teams won prizes at our city's youth hackathon, competing against students from schools with dedicated computer science programs. More importantly, 80% of participants reported increased interest in STEM careers, and twelve have since enrolled in advanced programming courses.

    This experience crystallized my purpose: democratizing tech education. At university, I plan to expand this model, partnering with the Innovation Foundation to reach students across the region. Technology should be a bridge, not a barrier, and I'm committed to building that bridge one student at a time.
    """


@pytest.fixture
def style_profile() -> Dict[str, Any]:
    """Sample style profile"""
    return {
        "tone": "professional",
        "sentence_structure": "varied",
        "key_phrases": ["innovation", "leadership", "community impact", "technology"],
        "emotional_vs_rational": 45,
        "person_perspective": "first person",
        "opening_style": "story",
        "closing_style": "forward-looking",
        "vocabulary_level": "moderate",
        "storytelling_approach": "narrative"
    }


@pytest.fixture
def mock_student_kb():
    """Mock vector database for student knowledge base"""
    kb = MagicMock()
    kb.query = MagicMock(return_value=[
        {
            "id": "exp_001",
            "text": "Led coding bootcamp for 50 students",
            "tags": ["leadership", "teaching", "technology"]
        },
        {
            "id": "exp_002",
            "text": "Developed AI app for elderly users",
            "tags": ["innovation", "social good", "AI"]
        },
        {
            "id": "exp_003",
            "text": "Organized community tech workshops",
            "tags": ["community", "outreach", "education"]
        }
    ])
    return kb


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing without API calls"""
    with patch('drafting_engine.content_selector.create_llm_client') as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


# ============================================================================
# CONTENT SELECTOR TESTS
# ============================================================================

class TestContentSelector:
    """Tests for ContentSelector component"""
    
    @pytest.fixture
    def selector(self):
        """Create ContentSelector with mocked LLM"""
        with patch('drafting_engine.content_selector.create_llm_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            selector = ContentSelector(temperature=0.3)
            selector.llm = client
            return selector
    
    @pytest.mark.asyncio
    async def test_select_content_returns_required_keys(
        self, selector, scholarship_profile, mock_student_kb
    ):
        """Test that select_content returns all required keys"""
        # Mock LLM response for relevance scoring
        selector.llm.call = AsyncMock(return_value=json.dumps({
            "raw_score": 8.5,
            "evidence_score": 8,
            "impact_score": 9,
            "specificity_score": 8,
            "authenticity_score": 9,
            "alignment_score": 8,
            "reasoning": "Strong leadership demonstration",
            "key_strengths": ["quantifiable impact", "direct evidence"],
            "key_weaknesses": []
        }))
        
        result = await selector.select_content(
            scholarship_profile=scholarship_profile,
            student_kb=mock_student_kb,
            strategy="weighted"
        )
        
        assert "primary_story" in result
        assert "supporting_stories" in result
        assert "avoid_stories" in result
        assert "selection_strategy" in result
        assert result["selection_strategy"] == "weighted"
    
    @pytest.mark.asyncio
    async def test_calculate_relevance_applies_weight(self, selector, scholarship_profile):
        """Test that relevance scoring applies priority weight correctly"""
        selector.llm.call = AsyncMock(return_value=json.dumps({
            "raw_score": 10.0,
            "evidence_score": 10,
            "impact_score": 10,
            "specificity_score": 10,
            "authenticity_score": 10,
            "alignment_score": 10,
            "reasoning": "Perfect score",
            "key_strengths": [],
            "key_weaknesses": []
        }))
        
        story = {"text": "Test story", "id": "test_001"}
        
        # Weight of 0.5 should result in score of 5.0 (10 * 0.5)
        score = await selector.calculate_relevance(
            story=story,
            priority="leadership",
            weight=0.5,
            scholarship_profile=scholarship_profile
        )
        
        assert score == 5.0
    
    @pytest.mark.asyncio
    async def test_diverse_ranking_covers_all_priorities(self, selector):
        """Test that diverse strategy selects from each priority"""
        stories = [
            {"story": {"id": "1"}, "priority": "leadership", "score": 9.0},
            {"story": {"id": "2"}, "priority": "leadership", "score": 8.0},
            {"story": {"id": "3"}, "priority": "innovation", "score": 7.0},
            {"story": {"id": "4"}, "priority": "community", "score": 6.0},
        ]
        priorities = {"leadership": 0.4, "innovation": 0.3, "community": 0.3}
        
        ranked = selector._diverse_ranking(stories, priorities)
        
        # First 3 should cover all priorities
        first_three_priorities = {s["priority"] for s in ranked[:3]}
        assert first_three_priorities == {"leadership", "innovation", "community"}
    
    @pytest.mark.asyncio
    async def test_focused_ranking_boosts_top_priority(self, selector):
        """Test that focused strategy boosts top priority stories"""
        stories = [
            {"story": {"id": "1"}, "priority": "innovation", "score": 8.0},
            {"story": {"id": "2"}, "priority": "leadership", "score": 7.0},
        ]
        priorities = {"leadership": 0.5, "innovation": 0.3}  # leadership is top
        
        ranked = selector._focused_ranking(stories, priorities)
        
        # Leadership story should be first due to 50% boost (7.0 * 1.5 = 10.5 > 8.0)
        assert ranked[0]["priority"] == "leadership"


# ============================================================================
# NARRATIVE ARCHITECT TESTS
# ============================================================================

class TestNarrativeArchitect:
    """Tests for NarrativeArchitect component"""
    
    @pytest.fixture
    def architect(self):
        """Create NarrativeArchitect with mocked LLM"""
        with patch('drafting_engine.narrative_architect.create_llm_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            architect = NarrativeArchitect(temperature=0.4)
            architect.llm = client
            return architect
    
    @pytest.mark.asyncio
    async def test_detect_narrative_style_returns_valid_style(
        self, architect, scholarship_profile
    ):
        """Test that narrative style detection returns valid archetype"""
        architect.llm.call = AsyncMock(return_value="hero_journey")
        
        style = await architect.detect_narrative_style(scholarship_profile)
        
        assert style in ["hero_journey", "achievement_showcase", "community_impact"]
    
    @pytest.mark.asyncio
    async def test_detect_narrative_style_handles_fuzzy_response(
        self, architect, scholarship_profile
    ):
        """Test that style detection handles imprecise LLM responses"""
        architect.llm.call = AsyncMock(return_value="I think hero journey would work best")
        
        style = await architect.detect_narrative_style(scholarship_profile)
        
        assert style == "hero_journey"
    
    def test_get_outline_template_hero_journey(self, architect):
        """Test hero journey outline template structure"""
        template = architect._get_outline_template("hero_journey")
        
        assert "sections" in template
        sections = template["sections"]
        assert "hook" in sections
        assert "challenge" in sections
        assert "action" in sections
        assert "impact" in sections
        assert "reflection" in sections
        
        # Check word allocations sum to ~1.0
        total_allocation = sum(
            s["allocation_percentage"] for s in sections.values()
        )
        assert 0.99 <= total_allocation <= 1.01
    
    def test_get_outline_template_achievement_showcase(self, architect):
        """Test achievement showcase outline template"""
        template = architect._get_outline_template("achievement_showcase")
        
        sections = template["sections"]
        assert "approach" in sections  # Unique to achievement
        assert "results" in sections
        assert "vision" in sections
    
    def test_get_outline_template_community_impact(self, architect):
        """Test community impact outline template"""
        template = architect._get_outline_template("community_impact")
        
        sections = template["sections"]
        assert "empathy" in sections  # Unique to community
        assert "commitment" in sections
    
    def test_allocate_word_counts(self, architect):
        """Test word count allocation calculation"""
        outline = {
            "sections": {
                "hook": {"allocation_percentage": 0.15},
                "body": {"allocation_percentage": 0.70},
                "conclusion": {"allocation_percentage": 0.15}
            }
        }
        word_limit = 500
        
        result = architect._allocate_word_counts(outline, word_limit)
        
        assert result["sections"]["hook"]["target_words"] == 75  # 500 * 0.15
        assert result["sections"]["body"]["target_words"] == 350  # 500 * 0.70
        assert result["sections"]["hook"]["word_range"]["min"] == 60  # 75 * 0.8
        assert result["sections"]["hook"]["word_range"]["max"] == 90  # 75 * 1.2
    
    @pytest.mark.asyncio
    async def test_create_outline_full_pipeline(
        self, architect, content_selection, scholarship_profile
    ):
        """Test full outline creation pipeline"""
        architect.llm.call = AsyncMock(side_effect=[
            "hero_journey",  # detect_narrative_style
            json.dumps({     # _generate_section_guidance
                "hook": "Start with the bootcamp moment",
                "challenge": "Describe the digital divide",
                "action": "Detail your teaching approach",
                "impact": "Highlight student achievements",
                "reflection": "Connect to future goals"
            })
        ])
        
        outline = await architect.create_outline(
            content_selection=content_selection,
            scholarship_profile=scholarship_profile,
            word_limit=650
        )
        
        assert outline["narrative_style"] == "hero_journey"
        assert outline["total_word_limit"] == 650
        assert "sections" in outline
        assert "section_guidance" in outline


# ============================================================================
# STYLE MATCHER TESTS
# ============================================================================

class TestStyleMatcher:
    """Tests for StyleMatcher component"""
    
    @pytest.fixture
    def matcher(self):
        """Create StyleMatcher with mocked LLM"""
        with patch('drafting_engine.style_matcher.create_llm_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            matcher = StyleMatcher(temperature=0.6)
            matcher.llm = client
            return matcher
    
    @pytest.mark.asyncio
    async def test_analyze_scholarship_style_returns_profile(
        self, matcher, scholarship_profile
    ):
        """Test style analysis returns complete profile"""
        matcher.llm.call = AsyncMock(return_value=json.dumps({
            "tone": "professional",
            "sentence_structure": "varied",
            "key_phrases": ["innovation", "leadership"],
            "emotional_vs_rational": 45,
            "person_perspective": "first person",
            "opening_style": "story",
            "closing_style": "forward-looking",
            "vocabulary_level": "moderate",
            "storytelling_approach": "narrative"
        }))
        
        profile = await matcher.analyze_scholarship_style(scholarship_profile)
        
        assert "tone" in profile
        assert "sentence_structure" in profile
        assert "key_phrases" in profile
        assert isinstance(profile["key_phrases"], list)
    
    @pytest.mark.asyncio
    async def test_adjust_draft_style_preserves_content(
        self, matcher, sample_draft, style_profile
    ):
        """Test style adjustment preserves core content"""
        adjusted_draft = "Adjusted version with same content..."
        matcher.llm.call = AsyncMock(return_value=adjusted_draft)
        
        result = await matcher.adjust_draft_style(
            draft=sample_draft,
            style_profile=style_profile,
            scholarship_name="Test Scholarship"
        )
        
        assert result == adjusted_draft
        # Verify LLM was called with preservation instructions
        call_args = matcher.llm.call.call_args
        assert "Preserve" in call_args[1]["user_message"] or "preserve" in call_args[1]["user_message"].lower()


# ============================================================================
# AUTHENTICITY FILTER TESTS
# ============================================================================

class TestAuthenticityFilter:
    """Tests for AuthenticityFilter component"""
    
    @pytest.fixture
    def auth_filter(self):
        """Create AuthenticityFilter with mocked LLMs"""
        with patch('drafting_engine.authenticity_filter.create_llm_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            auth_filter = AuthenticityFilter(temperature=0.4)
            auth_filter.analysis_llm = client
            auth_filter.humanization_llm = client
            return auth_filter
    
    def test_detect_generic_phrases_finds_known_phrases(self, auth_filter):
        """Test generic phrase detection"""
        text = "From a young age, I have always been passionate about coding. Throughout my life, this passion has grown."
        
        result = auth_filter.detect_generic_phrases(text)
        
        assert result["count"] >= 2
        found_phrases = [p["phrase"] for p in result["found"]]
        assert "from a young age" in found_phrases
        assert "throughout my life" in found_phrases
    
    def test_detect_generic_phrases_clean_text(self, auth_filter):
        """Test that clean text has no generic phrases"""
        text = "At 3 AM on a Tuesday, I debugged my first kernel panic. The server logs told a story of cascading failures."
        
        result = auth_filter.detect_generic_phrases(text)
        
        assert result["count"] == 0
        assert result["severity"] == "none"
    
    def test_count_passive_voice(self, auth_filter):
        """Test passive voice detection"""
        text = "The project was completed by the team. The results were analyzed. The report was written."
        
        result = auth_filter.count_passive_voice(text)
        
        assert result["count"] >= 2
        assert result["severity"] in ["low", "medium", "high"]
    
    def test_find_cliches(self, auth_filter):
        """Test cliché detection"""
        text = "I had to think outside the box and push myself to my limits. At the end of the day, I rose to the challenge."
        
        result = auth_filter.find_cliches(text)
        
        assert result["count"] >= 2
        assert "think outside the box" in result["found"]
    
    def test_measure_specificity_high_specificity(self, auth_filter):
        """Test specificity measurement for detailed text"""
        text = "I led a team of 12 engineers at Google to develop TensorFlow 2.0, reducing training time by 40% for 50,000 users."
        
        result = auth_filter.measure_specificity(text)
        
        assert result["numbers_count"] >= 3
        assert result["proper_nouns_count"] >= 1
    
    def test_measure_specificity_low_specificity(self, auth_filter):
        """Test specificity measurement for vague text"""
        text = "I did many things with various people in different areas. It was a really good experience that taught me stuff."
        
        result = auth_filter.measure_specificity(text)
        
        assert result["vague_words_count"] >= 3
        assert result["severity"] in ["medium", "high"]
    
    def test_detect_repetition(self, auth_filter):
        """Test word repetition detection"""
        text = "Leadership leadership leadership. I showed leadership through leadership activities. My leadership skills are leadership-focused."
        
        result = auth_filter.detect_repetition(text)
        
        assert len(result["overused_words"]) > 0
        assert ("leadership", 6) in result["overused_words"] or any(
            w[0] == "leadership" and w[1] >= 5 for w in result["overused_words"]
        )
    
    def test_check_vocabulary_naturalness(self, auth_filter):
        """Test unnatural vocabulary detection"""
        text = "I endeavored to utilize my skills to facilitate the commencement of this initiative. Subsequently, I ascertained its success."
        
        result = auth_filter.check_vocabulary_naturalness(text)
        
        assert result["count"] >= 3
        assert "utilize" in result["found"]
        assert "endeavor" in result["found"]
    
    def test_calculate_authenticity_score(self, auth_filter):
        """Test overall authenticity score calculation"""
        checks = {
            "generic_phrases": {"count": 2},
            "passive_voice": {"percentage": 20},
            "cliche_detector": {"count": 1},
            "specificity_score": {"score": 6},
            "ai_patterns": {"ai_likelihood_score": 4}
        }
        
        score = auth_filter.calculate_authenticity_score(checks)
        
        assert 0 <= score <= 10
        assert isinstance(score, float)
    
    @pytest.mark.asyncio
    async def test_detect_ai_patterns(self, auth_filter, sample_draft):
        """Test AI pattern detection via LLM"""
        auth_filter.analysis_llm.call = AsyncMock(return_value=json.dumps({
            "ai_likelihood_score": 3.5,
            "detected_patterns": [
                {"pattern": "Varied transitions", "examples": ["However", "Moreover"], "severity": "low"}
            ],
            "human_indicators": ["Personal anecdotes", "Specific numbers"],
            "overall_assessment": "Mostly human-written with light editing",
            "confidence": "medium"
        }))
        
        result = await auth_filter.detect_ai_patterns(sample_draft)
        
        assert "ai_likelihood_score" in result
        assert 0 <= result["ai_likelihood_score"] <= 10
    
    @pytest.mark.asyncio
    async def test_humanize_draft(self, auth_filter, sample_draft):
        """Test draft humanization"""
        humanized = "More natural sounding version..."
        auth_filter.humanization_llm.call = AsyncMock(return_value=humanized)
        
        issues = {"generic_phrases": {"count": 2}, "ai_patterns": {"ai_likelihood_score": 7}}
        
        result = await auth_filter.humanize_draft(
            draft=sample_draft,
            issues=issues
        )
        
        assert result == humanized
    
    def test_score_to_grade(self, auth_filter):
        """Test score to letter grade conversion"""
        assert "A+" in auth_filter._score_to_grade(9.5)
        assert "A" in auth_filter._score_to_grade(8.5)
        assert "B" in auth_filter._score_to_grade(7.5)
        assert "C" in auth_filter._score_to_grade(6.5)
        assert "D" in auth_filter._score_to_grade(5.0)


# ============================================================================
# REFINEMENT LOOP TESTS
# ============================================================================

class TestRefinementLoop:
    """Tests for RefinementLoop component"""
    
    @pytest.fixture
    def refiner(self):
        """Create RefinementLoop with mocked LLMs"""
        with patch('drafting_engine.refinement_loop.create_llm_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            refiner = RefinementLoop(temperature=0.6)
            refiner.critic_llm = client
            refiner.revision_llm = client
            return refiner
    
    @pytest.mark.asyncio
    async def test_critic_agent_returns_structured_critique(
        self, refiner, sample_draft, scholarship_profile
    ):
        """Test critic agent returns properly structured critique"""
        refiner.critic_llm.call = AsyncMock(return_value=json.dumps({
            "dimensions": {
                "ALIGNMENT": {"score": 8, "evidence": "...", "suggestion": "..."},
                "SPECIFICITY": {"score": 9, "evidence": "...", "suggestion": "..."},
                "IMPACT": {"score": 8, "evidence": "...", "suggestion": "..."},
                "AUTHENTICITY": {"score": 7, "evidence": "...", "suggestion": "..."},
                "NARRATIVE_FLOW": {"score": 8, "evidence": "...", "suggestion": "..."},
                "TONE_MATCH": {"score": 8, "evidence": "...", "suggestion": "..."},
                "HOOK_STRENGTH": {"score": 9, "evidence": "...", "suggestion": "..."},
                "CONCLUSION": {"score": 7, "evidence": "...", "suggestion": "..."},
                "WORD_EFFICIENCY": {"score": 8, "evidence": "...", "suggestion": "..."},
                "DIFFERENTIATION": {"score": 7, "evidence": "...", "suggestion": "..."}
            },
            "overall_score": 7.9,
            "top_strengths": ["Specific numbers", "Strong opening", "Clear narrative"],
            "top_weaknesses": ["Conclusion could be stronger", "Some generic phrases"],
            "line_edits": []
        }))
        
        critique = await refiner.critic_agent(sample_draft, scholarship_profile)
        
        assert "dimensions" in critique
        assert "overall_score" in critique
        assert 0 <= critique["overall_score"] <= 10
        assert "top_strengths" in critique
        assert "top_weaknesses" in critique
    
    def test_generate_improvements_prioritizes_low_scores(self, refiner):
        """Test that improvements target lowest-scoring dimensions"""
        critique = {
            "dimensions": {
                "ALIGNMENT": {"score": 9, "evidence": "...", "suggestion": "..."},
                "SPECIFICITY": {"score": 4, "evidence": "Vague", "suggestion": "Add numbers"},
                "HOOK_STRENGTH": {"score": 5, "evidence": "Weak", "suggestion": "Stronger open"}
            }
        }
        
        improvements = refiner.generate_improvements(critique)
        
        # Should prioritize SPECIFICITY (score 4) over others
        assert len(improvements) >= 1
        assert improvements[0]["dimension"] == "SPECIFICITY"
        assert improvements[0]["priority"] == "high"
    
    def test_calculate_improvement_trajectory(self, refiner):
        """Test improvement metrics calculation"""
        history = [
            {"critique": {"overall_score": 6.5}},
            {"critique": {"overall_score": 7.5}},
            {"critique": {"overall_score": 8.5}}
        ]
        
        metrics = refiner.calculate_improvement(history)
        
        assert metrics["initial_score"] == 6.5
        assert metrics["final_score"] == 8.5
        assert metrics["improvement"] == 2.0
        assert metrics["iterations_needed"] == 3
        assert metrics["consistent_improvement"] is True
    
    @pytest.mark.asyncio
    async def test_refine_draft_stops_at_target_score(
        self, refiner, sample_draft, scholarship_profile
    ):
        """Test that refinement stops when target score is reached"""
        # First critique returns high score
        refiner.critic_llm.call = AsyncMock(return_value=json.dumps({
            "dimensions": {
                "ALIGNMENT": {"score": 9, "evidence": "...", "suggestion": "..."}
            },
            "overall_score": 9.0,
            "top_strengths": ["Excellent"],
            "top_weaknesses": [],
            "line_edits": []
        }))
        
        result = await refiner.refine_draft(
            draft=sample_draft,
            scholarship_profile=scholarship_profile,
            max_iterations=3,
            target_score=8.5
        )
        
        # Should stop after first iteration since score > target
        assert result["total_iterations"] == 1
        assert result["iterations"][0]["status"] == "target_reached"


# ============================================================================
# MULTI-DRAFT GENERATOR TESTS (continued)
# ============================================================================

class TestMultiDraftGenerator:
    """Tests for MultiDraftGenerator component"""
    
    @pytest.fixture
    def generator(self):
        """Create MultiDraftGenerator with mocked LLMs"""
        with patch('drafting_engine.multi_draft_generator.create_llm_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            generator = MultiDraftGenerator(temperature=0.7)
            generator.llm = client
            generator.transition_llm = client
            return generator
    
    @pytest.mark.asyncio
    async def test_generate_drafts_returns_correct_count(
        self, generator, essay_outline, content_selection, scholarship_profile
    ):
        """Test that correct number of drafts are generated"""
        generator.llm.call = AsyncMock(return_value="Generated section content...")
        generator.transition_llm.call = AsyncMock(return_value="NONE")
        
        drafts = await generator.generate_drafts(
            outline=essay_outline,
            content_selection=content_selection,
            scholarship_profile=scholarship_profile,
            num_drafts=3
        )
        
        assert len(drafts) == 3
        assert drafts[0]["emphasis"] == "primary_priority"
        assert drafts[1]["emphasis"] == "balanced"
        assert drafts[2]["emphasis"] == "storytelling"
    
    @pytest.mark.asyncio
    async def test_generate_drafts_includes_required_fields(
        self, generator, essay_outline, content_selection, scholarship_profile
    ):
        """Test that each draft has required fields"""
        generator.llm.call = AsyncMock(return_value="Generated content...")
        generator.transition_llm.call = AsyncMock(return_value="NONE")
        
        drafts = await generator.generate_drafts(
            outline=essay_outline,
            content_selection=content_selection,
            scholarship_profile=scholarship_profile,
            num_drafts=1
        )
        
        draft = drafts[0]
        assert "version" in draft
        assert "emphasis" in draft
        assert "draft" in draft
        assert "rationale" in draft
        assert "word_count" in draft
    
    def test_get_emphasis_guidance_primary_priority(self, generator, scholarship_profile):
        """Test emphasis guidance for primary priority strategy"""
        guidance = generator._get_emphasis_guidance("primary_priority", scholarship_profile)
        
        assert "leadership" in guidance.lower()  # Top priority
        assert "focus" in guidance.lower() or "heavily" in guidance.lower()
    
    def test_get_emphasis_guidance_balanced(self, generator, scholarship_profile):
        """Test emphasis guidance for balanced strategy"""
        guidance = generator._get_emphasis_guidance("balanced", scholarship_profile)
        
        assert "distribute" in guidance.lower() or "multiple" in guidance.lower()
    
    def test_get_emphasis_guidance_storytelling(self, generator, scholarship_profile):
        """Test emphasis guidance for storytelling strategy"""
        guidance = generator._get_emphasis_guidance("storytelling", scholarship_profile)
        
        assert "narrative" in guidance.lower() or "story" in guidance.lower()
    
    def test_get_relevant_content_maps_sections(self, generator, content_selection):
        """Test that content is correctly mapped to sections"""
        # Add test content
        content_selection["outcomes"] = "50 students trained, 15 apps built"
        content_selection["leadership_examples"] = "Led team of mentors"
        
        impact_content = generator.get_relevant_content("impact", content_selection)
        action_content = generator.get_relevant_content("action", content_selection)
        
        assert "outcomes" in impact_content
        assert "leadership" in action_content.lower()
    
    @pytest.mark.asyncio
    async def test_generate_transition_returns_none_when_unnecessary(self, generator):
        """Test that transition returns empty when not needed"""
        generator.transition_llm.call = AsyncMock(return_value="NONE")
        
        transition = await generator.generate_transition(
            current_section="First paragraph ending naturally.",
            next_section="Second paragraph continues the flow."
        )
        
        assert transition == ""
    
    @pytest.mark.asyncio
    async def test_generate_transition_returns_text_when_needed(self, generator):
        """Test that transition returns text when appropriate"""
        generator.transition_llm.call = AsyncMock(return_value="This experience shaped my approach.")
        
        transition = await generator.generate_transition(
            current_section="First topic discussed.",
            next_section="Completely different topic."
        )
        
        assert transition == "This experience shaped my approach."
    
    @pytest.mark.asyncio
    async def test_weave_sections_combines_in_order(self, generator, essay_outline):
        """Test that sections are woven together in correct order"""
        sections = {
            "hook": "Opening hook paragraph.",
            "challenge": "Challenge paragraph.",
            "action": "Action paragraph.",
            "impact": "Impact paragraph.",
            "reflection": "Reflection paragraph."
        }
        generator.transition_llm.call = AsyncMock(return_value="NONE")
        
        full_essay = await generator.weave_sections(sections, essay_outline)
        
        # Check order is preserved
        assert full_essay.index("Opening hook") < full_essay.index("Challenge")
        assert full_essay.index("Challenge") < full_essay.index("Action")
        assert full_essay.index("Action") < full_essay.index("Impact")
        assert full_essay.index("Impact") < full_essay.index("Reflection")


# ============================================================================
# SUPPLEMENTARY GENERATOR TESTS
# ============================================================================

class TestSupplementaryGenerator:
    """Tests for SupplementaryGenerator component"""
    
    @pytest.fixture
    def supp_generator(self):
        """Create SupplementaryGenerator with mocked LLM"""
        with patch('drafting_engine.supplementary_generator.create_llm_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            generator = SupplementaryGenerator(temperature=0.6)
            generator.llm = client
            return generator
    
    @pytest.mark.asyncio
    async def test_generate_resume_bullets_returns_list(
        self, supp_generator, content_selection, scholarship_profile
    ):
        """Test resume bullet generation returns list"""
        supp_generator.llm.call = AsyncMock(return_value=json.dumps([
            {
                "section": "Experience",
                "original": "Taught coding",
                "improved": "Trained 50 students in Python, achieving 80% course completion rate",
                "rationale": "Adds quantifiable metrics",
                "impact_metrics": "50 students, 80% completion",
                "priority": "high"
            },
            {
                "section": "Leadership",
                "original": "Led volunteer team",
                "improved": "Directed 5-person mentor team, delivering 12-week curriculum",
                "rationale": "Specifies team size and duration",
                "impact_metrics": "5 mentors, 12 weeks",
                "priority": "medium"
            }
        ]))
        
        bullets = await supp_generator.generate_resume_bullets(
            content_selection=content_selection,
            scholarship_profile=scholarship_profile
        )
        
        assert isinstance(bullets, list)
        assert len(bullets) >= 1
        assert "section" in bullets[0]
        assert "improved" in bullets[0]
    
    @pytest.mark.asyncio
    async def test_generate_cover_letter_returns_string(
        self, supp_generator, content_selection, scholarship_profile
    ):
        """Test cover letter generation returns formatted string"""
        cover_letter_text = """
        Dear Selection Committee,
        
        I am excited to apply for the Tech Leaders Scholarship...
        
        [Body paragraph about leadership experience]
        
        Sincerely,
        [Student Name]
        """
        supp_generator.llm.call = AsyncMock(return_value=cover_letter_text)
        
        letter = await supp_generator.generate_cover_letter(
            content_selection=content_selection,
            scholarship_profile=scholarship_profile
        )
        
        assert isinstance(letter, str)
        assert len(letter) > 100  # Reasonable length


# ============================================================================
# DRAFTING ENGINE (ORCHESTRATOR) TESTS
# ============================================================================

class TestDraftingEngine:
    """Tests for main DraftingEngine orchestrator"""
    
    @pytest.fixture
    def engine(self):
        """Create DraftingEngine with all components mocked"""
        with patch('drafting_engine.drafting_engine.ContentSelector') as MockCS, \
            patch('drafting_engine.drafting_engine.NarrativeArchitect') as MockNA, \
            patch('drafting_engine.drafting_engine.MultiDraftGenerator') as MockMD, \
            patch('drafting_engine.drafting_engine.StyleMatcher') as MockSM, \
            patch('drafting_engine.drafting_engine.AuthenticityFilter') as MockAF, \
            patch('drafting_engine.drafting_engine.RefinementLoop') as MockRL:
            
            # Create mock instances with default behavior
            MockCS.return_value = MagicMock()
            MockNA.return_value = MagicMock()
            MockMD.return_value = MagicMock()
            MockSM.return_value = MagicMock()
            MockAF.return_value = MagicMock()
            MockRL.return_value = MagicMock()
            
            engine = DraftingEngine()
            yield engine
    
    def test_engine_initializes_all_components(self):
        """Test that engine initializes all required components"""
        engine = DraftingEngine()
        
        assert hasattr(engine, 'content_selector')
        assert hasattr(engine, 'narrative_architect')
        assert hasattr(engine, 'multi_draft_generator')
        assert hasattr(engine, 'style_matcher')
        assert hasattr(engine, 'authenticity_filter')
        assert hasattr(engine, 'refinement_loop')
        
        assert engine.content_selector is not None
        assert engine.narrative_architect is not None
        assert engine.multi_draft_generator is not None
        assert engine.style_matcher is not None
        assert engine.authenticity_filter is not None
        assert engine.refinement_loop is not None
    
    @pytest.mark.asyncio
    async def test_generate_application_materials_full_pipeline(
        self, scholarship_profile, mock_student_kb
    ):
        """Test full pipeline execution"""
        
        # Create a real engine instance
        engine = DraftingEngine()
        
        # Now mock its components directly
        engine.content_selector.select_content = AsyncMock(return_value={
            "primary_story": {"story": {"text": "..."}, "score": 8.5},
            "supporting_stories": [],
            "avoid_stories": []
        })
        
        engine.narrative_architect.create_outline = AsyncMock(return_value={
            "narrative_style": "hero_journey",
            "sections": {"hook": {"target_words": 100}},
            "total_word_limit": 650
        })
        
        engine.multi_draft_generator.generate_drafts = AsyncMock(return_value=[
            {"version": 1, "emphasis": "primary_priority", "draft": "Draft 1 with many words here to make it longer"},
            {"version": 2, "emphasis": "balanced", "draft": "Draft 2 with many words here to make it longer"},
            {"version": 3, "emphasis": "storytelling", "draft": "Draft 3 with many words here to make it longer"}
        ])
        
        engine.style_matcher.analyze_scholarship_style = AsyncMock(return_value={
            "tone": "professional"
        })
        engine.style_matcher.adjust_draft_style = AsyncMock(return_value="Styled draft with many words here to make it longer")
        
        engine.authenticity_filter.check_authenticity = AsyncMock(return_value={
            "score": 8.0,
            "issues": {}
        })
        
        engine.refinement_loop.refine_draft = AsyncMock(return_value={
            "final_draft": "Final polished essay with sufficient words to meet requirements...",
            "iterations": [{"iteration": 1, "score": 7.5}, {"iteration": 2, "score": 8.5}],
            "improvement_trajectory": {"initial_score": 7, "final_score": 8.5},
            "total_iterations": 2
        })
        
        # Mock the supplementary generator - use AsyncMock for async methods
        with patch('drafting_engine.supplementary_generator.SupplementaryGenerator') as MockSupp:
            # Create an AsyncMock instance instead of MagicMock
            mock_supp_instance = AsyncMock()
            
            # Set up the async methods to return coroutines
            mock_supp_instance.generate_resume_bullets = AsyncMock(return_value=[
                "Led team of 5 to complete project ahead of schedule",
                "Increased efficiency by 40%"
            ])
            mock_supp_instance.generate_cover_letter = AsyncMock(return_value="Dear Selection Committee...")
            mock_supp_instance.generate_short_answers = AsyncMock(return_value={
                "answer1": "Short answer 1",
                "answer2": "Short answer 2"
            })
            
            # Make the constructor return our async mock instance
            MockSupp.return_value = mock_supp_instance
            
            # Execute the full pipeline
            result = await engine.generate_application_materials(
                scholarship_profile=scholarship_profile,
                student_kb=mock_student_kb,
                strategy="weighted",
                word_limit=650
            )
        
        # Verify output structure
        assert "primary_essay" in result
        assert isinstance(result["primary_essay"], str)
        assert len(result["primary_essay"]) > 0
        
        assert "alternative_versions" in result
        assert len(result["alternative_versions"]) == 3
        
        assert "refinement_history" in result
        assert isinstance(result["refinement_history"], list)
        
        assert "improvement_metrics" in result
        assert "final_score" in result["improvement_metrics"]
        
        assert "supplementary_materials" in result
        assert "resume_bullets" in result["supplementary_materials"]
        assert "cover_letter_template" in result["supplementary_materials"]
        
        assert "generation_metadata" in result
        assert result["generation_metadata"]["content_strategy"] == "weighted"
        
        # Verify all components were called
        engine.content_selector.select_content.assert_called_once()
        engine.narrative_architect.create_outline.assert_called_once()
        engine.multi_draft_generator.generate_drafts.assert_called_once()
        engine.style_matcher.analyze_scholarship_style.assert_called_once()
        assert engine.style_matcher.adjust_draft_style.call_count == 3
        assert engine.authenticity_filter.check_authenticity.call_count >= 3
        engine.refinement_loop.refine_draft.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_quick_draft_mode(self, scholarship_profile, mock_student_kb):
        """Test quick draft mode skips appropriate steps"""
        
        # Create real engine
        engine = DraftingEngine()
        
        # Mock its component methods
        engine.content_selector.select_content = AsyncMock(return_value={
            "primary_story": {"story": {"text": "..."}},
            "supporting_stories": []
        })
        
        engine.narrative_architect.create_outline = AsyncMock(return_value={
            "narrative_style": "hero_journey",
            "sections": {}
        })
        
        engine.multi_draft_generator.generate_drafts = AsyncMock(return_value=[
            {"version": 1, "draft": "Quick draft with sufficient content to test..."}
        ])
        
        engine.refinement_loop.refine_draft = AsyncMock(return_value={
            "final_draft": "Refined quick draft with improvements..."
        })
        
        result = await engine.quick_draft(
            scholarship_profile=scholarship_profile,
            student_kb=mock_student_kb,
            word_limit=500,
            skip_refinement=False
        )
        
        assert isinstance(result, str)
        engine.multi_draft_generator.generate_drafts.assert_called_once()
        call_args = engine.multi_draft_generator.generate_drafts.call_args
        assert call_args[1]["num_drafts"] == 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for component interactions"""
    
    @pytest.mark.asyncio
    async def test_content_to_outline_flow(
        self, scholarship_profile, mock_student_kb
    ):
        """Test content selection feeds correctly into outline creation"""
        with patch('drafting_engine.content_selector.create_llm_client') as mock1, \
             patch('drafting_engine.narrative_architect.create_llm_client') as mock2:
            
            # Setup mocks
            selector_client = AsyncMock()
            selector_client.call = AsyncMock(return_value=json.dumps({
                "raw_score": 8, "evidence_score": 8, "impact_score": 8,
                "specificity_score": 8, "authenticity_score": 8, "alignment_score": 8,
                "reasoning": "Good", "key_strengths": [], "key_weaknesses": []
            }))
            mock1.return_value = selector_client
            
            architect_client = AsyncMock()
            architect_client.call = AsyncMock(side_effect=[
                "hero_journey",
                json.dumps({"hook": "guidance", "challenge": "guidance"})
            ])
            mock2.return_value = architect_client
            
            # Create components
            selector = ContentSelector()
            selector.llm = selector_client
            
            architect = NarrativeArchitect()
            architect.llm = architect_client
            
            # Run flow
            content = await selector.select_content(
                scholarship_profile=scholarship_profile,
                student_kb=mock_student_kb,
                strategy="weighted"
            )
            
            outline = await architect.create_outline(
                content_selection=content,
                scholarship_profile=scholarship_profile,
                word_limit=650
            )
            
            assert outline["narrative_style"] == "hero_journey"
            assert "sections" in outline
    
    @pytest.mark.asyncio
    async def test_authenticity_to_humanization_flow(self, sample_draft):
        """Test authenticity check triggers humanization when needed"""
        with patch('drafting_engine.authenticity_filter.create_llm_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            
            auth_filter = AuthenticityFilter()
            auth_filter.analysis_llm = client
            auth_filter.humanization_llm = client
            
            # Mock low authenticity score
            client.call = AsyncMock(side_effect=[
                json.dumps({  # AI pattern detection
                    "ai_likelihood_score": 8,
                    "detected_patterns": [{"pattern": "Too perfect", "examples": [], "severity": "high"}],
                    "human_indicators": [],
                    "overall_assessment": "Likely AI",
                    "confidence": "high"
                }),
                json.dumps([  # Improvement suggestions
                    "Add personal voice"
                ]),
                "Humanized version of the essay..."  # Humanization
            ])
            
            # Check authenticity
            check_result = await auth_filter.check_authenticity(sample_draft)
            
            # Should have low score due to high AI likelihood
            assert check_result["score"] < 7.0
            
            # Humanize if needed
            if check_result["score"] < 7.0:
                humanized = await auth_filter.humanize_draft(
                    draft=sample_draft,
                    issues=check_result["issues"]
                )
                assert humanized is not None


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_empty_draft_authenticity(self):
        """Test authenticity filter handles empty text"""
        with patch('drafting_engine.authenticity_filter.create_llm_client'):
            auth_filter = AuthenticityFilter()
            
            result = auth_filter.detect_generic_phrases("")
            assert result["count"] == 0
            
            result = auth_filter.find_cliches("")
            assert result["count"] == 0
    
    def test_very_short_draft(self):
        """Test components handle very short drafts"""
        with patch('drafting_engine.authenticity_filter.create_llm_client'):
            auth_filter = AuthenticityFilter()
            
            short_text = "I led a team."
            
            result = auth_filter.count_passive_voice(short_text)
            assert "count" in result
            
            result = auth_filter.measure_specificity(short_text)
            assert "score" in result
    
    def test_special_characters_in_draft(self):
        """Test handling of special characters"""
        with patch('drafting_engine.authenticity_filter.create_llm_client'):
            auth_filter = AuthenticityFilter()
            
            text_with_special = "I improved efficiency by 40%! Cost: $10,000. Email: test@example.com"
            
            result = auth_filter.measure_specificity(text_with_special)
            assert result["numbers_count"] >= 2  # 40 and 10000
    
    @pytest.mark.asyncio
    async def test_json_parsing_failure_handling(self):
        """Test graceful handling of malformed LLM responses"""
        with patch('drafting_engine.content_selector.create_llm_client') as mock:
            client = AsyncMock()
            # Return invalid JSON
            client.call = AsyncMock(return_value="This is not valid JSON {{{")
            mock.return_value = client
            
            selector = ContentSelector()
            selector.llm = client
            
            # Should handle error and return default score
            score = await selector.calculate_relevance(
                story={"text": "Test story"},
                priority="leadership",
                weight=0.5,
                scholarship_profile={"name": "Test"}
            )
            
            # Should return fallback score (5.0 * weight)
            assert score == 2.5
    
    def test_missing_scholarship_fields(self):
        """Test handling of incomplete scholarship profiles"""
        with patch('drafting_engine.narrative_architect.create_llm_client'):
            architect = NarrativeArchitect()
            
            # Minimal profile
            minimal_profile = {"name": "Test Scholarship"}
            
            # Should use defaults for missing fields
            template = architect._get_outline_template("hero_journey")
            assert template is not None
    
    def test_zero_word_limit(self):
        """Test handling of zero word limit"""
        with patch('drafting_engine.narrative_architect.create_llm_client'):
            architect = NarrativeArchitect()
            
            outline = {
                "sections": {
                    "hook": {"allocation_percentage": 0.5},
                    "body": {"allocation_percentage": 0.5}
                }
            }
            
            result = architect._allocate_word_counts(outline, 0)
            
            assert result["sections"]["hook"]["target_words"] == 0
            assert result["sections"]["body"]["target_words"] == 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance-related tests"""
    
    @pytest.mark.asyncio
    async def test_refinement_max_iterations_respected(self):
        """Test that refinement loop respects max iterations"""
        with patch('drafting_engine.refinement_loop.create_llm_client') as mock:
            client = AsyncMock()
            # Always return low score to force max iterations
            client.call = AsyncMock(return_value=json.dumps({
                "dimensions": {"TEST": {"score": 5, "evidence": "...", "suggestion": "..."}},
                "overall_score": 5.0,
                "top_strengths": [],
                "top_weaknesses": ["Low score"],
                "line_edits": []
            }))
            mock.return_value = client
            
            refiner = RefinementLoop()
            refiner.critic_llm = client
            refiner.revision_llm = AsyncMock(return_value="Revised draft...")
            
            result = await refiner.refine_draft(
                draft="Test draft",
                scholarship_profile={"name": "Test"},
                max_iterations=2,
                target_score=9.0  # Unreachable
            )
            
            # Should stop at max_iterations
            assert result["total_iterations"] <= 2


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks between tests"""
    yield
    # Cleanup happens automatically


def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )