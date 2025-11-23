# ScholarMatch: The First "Chameleon" AI for Scholarships

## 💡 Inspiration
Every year, millions of students copy-paste the same generic essay into 50 different scholarship applications. They talk about their "passion for learning" or "dedication to service," hoping one sticks.

But scholarship committees aren't looking for generic. They are looking for **specific values** hidden in their mission statements—values that most students miss because they are too busy applying to read between the lines.

We asked: **What if an AI could read the "mind" of the scholarship committee and rewrite your story to match their hidden criteria?**

That's how **ScholarMatch** was born. It's not just an essay writer; it's a "Chameleon Engine" that adapts your authentic experiences to fit the specific "personality" of any scholarship.

## 🧠 What it does
ScholarMatch is an agentic workflow that:
1.  **Decodes the Scholarship**: Scrapes the donor's website, "About Us" page, and past winner bios to build a "Value Profile" (e.g., "Values grit over grades" or "Prefers creative risk-takers").
2.  **Profiles the Student**: Ingests the student's resume and past essays into a vector database.
3.  **Finds the Gaps**: Compares the student's profile to the scholarship's values. If a critical value is missing (e.g., "Community Leadership"), it **interviews the student** to dig up a relevant story they forgot to mention.
4.  **Drafts the "Winning" Essay**: Generates a unique essay that highlights the specific traits the committee cares about, using the organization's own vocabulary and tone.
5.  **Automates Outreach**: Identifies the decision-makers and drafts a personalized inquiry email to establish contact before the application is even sent.

## ⚙️ How we built it
We built a **multi-agent system** using **LangGraph** to orchestrate 7 specialized AI agents, each with a distinct role:

*   **Agent A (Scout)**: Uses `Firecrawl` and `Tavily` to scrape scholarship pages and find hidden contact info.
*   **Agent B (Profiler)**: Parses student PDFs and creates vector embeddings using `ChromaDB`.
*   **Agent C (Decoder)**: An analytical LLM (Claude 3.5 Sonnet) that extracts ranking criteria and "tone indicators" from the scholarship text.
*   **Agent D (Matchmaker)**: Performs semantic search to align student stories with scholarship criteria.
*   **Agent E (Interviewer)**: A chat bot that wakes up *only* when information is missing, asking targeted questions to fill the gaps.
*   **Agent F (Optimizer)**: Re-ranks the student's resume bullet points to prioritize what matters for *this specific* application.
*   **Agent G (Ghostwriter)**: The final creative engine that synthesizes all data into a persuasive, tone-matched narrative.

The frontend is built with **Next.js** and **Tailwind CSS**, featuring a "Glassmorphism" design to feel premium and futuristic. The backend is **FastAPI**, serving the LangGraph workflow via asynchronous endpoints.

## 🚧 Challenges we ran into
*   **The "Generic" Trap**: Early versions of the AI just summarized the resume. We had to implement a "Gap Analysis" phase (The Matchmaker) to force the AI to look for what was *missing* rather than just repeating what was there.
*   **State Management**: Orchestrating 7 agents where some steps (like the Interview) require human input was complex. We used LangGraph's `interrupt_before` functionality to pause the workflow, wait for the user's chat response, and then resume execution with the new context.
*   **Scraping Resilience**: Scholarship websites are notoriously messy. We had to build a robust scraper (Scout) that could handle everything from modern SPAs to old government HTML pages.

## 🏆 Accomplishments that we're proud of
*   **The "Interviewer" Agent**: It feels like magic when the AI stops and asks, *"I see you applied for a Leadership Grant, but your resume doesn't mention leading a team. Can you tell me about a time you led a project?"* It turns a static form into a dynamic conversation.
*   **Automated Outreach**: We didn't just stop at the essay. The system now finds the email address of the scholarship chair and drafts a "warm introduction" email, giving students a massive networking advantage.
*   **Real-time RAG**: We successfully implemented a Retrieval-Augmented Generation pipeline that runs in seconds, making the tool feel responsive and alive.

## 📚 What we learned
*   **Agents need narrow scopes**: We initially tried to have one "Smart Agent" do everything. It failed. Breaking it down into "Scout," "Decoder," etc., made the system far more reliable and debuggable.
*   **Context is King**: The quality of the essay is 100% dependent on the quality of the "Decoder" analysis. Spending time on the prompt engineering for the analysis phase paid off 10x in the generation phase.
*   **LangGraph is powerful**: The ability to define cyclic graphs (loops for interviews) and conditional edges (skip interview if match is high) allowed us to build logic that linear chains simply couldn't handle.

## 🚀 What's next for ScholarMatch
*   **Batch Processing**: Upload one resume and apply to 50 scholarships overnight.
*   **Alumni Network**: Connect students with past winners (found by Scout) for mentorship.
*   **Mobile App**: A "Tinder for Scholarships" where you swipe right to apply, and the AI handles the paperwork.
