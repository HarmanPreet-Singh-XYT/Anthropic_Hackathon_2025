"""
Agent A: The Scout (Firecrawl-powered)
Scrapes scholarship URL and searches for past winner intelligence
"""

import asyncio
import os
import re
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from firecrawl import FirecrawlApp

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

VALIDATION_THRESHOLD = 0.01  # Lowered for testing
MAX_VALIDATION_CONCURRENCY = 5
MIN_CONTENT_LENGTH = 100


class ScoutAgent:
    """
    Firecrawl-powered Scout Agent
    - Scrapes official scholarship page with /scrape endpoint
    - Performs parallel deep search for past winners + community insights
    - Uses Firecrawl's internal LLM for validation during scraping
    """

    def __init__(self(self, firecrawl_api_key: str = None):
        """
        Initialize Scout Agent

        Args:
            firecrawl_api_key: Firecrawl API key (or reads from env)
        """
        api_key = firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment or arguments")

        self.firecrawl = FirecrawlApp(api_key=api_key)
        
        # Google Search Credentials
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        print(f"✓ Scout Agent initialized with Firecrawl")

    def _build_official_prompt(self) -> str:
        """Prompt for rich official-page extraction."""
        return """
You are extracting scholarship requirements from the OFFICIAL scholarship page.
Return JSON matching the provided schema. Be precise and only include facts explicitly stated.

Capture:
- scholarship_name, organization
- keywords: high-signal phrases on the page
- explicit_requirements: GPA numbers, deadlines, documents, eligibility bullets, counts
- explicit_instructions: things applicants must/should do/have
- metrics: award amount, number of awards, GPA thresholds, dates
- primary_values + implicit_values + tone
- eligibility (citizenship, grade level, geography), selection emphasis, application components, deadline, award_amount, num_awards

If a field is not present, leave it empty or null. Do NOT guess.
"""

    def _parse_markdown_fallback(self, markdown_content: str) -> Dict[str, Any]:
        """Lightweight regex-based extraction when structured extract fails."""
        award_amount = None
        deadline = None
        gpa_requirement = None
        metrics: List[str] = []
        explicit_requirements: List[str] = []
        explicit_instructions: List[str] = []

        dollar_matches = re.findall(r"\$[\d,.]+", markdown_content)
        if dollar_matches:
            award_amount = dollar_matches[0]
            metrics.append(f"Award amount mentioned: {award_amount}")

        deadline_matches = re.findall(
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}",
            markdown_content,
            flags=re.IGNORECASE
        )
        if deadline_matches:
            deadline = deadline_matches[0]
            explicit_requirements.append(f"Deadline: {deadline}")
            metrics.append(f"Deadline mentioned: {deadline}")

        gpa_matches = re.findall(r"GPA[^0-9]*([0-4]\.\d{1,2})", markdown_content, flags=re.IGNORECASE)
        if gpa_matches:
            gpa_requirement = float(gpa_matches[0])
            explicit_requirements.append(f"GPA requirement: {gpa_requirement}")
            metrics.append(f"GPA requirement: {gpa_requirement}")

        for line in markdown_content.splitlines():
            if len(line) < 6:
                continue
            if re.search(r"\bmust\b|\brequired\b|\bshould\b|\bneed to\b", line, flags=re.IGNORECASE):
                explicit_instructions.append(line.strip())

        keywords = list({w for w in re.findall(r"[A-Za-z]{4,}", markdown_content)[:30]})

        return {
            "award_amount": award_amount,
            "deadline": deadline,
            "gpa_requirement": gpa_requirement,
            "metrics": metrics,
            "explicit_requirements": explicit_requirements,
            "explicit_instructions": explicit_instructions,
            "keywords": keywords
        }



    async def _run_firecrawl_extract(self, *, urls: List[str], prompt: str, schema: Dict[str, Any]) -> Any:
        """Run Firecrawl extract in a thread to avoid blocking the event loop."""
        return await asyncio.to_thread(self.firecrawl.extract, urls=urls, prompt=prompt, schema=schema)

    async def _run_firecrawl_search(self, *, query: str, limit: int) -> Any:
        """Run Firecrawl search in a thread."""
        # Request markdown and links content in search results
        params = {
            "query": query,
            "limit": limit,
            "scrape_options": {"formats": ["markdown", "links"]}
        }
        return await asyncio.to_thread(self.firecrawl.search, **params)

    async def _run_google_search(self, *, query: str, limit: int) -> List[Any]:
        """
        Run Google Custom Search.
        Returns a list of objects with .url and .markdown attributes.
        """
        if not self.google_api_key or not self.google_cse_id:
            print("    [WARNING] Google API credentials not found. Skipping search.")
            return []

        def _search():
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_cse_id,
                "q": query,
                "num": min(limit, 10)  # Google API max limit is 10
            }
            try:
                resp = requests.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for item in data.get("items", []):
                    # Create a simple object to match Firecrawl result structure
                    class GoogleResult:
                        def __init__(self, item):
                            self.url = item.get("link")
                            self.title = item.get("title")
                            self.description = item.get("snippet")
                            self.markdown = ""  # Empty content triggers fallback scraping
                            
                    results.append(GoogleResult(item))
                return results
            except Exception as e:
                print(f"    [ERROR] Google Search failed: {e}")
                return []

        return await asyncio.to_thread(_search)

    async def _run_firecrawl_scrape(self, *, url: str) -> Any:
        """Run Firecrawl scrape in a thread."""
        return await asyncio.to_thread(self.firecrawl.scrape, url=url, formats=['markdown'], only_main_content=True)

    async def _run_firecrawl_scrape(self, *, url: str) -> Any:
        """Run Firecrawl scrape in a thread."""
        return await asyncio.to_thread(self.firecrawl.scrape, url=url, formats=['markdown'], only_main_content=True)

    async def _validate_with_firecrawl(self, url: str, mode: str, content_hint: str = "") -> Optional[ValidationResult]:
        """Call Firecrawl LLM to classify and score a search hit."""
        prompt = f"""
You are validating a {mode} result for a scholarship. Only return JSON.
- content_type: essay/resume/profile/tip/stat/insight/warning
- validation_score: 0-1, confidence of relevance + truthfulness (>=0.95 required to keep)
- validation_reason: 1-2 sentences explaining the score
- winner_name, year (if applicable)
- key_takeaways: 3-5 concise takeaways
- credibility: short source credibility note

Base your answer ONLY on the provided page content. Do not guess beyond the page.
"""
        try:
            result = await self._run_firecrawl_extract(
                urls=[url],
                prompt=prompt,
                schema=ValidationResult.model_json_schema()
            )
            data = result.data if hasattr(result, "data") else None
            if isinstance(data, list):
                data = data[0] if data else None
            if not data:
                return None
            return ValidationResult.model_validate(data)
        except Exception as e:
            print(f"  ⚠ Validation failed for {url}: {e}")
            return None

    async def _validate_results(self, web_results: List[Any], mode: str, debug: bool = False) -> List[Any]:
        """Validate a batch of search results with Firecrawl LLM."""
        semaphore = asyncio.Semaphore(MAX_VALIDATION_CONCURRENCY)
        tasks = []
        seen_urls = set()

        async def _validate_single(res):
            if debug and len(seen_urls) == 0:
                print(f"      [DEBUG] First result object keys: {res.__dict__ if hasattr(res, '__dict__') else 'No __dict__'}")
            
            url = getattr(res, "url", "")
            
            if debug:
                print(f"      [DEBUG] Processing URL: {url}")
            
            if not url or url in seen_urls:
                if debug:
                    print(f"      [DEBUG] Skipping - empty or duplicate: {url}")
                return None
            seen_urls.add(url)

            # Skip social media URLs - they can't be scraped by Firecrawl
            social_media_domains = ["reddit.com", "linkedin.com", "facebook.com", "x.com", "twitter.com", "tiktok.com", "instagram.com"]
            if any(domain in url for domain in social_media_domains):
                if debug:
                    print(f"      [DEBUG] Skipping social media URL: {url}")
                return None

            content = getattr(res, "markdown", "") or ""
            
            if debug:
                print(f"      [DEBUG] Initial content length for {url}: {len(content)} chars")
            
            # If markdown is missing from search results, scrape the URL to get it
            if len(content) < MIN_CONTENT_LENGTH:
                if debug:
                    print(f"      [DEBUG] No markdown in search result for {url}, scraping...")
                try:
                    # Check if it's a Reddit URL - use Reddit API instead of Firecrawl
                    if "reddit.com" in url:
                        if debug:
                            print(f"      [DEBUG] Using Reddit API for {url}")
                        content = await self._scrape_reddit_url(url)
                    else:
                        async with semaphore:
                            scrape_result = await self._run_firecrawl_scrape(url=url)
                            content = getattr(scrape_result, "markdown", "") or ""
                    
                    if debug and content:
                        print(f"      [DEBUG] Scraped {len(content)} chars from {url}")
                except Exception as e:
                    if debug:
                        print(f"      [DEBUG] Scrape failed for {url}: {e}")
                    return None
            
            # Check content length again after potential scraping
            if len(content) < MIN_CONTENT_LENGTH:
                if debug:
                    print(f"      [DEBUG] Skipping {url} (too short: {len(content)})")
                return None

            if debug:
                print(f"      [DEBUG] About to validate {url} with {len(content)} chars of content")

            async with semaphore:
                vr = await self._validate_with_firecrawl(url, mode, content_hint=content)
            
            if debug:
                print(f"      [DEBUG] Validation returned: {vr}")
            
            if not vr:
                if debug:
                    print(f"      [DEBUG] Validation failed/null for {url}")
                return None
                
            if debug:
                print(f"      [DEBUG] {url} -> Score: {vr.validation_score} ({vr.validation_reason})")

            if vr.validation_score < VALIDATION_THRESHOLD:
                return None
            
            # Store the scraped content back into the result object for later use
            if hasattr(res, 'markdown'):
                res.markdown = content
            
            return res, vr

        for res in web_results:
            tasks.append(asyncio.create_task(_validate_single(res)))

        validated = []
        for pair in await asyncio.gather(*tasks):
            if pair:
                validated.append(pair)
        return validated

    async def scrape_official_page(self, url: str) -> OfficialScholarshipData:
        """
        Scrape official scholarship page using Firecrawl /extract endpoint

        Args:
            url: Scholarship webpage URL

        Returns:
            Structured scholarship data
        """
        print(f"  → Extracting scholarship data from: {url}")

        # Detailed extraction prompt for Firecrawl's internal LLM
        extraction_prompt = self._build_official_prompt()

        try:
            # Use Firecrawl's /extract endpoint with internal LLM
            result = await self._run_firecrawl_extract(
                urls=[url],
                prompt=extraction_prompt,
                schema=OfficialScholarshipData.model_json_schema()
            )

            # Firecrawl returns extracted data matching our schema
            # The result.data contains the extracted information
            extracted_data = result.data if hasattr(result, 'data') else None

            if not extracted_data:
                raise ValueError("Firecrawl extract returned no data")

            # Validate and create OfficialScholarshipData instance
            # If extracted_data is a list, take first item
            if isinstance(extracted_data, list):
                extracted_data = extracted_data[0] if extracted_data else {}

            extracted_data = extracted_data or {}
            extracted_data.setdefault("explicit_requirements", [])
            extracted_data.setdefault("explicit_instructions", [])
            extracted_data.setdefault("keywords", [])
            extracted_data.setdefault("metrics", [])

            # Ensure source_url is set
            if isinstance(extracted_data, dict):
                extracted_data['source_url'] = url
                official_data = OfficialScholarshipData.model_validate(extracted_data)
            else:
                # If it's already a Pydantic model
                official_data = extracted_data
                official_data.source_url = url

            print(f"  ✓ Extracted: {official_data.scholarship_name}")
            return official_data

        except Exception as e:
            print(f"  ⚠ Firecrawl extract failed: {e}")
            print(f"  → Falling back to basic scrape...")

            # Fallback: Use basic scrape if extract fails
            result = await self._run_firecrawl_scrape(url=url)

            markdown_content = result.markdown or ''
            fallback_fields = self._parse_markdown_fallback(markdown_content)

            # Extract scholarship name from first heading as fallback
            lines = markdown_content.split('\n')
            scholarship_name = "Unknown Scholarship"
            for line in lines:
                if line.startswith('# '):
                    scholarship_name = line.replace('# ', '').strip()
                    break

            # Return minimal data structure
            print(f"  ✓ Fallback scrape completed: {scholarship_name}")
            return OfficialScholarshipData(
                scholarship_name=scholarship_name,
                organization=None,
                keywords=fallback_fields.get("keywords", []),
                explicit_requirements=fallback_fields.get("explicit_requirements", []),
                explicit_instructions=fallback_fields.get("explicit_instructions", []),
                metrics=fallback_fields.get("metrics", []),
                primary_values=["Leadership", "Service", "Academic Excellence"],
                implicit_values=[],
                tone_indicators="Professional",
                eligibility_criteria=EligibilityCriteria(
                    gpa_requirement=fallback_fields.get("gpa_requirement", None)
                ),
                selection_emphasis=SelectionEmphasis(),
                award_amount=fallback_fields.get("award_amount"),
                num_awards=None,
                deadline=fallback_fields.get("deadline"),
                application_components=[],
                source_url=url
            )

    async def search_past_winner_items(
        self,
        scholarship_hint: str,
        domain: str,
        debug: bool = False
    ) -> List[PastWinnerItem]:
        """
        Search for past winner essays and resumes with LLM validation
        """
        print(f"  → Searching for past winner essays/resumes...")
        
        queries = [
            f'"{scholarship_hint}" winner essay (site:edu OR site:org OR PrepScholar OR IvyScholars) {SOCIAL_MEDIA_EXCLUSIONS}',
            f'"{scholarship_hint}" winning essay example (site:edu OR site:org) {SOCIAL_MEDIA_EXCLUSIONS}',
            f'"{scholarship_hint}" personal statement example PrepScholar OR IvyScholars {SOCIAL_MEDIA_EXCLUSIONS}',
            f'"{scholarship_hint}" finalist profile (site:edu OR site:org) {SOCIAL_MEDIA_EXCLUSIONS}',
            f'how to win "{scholarship_hint}" scholarship tips {SOCIAL_MEDIA_EXCLUSIONS}'
        ]

        items: List[PastWinnerItem] = []

        for query in queries:
            if debug:
                print(f"    [DEBUG] Query: {query}")
            try:
                # Use Google Search instead of Firecrawl Search
                web_results = await self._run_google_search(
                    query=query,
                    limit=4
                )

                if debug:
                    print(f"    [DEBUG] Found {len(web_results)} raw results")
                
                validated = await self._validate_results(web_results, mode="past winner essay or resume", debug=debug)

                for res, vr in validated:
                    content = getattr(res, "markdown", "") or ""
                    items.append(PastWinnerItem(
                        type=vr.content_type if vr.content_type in ["essay", "resume", "profile"] else "essay",
                        title=getattr(res, "title", "") or "Past Winner Content",
                        url=getattr(res, "url", "") or "",
                        content=content[:2000],
                        validation_score=vr.validation_score,
                        validation_reason=vr.validation_reason,
                        key_takeaways=vr.key_takeaways or [],
                        winner_name=vr.winner_name,
                        year=vr.year,
                        narrative_style=None
                    ))
            except Exception as e:
                print(f"    [ERROR] Search failed for query '{query}': {e}")
                continue

        print(f"  ✓ Found {len(items)} validated winner items")
        return items

    async def search_community_insights(
        self,
        scholarship_hint: str,
        debug: bool = False
    ) -> List[InsightData]:
        """
        Search educational sites for tips, stats, and insights

        Uses Firecrawl Search with in-prompt validation

        Args:
            scholarship_name: Name of scholarship

        Returns:
            List of validated insights
        """
        print(f"  → Searching for scholarship guidance and insights...")

        queries = [
            f'"{scholarship_hint}" scholarship application tips (PrepScholar OR IvyScholars OR site:edu) {SOCIAL_MEDIA_EXCLUSIONS}',
            f'"{scholarship_hint}" scholarship how to win guide (site:edu OR site:org) {SOCIAL_MEDIA_EXCLUSIONS}',
            f'"{scholarship_hint}" scholarship advice strategies PrepScholar {SOCIAL_MEDIA_EXCLUSIONS}',
            f'"{scholarship_hint}" scholarship what they look for (site:edu OR site:org) {SOCIAL_MEDIA_EXCLUSIONS}',
        ]

        insights = []

        for query in queries:
            if debug:
                print(f"    [DEBUG] Query: {query}")
            try:
                # Determine source from query
                if "reddit.com" in query:
                    source = "reddit"
                elif "linkedin.com" in query:
                    source = "linkedin"
                else:
                    source = "other"

                # Use Google Search instead of Firecrawl Search
                web_results = await self._run_google_search(
                    query=query,
                    limit=3
                )
                
                if debug:
                    print(f"    [DEBUG] Found {len(web_results)} raw results")

                validated = await self._validate_results(web_results, mode="tips or recommendations", debug=debug)

                for res, vr in validated:
                    content = getattr(res, "markdown", "") or ""
                    insights.append(InsightData(
                        source=source,
                        type=vr.content_type if vr.content_type in ["tip", "stat", "insight", "warning"] else "tip",
                        content=content[:800],
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

    async def deep_search_parallel(
        self,
        scholarship_url: str,
        scholarship_hint: str,
        debug: bool = False
    ) -> PastWinnerContext:
        """
        Execute parallel deep search for past winners and insights
        
        Args:
            scholarship_name: Name of scholarship
            scholarship_url: Official URL
            debug: Enable debug printing
        """
        """
        Execute parallel deep search for past winners and insights

        Runs 2 searches simultaneously:
        1. Past winner essays/resumes
        2. Reddit/LinkedIn insights

        Args:
            scholarship_name: Name of scholarship
            scholarship_url: Official URL

        Returns:
            PastWinnerContext with item + data structure
        """
        domain = urlparse(scholarship_url).netloc

        # Run searches in parallel
        items_task = asyncio.create_task(
            self.search_past_winner_items(scholarship_hint, domain, debug)
        )

        insights_task = asyncio.create_task(
            self.search_community_insights(scholarship_hint, debug)
        )

        # Wait for both
        items, insights = await asyncio.gather(items_task, insights_task)

        # Filter by validation threshold (>= 0.7)
        filtered_items = [item for item in items if item.validation_score >= 0.7]
        filtered_insights = [insight for insight in insights if insight.validation_score >= 0.7]

        # Create summary
        summary = SearchSummary(
            total_items_found=len(items),
            total_data_points_found=len(insights),
            items_after_validation=len(filtered_items),
            data_after_validation=len(filtered_insights),
            average_validation_score=(
                sum(i.validation_score for i in filtered_items + filtered_insights) /
                len(filtered_items + filtered_insights)
                if (filtered_items or filtered_insights) else 0.0
            ),
            search_queries_used=[
                f'Past winner essays/resumes (3 queries)',
                f'Reddit/LinkedIn insights (3 queries)'
            ]
        )

        return PastWinnerContext(
            item=filtered_items,
            data=filtered_insights,
            search_summary=summary
        )

    def format_combined_intelligence(
        self,
        official: OfficialScholarshipData,
        context: PastWinnerContext
    ) -> str:
        """
        Format combined intelligence for Decoder agent

        Args:
            official: Official scholarship data
            context: Past winner context

        Returns:
            Formatted text blob
        """
        sections = []

        # Official section
        sections.append(f"""
# {official.scholarship_name}

## Primary Values
{', '.join(official.primary_values)}

## Tone Indicators
{official.tone_indicators}

## Eligibility Criteria
- GPA Requirement: {official.eligibility_criteria.gpa_requirement or 'Not specified'}
- Grade Levels: {', '.join(official.eligibility_criteria.grade_levels) or 'Not specified'}
- Citizenship: {', '.join(official.eligibility_criteria.citizenship) or 'Not specified'}

## Award Details
- Amount: {official.award_amount or 'Not specified'}
- Number of Awards: {official.num_awards or 'Not specified'}
- Deadline: {official.deadline or 'Not specified'}
""")

        # Past winner items
        if context.item:
            sections.append("\n## Past Winner Examples\n")
            for item in context.item[:3]:  # Top 3
                sections.append(f"""
### {item.title}
- Type: {item.type}
- Validation Score: {item.validation_score:.0%}
- Key Takeaways: {', '.join(item.key_takeaways)}
- URL: {item.url}
""")

        # Community insights
        if context.data:
            sections.append("\n## Community Insights\n")
            for insight in context.data[:3]:  # Top 3
                sections.append(f"""
### {insight.type.upper()} from {insight.source}
- {insight.content[:200]}...
- Credibility: {insight.credibility}
- Validation Score: {insight.validation_score:.0%}
""")

        return "\n".join(sections)

    async def run(self, scholarship_url: str, debug: bool = False) -> Dict[str, Any]:
        """
        Execute complete Scout workflow with SEQUENTIAL execution for accuracy
        
        1. Scrape Official Page -> Get REAL Scholarship Name
        2. Deep Search -> Use REAL Name for queries
        
        Args:
            scholarship_url: URL of the scholarship
            debug: If True, print detailed validation info
            
        Returns:
            Dict containing ScoutIntelligence data
        """
        print("=" * 60)
        print("🔍 Scout Agent: Starting intelligence gathering...")
        print("=" * 60)

        # STEP 1: Official Scrape (Critical for accurate name)
        print("\n[STEP 1] Scraping official page to identify scholarship...")
        official_data = await self.scrape_official_page(scholarship_url)
        
        scholarship_name = official_data.scholarship_name
        print(f"  ✓ Identified: {scholarship_name}")
        
        # STEP 2: Deep Search (Using accurate name)
        print(f"\n[STEP 2] Starting deep search for '{scholarship_name}'...")
        
        past_winner_context = await self.deep_search_parallel(
            scholarship_url=scholarship_url,
            scholarship_hint=scholarship_name,
            debug=debug
        )

        # Format combined intelligence
        combined_text = self.format_combined_intelligence(
            official_data,
            past_winner_context
        )

        # Build final output
        intelligence = ScoutIntelligence(
            official=official_data,
            past_winner_context=past_winner_context,
            combined_text=combined_text
        )

        print("\n" + "=" * 60)
        print("✅ Scout Agent: Intelligence gathering complete!")
        print(f"   - Official data: ✓")
        print(f"   - Past winner items: {len(past_winner_context.item)}")
        print(f"   - Community insights: {len(past_winner_context.data)}")
        print(f"   - Average validation score: {past_winner_context.search_summary.average_validation_score:.0%}")
        print("=" * 60)

        return {
            "scholarship_intelligence": intelligence.model_dump(),
            "combined_text": combined_text
        }
