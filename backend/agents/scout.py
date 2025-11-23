"""
Agent A: The Scout (Custom Scraping Pipeline)
Scrapes scholarship URL and searches for past winner intelligence
"""

import asyncio
import os
import re
import requests
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import markdownify

from .scout_schemas import (
    OfficialScholarshipData,
    EligibilityCriteria,
    SelectionEmphasis,
    PastWinnerItem,
    InsightData,
    SearchSummary,
    PastWinnerContext,
    ScoutIntelligence,
    ValidationResult
)
from utils.llm_client import LLMClient, create_llm_client

VALIDATION_THRESHOLD = 0.7
MAX_VALIDATION_CONCURRENCY = 5
MIN_CONTENT_LENGTH = 1000
SOCIAL_MEDIA_EXCLUSIONS = "-reddit -linkedin -facebook -twitter -instagram -tiktok"


class ScoutAgent:
    """
    Custom Scout Agent
    - Scrapes official scholarship page using requests + BeautifulSoup
    - Performs parallel deep search for past winners + community insights
    - Uses Claude for validation and extraction
    """

    def __init__(self):
        """Initialize Scout Agent"""
        # Google Search Credentials
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        
        # LLM Client for extraction and validation
        self.llm_client = create_llm_client(temperature=0.0) # Low temp for extraction
        
        # User Agent rotator
        self.ua = UserAgent()
        
        print(f"✓ Scout Agent initialized (Custom Pipeline)")

    def _fetch_and_clean(self, url: str) -> str:
        """
        Fetch URL and convert to clean Markdown
        
        Args:
            url: URL to fetch
            
        Returns:
            Cleaned Markdown string
        """
        try:
            # Use Jina Reader for better scraping (handles JS/SPA)
            jina_url = f"https://r.jina.ai/{url}"
            headers = {
                'User-Agent': self.ua.random,
                'X-Target-Selector': 'body' # Optional: target specific element
            }
            
            print(f"    [INFO] Fetching via Jina Reader: {jina_url}")
            response = requests.get(jina_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Jina returns markdown directly
            markdown = response.text
            
            # Basic cleanup
            if "Title:" in markdown[:100]:
                # Jina often adds metadata at top, keep it as it's useful
                pass
                
            return markdown
            
        except Exception as e:
            print(f"    [ERROR] Jina Fetch failed for {url}: {e}")
            # Fallback to direct requests (unlikely to work for SPA but good safety)
            try:
                print(f"    [INFO] Falling back to direct requests...")
                headers = {'User-Agent': self.ua.random}
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'lxml')
                for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'iframe', 'noscript', 'svg', 'canvas']):
                    tag.decompose()
                markdown = markdownify.markdownify(str(soup), heading_style="ATX", strip=['a', 'img'])
                return re.sub(r'\n{3,}', '\n\n', markdown).strip()
            except Exception as e2:
                print(f"    [ERROR] Direct fetch also failed: {e2}")
                return ""

    async def _extract_official_data(self, markdown: str, url: str) -> OfficialScholarshipData:
        """Use LLM to extract structured data from official page markdown"""
        
        system_prompt = """
You are an expert scholarship analyst. Extract structured data from the provided scholarship page content.
Return ONLY valid JSON matching the schema.
"""
        
        user_prompt = f"""
EXTRACT SCHOLARSHIP DATA FROM THIS TEXT:

{markdown[:15000]}

RETURN VALID JSON WITH THESE EXACT FIELDS:
{{
  "scholarship_name": "string (required)",
  "organization": "string or null",
  "contact_email": "string or null",
  "contact_name": "string or null",
  "keywords": ["list of strings"],
  "explicit_requirements": ["list of strings"],
  "explicit_instructions": ["list of strings"],
  "metrics": ["list of strings"],
  "primary_values": ["Leadership", "Service", "Academic Excellence"],
  "implicit_values": ["list of strings"],
  "tone_indicators": "string (e.g. 'Professional, Inspirational')",
  "eligibility_criteria": {{
    "gpa_requirement": null,
    "grade_levels": [],
    "citizenship": [],
    "demographics": [],
    "majors_fields": [],
    "geographic": [],
    "other": []
  }},
  "selection_emphasis": {{
    "leadership_weight": null,
    "academic_weight": null,
    "service_weight": null,
    "financial_need_weight": null,
    "specific_talents": [],
    "other_factors": []
  }},
  "award_amount": "string or null",
  "num_awards": null,
  "deadline": "string or null",
  "application_components": ["list of strings"]
}}

OUTPUT ONLY THE JSON, NO EXPLANATION.
"""
        try:
            response = await self.llm_client.call(
                system_prompt=system_prompt,
                user_message=user_prompt
            )
            
            # Clean and parse JSON
            cleaned = response.strip()
            if cleaned.startswith("```json"): cleaned = cleaned[7:]
            if cleaned.endswith("```"): cleaned = cleaned[:-3]
            
            data = json.loads(cleaned)
            
            # Ensure source_url is set
            data['source_url'] = url
            
            return OfficialScholarshipData.model_validate(data)
            
        except Exception as e:
            print(f"    [ERROR] LLM Extraction failed: {e}")
            # Return minimal fallback
            return OfficialScholarshipData(
                scholarship_name="Unknown Scholarship",
                primary_values=["Leadership", "Service", "Academic Excellence"],
                tone_indicators="Professional",
                eligibility_criteria=EligibilityCriteria(),
                source_url=url
            )

    async def scrape_official_page(self, url: str) -> OfficialScholarshipData:
        """
        Scrape official scholarship page using robust fallback chain:
        1. Try Jina Reader (handles JS/SPA)
        2. If fails or too short, use Google Search snippets
        3. If all fails, return minimal fallback
        """
        print(f"  → Extracting scholarship data from: {url}")
        
        markdown = ""
        
        # Step 1: Try Jina Reader for JS/SPA content
        try:
            jina_url = f"https://r.jina.ai/{url}"
            headers = {'User-Agent': self.ua.random}
            
            print(f"    [INFO] Fetching via Jina Reader...")
            response = requests.get(jina_url, headers=headers, timeout=10)
            response.raise_for_status()
            markdown = response.text
            
            print(f"    ✓ Jina fetched {len(markdown)} chars")
            
            # Validate content relevance - check for key terms
            # If it's just nav links, it won't have these
            key_terms = ["criteria", "requirement", "eligibility", "qualification", "selection", "apply", "deadline"]
            found_terms = [term for term in key_terms if term in markdown.lower()]
            
            if len(found_terms) < 2:
                print(f"    ⚠ Content lacks key terms (found {found_terms}). Treating as insufficient.")
                markdown = "" # Force fallback
            else:
                print(f"    ✓ Content seems relevant (found {len(found_terms)} key terms)")
            
        except Exception as e:
            print(f"    [ERROR] Jina fetch failed: {e}")
        
        # Step 2: If Jina failed or content too short, try Google Search snippets
        if not markdown or len(markdown) < MIN_CONTENT_LENGTH:
            print(f"    ⚠ Jina content insufficient ({len(markdown)} chars < {MIN_CONTENT_LENGTH})")
            print(f"    → Attempting Google Search fallback...")
            
            try:
                # Guess scholarship name from URL
                name_guess = url.split("/")[-1].replace("-", " ").title()
                query = f"{name_guess} scholarship requirements review criteria eligibility"
                
                print(f"    → Searching for: '{query}'")
                results = await self._run_google_search(query=query, limit=10)
                
                if results:
                    print(f"    ✓ Found {len(results)} search results")
                    snippet_markdown = ""
                    for res in results:
                        desc = getattr(res, "description", "")
                        if desc:
                            snippet_markdown += f"\n# Source: {res.title}\n{desc}\n"
                    
                    if len(snippet_markdown) > 300:
                        markdown = snippet_markdown
                    else:
                        pass
                    
                else:
                    print(f"    ⚠ No search results found")
                    
            except Exception as e:
                print(f"    [ERROR] Google Search fallback failed: {e}")
        
        # Step 3: If still no content, return minimal fallback
        if not markdown or len(markdown) < 100:
            print("    ❌ All scraping methods failed")
            return OfficialScholarshipData(
                scholarship_name="Unknown Scholarship",
                primary_values=["Leadership", "Service", "Academic Excellence"],
                tone_indicators="Professional",
                eligibility_criteria=EligibilityCriteria(),
                source_url=url
            )
        
        # Extract data with LLM
        print(f"    → Extracting with LLM from {len(markdown)} chars...")
        official_data = await self._extract_official_data(markdown, url)
        
        print(f"    ✓ Extracted: {official_data.scholarship_name}")
        return official_data

    async def _run_google_search(self, *, query: str, limit: int) -> List[Any]:
        """Run Google Custom Search"""
        if not self.google_api_key or not self.google_cse_id:
            print("    [WARNING] Google API credentials not found. Skipping search.")
            return []

        def _search():
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_cse_id,
                "q": query,
                "num": min(limit, 10)
            }
            try:
                resp = requests.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for item in data.get("items", []):
                    class GoogleResult:
                        def __init__(self, item):
                            self.url = item.get("link")
                            self.title = item.get("title")
                            self.description = item.get("snippet")
                            self.markdown = "" 
                    results.append(GoogleResult(item))
                return results
            except Exception as e:
                print(f"    [ERROR] Google Search failed: {e}")
                return []

        return await asyncio.to_thread(_search)

    async def _validate_with_llm(self, content: str, mode: str) -> Optional[ValidationResult]:
        """Use LLM to validate content relevance and extract insights"""
        
        system_prompt = f"""
You are a scholarship content validator. Analyze the text to determine if it is relevant for: {mode}.
Return ONLY valid JSON.
"""
        
        user_prompt = f"""
ANALYZE THIS CONTENT:

{content[:4000]}

TASK:
1. Score relevance (0.0-1.0). Must be >0.7 to be useful.
2. Identify content type (essay, resume, tip, stat, insight).
3. Extract key takeaways/strategies.

SCHEMA:
- content_type: essay/resume/profile/tip/stat/insight/warning
- validation_score: float 0-1
- validation_reason: string
- winner_name: string (optional)
- year: string (optional)
- key_takeaways: list[string] (Specific winning strategies)
- credibility: string (e.g. "Verified Source", "Anonymous")

OUTPUT JSON ONLY.
"""
        try:
            response = await self.llm_client.call(
                system_prompt=system_prompt,
                user_message=user_prompt
            )
            
            cleaned = response.strip()
            if cleaned.startswith("```json"): cleaned = cleaned[7:]
            if cleaned.endswith("```"): cleaned = cleaned[:-3]
            
            data = json.loads(cleaned)
            return ValidationResult.model_validate(data)
            
        except Exception as e:
            # print(f"      [DEBUG] Validation error: {e}")
            return None

    async def _validate_results(self, web_results: List[Any], mode: str, debug: bool = False) -> List[Any]:
        """Validate a batch of search results"""
        semaphore = asyncio.Semaphore(MAX_VALIDATION_CONCURRENCY)
        tasks = []
        seen_urls = set()

        async def _validate_single(res):
            url = getattr(res, "url", "")
            if not url or url in seen_urls: return None
            seen_urls.add(url)

            # Skip PDF files - they contain binary data that breaks LLM processing
            if url.lower().endswith('.pdf'):
                if debug:
                    print(f"      [DEBUG] Skipping PDF URL: {url}")
                return None

            # Skip social media (hard to scrape without API)
            if any(domain in url for domain in ["facebook.com", "x.com", "twitter.com", "tiktok.com", "instagram.com"]):
                return None

            # 1. Fetch & Clean
            async with semaphore:
                content = await asyncio.to_thread(self._fetch_and_clean, url)
            
            if not content or len(content) < MIN_CONTENT_LENGTH:
                return None
            
            # Additional check: skip if content looks like binary/PDF data
            if content.startswith('%PDF') or '\\x00' in content[:100]:
                # if debug:
                #    print(f"      [DEBUG] Skipping binary content from {url}")
                return None

            # 2. Validate with LLM
            async with semaphore:
                vr = await self._validate_with_llm(content, mode)
            
            if not vr or vr.validation_score < VALIDATION_THRESHOLD:
                return None
            
            # Store content
            res.markdown = content
            return res, vr

        for res in web_results:
            tasks.append(asyncio.create_task(_validate_single(res)))

        validated = []
        for pair in await asyncio.gather(*tasks):
            if pair:
                validated.append(pair)
        return validated

    async def search_past_winner_items(self, scholarship_hint: str, domain: str, debug: bool = False) -> List[PastWinnerItem]:
        """Search for past winner essays/resumes"""
        # Clean the hint to get the core name
        # Remove price, "Scholarship", "Program", year, etc.
        core_name = scholarship_hint
        for remove in ["Scholarship", "Program", "Foundation", "Award", "Grant", "2024", "2025", "2026"]:
            core_name = core_name.replace(remove, "")
        core_name = re.sub(r'\$\d+(,\d+)?', '', core_name).strip()
        core_name = re.sub(r'\s+', ' ', core_name).strip()
        
        print(f"  → Core name for search: '{core_name}'")

        queries = [
            f'"{core_name}" winner essay (site:edu OR site:org OR PrepScholar OR IvyScholars) {SOCIAL_MEDIA_EXCLUSIONS}',
            f'"{core_name}" winning essay example {SOCIAL_MEDIA_EXCLUSIONS}',
            f'{core_name} scholarship recipient profile {SOCIAL_MEDIA_EXCLUSIONS}',
            f'{core_name} scholarship past winners {SOCIAL_MEDIA_EXCLUSIONS}'
        ]

        items: List[PastWinnerItem] = []
        
        for query in queries:
            try:
                web_results = await self._run_google_search(query=query, limit=3)
                validated = await self._validate_results(web_results, mode="past winner essay or resume", debug=debug)

                for res, vr in validated:
                    items.append(PastWinnerItem(
                        type=vr.content_type if vr.content_type in ["essay", "resume", "profile"] else "essay",
                        title=getattr(res, "title", "") or "Past Winner Content",
                        url=getattr(res, "url", "") or "",
                        content=getattr(res, "markdown", "")[:2000],
                        validation_score=vr.validation_score,
                        validation_reason=vr.validation_reason,
                        key_takeaways=vr.key_takeaways or [],
                        winner_name=vr.winner_name,
                        year=vr.year
                    ))
            except Exception as e:
                print(f"    [ERROR] Search failed for query '{query}': {e}")
                continue

        print(f"  ✓ Found {len(items)} validated winner items")
        return items

    async def search_community_insights(self, scholarship_hint: str, debug: bool = False) -> List[InsightData]:
        """Search for tips and insights"""
        print(f"  → Searching for scholarship guidance and insights...")

        # Clean name logic (duplicated for now, could be a helper)
        core_name = scholarship_hint
        for remove in ["Scholarship", "Program", "Foundation", "Award", "Grant", "2024", "2025", "2026"]:
            core_name = core_name.replace(remove, "")
        core_name = re.sub(r'\$\d+(,\d+)?', '', core_name).strip()
        core_name = re.sub(r'\s+', ' ', core_name).strip()

        queries = [
            f'"{core_name}" scholarship tips strategies {SOCIAL_MEDIA_EXCLUSIONS}',
            f'how to win {core_name} scholarship guide {SOCIAL_MEDIA_EXCLUSIONS}',
            f'{core_name} scholarship selection criteria reddit'
        ]

        insights = []

        for query in queries:
            try:
                source = "reddit" if "reddit.com" in query else "other"
                web_results = await self._run_google_search(query=query, limit=3)
                validated = await self._validate_results(web_results, mode="tips or recommendations", debug=debug)

                for res, vr in validated:
                    insights.append(InsightData(
                        source=source,
                        type=vr.content_type if vr.content_type in ["tip", "stat", "insight", "warning"] else "tip",
                        content=getattr(res, "markdown", "")[:1000],
                        url=getattr(res, "url", "") or "",
                        validation_score=vr.validation_score,
                        validation_reason=vr.validation_reason,
                        credibility=vr.credibility or source,
                        warnings=vr.warnings or []
                    ))
            except Exception as e:
                print(f"  ⚠ Search failed for '{query}': {e}")
                continue

        print(f"  ✓ Found {len(insights)} insights")
        return insights

    async def deep_search_parallel(self, scholarship_url: str, scholarship_hint: str, debug: bool = False) -> PastWinnerContext:
        """Execute parallel deep search"""
        domain = urlparse(scholarship_url).netloc

        items_task = asyncio.create_task(self.search_past_winner_items(scholarship_hint, domain, debug))
        insights_task = asyncio.create_task(self.search_community_insights(scholarship_hint, debug))

        items, insights = await asyncio.gather(items_task, insights_task)

        summary = SearchSummary(
            total_items_found=len(items),
            total_data_points_found=len(insights),
            items_after_validation=len(items),
            data_after_validation=len(insights),
            average_validation_score=0.8, # Placeholder
            search_queries_used=["Past winner search", "Insight search"]
        )

        return PastWinnerContext(
            item=items,
            data=insights,
            search_summary=summary
        )

    def format_combined_intelligence(self, official: OfficialScholarshipData, context: PastWinnerContext) -> str:
        """Format combined intelligence for Decoder agent"""
        sections = []
        
        # Official section
        sections.append(f"# {official.scholarship_name}\n")
        sections.append(f"## Primary Values\n{', '.join(official.primary_values)}\n")
        sections.append(f"## Tone Indicators\n{official.tone_indicators}\n")
        
        # Past winner items
        if context.item:
            sections.append("\n## Past Winner Examples\n")
            for item in context.item[:3]:
                sections.append(f"### {item.title}\n- Key Takeaways: {', '.join(item.key_takeaways)}\n")

        # Community insights
        if context.data:
            sections.append("\n## Winning Strategies & Tips\n")
            for insight in context.data[:3]:
                sections.append(f"- {insight.content[:300]}...\n")

        return "\n".join(sections)

    async def run(self, scholarship_url: str, debug: bool = False) -> Dict[str, Any]:
        """Execute complete Scout workflow"""
        print("=" * 60)
        print("🔍 Scout Agent: Starting intelligence gathering (Custom Pipeline)...")
        print("=" * 60)

        # STEP 1: Official Scrape
        print("\n[STEP 1] Scraping official page...")
        official_data = await self.scrape_official_page(scholarship_url)
        
        # Prompt for official_data extraction:
        # - scholarship_name, organization
        # - contact_email, contact_name (if available)
        # - keywords: high-signal phrases on the page
        scholarship_name = official_data.scholarship_name
        print(f"  ✓ Identified: {scholarship_name}")
        
        # STEP 2: Deep Search
        print(f"\n[STEP 2] Starting deep search for '{scholarship_name}'...")
        past_winner_context = await self.deep_search_parallel(
            scholarship_url=scholarship_url,
            scholarship_hint=scholarship_name,
            debug=debug
        )

        # Format combined intelligence
        combined_text = self.format_combined_intelligence(official_data, past_winner_context)

        # Build final output
        intelligence = ScoutIntelligence(
            official=official_data,
            past_winner_context=past_winner_context,
            combined_text=combined_text
        )

        print("\n" + "=" * 60)
        print("✅ Scout Agent: Intelligence gathering complete!")
        print("=" * 60)

        return {
            "scholarship_intelligence": intelligence.model_dump(),
            "combined_text": combined_text
        }
