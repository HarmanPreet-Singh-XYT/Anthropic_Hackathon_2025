# Agent Input/Output Specifications

This document details the input and output data structures for every node in the [ScholarshipWorkflow](file:///Applications/Development/Anthropic_Hack/backend/workflows/scholarship_graph.py#44-340).

## 1. Agent A: Scout (Ingestion)
**Purpose:** Scrapes scholarship URL and gathers intelligence on past winners.

*   **Input:**
    *   `scholarship_url` (str): URL of the scholarship page.
    *   Example: `"https://www.coca-colascholarsfoundation.org/apply/"`

*   **Output:**
    *   `scholarship_intelligence` (dict): Structured data including official requirements and past winner insights.
    *   `combined_text` (str): A consolidated text blob of all findings for downstream analysis.
    *   Example:
        ```json
        {
          "scholarship_intelligence": {
            "official": {
              "scholarship_name": "Coca-Cola Scholars Program",
              "organization": "Coca-Cola Scholars Foundation",
              "metrics": ["$20,000 award", "150 awards"],
              "explicit_requirements": ["High school senior", "US Citizen"]
            },
            "past_winner_context": { ... }
          },
          "combined_text": "OFFICIAL SCHOLARSHIP DATA...\nPAST WINNER INSIGHTS..."
        }
        ```

## 2. Agent B: Profiler (Ingestion)
**Purpose:** Parses resume PDF and stores embeddings in Vector Store.

*   **Input:**
    *   `resume_pdf_path` (str): Path to the student's resume PDF.
    *   Example: `"/path/to/student_resume.pdf"`

*   **Output:**
    *   [text](file:///Applications/Development/Anthropic_Hack/backend/agents/profiler.py#49-100) (str): Full extracted text from the resume.
    *   *Side Effect:* Stores resume chunks in ChromaDB vector store.
    *   Example:
        ```json
        {
          "text": "John Doe\nEducation: Anytown High School..."
        }
        ```

## 3. Agent C: Decoder (Analysis)
**Purpose:** Analyzes scholarship text to extract values, weights, and tone.

*   **Input:**
    *   `scholarship_text` (str): The `combined_text` from Scout.

*   **Output:**
    *   `decoder_analysis` (dict): JSON object with analysis results.
    *   Example:
        ```json
        {
          "primary_values": ["Leadership", "Service", "Grit"],
          "hidden_weights": {
            "Leadership": 0.4,
            "Service": 0.3,
            "Academic Excellence": 0.3
          },
          "tone": "Inspirational and community-focused",
          "missing_evidence_query": "Tell us about a time you led a community initiative."
        }
        ```

## 4. Agent D: Matchmaker (Analysis)
**Purpose:** Compares resume to scholarship values and identifies gaps.

*   **Input:**
    *   `decoder_output` (dict): The output from Agent C.

*   **Output:**
    *   [match_score](file:///Applications/Development/Anthropic_Hack/backend/agents/matchmaker.py#192-219) (float): 0.0 to 1.0 relevance score.
    *   `evidence` (dict): Snippets from resume matching each criteria.
    *   [gaps](file:///Applications/Development/Anthropic_Hack/backend/agents/matchmaker.py#220-247) (list): List of criteria with low evidence.
    *   `trigger_interview` (bool): True if score < 0.7 or gaps exist.
    *   Example:
        ```json
        {
          "match_score": 0.65,
          "evidence": {
            "Leadership": ["President of Student Council..."],
            "Service": []
          },
          "gaps": ["Service"],
          "trigger_interview": true
        }
        ```

## 5. Agent E: Interviewer (Human-in-the-Loop)
**Purpose:** Generates a question to fill the highest-priority gap.

*   **Input:**
    *   [resume_text](file:///Applications/Development/Anthropic_Hack/backend/utils/pdf_parser.py#128-164) (str): Full resume text.
    *   [gaps](file:///Applications/Development/Anthropic_Hack/backend/agents/matchmaker.py#220-247) (list): List of missing criteria (e.g., `["Service"]`).
    *   `weights` (dict): Criteria weights.

*   **Output:**
    *   [question](file:///Applications/Development/Anthropic_Hack/backend/agents/interviewer.py#40-93) (str): The generated interview question.
    *   `target_gap` (str): The specific gap being addressed.
    *   Example:
        ```json
        {
          "question": "I noticed your resume highlights leadership, but the scholarship emphasizes service. Can you tell me about a time you volunteered in your community?",
          "target_gap": "Service"
        }
        ```

## 6. Agent F: Optimizer (Generation)
**Purpose:** Rewrites resume bullets to align with scholarship values.

*   **Input:**
    *   [resume_text](file:///Applications/Development/Anthropic_Hack/backend/utils/pdf_parser.py#128-164) (str): Full resume text.
    *   `decoder_output` (dict): Analysis from Agent C.

*   **Output:**
    *   `optimizations` (list): List of optimized bullet points.
    *   Example:
        ```json
        {
          "optimizations": [
            {
              "original": "Led team meetings.",
              "improved": "Orchestrated weekly strategic planning sessions for 20+ members, fostering a culture of collaboration.",
              "rationale": "Aligns with 'Leadership' value by showing scale and impact."
            }
          ]
        }
        ```

## 7. Agent G: Ghostwriter (Generation)
**Purpose:** Drafts the scholarship essay.

*   **Input:**
    *   `decoder_output` (dict): Analysis from Agent C.
    *   [resume_text](file:///Applications/Development/Anthropic_Hack/backend/utils/pdf_parser.py#128-164) (str): Full resume text.
    *   `bridge_story` (str, optional): User's answer from the interview.

*   **Output:**
    *   [essay](file:///Applications/Development/Anthropic_Hack/backend/agents/ghostwriter.py#38-108) (str): The drafted essay.
    *   `strategy_note` (str): Explanation of the narrative strategy.
    *   `word_count` (int): Length of the essay.
    *   Example:
        ```json
        {
          "essay": "Community service has always been my compass...",
          "strategy_note": "This essay uses your volunteer experience as a bridge to demonstrate the scholarship's core value of Service.",
          "word_count": 485
        }
        ```

## Orchestrator State ([ScholarshipState](file:///Applications/Development/Anthropic_Hack/backend/workflows/scholarship_graph.py#10-42))
The data flowing through the graph:

```python
class ScholarshipState(TypedDict):
    scholarship_url: str
    resume_pdf_path: str
    current_phase: str
    errors: List[str]
    
    # Populated by Agents
    scholarship_intelligence: Optional[Dict[str, Any]] # Scout
    resume_text: Optional[str]                         # Profiler
    decoder_analysis: Optional[Dict[str, Any]]         # Decoder
    match_score: Optional[float]                       # Matchmaker
    trigger_interview: Optional[bool]                  # Matchmaker
    identified_gaps: Optional[List[str]]               # Matchmaker
    interview_question: Optional[str]                  # Interviewer
    bridge_story: Optional[str]                        # User Input
    resume_optimizations: Optional[List[Dict]]         # Optimizer
    essay_draft: Optional[str]                         # Ghostwriter
    strategy_note: Optional[str]                       # Ghostwriter
```
