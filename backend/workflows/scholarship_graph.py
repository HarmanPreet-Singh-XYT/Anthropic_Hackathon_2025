"""
LangGraph Workflow for ScholarFit AI
Orchestrates the 7-agent system with human-in-the-loop capability
"""

from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END


class ScholarshipState(TypedDict):
    """
    State schema for the scholarship application workflow
    Passed between all agents and modified throughout execution
    """
    # Inputs
    scholarship_url: str
    resume_pdf_path: str

    # Phase 1: Parallel Ingestion
    scholarship_intelligence: Optional[Dict[str, Any]]  # Scout output
    resume_processed: Optional[bool]  # Profiler completion status
    resume_text: Optional[str]  # Extracted resume content

    # Phase 2: Gap Analysis
    decoder_analysis: Optional[Dict[str, Any]]  # Keyword weights, tone
    match_score: Optional[float]  # 0.0-1.0 score
    trigger_interview: Optional[bool]  # Decision gate
    identified_gaps: Optional[List[str]]  # Missing keywords
    matchmaker_results: Optional[Dict[str, Any]]  # Full matchmaker output for frontend

    # Phase 3: Human-in-the-Loop
    interview_question: Optional[str]  # Question for student
    bridge_story: Optional[str]  # Student's response

    # Phase 4: Adaptive Generation
    resume_optimizations: Optional[List[Dict[str, str]]]  # Bullet rewrites
    essay_draft: Optional[str]  # Generated essay
    strategy_note: Optional[str]  # Explanation

    # Workflow control
    current_phase: str  # Track progress
    errors: Optional[List[str]]  # Error collection


class ScholarshipWorkflow:
    """
    LangGraph-based workflow orchestrator for ScholarFit AI
    Manages state transitions and human-in-the-loop interactions
    """

    def __init__(self, agents: Dict[str, Any]):
        """
        Initialize workflow with agent instances

        Args:
            agents: Dict containing all 7 agent instances
                - scout: ScoutAgent
                - profiler: ProfilerAgent
                - decoder: DecoderAgent
                - matchmaker: MatchmakerAgent
                - interviewer: InterviewerAgent
                - optimizer: OptimizerAgent
                - ghostwriter: GhostwriterAgent
        """
        self.agents = agents
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Construct the LangGraph state machine

        Returns:
            Configured StateGraph instance
        """
        workflow = StateGraph(ScholarshipState)

        # Add nodes
        workflow.add_node("scout", self.scout_node)
        workflow.add_node("profiler", self.profiler_node)
        workflow.add_node("decoder", self.decoder_node)
        workflow.add_node("matchmaker", self.matchmaker_node)
        workflow.add_node("interviewer", self.interviewer_node)
        workflow.add_node("optimizer", self.optimizer_node)
        workflow.add_node("ghostwriter", self.ghostwriter_node)

        # Define edges
        # Phase 1: Parallel Ingestion (simulated as sequential for now or parallel branches)
        # LangGraph allows parallel execution if nodes branch from start
        # For simplicity, let's do: Start -> Scout -> Profiler -> Decoder ...
        # Or better: Start -> [Scout, Profiler] -> Decoder
        
        # We'll start with Scout
        workflow.set_entry_point("scout")
        
        # Scout -> Profiler
        workflow.add_edge("scout", "profiler")
        
        # Profiler -> Decoder
        workflow.add_edge("profiler", "decoder")
        
        # Decoder -> Matchmaker
        workflow.add_edge("decoder", "matchmaker")
        
        # Matchmaker -> Conditional (Interviewer OR Optimizer)
        workflow.add_conditional_edges(
            "matchmaker",
            self.should_interview,
            {
                "interviewer": "interviewer",
                "optimizer": "optimizer"
            }
        )
        
        # Interviewer -> Optimizer (after human input)
        workflow.add_edge("interviewer", "optimizer")
        
        # Optimizer -> Ghostwriter
        workflow.add_edge("optimizer", "ghostwriter")
        
        # Ghostwriter -> End
        workflow.add_edge("ghostwriter", END)

        return workflow.compile(interrupt_after=["interviewer"])

    async def scout_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Scout Agent - Phase 1"""
        print("\n🔵 NODE: Scout Agent")
        state["current_phase"] = "ingestion"
        
        try:
            result = await self.agents["scout"].run(state["scholarship_url"])
            return {
                "scholarship_intelligence": result["scholarship_intelligence"],
                "resume_text": state.get("resume_text"), # Preserve existing
                "current_phase": "ingestion"
            }
        except Exception as e:
            print(f"❌ Scout failed: {e}")
            return {"errors": state.get("errors", []) + [str(e)]}

    async def profiler_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Profiler Agent - Phase 1"""
        print("\n🔵 NODE: Profiler Agent")
        
        try:
            # Run profiler
            result = await self.agents["profiler"].run(state["resume_pdf_path"])
            return {
                "resume_processed": True,
                "resume_text": result.get("text", "")
            }
        except Exception as e:
            print(f"❌ Profiler failed: {e}")
            return {"errors": state.get("errors", []) + [str(e)]}

    async def decoder_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Decoder Agent - Phase 2"""
        print("\n🔵 NODE: Decoder Agent")
        state["current_phase"] = "analysis"
        
        try:
            # Get combined text from scout output
            scout_data = state.get("scholarship_intelligence", {})
            combined_text = scout_data.get("combined_text", "")
            
            if not combined_text:
                # Fallback if combined_text missing
                combined_text = str(scout_data)
            
            analysis = await self.agents["decoder"].run(combined_text)
            return {
                "decoder_analysis": analysis,
                "current_phase": "analysis"
            }
        except Exception as e:
            print(f"❌ Decoder failed: {e}")
            return {"errors": state.get("errors", []) + [str(e)]}

    async def matchmaker_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Matchmaker Agent - Phase 2"""
        print("\n🔵 NODE: Matchmaker Agent")
        
        try:
            analysis = state.get("decoder_analysis", {})
            result = await self.agents["matchmaker"].run(analysis)
            
            return {
                "match_score": result["match_score"],
                "trigger_interview": result["trigger_interview"],
                "identified_gaps": result["gaps"],
                "matchmaker_results": result  # Store full results for frontend
            }
        except Exception as e:
            print(f"❌ Matchmaker failed: {e}")
            return {"errors": state.get("errors", []) + [str(e)]}

    def should_interview(self, state: ScholarshipState) -> str:
        """Conditional routing"""
        if state.get("trigger_interview", False):
            print("  🔀 Routing to: Interviewer (Gap detected)")
            return "interviewer"
        else:
            print("  🔀 Routing to: Optimizer (No significant gaps)")
            return "optimizer"

    async def interviewer_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Interviewer Agent - Phase 3"""
        print("\n🔵 NODE: Interviewer Agent")
        state["current_phase"] = "interview"
        
        # If we already have a bridge story (resuming), skip generation
        if state.get("bridge_story"):
            print("  ✓ Bridge story present, proceeding...")
            return {}

        try:
            resume_text = state.get("resume_text", "")
            gaps = state.get("identified_gaps", [])
            weights = state.get("decoder_analysis", {}).get("hidden_weights", {})
            
            result = await self.agents["interviewer"].run(resume_text, gaps, weights)
            
            # If no question generated, we might skip interrupt, but for now let's set it
            return {
                "interview_question": result["question"],
                "current_phase": "interview"
            }
        except Exception as e:
            print(f"❌ Interviewer failed: {e}")
            return {"errors": state.get("errors", []) + [str(e)]}

    async def optimizer_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Optimizer Agent - Phase 4"""
        print("\n🔵 NODE: Optimizer Agent")
        state["current_phase"] = "generation"
        
        try:
            resume_text = state.get("resume_text", "")
            decoder_output = state.get("decoder_analysis", {})
            
            result = await self.agents["optimizer"].run(resume_text, decoder_output)
            return {"resume_optimizations": result["optimizations"]}
        except Exception as e:
            print(f"❌ Optimizer failed: {e}")
            return {"errors": state.get("errors", []) + [str(e)]}

    async def ghostwriter_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Ghostwriter Agent - Phase 4"""
        print("\n🔵 NODE: Ghostwriter Agent")
        
        try:
            decoder_output = state.get("decoder_analysis", {})
            resume_text = state.get("resume_text", "")
            bridge_story = state.get("bridge_story")
            
            result = await self.agents["ghostwriter"].run(
                decoder_output=decoder_output,
                resume_text=resume_text,
                bridge_story=bridge_story
            )
            
            return {
                "essay_draft": result["essay"],
                "strategy_note": result["strategy_note"],
                "current_phase": "complete"
            }
        except Exception as e:
            print(f"❌ Ghostwriter failed: {e}")
            return {"errors": state.get("errors", []) + [str(e)]}

    async def run(
        self,
        scholarship_url: str,
        resume_pdf_path: str
    ) -> Dict[str, Any]:
        """Execute the full workflow"""
        print(f"🚀 Starting Scholarship Workflow for {scholarship_url}")
        
        initial_state = ScholarshipState(
            scholarship_url=scholarship_url,
            resume_pdf_path=resume_pdf_path,
            current_phase="start",
            errors=[]
        )
        
        # Run until interrupt or end
        # For LangGraph, we usually use .stream() or .invoke()
        # Since we have an interrupt, we need to handle it.
        # But here we just return the final state or the interrupted state.
        
        # Note: compiled graph is in self.graph
        # We need to await the invocation
        
        # Using ainvoke for async execution
        final_state = await self.graph.ainvoke(initial_state)
        return final_state

    async def resume_after_interview(
        self,
        bridge_story: str,
        checkpoint_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resume workflow after receiving student's bridge story"""
        print("🔄 Resuming workflow with bridge story...")
        
        # Update state with user input
        checkpoint_state["bridge_story"] = bridge_story
        
        # Resume execution
        # We need to continue from where we left off (Interviewer node)
        # Since we updated the state, the next step after Interviewer is Optimizer
        # But we need to make sure the graph knows we are resuming.
        # In standard LangGraph, we'd use the checkpoint ID.
        # Here, we are simulating it by re-invoking with the updated state,
        # assuming the graph logic handles "already done" nodes or we just start from the next node.
        # However, re-running from start is inefficient.
        # A better way for this simple implementation:
        # Just run the remaining nodes manually or create a sub-graph.
        # OR, since we are using ainvoke, we can't easily "resume" without a persistent checkpointer.
        #
        # Workaround: We will just re-run the graph but with the bridge_story already in state.
        # The Interviewer node checks `if state.get("bridge_story")` and returns immediately if present.
        # This effectively skips the generation and the interrupt (since we won't hit interrupt if we don't stop? 
        # Wait, interrupt_before=["interviewer"] means it stops BEFORE interviewer.
        # If we want to resume, we need to bypass that interrupt or change the config.
        #
        # Actually, if we re-run, we start from Scout again. That's bad.
        #
        # Correct LangGraph pattern: Use a Checkpointer.
        # But we haven't set up a DB for checkpoints.
        #
        # Alternative: Create a "GenerationPhase" graph for the second half.
        # Or just call the remaining agents manually in this method.
        # Given the complexity, calling agents manually for the second half is safest for this prototype.
        
        print("  → Manually executing remaining phases...")
        
        # 1. Optimizer
        opt_state = await self.optimizer_node(checkpoint_state)
        checkpoint_state.update(opt_state)
        
        # 2. Ghostwriter
        gw_state = await self.ghostwriter_node(checkpoint_state)
        checkpoint_state.update(gw_state)
        
        return checkpoint_state
