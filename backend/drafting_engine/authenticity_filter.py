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
    
    async def check_authenticity(self, draft: str) -> Dict[str, Any]:
        """
        Score draft on authenticity metrics
        
        Args:
            draft: Essay text to evaluate
        
        Returns:
            Dictionary with overall score, specific issues, and suggestions
        """
        
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
        
        system_prompt = """
        You are an expert at detecting AI-generated writing.
        Analyze text for patterns that indicate artificial generation.
        Be thorough and provide specific evidence.
        Return only valid JSON.
        """
        
        user_message = f"""
        Analyze this essay for AI-generated writing patterns.
        
        TEXT:
        {text}
        
        Check for these AI tells:
        1. **Overly perfect structure**: Too balanced, every paragraph same length
        2. **Lack of personal voice**: No quirks, idiosyncrasies, or natural speech patterns
        3. **Generic transitions**: Overuse of "Moreover", "Furthermore", "Additionally", "In addition"
        4. **Hedging language**: Excessive "quite", "rather", "somewhat", "fairly", "relatively"
        5. **Thesaurus syndrome**: Suspiciously varied vocabulary, unnatural word choices
        6. **List-like structure**: Everything in threes or numbered patterns
        7. **Lack of contractions**: Too formal, no natural contractions
        8. **Perfect grammar**: No minor imperfections that real students have
        9. **Abstract over concrete**: Vague concepts instead of specific details
        10. **Emotional distance**: Discussing personal topics without genuine emotion
        
        Score 0-10:
        - 0-2: Definitely human-written, natural voice
        - 3-4: Mostly human, minor AI editing
        - 5-6: Mixed, significant AI assistance
        - 7-8: Likely AI-generated with human editing
        - 9-10: Obviously AI-generated
        
        Provide analysis as JSON:
        {{
            "ai_likelihood_score": 0-10,
            "detected_patterns": [
                {{
                    "pattern": "Pattern name",
                    "examples": ["specific example 1", "specific example 2"],
                    "severity": "high" | "medium" | "low"
                }}
            ],
            "human_indicators": ["things that suggest human authorship"],
            "overall_assessment": "Brief summary of findings",
            "confidence": "How confident are you in this assessment (low/medium/high)"
        }}
        """
        
        try:
            ai_analysis_json = await self.analysis_llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            return json.loads(ai_analysis_json)
        
        except json.JSONDecodeError as e:
            print(f"Error parsing AI pattern detection: {e}")
            return {
                "ai_likelihood_score": 5.0,
                "detected_patterns": [],
                "human_indicators": [],
                "overall_assessment": "Unable to complete analysis",
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
        generic_count = checks['generic_phrases']['count']
        score -= min(2.0, generic_count * 0.3)
        
        # Deduct for passive voice (max -1.5 points)
        passive_pct = checks['passive_voice']['percentage']
        score -= min(1.5, passive_pct / 20)
        
        # Deduct for clichés (max -1.5 points)
        cliche_count = checks['cliche_detector']['count']
        score -= min(1.5, cliche_count * 0.5)
        
        # Deduct for low specificity (max -2 points)
        specificity = checks['specificity_score']['score']
        score -= max(0, (5 - specificity) * 0.4)
        
        # Deduct for AI patterns (max -3 points)
        ai_score = checks['ai_patterns'].get('ai_likelihood_score', 5)
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
        
        system_prompt = """
        You are an expert essay writing coach.
        Provide specific, actionable suggestions to improve essay authenticity.
        Focus on concrete changes, not general advice.
        """
        
        user_message = f"""
        Based on these authenticity issues, provide specific improvement suggestions:
        
        ISSUES DETECTED:
        {json.dumps(checks, indent=2)}
        
        ESSAY EXCERPT:
        {draft[:500]}...
        
        Provide 5-7 specific, actionable suggestions as a JSON array:
        [
            "Replace '[generic phrase]' with a specific detail about...",
            "Change passive 'was implemented' to active 'I implemented...'",
            "Add a concrete number or metric to support the claim about..."
        ]
        
        Make suggestions specific to this essay, not general advice.
        """
        
        try:
            suggestions_json = await self.analysis_llm.call(
                system_prompt=system_prompt,
                user_message=user_message
            )
            
            return json.loads(suggestions_json)
        
        except json.JSONDecodeError:
            # Fallback to rule-based suggestions
            return self._generate_fallback_suggestions(checks)
    
    def _generate_fallback_suggestions(self, checks: Dict[str, Any]) -> List[str]:
        """Generate basic suggestions if LLM fails"""
        suggestions = []
        
        if checks['generic_phrases']['count'] > 0:
            suggestions.append(f"Remove {checks['generic_phrases']['count']} generic phrases and replace with specific details")
        
        if checks['passive_voice']['percentage'] > 15:
            suggestions.append("Convert passive voice to active voice for stronger impact")
        
        if checks['cliche_detector']['count'] > 0:
            suggestions.append("Replace clichés with original, specific descriptions")
        
        if checks['specificity_score']['score'] < 5:
            suggestions.append("Add more concrete numbers, names, and specific details")
        
        if checks['ai_patterns'].get('ai_likelihood_score', 0) > 6:
            suggestions.append("Make writing less polished and more natural/conversational")
        
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
        
        system_prompt = """
        You are an expert at making essays sound authentically student-written.
        Your goal is to maintain all content while making the voice more natural and genuine.
        Preserve all specific facts, achievements, and examples exactly.
        """
        
        user_message = f"""
        This essay is too polished and AI-like. Make it sound like a real college student wrote it.
        
        ORIGINAL ESSAY:
        {draft}
        
        SPECIFIC ISSUES TO ADDRESS:
        {json.dumps(issues, indent=2)}
        
        HUMANIZATION TECHNIQUES TO APPLY:
        1. **Add personality**: Include natural asides, personal reflections, or authentic reactions
        2. **Vary rhythm**: Mix short, punchy sentences with longer, flowing ones
        3. **Use contractions**: "I'm" instead of "I am", "wasn't" instead of "was not"
        4. **Add sensory details**: What did you see, hear, feel in key moments?
        5. **Minor imperfections**: Occasional sentences that aren't perfectly balanced
        6. **Conversational tone**: Write like you're explaining to a friend, not a committee
        7. **Specific over abstract**: Replace vague concepts with concrete examples
        8. **Show emotion**: Let genuine feelings come through naturally
        
        CRITICAL RULES:
        - Keep ALL specific facts, numbers, achievements, and examples exactly as written
        - Maintain the same stories and experiences
        - Preserve the same length (±50 words)
        - Don't change the fundamental message or content
        - Only adjust style, voice, and naturalness
        
        Return ONLY the humanized essay, no explanations or notes.
        """
        
        humanized = await self.humanization_llm.call(
            system_prompt=system_prompt,
            user_message=user_message
        )
        
        return humanized.strip()
    
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
        
        if checks['generic_phrases']['severity'] == 'high':
            critical.append("Too many generic phrases - essay sounds templated")
        
        if checks['ai_patterns'].get('ai_likelihood_score', 0) > 7:
            critical.append("High AI likelihood - needs significant humanization")
        
        if checks['specificity_score']['severity'] == 'high':
            critical.append("Lacks specific details - too vague and general")
        
        if checks['passive_voice']['severity'] == 'high':
            critical.append("Excessive passive voice - weakens impact")
        
        return critical