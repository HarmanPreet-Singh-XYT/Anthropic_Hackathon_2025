"""
backend/drafting_engine/authenticity_filter.py
Evaluates and enhances essay authenticity, filtering generic and AI-like patterns
"""

import json
import re
from typing import Dict, Any, List
from utils.llm_client import create_llm_client


class AuthenticityFilter:
    """
    Detects and corrects inauthenticity in scholarship essays
    """
    
    def __init__(self, temperature: float = 0.4):
        """
        Initialize AuthenticityFilter with LLM client
        
        Args:
            temperature: Sampling temperature for analysis (lower for consistent detection)
        """
        self.analysis_llm = create_llm_client(temperature=0.3)  # Consistent analysis
        self.humanization_llm = create_llm_client(temperature=0.8)  # Creative rewriting
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean LLM response to extract pure JSON
        """
        if not response:
            return "{}"
        
        # Remove markdown code blocks
        response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'^```\s*', '', response, flags=re.MULTILINE)
        response = re.sub(r'\s*```$', '', response, flags=re.MULTILINE)
        
        # Try to find JSON object or array
        json_match = re.search(r'[\{$$].*[\}$$]', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return response.strip()
    
    async def check_authenticity(self, draft: str) -> Dict[str, Any]:
        """
        Score draft on authenticity metrics
        
        Args:
            draft: Essay text to evaluate
        
        Returns:
            Dictionary with overall score, specific issues, and suggestions
        """
        
        print("    🔍 Running authenticity checks...")
        
        # Run all authenticity checks
        checks = {
            "generic_phrases": self.detect_generic_phrases(draft),
            "passive_voice": self.count_passive_voice(draft),
            "cliche_detector": self.find_cliches(draft),
            "specificity_score": self.measure_specificity(draft),
            "ai_patterns": await self.detect_ai_patterns(draft),
            "repetition_issues": self.detect_repetition(draft),
            "vocabulary_naturalness": self.check_vocabulary_naturalness(draft)
        }
        
        # Calculate overall authenticity score
        overall_score = self.calculate_authenticity_score(checks)
        
        print(f"    📊 Authenticity score: {overall_score}/10")
        
        # Generate specific improvement suggestions
        suggestions = await self.generate_improvements(checks, draft)
        
        return {
            "score": overall_score,
            "grade": self._score_to_grade(overall_score),
            "issues": checks,
            "suggestions": suggestions,
            "critical_issues": self._identify_critical_issues(checks),
            "pass_threshold": overall_score >= 7.0
        }
    
    def detect_generic_phrases(self, text: str) -> Dict[str, Any]:
        """
        Flag overused scholarship essay phrases
        
        Args:
            text: Essay text
        
        Returns:
            Dictionary with found phrases and their locations
        """
        
        generic_red_flags = [
            "from a young age",
            "from an early age",
            "throughout my life",
            "ever since I was",
            "I have always been passionate",
            "I have always had a passion",
            "made me realize",
            "taught me valuable lessons",
            "taught me the importance of",
            "stepping stone",
            "journey of self-discovery",
            "outside my comfort zone",
            "made me who I am today",
            "shaped me into",
            "I am writing to apply",
            "I am honored to apply",
            "given the opportunity",
            "it would be an honor",
            "I strongly believe",
            "in today's society",
            "in today's world",
            "growing up",
            "since childhood"
        ]
        
        found_phrases = []
        text_lower = text.lower()
        
        for phrase in generic_red_flags:
            if phrase.lower() in text_lower:
                # Find all occurrences
                count = text_lower.count(phrase.lower())
                # Extract context (30 chars before and after)
                matches = []
                start = 0
                while True:
                    pos = text_lower.find(phrase.lower(), start)
                    if pos == -1:
                        break
                    context_start = max(0, pos - 30)
                    context_end = min(len(text), pos + len(phrase) + 30)
                    context = text[context_start:context_end]
                    matches.append(context)
                    start = pos + 1
                
                found_phrases.append({
                    "phrase": phrase,
                    "count": count,
                    "contexts": matches[:3]  # Limit to first 3 occurrences
                })
        
        return {
            "found": found_phrases,
            "count": len(found_phrases),
            "severity": "high" if len(found_phrases) > 3 else "medium" if len(found_phrases) > 0 else "none"
        }
    
    def count_passive_voice(self, text: str) -> Dict[str, Any]:
        """
        Count passive voice constructions
        
        Args:
            text: Essay text
        
        Returns:
            Passive voice statistics
        """
        
        # Common passive voice patterns
        passive_patterns = [
            r'\b(is|are|was|were|be|been|being)\s+\w+ed\b',
            r'\b(is|are|was|were|be|been|being)\s+\w+en\b'
        ]
        
        passive_instances = []
        for pattern in passive_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 30)
                context_end = min(len(text), match.end() + 30)
                context = text[context_start:context_end]
                passive_instances.append({
                    "match": match.group(),
                    "context": context
                })
        
        # Count total sentences (approximate)
        sentence_count = len(re.findall(r'[.!?]+', text))
        passive_percentage = (len(passive_instances) / sentence_count * 100) if sentence_count > 0 else 0
        
        return {
            "count": len(passive_instances),
            "percentage": round(passive_percentage, 1),
            "instances": passive_instances[:5],  # First 5 examples
            "severity": "high" if passive_percentage > 30 else "medium" if passive_percentage > 15 else "low"
        }
    
    def find_cliches(self, text: str) -> Dict[str, Any]:
        """
        Detect common essay clichés
        
        Args:
            text: Essay text
        
        Returns:
            Found clichés with severity
        """
        
        cliche_list = [
            "at the end of the day",
            "think outside the box",
            "pushed me to my limits",
            "blood, sweat, and tears",
            "rose to the challenge",
            "face my fears",
            "follow my dreams",
            "pursue my passion",
            "make a difference",
            "change the world",
            "give back to the community",
            "reach for the stars",
            "sky is the limit",
            "jack of all trades",
            "hit the ground running",
            "learn the ropes",
            "trial and error",
            "took the initiative",
            "went above and beyond"
        ]
        
        found_cliches = []
        text_lower = text.lower()
        
        for cliche in cliche_list:
            if cliche.lower() in text_lower:
                found_cliches.append(cliche)
        
        return {
            "found": found_cliches,
            "count": len(found_cliches),
            "severity": "high" if len(found_cliches) > 2 else "medium" if len(found_cliches) > 0 else "none"
        }
    
    def measure_specificity(self, text: str) -> Dict[str, Any]:
        """
        Measure how specific vs. vague the writing is
        
        Args:
            text: Essay text
        
        Returns:
            Specificity metrics
        """
        
        # Count specific indicators
        numbers = len(re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?%?\b', text))
        proper_nouns = len(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text))
        
        # Count vague words
        vague_words = [
            "many", "some", "several", "various", "numerous", "multiple",
            "things", "stuff", "aspects", "areas", "ways", "people",
            "good", "bad", "nice", "great", "amazing", "awesome",
            "very", "really", "quite", "pretty", "somewhat"
        ]
        
        vague_count = sum(text.lower().count(f" {word} ") for word in vague_words)
        
        word_count = len(text.split())
        specificity_score = min(10, (numbers * 0.5 + proper_nouns * 0.3 - vague_count * 0.1) / word_count * 100)
        specificity_score = max(0, specificity_score)
        
        return {
            "score": round(specificity_score, 1),
            "numbers_count": numbers,
            "proper_nouns_count": proper_nouns,
            "vague_words_count": vague_count,
            "severity": "low" if specificity_score > 6 else "medium" if specificity_score > 3 else "high"
        }
    
    def detect_repetition(self, text: str) -> Dict[str, Any]:
        """
        Detect repetitive words and phrases
        
        Args:
            text: Essay text
        
        Returns:
            Repetition analysis
        """
        
        # Tokenize into words (excluding common words)
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        common_words = {'that', 'this', 'with', 'from', 'have', 'been', 'were', 'their', 'what', 'when', 'which', 'about', 'would', 'there', 'could', 'these', 'those', 'through', 'where'}
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in common_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Find overused words
        overused = [(word, count) for word, count in word_freq.items() if count > 5]
        overused.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "overused_words": overused[:10],
            "severity": "high" if len(overused) > 5 else "medium" if len(overused) > 2 else "low"
        }
    
    def check_vocabulary_naturalness(self, text: str) -> Dict[str, Any]:
        """
        Check for unnatural vocabulary choices (thesaurus syndrome)
        
        Args:
            text: Essay text
        
        Returns:
            Vocabulary naturalness assessment
        """
        
        # Words that are often used unnaturally by AI or thesaurus users
        unnatural_words = [
            "utilize", "endeavor", "facilitate", "ascertain", "commence",
            "subsequent", "prior to", "in order to", "due to the fact that",
            "in spite of the fact that", "at this point in time", "plethora",
            "myriad", "quintessential", "paramount", "instrumental"
        ]
        
        found_unnatural = []
        text_lower = text.lower()
        
        for word in unnatural_words:
            if word in text_lower:
                found_unnatural.append(word)
        
        return {
            "found": found_unnatural,
            "count": len(found_unnatural),
            "severity": "high" if len(found_unnatural) > 3 else "medium" if len(found_unnatural) > 0 else "none"
        }
    
    async def detect_ai_patterns(self, text: str) -> Dict[str, Any]:
        """
        Identify telltale AI writing patterns using LLM
        
        Args:
            text: Essay text
        
        Returns:
            AI pattern detection results with score and examples
        """
        
        system_prompt = """You are an expert at detecting AI-generated writing. Analyze text for patterns that indicate artificial generation. Be thorough and provide specific evidence. Return ONLY valid JSON with no markdown or additional text."""
        
        # Truncate text if too long
        text_preview = text if len(text) < 1500 else text[:1500] + "..."
        
        user_message = f"""Analyze this essay for AI-generated writing patterns.

TEXT:
{text_preview}

Check for AI tells:
1. Overly perfect structure
2. Lack of personal voice
3. Generic transitions ("Moreover", "Furthermore", "Additionally")
4. Hedging language ("quite", "rather", "somewhat")
5. Thesaurus syndrome
6. List-like structure
7. Lack of contractions
8. Perfect grammar
9. Abstract over concrete
10. Emotional distance

Score 0-10 (0=definitely human, 10=obviously AI)

Return ONLY valid JSON (no markdown):
{{
    "ai_likelihood_score": 5.0,
    "detected_patterns": [
        {{
            "pattern": "Pattern name",
            "examples": ["example 1", "example 2"],
            "severity": "high"
        }}
    ],
    "human_indicators": ["things suggesting human authorship"],
    "overall_assessment": "Brief summary",
    "confidence": "low/medium/high"
}}"""
        
        try:
            ai_analysis_json = await self.analysis_llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            print(f"    [DEBUG] AI pattern response length: {len(ai_analysis_json) if ai_analysis_json else 0}")
            
            if not ai_analysis_json or not ai_analysis_json.strip():
                print("    [WARNING] Empty AI pattern response")
                return self._get_default_ai_analysis()
            
            cleaned_json = self._clean_json_response(ai_analysis_json)
            ai_analysis = json.loads(cleaned_json)
            
            # Validate ai_likelihood_score
            if 'ai_likelihood_score' not in ai_analysis or not isinstance(ai_analysis.get('ai_likelihood_score'), (int, float)):
                print("    [WARNING] Invalid ai_likelihood_score")
                ai_analysis['ai_likelihood_score'] = 5.0
            
            # Ensure required fields exist
            if 'detected_patterns' not in ai_analysis:
                ai_analysis['detected_patterns'] = []
            if 'human_indicators' not in ai_analysis:
                ai_analysis['human_indicators'] = ["Natural voice present"]
            if 'overall_assessment' not in ai_analysis:
                ai_analysis['overall_assessment'] = "Analysis complete"
            if 'confidence' not in ai_analysis:
                ai_analysis['confidence'] = "medium"
            
            return ai_analysis
        
        except json.JSONDecodeError as e:
            print(f"    [ERROR] Failed to parse AI pattern detection: {e}")
            print(f"    [ERROR] Response: {ai_analysis_json[:300] if ai_analysis_json else 'EMPTY'}")
            return self._get_default_ai_analysis()
        
        except Exception as e:
            print(f"    [ERROR] Unexpected error in AI pattern detection: {e}")
            return self._get_default_ai_analysis()
    
    def _get_default_ai_analysis(self) -> Dict[str, Any]:
        """Return default AI analysis when detection fails"""
        return {
            "ai_likelihood_score": 5.0,
            "detected_patterns": [],
            "human_indicators": ["Analysis unavailable"],
            "overall_assessment": "Unable to complete AI detection",
            "confidence": "low"
        }
    
    def calculate_authenticity_score(self, checks: Dict[str, Any]) -> float:
        """
        Calculate overall authenticity score from individual checks
        
        Args:
            checks: Dictionary of all authenticity checks
        
        Returns:
            Overall score 0-10 (10 = most authentic)
        """
        
        # Start with perfect score
        score = 10.0
        
        # Deduct for generic phrases (max -2 points)
        generic_count = checks.get('generic_phrases', {}).get('count', 0)
        score -= min(2.0, generic_count * 0.3)
        
        # Deduct for passive voice (max -1.5 points)
        passive_pct = checks.get('passive_voice', {}).get('percentage', 0)
        score -= min(1.5, passive_pct / 20)
        
        # Deduct for clichés (max -1.5 points)
        cliche_count = checks.get('cliche_detector', {}).get('count', 0)
        score -= min(1.5, cliche_count * 0.5)
        
        # Deduct for low specificity (max -2 points)
        specificity = checks.get('specificity_score', {}).get('score', 5)
        score -= max(0, (5 - specificity) * 0.4)
        
        # Deduct for AI patterns (max -3 points)
        ai_score = checks.get('ai_patterns', {}).get('ai_likelihood_score', 5)
        score -= (ai_score / 10) * 3.0
        
        return max(0.0, round(score, 1))
    
    async def generate_improvements(
        self,
        checks: Dict[str, Any],
        draft: str
    ) -> List[str]:
        """
        Generate specific improvement suggestions based on detected issues
        
        Args:
            checks: Authenticity check results
            draft: Original essay text
        
        Returns:
            List of actionable suggestions
        """
        
        system_prompt = """You are an expert essay writing coach. Provide specific, actionable suggestions to improve essay authenticity. Focus on concrete changes, not general advice. Return ONLY a JSON array of strings with no markdown."""
        
        # Truncate draft for prompt
        draft_preview = draft[:500] if len(draft) > 500 else draft
        
        # Simplify checks for prompt
        issues_summary = {
            "generic_phrases_count": checks.get('generic_phrases', {}).get('count', 0),
            "passive_voice_percentage": checks.get('passive_voice', {}).get('percentage', 0),
            "cliche_count": checks.get('cliche_detector', {}).get('count', 0),
            "specificity_score": checks.get('specificity_score', {}).get('score', 5),
                        "ai_likelihood": checks.get('ai_patterns', {}).get('ai_likelihood_score', 5)
        }
        
        user_message = f"""Based on these authenticity issues, provide specific improvement suggestions:

ISSUES DETECTED:
{json.dumps(issues_summary, indent=2)}

ESSAY EXCERPT:
{draft_preview}...

Provide 5-7 specific, actionable suggestions as a JSON array (no markdown):
[
    "Replace 'from a young age' with a specific age and context",
    "Change passive 'was implemented' to active 'I implemented'",
    "Add a concrete number to support the claim about membership growth"
]

Make suggestions specific to this essay, not general advice."""
        
        try:
            suggestions_json = await self.analysis_llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            print(f"    [DEBUG] Suggestions response length: {len(suggestions_json) if suggestions_json else 0}")
            
            if not suggestions_json or not suggestions_json.strip():
                print("    [WARNING] Empty suggestions response")
                return self._generate_fallback_suggestions(checks)
            
            cleaned_json = self._clean_json_response(suggestions_json)
            suggestions = json.loads(cleaned_json)
            
            # Validate it's a list
            if not isinstance(suggestions, list):
                print("    [WARNING] Suggestions not a list")
                return self._generate_fallback_suggestions(checks)
            
            return suggestions
        
        except json.JSONDecodeError as e:
            print(f"    [ERROR] Failed to parse suggestions: {e}")
            print(f"    [ERROR] Response: {suggestions_json[:300] if suggestions_json else 'EMPTY'}")
            return self._generate_fallback_suggestions(checks)
        
        except Exception as e:
            print(f"    [ERROR] Unexpected error generating suggestions: {e}")
            return self._generate_fallback_suggestions(checks)
    
    def _generate_fallback_suggestions(self, checks: Dict[str, Any]) -> List[str]:
        """Generate basic suggestions if LLM fails"""
        suggestions = []
        
        generic_count = checks.get('generic_phrases', {}).get('count', 0)
        if generic_count > 0:
            suggestions.append(f"Remove {generic_count} generic phrase(s) and replace with specific details")
        
        passive_pct = checks.get('passive_voice', {}).get('percentage', 0)
        if passive_pct > 15:
            suggestions.append("Convert passive voice to active voice for stronger impact")
        
        cliche_count = checks.get('cliche_detector', {}).get('count', 0)
        if cliche_count > 0:
            suggestions.append("Replace clichés with original, specific descriptions")
        
        specificity_score = checks.get('specificity_score', {}).get('score', 5)
        if specificity_score < 5:
            suggestions.append("Add more concrete numbers, names, and specific details")
        
        ai_score = checks.get('ai_patterns', {}).get('ai_likelihood_score', 5)
        if ai_score > 6:
            suggestions.append("Make writing less polished and more natural/conversational")
        
        if not suggestions:
            suggestions.append("Review essay for authenticity and specific details")
        
        return suggestions
    
    async def humanize_draft(
        self,
        draft: str,
        issues: Dict[str, Any]
    ) -> str:
        """
        Make AI-generated or overly polished text more authentic
        
        Args:
            draft: Essay text to humanize
            issues: Detected authenticity issues
        
        Returns:
            Humanized essay text
        """
        
        print("    🤖➡️👤 Humanizing draft...")
        
        system_prompt = """You are an expert at making essays sound authentically student-written. Your goal is to maintain all content while making the voice more natural and genuine. Preserve all specific facts, achievements, and examples exactly. Return ONLY the humanized essay with no preamble or explanation."""
        
        # Simplify issues for prompt
        issues_summary = {
            "authenticity_score": issues.get('score', 7.0),
            "generic_phrases": issues.get('issues', {}).get('generic_phrases', {}).get('count', 0),
            "ai_likelihood": issues.get('issues', {}).get('ai_patterns', {}).get('ai_likelihood_score', 5),
            "cliches": issues.get('issues', {}).get('cliche_detector', {}).get('count', 0)
        }
        
        user_message = f"""This essay is too polished and AI-like. Make it sound like a real college student wrote it.

ORIGINAL ESSAY:
{draft}

SPECIFIC ISSUES TO ADDRESS:
{json.dumps(issues_summary, indent=2)}

HUMANIZATION TECHNIQUES:
1. Add personality: Include natural asides, personal reflections
2. Vary rhythm: Mix short and long sentences
3. Use contractions: "I'm" not "I am", "wasn't" not "was not"
4. Add sensory details: What did you see, hear, feel?
5. Minor imperfections: Occasional sentences that aren't perfectly balanced
6. Conversational tone: Write like explaining to a friend
7. Specific over abstract: Replace vague concepts with concrete examples
8. Show emotion: Let genuine feelings come through naturally

CRITICAL RULES:
- Keep ALL specific facts, numbers, achievements, and examples exactly as written
- Maintain the same stories and experiences
- Preserve the same length (±50 words)
- Don't change the fundamental message or content
- Only adjust style, voice, and naturalness

Return ONLY the humanized essay, no explanations or notes."""
        
        try:
            humanized = await self.humanization_llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            if not humanized or not humanized.strip():
                print("    [WARNING] Empty humanization response, using original")
                return draft
            
            # Clean any metadata or labels
            humanized = re.sub(r'^(HUMANIZED|ESSAY|REVISED):\s*', '', humanized, flags=re.IGNORECASE)
            humanized = re.sub(r'^\*\*.*?\*\*:?\s*', '', humanized, flags=re.MULTILINE)
            humanized = re.sub(r'^#{1,6}\s+.*$', '', humanized, flags=re.MULTILINE)
            
            word_count_diff = abs(len(humanized.split()) - len(draft.split()))
            if word_count_diff > len(draft.split()) * 0.2:  # More than 20% change
                print(f"    [WARNING] Humanization changed length significantly ({word_count_diff} words)")
            
            print(f"    ✅ Humanization complete")
            return humanized.strip()
            
        except Exception as e:
            print(f"    [ERROR] Humanization failed: {e}")
            print("    [FALLBACK] Using original draft")
            return draft
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 9.0:
            return "A+ (Excellent authenticity)"
        elif score >= 8.0:
            return "A (Very authentic)"
        elif score >= 7.0:
            return "B (Good, minor issues)"
        elif score >= 6.0:
            return "C (Needs improvement)"
        else:
            return "D (Major authenticity concerns)"
    
    def _identify_critical_issues(self, checks: Dict[str, Any]) -> List[str]:
        """Identify most critical issues requiring immediate attention"""
        critical = []
        
        generic_severity = checks.get('generic_phrases', {}).get('severity', 'none')
        if generic_severity == 'high':
            critical.append("Too many generic phrases - essay sounds templated")
        
        ai_score = checks.get('ai_patterns', {}).get('ai_likelihood_score', 0)
        if ai_score > 7:
            critical.append("High AI likelihood - needs significant humanization")
        
        specificity_severity = checks.get('specificity_score', {}).get('severity', 'low')
        if specificity_severity == 'high':
            critical.append("Lacks specific details - too vague and general")
        
        passive_severity = checks.get('passive_voice', {}).get('severity', 'low')
        if passive_severity == 'high':
            critical.append("Excessive passive voice - weakens impact")
        
        return critical