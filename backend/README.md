# ScholarFit AI Backend

> Multi-agent AI system for intelligent scholarship application optimization

This is the backend service for ScholarFit AI, built with FastAPI, LangGraph, and Claude 3.5 Sonnet. It orchestrates seven specialized AI agents to analyze scholarships, profile students, and generate perfectly aligned application materials.

## 🏗️ Architecture

### Multi-Agent System

The backend uses **LangGraph** to orchestrate a complex workflow with conditional routing and human-in-the-loop capabilities:

1. **Scout Agent** (`agents/scout.py`)
   - Scrapes scholarship websites using Firecrawl
   - Searches for past winner profiles via Tavily API
   - Extracts official criteria and hidden signals
   - **Output**: Comprehensive scholarship intelligence report

2. **Profiler Agent** (`agents/profiler.py`)
   - Parses PDF resumes using PyPDF
   - Chunks text and creates sentence embeddings
   - Stores in ChromaDB vector database for semantic search
   - **Output**: Queryable student profile database

3. **Decoder Agent** (`agents/decoder.py`)
   - Analyzes scholarship text using Claude
   - Extracts weighted keyword map and implicit values
   - Identifies preferred tone and writing style
   - **Output**: Structured JSON with scholarship "DNA"

4. **Matchmaker Agent** (`agents/matchmaker.py`)
   - Performs RAG queries against student vector DB
   - Calculates match scores for each criterion
   - Determines if interview is needed (threshold: 0.8)
   - **Output**: Gap analysis and decision routing

5. **Interviewer Agent** (`agents/interviewer.py` & `agents/interview_manager.py`)
   - Generates contextual questions for identified gaps
   - Conducts chat-based interview via WebSocket
   - Extracts "bridge stories" from user responses
   - **Output**: Authentic student experiences filling gaps

6. **Optimizer Agent** (`agents/optimizer.py`)
   - Rewrites resume bullets using scholarship vocabulary
   - Provides strategic suggestions with explanations
   - Maintains authenticity while improving alignment
   - **Output**: Optimized resume markdown and suggestions

7. **Ghostwriter Agent** (`agents/ghostwriter.py`)
   - Drafts essays using bridge stories as hooks
   - Matches scholarship tone and structure preferences
   - Includes strategy notes explaining narrative choices
   - **Output**: Complete essay draft with explanations

### Workflow State Machine

The LangGraph workflow (`workflows/scholarship_graph.py`) manages:
- **Parallel ingestion** of scholarship and student data
- **Conditional routing** based on match scores
- **Human-in-the-loop pauses** for interview interactions
- **Checkpointing** for session recovery
- **Progress tracking** for frontend polling

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Required API keys:
  - Anthropic API key (Claude)
  - Tavily API key (web search)

### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp ../.env.example ../.env
   # Edit .env with your API keys
   ```

3. **Run the server**
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
   python3 -m uvicorn api:app --reload --port 8000
   ```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Session Management
- `POST /api/session/create` - Create new workflow session
- `POST /api/session/{session_id}/upload-resume` - Upload resume PDF

### Workflow Control
- `POST /api/workflow/start` - Start scholarship analysis workflow
- `GET /api/workflow/status/{session_id}` - Get current workflow status
- `POST /api/workflow/continue` - Continue after interview

### Results
- `GET /api/workflow/match-result/{session_id}` - Get match analysis
- `GET /api/workflow/resume/{session_id}` - Get optimized resume
- `GET /api/workflow/essay/{session_id}` - Get generated essay

### Interview
- `POST /api/interview/initialize/{session_id}` - Start interview session
- `POST /api/interview/message` - Send user message
- `GET /api/interview/history/{session_id}` - Get chat history

### Outreach
- `GET /api/outreach/generate/{session_id}` - Generate outreach email

See `api.py` for complete endpoint documentation.

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Suites
```bash
pytest tests/test_workflow_integration.py  # Workflow tests
pytest tests/test_api.py                   # API endpoint tests
pytest test_e2e_session_workflow.py        # End-to-end tests
```

### Test with Verbose Output
```bash
pytest -v
```

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing strategies.

## 📁 Project Structure

```
backend/
├── agents/                 # AI agent implementations
│   ├── scout.py           # Scholarship intelligence
│   ├── profiler.py        # Resume parsing & RAG
│   ├── decoder.py         # Pattern recognition
│   ├── matchmaker.py      # Gap analysis
│   ├── interviewer.py     # Question generation
│   ├── interview_manager.py # Chat orchestration
│   ├── optimizer.py       # Resume optimization
│   └── ghostwriter.py     # Essay drafting
│
├── workflows/             # LangGraph workflow definitions
│   └── scholarship_graph.py # Main state machine
│
├── prompts/               # LLM prompt templates
│   ├── decoder.md         # Keyword extraction
│   ├── optimizer.md       # Resume optimization
│   ├── ghostwriter.md     # Essay generation
│   └── outreach.md        # Email drafting
│
├── tools/                 # Agent tools and utilities
│   └── web_tools.py       # Tavily search, scraping
│
├── utils/                 # Helper modules
│   ├── llm_client.py      # Claude API wrapper
│   ├── resume_parser.py   # PDF parsing
│   └── vector_store.py    # ChromaDB interface
│
├── config/                # Configuration management
│   └── settings.py        # Environment variables
│
├── tests/                 # Test suites
│   ├── test_workflow_integration.py
│   ├── test_api.py
│   └── test_interview_improvements.py
│
├── api.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
└── TESTING_GUIDE.md       # Testing documentation
```

## 🔧 Configuration

Configure via environment variables in `../.env`:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...

# Optional
LLM_MODEL=claude-3-5-sonnet-20241022
TEMPERATURE=0.7
CHUNK_SIZE=500
MATCH_THRESHOLD=0.8
DEFAULT_WORD_LIMIT=500
```

## 🐛 Debugging

### View Vector Store Contents
```bash
python debug_vector_store.py
```

### Clear Vector Database
```bash
python clear_vector_db.py
```

### Verify Agent Outputs
```bash
python verify_scout.py          # Test Scout agent
python verify_outreach.py       # Test outreach generation
python verify_session_data.py   # Check session state
```

See [../docs/DEBUGGING_GUIDE.md](../docs/DEBUGGING_GUIDE.md) for detailed troubleshooting.

## 📊 Data Flow

```
User Input (Resume PDF + URL)
         ↓
    [Scout] ← Tavily API
         ↓
    [Profiler] → ChromaDB
         ↓
    [Decoder] ← Claude
         ↓
    [Matchmaker] ← Vector Search
         ↓
   Score < 0.8? → [Interviewer] → User Chat
         ↓                           ↓
   Score ≥ 0.8                  Bridge Stories
         ↓                           ↓
         └──────────┬────────────────┘
                    ↓
              [Optimizer]
                    ↓
              [Ghostwriter]
                    ↓
         Essay + Resume + Email
```

## 🚧 Development

### Adding a New Agent

1. Create agent file in `agents/`
2. Define agent class with `run()` method
3. Add prompt template to `prompts/`
4. Integrate into workflow graph
5. Add tests in `tests/`

### Modifying the Workflow

Edit `workflows/scholarship_graph.py` to change:
- State schema
- Agent execution order
- Conditional routing logic
- Checkpoint behavior

## 📚 Additional Documentation

- [Production Testing Guide](../docs/PRODUCTION_TESTING.md)
- [Agent Input/Output Specifications](../docs/Agent_Input_Output.md)
- [Agentic Workflow Deep Dive](../docs/Agentic_workflow.md)
- [Scout Implementation Details](../docs/SCOUT_IMPLEMENTATION.md)

## 🔐 Security Notes

- Never commit `.env` files with real API keys
- User uploads stored in `uploads/` (gitignored)
- Vector DB stored in `chroma_db/` (gitignored)
- Session data is ephemeral and not persisted long-term

---

Built with Claude 3.5 Sonnet, LangGraph, and FastAPI 🚀
