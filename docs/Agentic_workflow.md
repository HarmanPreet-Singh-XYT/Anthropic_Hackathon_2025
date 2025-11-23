# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ScholarFit AI** is an agentic application that analyzes scholarship requirements and student resumes to identify narrative gaps, then conducts adaptive interviews to extract missing stories and generate tailored essays and resume optimizations.

Core innovation: Instead of hallucinating content, the system uses a "Human-in-the-Loop" approach to extract authentic student stories that align with scholarship values.

## File Structure

```
/
├── backend/
│   ├── agents/
│   │   ├── __init__.py           # Agent package exports
│   │   ├── scout.py              # Agent A: Web scraping + Tavily search
│   │   ├── profiler.py           # Agent B: PDF parsing + embeddings
│   │   ├── decoder.py            # Agent C: Keyword extraction + weighting
│   │   ├── matchmaker.py         # Agent D: RAG comparison + decision gate
│   │   ├── interviewer.py        # Agent E: Gap-based question generation
│   │   ├── optimizer.py          # Agent F: Resume bullet optimization
│   │   └── ghostwriter.py        # Agent G: Essay drafting
│   ├── prompts/
│   │   ├── decoder.md            # Decoder system prompt template
│   │   ├── interviewer.md        # Interviewer system prompt template
│   │   ├── optimizer.md          # Optimizer system prompt template
│   │   └── ghostwriter.md        # Ghostwriter system prompt template
│   ├── workflows/
│   │   ├── __init__.py           # Workflow package exports
│   │   └── scholarship_graph.py  # LangGraph state machine orchestration
│   ├── utils/
│   │   ├── __init__.py           # Utilities package exports
│   │   ├── pdf_parser.py         # PDF text extraction utilities
│   │   ├── vector_store.py       # ChromaDB wrapper
│   │   └── prompt_loader.py      # Markdown prompt loader with variables
│   ├── config/
│   │   ├── __init__.py           # Config package exports
│   │   └── settings.py           # Environment-based configuration
│   ├── main.py                   # Application entry point
│   └── requirements.txt          # Python dependencies
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── CLAUDE.md                     # This file
├── PRD.md                        # Product requirements document
└── README.md                     # Project readme
```

## Architecture

### Multi-Agent System (7 Agents)

The system follows a **Parallel Ingestion → Convergent Analysis → Interactive Generation** model:

**Phase 1: Parallel Ingestion**
- **Agent A (Scout)**: Scrapes scholarship URL + searches Tavily API for past winner profiles
- **Agent B (Profiler)**: Parses resume PDF, creates embeddings, stores in ChromaDB vector store

**Phase 2: Gap Analysis**
- **Agent C (Decoder)**: Extracts weighted keyword map from scholarship data (JSON output with primary_values, hidden_weights, tone)
- **Agent D (Matchmaker)**: RAG comparison between resume vector store and scholarship values; triggers interview mode if match score < 0.8

**Phase 3: Human-in-the-Loop**
- **Agent E (Interviewer)**: Generates contextual questions to extract "bridge stories" when gaps are detected

**Phase 4: Adaptive Generation**
- **Agent F (Resume Optimizer)**: Rewrites resume bullets using scholarship vocabulary
- **Agent G (Ghostwriter)**: Drafts essay using bridge story + scholarship weights + resume context

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Orchestrator | LangGraph (Python) | State management + human-in-the-loop pause logic |
| LLM | Claude 3.5 Sonnet | Nuanced writing + complex JSON instruction following |
| Search | Tavily API | LLM-optimized search for past winner profiles |
| Vector DB | ChromaDB | Local resume RAG storage |
| Frontend | Streamlit or React | Mission control dashboard UI |

## Key Data Structures

### Decoder Output (Agent C)
```json
{
  "primary_values": ["Community Leadership", "Grit"],
  "hidden_weights": {"Academic": 0.3, "Altruism": 0.7},
  "tone": "Humble, Servant-Leader"
}
```

### Matchmaker Decision Gate (Agent D)
- Match Score > 0.8: Proceed to drafting
- Match Score < 0.8: Trigger interview mode

### Testing Individual Agents
```python
# Example: Test Scout Agent independently
from agents import ScoutAgent
scout = ScoutAgent(tavily_api_key="your_key")
result = await scout.run("https://scholarship-url.com")
```

### Frontend Setup (Streamlit - when ready)
```bash
pip install streamlit
streamlit run app.py
```

### Frontend Setup (React alternative - when ready)
```bash
npm install
npm run dev
```

## ⚠️ CRITICAL: Use Provided Utilities - Avoid Code Duplication

**IMPORTANT:** Four fully-implemented utility modules are provided in `backend/utils/`. **ALWAYS use these instead of creating repetitive code** in your agent implementations.

### 1. Prompt Loader (`utils/prompt_loader.py`)

**Purpose:** Load and manage externalized prompt templates with variable substitution

**Functions:**
- `load_prompt(prompt_name, variables)` - Load .md prompt with variable substitution
- `list_available_prompts()` - List all available prompt templates
- `validate_prompt_variables(prompt_name, variables)` - Validate required variables
- `get_prompt_info(prompt_name)` - Get prompt metadata and required variables

**Usage in agents:**
```python
from utils.prompt_loader import load_prompt

class DecoderAgent:
    def __init__(self, anthropic_client, prompt_dir):
        self.client = anthropic_client
        # DON'T create prompt loading logic - use the utility!

    async def analyze_scholarship(self, scholarship_text: str):
        # Load prompt with variable substitution
        system_prompt = load_prompt("decoder", {
            "scholarship_text": scholarship_text
        })
        # Use with LLM...
```

**Arguments:**
- `prompt_name` (str): Name without .md extension (e.g., "decoder", "interviewer")
- `variables` (Dict[str, Any]): Key-value pairs for {variable} substitution

### 2. PDF Parser (`utils/pdf_parser.py`)

**Purpose:** Extract and process text from resume PDFs

**Functions:**
- `parse_pdf(pdf_path)` - Extract all text from PDF, returns cleaned string
- `validate_pdf(pdf_path)` - Validate PDF is readable, returns (is_valid, error_msg)
- `extract_sections(pdf_text)` - Auto-detect resume sections (Education, Experience, etc.)
- `clean_resume_text(text)` - Normalize whitespace and remove PDF artifacts
- `get_pdf_metadata(pdf_path)` - Get page count, word count, file size

**Usage in agents:**
```python
from utils.pdf_parser import parse_pdf, validate_pdf, extract_sections

class ProfilerAgent:
    async def parse_resume_pdf(self, pdf_path: str):
        # DON'T write PDF parsing code - use the utility!

        # Validate first
        is_valid, error = validate_pdf(pdf_path)
        if not is_valid:
            raise ValueError(f"Invalid PDF: {error}")

        # Parse (already cleaned and normalized)
        resume_text = parse_pdf(pdf_path)

        # Optional: Extract structured sections
        sections = extract_sections(resume_text)
        # sections = {"education": "...", "experience": "...", ...}
```

**Arguments:**
- `pdf_path` (str): Absolute or relative path to PDF file
- Returns cleaned, normalized text ready for embedding

### 3. LLM Client (`utils/llm_client.py`)

**Purpose:** Simple Anthropic API wrapper - initialize once per agent, call repeatedly

**Class:**
- `LLMClient(api_key, model, temperature, max_tokens)` - Initialize with settings
- `async call(system_prompt, user_message)` - **Single method** for API calls

**Factory function:**
- `create_llm_client(api_key, model, temperature)` - Creates client with config defaults

**Usage in agents:**
```python
from utils.llm_client import create_llm_client
from utils.prompt_loader import load_prompt
import json

class DecoderAgent:
    def __init__(self):
        # DON'T create Anthropic client directly - use the utility!
        # Initialize once with desired temperature
        self.llm = create_llm_client(temperature=0.3)  # Lower for structured JSON output

    async def analyze_scholarship(self, scholarship_text: str):
        # Load prompt from file
        system_prompt = load_prompt("decoder", {
            "scholarship_text": scholarship_text
        })

        # Call API
        response = await self.llm.call(
            system_prompt=system_prompt,
            user_message="Analyze this scholarship and return the JSON."
        )

        # Parse JSON yourself
        result = json.loads(response)
        return result

class InterviewerAgent:
    def __init__(self):
        # Uses default temperature (0.7) from settings
        self.llm = create_llm_client()

    async def generate_question(self, gaps: list[str], context: str):
        system_prompt = load_prompt("interviewer", {
            "resume_summary": context,
            "target_gap": gaps[0],
            "gap_weight": "0.7",
            "resume_focus": "technical skills"
        })

        # Returns text directly
        question = await self.llm.call(
            system_prompt=system_prompt,
            user_message="Generate a contextual question for this gap."
        )

        return question
```

**Arguments:**
- `api_key` (str): Anthropic API key (auto-loaded from settings if omitted)
- `model` (str): Model ID (default: "claude-3-5-sonnet-20241022")
- `temperature` (float): 0.0-1.0, set at initialization (default: 0.7)
- `max_tokens` (int): Maximum response tokens (default: 4096)
- `system_prompt` (str): System instruction for the model
- `user_message` (str): User query or input

**Key Features:**
- Simple: Just one `call()` method
- Stateful: Initialize once with settings, reuse for all calls
- Clean: Agents handle their own JSON parsing
- Async-only: All agents use async/await pattern

### 4. Vector Store (`utils/vector_store.py`)

**Purpose:** ChromaDB wrapper for resume embedding storage and RAG queries

**Methods:**
- `__init__(collection_name, persist_directory)` - Initialize persistent vector store
- `add_documents(documents, metadatas, ids)` - Add text chunks with optional metadata
- `query(query_text, n_results)` - Semantic search for similar documents
- `query_with_filter(query_text, filter_dict, n_results)` - Query with metadata filters
- `get_collection_stats()` - Get document count and collection info
- `clear_collection()` - Remove all documents but keep collection
- `delete_documents(document_ids)` - Delete specific documents

**Usage in agents:**
```python
from utils.vector_store import VectorStore

class ProfilerAgent:
    def __init__(self, vector_store: VectorStore):
        # DON'T create ChromaDB initialization code - use the utility!
        self.vector_store = vector_store

    async def run(self, resume_pdf_path: str):
        # Parse PDF using pdf_parser utility
        resume_text = parse_pdf(resume_pdf_path)

        # Chunk text
        chunks = self.chunk_text(resume_text)

        # Add to vector store (embeddings handled automatically)
        self.vector_store.add_documents(
            documents=chunks,
            metadatas=[{"source": "resume", "chunk_index": i} for i in range(len(chunks))]
        )

class MatchmakerAgent:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    async def query_resume(self, primary_values: list[str]):
        # DON'T write vector search code - use the utility!
        results = self.vector_store.query(
            query_text=" ".join(primary_values),
            n_results=5
        )
        # results = {"documents": [...], "distances": [...], "metadatas": [...]}
```

**Arguments:**
- `collection_name` (str): Name for ChromaDB collection (default: "resumes")
- `persist_directory` (str): Where to save ChromaDB data (default: "./chroma_db")
- `documents` (List[str]): Text chunks to store/query
- `metadatas` (List[Dict]): Optional metadata per chunk
- `n_results` (int): Number of similar documents to return

**Key Features:**
- Automatic embedding generation (no need to call embedding models)
- Persistent storage across sessions
- Metadata filtering for structured queries
- Thread-safe operations

---

## Critical Implementation Notes

### Prompt Management Architecture (Detailed)

**All agent prompts are externalized to `.md` files** in `backend/prompts/`:
- `decoder.md` - Scholarship analysis system prompt (requires: `{scholarship_text}`)
- `interviewer.md` - Gap-based question generation prompt (requires: `{resume_summary}`, `{target_gap}`, `{gap_weight}`, `{resume_focus}`)
- `optimizer.md` - Resume bullet optimization prompt (requires: `{resume_text}`, `{primary_values}`, `{hidden_weights}`, `{tone}`)
- `ghostwriter.md` - Essay drafting prompt (requires: `{primary_values}`, `{hidden_weights}`, `{tone}`, `{bridge_story}`, `{resume_context}`, `{word_limit}`)

**Loading prompts in agent code (use the utility!):**
```python
from utils.prompt_loader import load_prompt

# In agent methods - NOT __init__ (variables aren't known yet)
async def analyze_scholarship(self, scholarship_text: str):
    # Load prompt with runtime variable substitution
    system_prompt = load_prompt("decoder", {
        "scholarship_text": scholarship_text
    })
    # Use with Anthropic API...
```

**Benefits:**
- Version control prompts separately from code
- Easy A/B testing of prompt variations
- Non-technical team members can iterate on prompts
- Template variables for dynamic content injection
- Auto-validation of required variables

### LangGraph State Management

The workflow uses a `ScholarshipState` TypedDict that flows through all agents:

```python
class ScholarshipState(TypedDict):
    # Inputs
    scholarship_url: str
    resume_pdf_path: str

    # Agent outputs (Optional - populated during workflow)
    scholarship_intelligence: Optional[Dict[str, Any]]
    decoder_analysis: Optional[Dict[str, Any]]
    match_score: Optional[float]
    trigger_interview: Optional[bool]
    bridge_story: Optional[str]
    # ... etc
```

**Key workflow patterns:**
1. **Parallel Execution**: Scout + Profiler run simultaneously in Phase 1
2. **Conditional Routing**: Matchmaker's `trigger_interview` flag routes to Interviewer or Optimizer
3. **Human-in-the-Loop**: Workflow pauses at Interviewer node, saves checkpoint, resumes with user input

### The Decoder Prompt (Agent C)

See `backend/prompts/decoder.md` for the full template. Key requirement: Returns JSON with exact schema:
```json
{
  "primary_values": ["value1", "value2", "value3", "value4", "value5"],
  "hidden_weights": {"category1": 0.4, "category2": 0.3, ...},
  "tone": "Writing style description",
  "missing_evidence_query": "Question template for gaps"
}
```

Weights MUST sum to 1.0. Validate in decoder agent implementation.

### Human-in-the-Loop Flow

The system MUST pause for user input when gaps are detected. LangGraph handles this state management:

1. Matchmaker detects `match_score < 0.8`
2. Sets `state["trigger_interview"] = True`
3. Interviewer generates question, saves to `state["interview_question"]`
4. **Workflow interrupts** - saves checkpoint state
5. Frontend displays question to user
6. User provides answer (bridge story)
7. Workflow resumes with `bridge_story` in state
8. Optimizer and Ghostwriter use bridge story in generation

**Never hallucinate missing stories** - always ask the user.

### Resume Optimization Strategy

Don't rewrite the entire resume. Target 3 specific bullet points and show:
- Original text
- Optimized version with scholarship vocabulary
- Explanation of why the change aligns with scholarship values

See `backend/prompts/optimizer.md` for implementation template.

## Implementation Workflow

### Phase 1: Core Agent Implementation (Priority Order)

1. **Start with Utilities** (`backend/utils/`)
   - `prompt_loader.py` - Critical for all agents
   - `pdf_parser.py` - Needed for Profiler
   - `vector_store.py` - Needed for Profiler & Matchmaker

2. **Implement Agents in Dependency Order**
   - **Scout** (`agents/scout.py`) - No dependencies, produces scholarship intelligence
   - **Profiler** (`agents/profiler.py`) - Depends on utils only
   - **Decoder** (`agents/decoder.py`) - Consumes Scout output, uses `prompts/decoder.md`
   - **Matchmaker** (`agents/matchmaker.py`) - Consumes Decoder output, queries vector store
   - **Interviewer** (`agents/interviewer.py`) - Consumes Matchmaker gaps, uses `prompts/interviewer.md`
   - **Optimizer** (`agents/optimizer.py`) - Uses Decoder output, uses `prompts/optimizer.md`
   - **Ghostwriter** (`agents/ghostwriter.py`) - Uses all prior outputs, uses `prompts/ghostwriter.md`

3. **Wire Up LangGraph Workflow** (`workflows/scholarship_graph.py`)
   - Define state transitions
   - Implement conditional routing
   - Configure human-in-the-loop interrupts
   - Test full flow integration

### Phase 2: Testing & Integration

**Unit Testing Pattern:**
```python
# Test each agent independently first
pytest backend/tests/test_scout.py
pytest backend/tests/test_profiler.py
# ... etc
```

**Integration Testing:**
```python
# Test full workflow with mock data
pytest backend/tests/test_workflow_integration.py
```

### Phase 3: Frontend Connection

After backend is stable, connect UI to workflow endpoints for human-in-the-loop interaction.

## 24-Hour Hackathon Roadmap

1. **Hours 0-4**: Implement utils + Scout (Tavily) + Profiler (PDF parser)
2. **Hours 4-8**: Decoder implementation + prompt engineering + JSON validation with 5 test URLs
3. **Hours 8-12**: Matchmaker RAG logic + interview trigger threshold + Interviewer question generation
4. **Hours 12-18**: Optimizer + Ghostwriter + LangGraph workflow integration
5. **Hours 18-24**: Frontend connection + human-in-the-loop testing + demo polish

## Hackathon Differentiation Strategy

| Feature | Why It Wins |
|---------|-------------|
| Tavily search for past winners | Shows market analysis, not just prompt summarization |
| Interviewer Agent | Complex human-in-the-loop vs. simple click-and-wait wrapper |
| Resume optimization | Full application package help, not just essay |
| JSON weight analysis | Explainable AI with mathematical justification |

## Testing Strategy

Test each agent independently before integration:
1. Scout: Verify Tavily returns relevant past winner data
2. Profiler: Test PDF parsing with various resume formats
3. Decoder: Validate JSON output reliability across 5+ scholarship URLs
4. Matchmaker: Verify threshold logic triggers interview mode correctly
5. Interviewer: Test question relevance for different gap scenarios
6. Resume Optimizer: Check vocabulary alignment quality
7. Ghostwriter: Verify essay incorporates bridge story naturally

## Value Proposition

> "Most students have the right experience but tell the wrong story. ScholarFit AI aligns your truth with their values."

The system analyzes the "Hidden DNA" of scholarships through scraping + past winner analysis, compares against student resume via RAG, identifies narrative gaps, then interviews to extract authentic stories - never hallucinating content.
