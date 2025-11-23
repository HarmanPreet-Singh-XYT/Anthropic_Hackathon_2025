"""
Pydantic schemas for Scout Agent data structures
Clean, type-safe models for scholarship intelligence
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
from datetime import datetime


class EligibilityCriteria(BaseModel):
    """Eligibility requirements for scholarship"""
    gpa_requirement: Optional[float] = Field(None, ge=0.0, le=4.0, description="Minimum GPA (0-4 scale)")
    grade_levels: List[str] = Field(default_factory=list, description="Eligible grade levels")
    citizenship: List[str] = Field(default_factory=list, description="Citizenship/residency requirements")
    demographics: List[str] = Field(default_factory=list, description="Demographic focus areas")
    majors_fields: List[str] = Field(default_factory=list, description="Required/preferred academic fields")
    geographic: List[str] = Field(default_factory=list, description="Geographic restrictions")
    other: List[str] = Field(default_factory=list, description="Other requirements")


class SelectionEmphasis(BaseModel):
    """What the scholarship prioritizes in selection"""
    leadership_weight: Optional[Union[str, int]] = Field(None, description="Emphasis on leadership (high, medium, low)")
    academic_weight: Optional[Union[str, int]] = Field(None, description="Emphasis on academics (high, medium, low)")
    service_weight: Optional[Union[str, int]] = Field(None, description="Emphasis on community service (high, medium, low)")
    financial_need_weight: Optional[Union[str, int]] = Field(None, description="Emphasis on financial need (high, medium, low)")
    specific_talents: List[str] = Field(default_factory=list, description="Specific talents or skills valued")
    other_factors: List[str] = Field(default_factory=list, description="Other selection factors")


class OfficialScholarshipData(BaseModel):
    """Structured data from official scholarship page"""
    scholarship_name: str = Field(description="Official scholarship name")
    organization: Optional[str] = Field(None, description="Sponsoring organization")
    contact_email: Optional[str] = Field(None, description="Official contact email address")
    contact_name: Optional[str] = Field(None, description="Name of contact person or committee")
    keywords: List[str] = Field(
        default_factory=list,
        description="High-signal keywords and phrases stated on the page"
    )
    explicit_requirements: List[str] = Field(
        default_factory=list,
        description="Concrete requirements (GPA numbers, deadlines, documents, eligibility)"
    )
    explicit_instructions: List[str] = Field(
        default_factory=list,
        description="Actions the applicant must do or have"
    )
    metrics: List[str] = Field(
        default_factory=list,
        description="Numeric metrics like award amount, slots, GPA, deadlines"
    )

    # Core values for Decoder agent
    primary_values: List[str] = Field(
        min_length=1,
        max_length=10,
        description="Top qualities the scholarship seeks"
    )
    implicit_values: List[str] = Field(
        default_factory=list,
        description="Values implied by language/tone"
    )
    tone_indicators: str = Field(
        description="Writing style (e.g., 'Humble, inspirational')"
    )

    # Eligibility & selection
    eligibility_criteria: EligibilityCriteria
    selection_emphasis: SelectionEmphasis = Field(
        default_factory=SelectionEmphasis,
        description="What scholarship prioritizes (leadership, service, etc.)"
    )

    # Application details
    award_amount: Optional[str] = Field(None, description="Award amount")
    num_awards: Optional[int] = Field(None, description="Number of awards")
    deadline: Optional[str] = Field(None, description="Application deadline")
    application_components: List[str] = Field(
        default_factory=list,
        description="Required components (essay, transcript, etc.)"
    )

    # Metadata
    source_url: str
    scraped_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PastWinnerItem(BaseModel):
    """Past winner essay or resume with validation"""
    type: Literal["essay", "resume", "profile"] = Field(description="Type of content")
    title: str = Field(description="Title or description")
    url: str = Field(description="Source URL")
    content: str = Field(description="Full text content")
    year: Optional[str] = Field(None, description="Year awarded")
    winner_name: Optional[str] = Field(None, description="Winner's name if mentioned")

    # Validation (scored by Firecrawl's LLM during scraping)
    validation_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Quality score from Firecrawl validation (0-1)"
    )
    validation_reason: Optional[str] = Field(
        None,
        description="Why this item received its validation score"
    )

    # Analysis (extracted by Firecrawl's LLM)
    key_takeaways: List[str] = Field(
        default_factory=list,
        description="Key lessons from this example"
    )
    narrative_style: Optional[str] = Field(
        None,
        description="How the winner structured their story"
    )


class InsightData(BaseModel):
    """Tips, stats, and insights from Reddit/LinkedIn"""
    source: Literal["reddit", "linkedin", "other"] = Field(description="Source platform")
    type: Literal["tip", "stat", "insight", "warning"] = Field(description="Type of information")
    content: str = Field(description="The actual tip/stat/insight")
    url: str = Field(description="Source URL")

    # Validation (scored by Firecrawl's LLM during scraping)
    validation_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Truthfulness + usefulness score (0-1)"
    )
    validation_reason: Optional[str] = Field(
        None,
        description="Why this item received its validation score"
    )
    credibility: str = Field(
        description="Source credibility assessment (e.g., 'verified_reviewer', 'anonymous_user')"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Negative constraints or warnings (e.g. 'Do not start with a quote')"
    )

    # Optional metadata
    author: Optional[str] = Field(None, description="Author if identifiable")
    date: Optional[str] = Field(None, description="Post date if available")


class SearchSummary(BaseModel):
    """Summary of deep search results"""
    total_items_found: int = Field(description="Total essays/resumes found before filtering")
    total_data_points_found: int = Field(description="Total tips/stats found before filtering")
    items_after_validation: int = Field(description="Items passing validation threshold")
    data_after_validation: int = Field(description="Data points passing validation threshold")
    average_validation_score: float = Field(ge=0.0, le=1.0, description="Average validation score")
    search_queries_used: List[str] = Field(description="Queries executed")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PastWinnerContext(BaseModel):
    """Complete past winner context with dual output structure"""
    item: List[PastWinnerItem] = Field(
        default_factory=list,
        description="Past winner essays and resumes"
    )
    data: List[InsightData] = Field(
        default_factory=list,
        description="Tips, stats, and insights from community"
    )
    search_summary: SearchSummary


class ScoutIntelligence(BaseModel):
    """Final output from Scout Agent"""
    official: OfficialScholarshipData
    past_winner_context: PastWinnerContext
    combined_text: str = Field(
        description="Formatted text for Decoder agent consumption"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "official": {
                    "scholarship_name": "Coca-Cola Scholars Program",
                    "primary_values": ["Leadership", "Service", "Academic Excellence"],
                    "tone_indicators": "Inspirational, community-focused"
                },
                "past_winner_context": {
                    "item": [
                        {
                            "type": "essay",
                            "title": "2024 Winner Essay: Sarah Chen",
                            "validation_score": 0.95,
                            "key_takeaways": ["Specific metrics", "Humble tone"]
                        }
                    ],
                    "data": [
                        {
                            "source": "reddit",
                            "type": "tip",
                            "content": "Essays with quantified impact score higher",
                            "validation_score": 0.88
                        }
                    ]
                }
            }
        }


class ValidationResult(BaseModel):
    """Validation payload returned from Firecrawl LLM"""
    content_type: Literal["essay", "resume", "profile", "tip", "stat", "insight", "warning"]
    validation_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that the item is relevant and truthful"
    )
    validation_reason: str = Field(description="Short justification for the score")
    winner_name: Optional[str] = Field(None, description="Winner name if applicable")
    year: Optional[str] = Field(None, description="Award year if available")
    key_takeaways: List[str] = Field(default_factory=list, description="Key takeaways extracted")
    credibility: Optional[str] = Field(
        None,
        description="Credibility assessment of the source"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Negative constraints or warnings found in the content"
    )
