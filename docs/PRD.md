Here is the rewritten, comprehensive Product Requirements Document (PRD). It is structured to be handed directly to your dev team (Frontend, Backend, AI Logic) to start building immediately.

-----

# PRD: ScholarFit AI (The Adaptive Narrative Engine)

## 1\. Executive Summary

**ScholarFit AI** is an agentic application that stops students from submitting generic, mismatched applications. By analyzing the "Hidden DNA" of a scholarship (via scraping and past winner analysis) and comparing it to the student's resume (via RAG), the system identifies **narrative gaps**.

Instead of hallucinating content, **it interviews the user** to extract the specific story needed to win, then generates a tailored essay and specific resume optimization suggestions.

## 2\. Core Value Proposition (The "Hook")

> *"Most students have the right experience but tell the wrong story. ScholarFit AI aligns your truth with their values."*

-----

## 3\. System Architecture & Agent Flow

The system operates on a **Parallel Ingestion -\> Convergent Analysis -\> Interactive Generation** model.

### Phase 1: Parallel Ingestion

**Goal:** Turn unstructured data (Web & PDF) into structured constraints.

  * **Agent A: The Scout (Scholarship Intelligence)**
      * **Trigger:** User provides URL.
      * **Primary Task:** Scrape the URL for official criteria.
      * **Secondary Task (Innovation):** Use **Tavily API** to search: `"[Scholarship Name] past winner stories"` or `"[Scholarship Name] recipient profile"`.
      * **Output:** A text blob containing *Criteria + Winner Context*.
  * **Agent B: The Profiler (Student Intelligence)**
      * **Trigger:** User uploads Resume (PDF).
      * **Task:** Parse PDF -\> Chunk Text -\> Create Embeddings (Vector Store).
      * **Tech:** `PyPDF2`, `ChromaDB`.

### Phase 2: The "Gap" Analysis

**Goal:** Determine what is missing from the student's profile relative to the scholarship's needs.

  * **Agent C: The Decoder (Pattern Recognition)**
      * **Input:** Output from Agent A (Scout).
      * **Logic:** LLM analyzes text to extract a **Weighted Keyword Map**.
      * **Output JSON:**
        ```json
        {
          "primary_values": ["Community Leadership", "Grit"],
          "hidden_weights": {"Academic": 0.3, "Altruism": 0.7},
          "tone": "Humble, Servant-Leader"
        }
        ```
  * **Agent D: The Matchmaker (RAG Comparison)**
      * **Action:** Query the **Resume Vector Store** using the `primary_values` from Agent C.
      * **Decision Gate:**
          * *If Match Score \> 0.8:* Proceed to drafting.
          * *If Match Score \< 0.8:* **TRIGGER INTERVIEW MODE.**

### Phase 3: The "Human-in-the-Loop" (Innovation)

**Goal:** Extract new, relevant data from the user without hallucinating.

  * **Agent E: The Interviewer**
      * **Context:** "The scholarship wants 'Altruism' (0.7 weight), but the resume is 90% 'Coding'."
      * **Action:** Generate a specific prompt for the user.
      * **User Output:** *"I see your resume is very technical. This scholarship prioritizes community service. Tell me about a time you used your skills to help a non-profit or neighbor."*
      * **Input:** User types a short paragraph (The "Bridge Story").

### Phase 4: Adaptive Generation

**Goal:** Create the final assets.

  * **Agent F: The Resume Optimizer**
      * **Input:** Original Resume + Scholarship Keywords.
      * **Action:** Rewrite 3 bullet points to use the scholarship's specific vocabulary.
      * **Output:** "Suggestion: Rename 'Head of Coding Club' to 'Community Tech Mentor' to align with their values."
  * **Agent G: The Ghostwriter (Essay Drafter)**
      * **Input:** Scholarship Weights + Resume Context + **Bridge Story**.
      * **Action:** Write the essay using the *Bridge Story* as the hook.
      * **Output:** Full draft + "Strategy Note" explaining why this story was chosen.

-----

## 4\. Technical Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Streamlit or React | Fast UI prototyping for Hackathon. |
| **Orchestrator** | **LangGraph** (Python) | Manages the state and the "Human-in-the-Loop" pause. |
| **LLM** | **Claude 3.5 Sonnet** | Best for nuanced writing and following complex JSON instructions. |
| **Search** | **Tavily API** | Optimized for LLM agents (returns clean text, not HTML). |
| **Vector DB** | **ChromaDB** | Local, lightweight storage for the Resume RAG. |

-----

## 5\. UI/UX Requirements (The Demo View)

The interface should look like a "Mission Control" dashboard.

**Zone 1: The Inputs (Left Panel)**

  * **Resume:** Drag & Drop PDF area.
  * **Target:** URL Input field.
  * **Status Log:** A terminal-like view showing the agents working.
      * *Example:* `[Scout] Found 2 past winners...`
      * *Example:* `[Decoder] Identified primary value: Resilience.`

**Zone 2: The Conversation (Center Panel)**

  * **Dynamic Chat:** This is where **The Interviewer** Agent lives.
  * *Critical:* It must look like a chat, not a form. The AI asks a question, user answers.

**Zone 3: The Deliverables (Right Panel - Tabbed)**

  * **Tab 1: The Essay:** Rich text editor with the generated draft.
  * **Tab 2: Resume Fixes:** A "Diff" view showing *Original Bullet Point* vs. *Optimized Bullet Point*.

-----

## 6\. Hackathon Success Criteria Mapping

| Feature | Judging Category | Why it Wins |
| :--- | :--- | :--- |
| **Web Search for Past Winners** | **Innovation** | Shows you aren't just summarizing the prompt; you are analyzing the *market*. |
| **The Interviewer Agent** | **Tech Execution** | Implements a complex "Human-in-the-Loop" flow rather than a simple "Click & Wait" wrapper. |
| **Resume Optimization** | **Drafting Quality** | Goes beyond the essay to help the student fix their *entire* application package. |
| **JSON Weight Analysis** | **Adaptive Scoring** | Provides the mathematical justification for the AI's decisions (Explainable AI). |

-----

## 7\. Implementation Roadmap (24-Hour Plan)

1.  **Hours 0-4 (Backend Core):** Set up LangGraph. Build the "Scout" (Tavily) and "Profiler" (PDF Parser) functions.
2.  **Hours 4-8 (The Brain):** Engineer the prompts for "The Decoder" to ensure reliable JSON output. Test with 5 different scholarship URLs.
3.  **Hours 8-12 (The Loop):** Build the logic that compares Resume Vector vs. Scholarship Keywords. If match \< threshold, trigger the user question.
4.  **Hours 12-18 (Frontend):** Connect Streamlit to the backend. Ensure the "Chat" triggers correctly.
5.  **Hours 18-24 (Polish):** Refine the "Ghostwriter" prompt to ensure the essay tone matches the "Decoder" analysis. **Hardcode the slide deck story.**

## 8\. One-Shot Prompt for "The Decoder" (Start Here)

*Use this prompt to jumpstart your development:*

> "You are an expert Scholarship Strategist. I will provide you with text describing a scholarship and its past winners.
>
> **Your Task:** Analyze the text and uncover the *implicit* values.
> **Output:** Return ONLY a JSON object with this schema:
> `{ "keywords": ["list", "of", "5", "keywords"], "weights": {"keyword_1": 0.8, "keyword_2": 0.4}, "tone_guidance": "string describing the required writing style", "missing_evidence_query": "A question to ask the user if they lack evidence for the highest weighted keyword" }`"