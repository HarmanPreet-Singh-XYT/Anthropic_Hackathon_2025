# ScholarMatch AI
<div align="center">
  <a href="https://youtu.be/JfjWb-Z1h7U">
    <img src="https://img.youtube.com/vi/JfjWb-Z1h7U/hqdefault.jpg" alt="Watch the video" />
  </a>
</div>

> Transform scholarship applications through intelligent narrative alignment

ScholarMatch AI is a revolutionary multi-agent AI platform that helps students win scholarships by aligning their authentic experiences with what scholarship committees truly value. Unlike generic AI essay writers, we analyze the "hidden DNA" of scholarships, identify narrative gaps using RAG technology, and conduct intelligent interviews to extract authentic stories—never fabricating content.

## 🎯 Key Features

- **🔍 Intelligent Scholarship Analysis**: Automatically scrapes scholarship websites and researches past winner profiles to uncover implicit selection criteria
- **📊 RAG-Powered Matching**: Uses vector embeddings to semantically compare student profiles against scholarship requirements
- **💬 Human-in-the-Loop Interviewing**: When gaps are detected, conducts contextual interviews to extract authentic stories students forgot to mention
- **📝 Optimized Resume Generation**: Rewrites resume bullets using scholarship-specific vocabulary while maintaining authenticity
- **✍️ Personalized Essay Drafting**: Generates perfectly aligned essays using extracted bridge stories and scholarship tone analysis
- **📧 Outreach Email Drafting**: Creates personalized communication to scholarship contacts for relationship-building
- **🎨 Premium UI/UX**: Modern glassmorphic interface with real-time progress tracking and animated workflows

## 🏗️ Technology Stack

### Backend
- **Framework**: FastAPI with Python 3.11+
- **AI Orchestration**: LangGraph for complex multi-agent workflows
- **LLM**: Claude 3.5 Sonnet (Anthropic)
- **Vector Database**: ChromaDB with sentence-transformers
- **Web Intelligence**: Tavily API for LLM-optimized search, Firecrawl for web scraping
- **PDF Processing**: PyPDF for resume parsing

### Frontend
- **Framework**: Next.js 16 (React 19)
- **Styling**: Tailwind CSS with custom glassmorphism design
- **UI Components**: Radix UI primitives with custom animations
- **Rich Text Editing**: TipTap for resume editing
- **PDF Export**: jsPDF for resume generation
- **Animations**: Framer Motion

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **npm**: 9.0 or higher
- **API Keys**:
  - Anthropic API key (for Claude)
  - Tavily API key (for web search)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Anthropic_Hack
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

### Running Locally

1. **Start the backend server** (from `backend/` directory)
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
   python3 -m uvicorn api:app --reload --port 8000
   ```
   The API will be available at `http://localhost:8000`

2. **Start the frontend development server** (from `frontend/` directory)
   ```bash
   npm run dev
   ```
   The application will be available at `http://localhost:3000`

3. **Open your browser** and navigate to `http://localhost:3000`

## 📖 How It Works

### The Multi-Agent Pipeline

ScholarMatch AI uses a sophisticated workflow orchestrated by LangGraph:

1. **Scout Agent** 🔎
   - Scrapes scholarship websites for official criteria
   - Searches for past winner profiles and committee backgrounds
   - Outputs comprehensive scholarship intelligence

2. **Profiler Agent** 📋
   - Parses uploaded resume PDFs
   - Creates semantic embeddings
   - Stores student profile in vector database

3. **Decoder Agent** 🧩
   - Analyzes scholarship text to extract weighted keyword map
   - Identifies implicit values and tone requirements
   - Outputs structured JSON with priorities

4. **Matchmaker Agent** 🎯
   - Performs RAG-based comparison between student profile and scholarship requirements
   - Calculates match scores for each criterion
   - Determines if interview is needed (threshold: 80%)

5. **Interviewer Agent** 💭
   - Generates contextual questions for identified gaps
   - Conducts chat-based interview to extract "bridge stories"
   - Never fabricates—only uses authentic student experiences

6. **Optimizer Agent** 🔧
   - Rewrites resume bullets using scholarship vocabulary
   - Maintains authenticity while improving alignment
   - Provides strategic suggestions with explanations

7. **Ghostwriter Agent** ✍️
   - Drafts essays using bridge stories as hooks
   - Matches scholarship tone and structure preferences
   - Includes strategy notes explaining narrative choices

## 📁 Project Structure

```
Anthropic_Hack/
├── backend/                # Python FastAPI backend
│   ├── agents/            # Individual AI agents
│   ├── workflows/         # LangGraph workflow definitions
│   ├── prompts/           # Agent prompt templates
│   ├── tools/             # Utility functions and tools
│   ├── utils/             # Helper modules (LLM client, parsers)
│   ├── config/            # Configuration management
│   ├── tests/             # Backend test suites
│   ├── api.py             # Main FastAPI application
│   └── requirements.txt   # Python dependencies
│
├── frontend/              # Next.js React frontend
│   ├── app/               # Next.js app directory (pages)
│   ├── components/        # Reusable React components
│   ├── lib/               # Frontend utilities
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
│
├── docs/                  # Documentation (PRD, guides, specs)
├── .env.example           # Environment variable template
└── README.md              # This file
```

## 🔧 Configuration

ScholarMatch AI can be configured via environment variables in `.env`:

```bash
# Required API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Model Configuration
LLM_MODEL=claude-3-5-sonnet-20241022
TEMPERATURE=0.7

# Vector Store Configuration
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_RETRIEVAL_RESULTS=5

# Matchmaker Configuration
MATCH_THRESHOLD=0.8

# Essay Configuration
DEFAULT_WORD_LIMIT=500
```

See [.env.example](.env.example) for all available options.

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest                                    # Run all tests
pytest tests/test_workflow_integration.py # Run specific test
pytest -v                                 # Verbose output
```

### Manual Testing
See `docs/PRODUCTION_TESTING.md` for comprehensive manual testing procedures.

## 📚 Documentation

- **[Product Requirements Document](docs/PRD.md)**: Detailed system architecture and agent specifications
- **[Investor Pitch](docs/INVESTOR_PITCH.md)**: Vision, market opportunity, and roadmap
- **[Agentic Workflow](docs/Agentic_workflow.md)**: Deep dive into the multi-agent orchestration
- **[Testing Guide](backend/TESTING_GUIDE.md)**: Backend testing strategies
- **[Debugging Guide](docs/DEBUGGING_GUIDE.md)**: Common issues and solutions

## 🤝 Contributing

This project was built for the Anthropic AI Hackathon. Contributions are welcome!

## 🙏 Acknowledgments

Built with:
- **Claude 3.5 Sonnet** by Anthropic for intelligent multi-agent orchestration
- **LangGraph** for robust workflow state management
- **Next.js** and **React** for modern frontend development
- **FastAPI** for high-performance backend APIs

---

**ScholarMatch AI**: Empowering students to discover, articulate, and amplify their authentic stories. 🎓✨
