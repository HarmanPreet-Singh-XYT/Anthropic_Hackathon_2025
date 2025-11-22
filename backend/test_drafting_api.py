"""
backend/api/test_drafting_api.py
FastAPI testing endpoint for Drafting Engine with dummy data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
import uvicorn
from datetime import datetime

# Assuming your drafting engine is here
import sys
sys.path.append('..')
from drafting_engine.drafting_engine import DraftingEngine


# ============================================================================
# DUMMY VECTOR DATABASE
# ============================================================================

class DummyVectorDB:
    """
    Mock vector database with realistic student stories
    """
    
    def __init__(self):
        self.stories = [
            {
                "id": "story_001",
                "text": """During my junior year, I founded TechBridge, a coding club that taught 
                programming to 50+ underrepresented students in my community. I developed curriculum, 
                recruited volunteer mentors from local tech companies, and secured $5,000 in funding 
                for laptops. Within 8 months, 15 students completed web development projects, and 
                3 won hackathon awards. I learned that leadership isn't about having all the answers—
                it's about empowering others to discover their potential.""",
                "category": "leadership",
                "tags": ["technology", "education", "community"],
                "impact": "50+ students trained, 3 hackathon winners",
                "date": "2023",
                "duration": "8 months"
            },
            {
                "id": "story_002",
                "text": """After my grandmother struggled to access healthcare due to language barriers, 
                I created a bilingual health literacy program at our local community center. I translated 
                medical resources into Spanish and Mandarin, trained 12 volunteer translators, and 
                partnered with 3 local clinics. Over 200 families accessed our services in the first year. 
                This experience taught me that innovation doesn't always require technology—sometimes it's 
                about bridging gaps with empathy and cultural understanding.""",
                "category": "community_service",
                "tags": ["healthcare", "translation", "advocacy"],
                "impact": "200+ families served",
                "date": "2022-2024",
                "duration": "2 years"
            },
            {
                "id": "story_003",
                "text": """I developed an AI model to predict crop yields for small farmers in developing 
                countries, achieving 87% accuracy. Working with a Stanford research lab, I collected 
                satellite imagery data, trained machine learning models, and field-tested the system 
                with farmers in Kenya via video calls. My research was published in a peer-reviewed 
                journal, but more importantly, farmers reported 23% increase in harvest efficiency. 
                This project showed me how academic excellence can drive real-world impact.""",
                "category": "academic_excellence",
                "tags": ["research", "AI", "agriculture", "global_impact"],
                "impact": "Published research, 23% efficiency increase",
                "date": "2023-2024",
                "duration": "14 months"
            },
            {
                "id": "story_004",
                "text": """As student body president, I led a campaign to implement mental health days 
                as excused absences. I surveyed 800+ students, presented data to the school board, 
                and mobilized 300 students to attend board meetings. Despite initial resistance, 
                the policy passed unanimously. During this process, I learned to navigate bureaucracy, 
                build coalitions across different student groups, and turn student voices into policy change. 
                The experience taught me that effective leadership requires persistence and strategic thinking.""",
                "category": "leadership",
                "tags": ["advocacy", "mental_health", "policy"],
                "impact": "School-wide policy change affecting 2,000 students",
                "date": "2023",
                "duration": "6 months"
            },
            {
                "id": "story_005",
                "text": """I organized a neighborhood climate action initiative that reduced our community's 
                carbon footprint by 15%. I created a composting program, installed 20 community garden boxes, 
                and coordinated monthly sustainability workshops. We engaged 150 households and diverted 
                2 tons of waste from landfills in our first year. Beyond the environmental impact, 
                I discovered that community organizing is about building relationships and making 
                sustainability accessible to everyone, regardless of their background.""",
                "category": "community_service",
                "tags": ["environment", "sustainability", "organizing"],
                "impact": "150 households engaged, 15% carbon reduction",
                "date": "2022-2024",
                "duration": "2 years"
            },
            {
                "id": "story_006",
                "text": """I achieved a perfect score in AP Calculus BC and went on to tutor 25 
                struggling students, with 80% improving their grades by at least one letter. 
                I created custom study materials and held free weekend review sessions. 
                More than the academic achievement, I learned that teaching others deepened 
                my own understanding and that everyone learns differently—adapting my approach 
                to each student's needs became my greatest skill.""",
                "category": "academic_excellence",
                "tags": ["mathematics", "tutoring", "education"],
                "impact": "25 students tutored, 80% grade improvement",
                "date": "2023",
                "duration": "1 year"
            },
            {
                "id": "story_007",
                "text": """When our school's art program faced budget cuts, I launched a fundraising 
                campaign that raised $30,000 in 3 months. I organized a community art auction, 
                secured corporate sponsorships, and rallied 50 student volunteers. We saved the 
                program and expanded it to include digital art classes. This taught me that 
                creativity and business acumen aren't opposites—they're powerful partners 
                in solving real problems.""",
                "category": "innovation",
                "tags": ["arts", "fundraising", "entrepreneurship"],
                "impact": "$30,000 raised, program saved and expanded",
                "date": "2023",
                "duration": "3 months"
            },
            {
                "id": "story_008",
                "text": """I built a mobile app that connects local restaurants with food banks to 
                reduce food waste. The app has facilitated over 5,000 meal donations in 6 months. 
                I taught myself iOS development, pitched to 30+ restaurants, and coordinated 
                logistics with 8 food banks. Seeing families access fresh meals that would have 
                been wasted showed me how technology can create tangible social good.""",
                "category": "innovation",
                "tags": ["technology", "social_entrepreneurship", "food_security"],
                "impact": "5,000+ meals donated, 8 food banks partnered",
                "date": "2023-2024",
                "duration": "6 months"
            },
            {
                "id": "story_009",
                "text": """As captain of our debate team, I rebuilt our program from 5 to 40 members 
                and led us to our first state championship in 15 years. I implemented peer 
                mentorship, created an inclusive culture welcoming students of all skill levels, 
                and secured funding for competition travel. Beyond trophies, I learned that 
                building a team culture where everyone feels valued creates sustainable success.""",
                "category": "leadership",
                "tags": ["debate", "teambuilding", "competition"],
                "impact": "Team grew 800%, state championship won",
                "date": "2022-2024",
                "duration": "2 years"
            },
            {
                "id": "story_010",
                "text": """I conducted independent research on microplastics in local water sources, 
                testing 50+ samples across 3 months. My findings revealed contamination levels 
                20% higher than EPA standards, prompting a city council investigation. 
                I presented my research at a regional science fair, winning first place, 
                but the real victory was sparking policy discussions about water quality 
                testing in our community.""",
                "category": "academic_excellence",
                "tags": ["research", "environmental_science", "policy_impact"],
                "impact": "City council investigation triggered, 1st place science fair",
                "date": "2024",
                "duration": "4 months"
            }
        ]
        
        self.structured_data = {
            "personal_info": {
                "name": "Alex Johnson",
                "email": "alex.johnson@email.com",
                "phone": "(555) 123-4567",
                "location": "San Francisco, CA",
                "linkedin": "linkedin.com/in/alexjohnson",
                "github": "github.com/alexjohnson"
            },
            "education": [
                {
                    "institution": "Lincoln High School",
                    "location": "San Francisco, CA",
                    "degree": "High School Diploma",
                    "gpa": "3.95/4.0",
                    "date_range": "2020 - 2024",
                    "honors": [
                        "National Merit Semifinalist",
                        "AP Scholar with Distinction",
                        "Principal's Honor Roll (4 years)"
                    ]
                }
            ],
            "experiences": [
                {
                    "title": "Founder & President",
                    "organization": "TechBridge Coding Club",
                    "location": "San Francisco, CA",
                    "date_range": "Aug 2023 - Present",
                    "bullets": [
                        "Founded coding education program serving 50+ underrepresented students",
                        "Secured $5,000 in funding and partnered with 3 tech companies for mentorship",
                        "Developed curriculum resulting in 15 completed web projects and 3 hackathon awards"
                    ]
                },
                {
                    "title": "Student Body President",
                    "organization": "Lincoln High School",
                    "location": "San Francisco, CA",
                    "date_range": "May 2023 - May 2024",
                    "bullets": [
                        "Led mental health policy initiative affecting 2,000 students, achieving unanimous board approval",
                        "Managed $50,000 student activities budget and 12-member executive board",
                        "Increased student government participation by 60% through inclusive outreach"
                    ]
                },
                {
                    "title": "Research Intern",
                    "organization": "Stanford AI Lab",
                    "location": "Stanford, CA",
                    "date_range": "Jun 2023 - Aug 2024",
                    "bullets": [
                        "Developed AI crop yield prediction model achieving 87% accuracy for smallholder farmers",
                        "Published findings in peer-reviewed journal; presented at regional conference",
                        "Collaborated with farmers in Kenya to field-test model, resulting in 23% efficiency gains"
                    ]
                }
            ],
            "skills": {
                "Technical": ["Python", "JavaScript", "React", "Machine Learning", "Data Analysis"],
                "Languages": ["English (Native)", "Spanish (Fluent)", "Mandarin (Conversational)"],
                "Leadership": ["Team Building", "Public Speaking", "Strategic Planning", "Fundraising"]
            },
            "awards": [
                {
                    "title": "National Merit Semifinalist",
                    "organization": "National Merit Scholarship Corporation",
                    "date": "2024"
                },
                {
                    "title": "1st Place - Environmental Science",
                    "organization": "Regional Science Fair",
                    "date": "2024"
                },
                {
                    "title": "Congressional App Challenge Winner",
                    "organization": "U.S. House of Representatives",
                    "date": "2023"
                }
            ],
            "activities": [
                "Debate Team Captain (2022-2024) - Led team to first state championship in 15 years",
                "Volunteer Translator - Community Health Clinic (2022-Present)",
                "Math Tutor - 25 students tutored, 80% grade improvement (2023-Present)"
            ]
        }
    
    def query(self, priority: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Simulate vector similarity search
        """
        # Simple keyword matching for demo
        priority_lower = priority.lower().replace('_', ' ')
        
        # Score stories based on category match and keyword presence
        scored_stories = []
        for story in self.stories:
            score = 0.0
            
            # Check category match
            if story['category'].lower() == priority_lower:
                score += 0.5
            
            # Check text/tags for keywords
            text_lower = story['text'].lower()
            if priority_lower in text_lower:
                score += 0.3
            
            for tag in story['tags']:
                if priority_lower in tag.lower():
                    score += 0.2
                    break
            
            scored_stories.append((score, story))
        
        # Sort by score and return top_k
        scored_stories.sort(key=lambda x: x[0], reverse=True)
        return [story for score, story in scored_stories[:top_k]]
    
    def get_structured_data(self) -> Dict[str, Any]:
        """
        Return structured resume data
        """
        return self.structured_data


# ============================================================================
# PYDANTIC MODELS FOR API
# ============================================================================

class ContentStrategy(str, Enum):
    weighted = "weighted"
    diverse = "diverse"
    focused = "focused"

class LaTeXTemplateStyle(str, Enum):
    modern = "modern"
    classic = "classic"
    minimal = "minimal"

class ScholarshipProfileRequest(BaseModel):
    name: str = Field(..., description="Scholarship name")
    mission: str = Field(..., description="Scholarship mission statement")
    priorities: List[str] = Field(..., description="List of scholarship priorities")
    weighted_priorities: Optional[Dict[str, float]] = Field(None, description="Weighted priorities")
    value_descriptions: Optional[Dict[str, str]] = Field(None, description="What scholarship values in each priority")
    short_answer_prompts: Optional[List[str]] = Field(None, description="Additional essay prompts")

class GenerateApplicationRequest(BaseModel):
    scholarship_profile: ScholarshipProfileRequest
    strategy: ContentStrategy = ContentStrategy.weighted
    word_limit: int = Field(650, ge=100, le=2000)
    include_latex_resume: bool = True
    latex_template_style: LaTeXTemplateStyle = LaTeXTemplateStyle.modern

class QuickDraftRequest(BaseModel):
    scholarship_profile: ScholarshipProfileRequest
    word_limit: int = Field(650, ge=100, le=2000)
    skip_refinement: bool = False

class LaTeXResumeRequest(BaseModel):
    scholarship_profile: ScholarshipProfileRequest
    template_style: LaTeXTemplateStyle = LaTeXTemplateStyle.modern

class CompareStrategiesRequest(BaseModel):
    scholarship_profile: ScholarshipProfileRequest
    word_limit: int = Field(650, ge=100, le=2000)


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Drafting Engine Test API",
    description="Testing API for essay drafting engine with dummy student data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
drafting_engine = DraftingEngine()
dummy_db = DummyVectorDB()


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API info endpoint"""
    return {
        "message": "Drafting Engine Test API",
        "version": "1.0.0",
        "endpoints": {
            "POST /generate-application": "Generate complete application package",
                        "POST /quick-draft": "Generate quick draft without full pipeline",
            "POST /generate-latex-resume": "Generate LaTeX resume only",
            "POST /compare-strategies": "Compare different content strategies",
            "GET /sample-scholarship": "Get sample scholarship profile",
            "GET /student-stories": "View all dummy student stories",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "drafting_engine": "operational",
            "dummy_database": "operational"
        }
    }

@app.get("/sample-scholarship")
async def get_sample_scholarship():
    """Get a sample scholarship profile for testing"""
    return {
        "name": "Gates Millennium Scholarship",
        "mission": "To promote academic excellence and provide opportunities for outstanding minority students with significant financial need to reach their full potential.",
        "priorities": [
            "leadership",
            "community_service",
            "academic_excellence",
            "innovation"
        ],
        "weighted_priorities": {
            "leadership": 0.35,
            "community_service": 0.30,
            "academic_excellence": 0.20,
            "innovation": 0.15
        },
        "value_descriptions": {
            "leadership": "Demonstrated ability to inspire and mobilize others toward positive change. We value leaders who empower their communities and create lasting impact.",
            "community_service": "Sustained commitment to improving communities through direct service and advocacy. We seek students who see service as a lifelong commitment.",
            "academic_excellence": "Strong academic performance combined with intellectual curiosity and love of learning. Excellence means pushing boundaries and pursuing knowledge.",
            "innovation": "Creative problem-solving and entrepreneurial thinking applied to real-world challenges. We value students who think differently and create new solutions."
        },
        "short_answer_prompts": [
            "Describe a time when you faced a significant challenge. How did you overcome it? (250 words)",
            "What does leadership mean to you? Provide a specific example. (150 words)",
            "How will this scholarship help you achieve your goals? (200 words)"
        ]
    }

@app.get("/student-stories")
async def get_student_stories():
    """View all dummy student stories in the database"""
    return {
        "total_stories": len(dummy_db.stories),
        "stories": dummy_db.stories,
        "student_info": dummy_db.structured_data["personal_info"]
    }

@app.post("/generate-application")
async def generate_application(request: GenerateApplicationRequest):
    """
    Generate complete application package (essay + resume + supplementary materials)
    
    This is the main endpoint that runs the full drafting pipeline.
    Expected processing time: 2-5 minutes depending on LLM response times.
    """
    try:
        print(f"\n{'='*80}")
        print(f"📝 Starting application generation for: {request.scholarship_profile.name}")
        print(f"{'='*80}\n")
        
        # Convert Pydantic model to dict
        scholarship_dict = request.scholarship_profile.dict()
        
        # Generate application materials
        result = await drafting_engine.generate_application_materials(
            scholarship_profile=scholarship_dict,
            student_kb=dummy_db,
            strategy=request.strategy.value,
            word_limit=request.word_limit,
            include_latex_resume=request.include_latex_resume,
            latex_template_style=request.latex_template_style.value
        )
        
        print(f"\n{'='*80}")
        print(f"✅ Application generation complete!")
        print(f"{'='*80}\n")
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "scholarship": request.scholarship_profile.name,
            "result": result
        }
        
    except Exception as e:
        print(f"\n❌ Error during generation: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/quick-draft")
async def generate_quick_draft(request: QuickDraftRequest):
    """
    Generate a quick single draft without full pipeline
    
    Faster than full generation (30-60 seconds).
    Good for rapid prototyping and testing.
    """
    try:
        print(f"\n{'='*80}")
        print(f"⚡ Starting quick draft for: {request.scholarship_profile.name}")
        print(f"{'='*80}\n")
        
        scholarship_dict = request.scholarship_profile.dict()
        
        draft = await drafting_engine.quick_draft(
            scholarship_profile=scholarship_dict,
            student_kb=dummy_db,
            word_limit=request.word_limit,
            skip_refinement=request.skip_refinement
        )
        
        print(f"\n{'='*80}")
        print(f"✅ Quick draft complete!")
        print(f"{'='*80}\n")
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "scholarship": request.scholarship_profile.name,
            "draft": draft,
            "word_count": len(draft.split()),
            "target_word_count": request.word_limit,
            "refinement_skipped": request.skip_refinement
        }
        
    except Exception as e:
        print(f"\n❌ Error during quick draft: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Quick draft failed: {str(e)}")

@app.post("/generate-latex-resume")
async def generate_latex_resume(request: LaTeXResumeRequest):
    """
    Generate LaTeX resume only (no essay)
    
    Returns LaTeX code that can be compiled to PDF.
    """
    try:
        print(f"\n{'='*80}")
        print(f"📄 Generating LaTeX resume ({request.template_style.value} template)")
        print(f"{'='*80}\n")
        
        scholarship_dict = request.scholarship_profile.dict()
        
        latex_resume = await drafting_engine.generate_latex_resume_only(
            scholarship_profile=scholarship_dict,
            student_kb=dummy_db,
            template_style=request.template_style.value
        )
        
        print(f"\n{'='*80}")
        print(f"✅ LaTeX resume generated!")
        print(f"{'='*80}\n")
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "template_style": request.template_style.value,
            "latex_resume": latex_resume
        }
        
    except Exception as e:
        print(f"\n❌ Error generating LaTeX resume: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"LaTeX generation failed: {str(e)}")

@app.post("/compare-strategies")
async def compare_strategies(request: CompareStrategiesRequest):
    """
    Compare different content selection strategies
    
    Generates drafts using "weighted", "diverse", and "focused" strategies
    and returns comparative analysis.
    """
    try:
        print(f"\n{'='*80}")
        print(f"🔬 Comparing strategies for: {request.scholarship_profile.name}")
        print(f"{'='*80}\n")
        
        scholarship_dict = request.scholarship_profile.dict()
        
        comparison = await drafting_engine.compare_strategies(
            scholarship_profile=scholarship_dict,
            student_kb=dummy_db,
            word_limit=request.word_limit
        )
        
        print(f"\n{'='*80}")
        print(f"✅ Strategy comparison complete!")
        print(f"{'='*80}\n")
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "scholarship": request.scholarship_profile.name,
            "comparison": comparison
        }
        
    except Exception as e:
        print(f"\n❌ Error during strategy comparison: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Strategy comparison failed: {str(e)}")

@app.get("/test-vector-db")
async def test_vector_db(priority: str = "leadership", top_k: int = 3):
    """
    Test the dummy vector database query functionality
    
    Args:
        priority: Priority to search for (e.g., "leadership", "community_service")
        top_k: Number of results to return
    """
    try:
        results = dummy_db.query(priority, top_k)
        
        return {
            "success": True,
            "query": {
                "priority": priority,
                "top_k": top_k
            },
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector DB query failed: {str(e)}")


# ============================================================================
# EXAMPLE REQUESTS (for documentation/testing)
# ============================================================================

@app.get("/examples")
async def get_examples():
    """Get example requests for each endpoint"""
    return {
        "generate_application": {
            "endpoint": "POST /generate-application",
            "example": {
                "scholarship_profile": {
                    "name": "Gates Millennium Scholarship",
                    "mission": "To promote academic excellence and provide opportunities...",
                    "priorities": ["leadership", "community_service", "academic_excellence"],
                    "weighted_priorities": {
                        "leadership": 0.35,
                        "community_service": 0.30,
                        "academic_excellence": 0.20,
                        "innovation": 0.15
                    },
                    "value_descriptions": {
                        "leadership": "Demonstrated ability to inspire and mobilize others...",
                        "community_service": "Sustained commitment to improving communities...",
                        "academic_excellence": "Strong academic performance combined with curiosity...",
                        "innovation": "Creative problem-solving and entrepreneurial thinking..."
                    }
                },
                "strategy": "weighted",
                "word_limit": 650,
                "include_latex_resume": True,
                "latex_template_style": "modern"
            }
        },
        "quick_draft": {
            "endpoint": "POST /quick-draft",
            "example": {
                "scholarship_profile": {
                    "name": "Sample Scholarship",
                    "mission": "Supporting future leaders",
                    "priorities": ["leadership", "academic_excellence"]
                },
                "word_limit": 500,
                "skip_refinement": False
            }
        },
        "generate_latex_resume": {
            "endpoint": "POST /generate-latex-resume",
            "example": {
                "scholarship_profile": {
                    "name": "Sample Scholarship",
                    "mission": "Supporting future leaders",
                    "priorities": ["leadership"]
                },
                "template_style": "modern"
            }
        }
    }


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                 DRAFTING ENGINE TEST API                         ║
    ║                                                                  ║
    ║  Server starting on http://localhost:8000                        ║
    ║  API Documentation: http://localhost:8000/docs                   ║
    ║  Alternative docs: http://localhost:8000/redoc                   ║
    ║                                                                  ║
    ║  Quick Start:                                                    ║
    ║  1. GET  /sample-scholarship  - Get sample data                  ║
    ║  2. GET  /student-stories     - View dummy student data          ║
    ║  3. POST /quick-draft         - Generate quick test draft        ║
    ║  4. POST /generate-application - Full pipeline                   ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "test_drafting_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )