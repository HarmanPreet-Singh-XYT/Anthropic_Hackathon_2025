"""
LangGraph Workflow for ScholarFit AI
Orchestrates the 7-agent system with human-in-the-loop capability
"""

from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END
from pathlib import Path

class ScholarshipState(TypedDict):
    """State schema for the scholarship application workflow"""
    # Inputs
    scholarship_url: str
    resume_pdf_path: str
    session_id: str
    
    # Phase 1: Parallel Ingestion
    scholarship_intelligence: Optional[Dict[str, Any]]
    resume_processed: Optional[bool]
    resume_text: Optional[str]
    
    # Phase 2: Gap Analysis
    decoder_analysis: Optional[Dict[str, Any]]
    match_score: Optional[float]
    trigger_interview: Optional[bool]
    identified_gaps: Optional[List[str]]
    matchmaker_results: Optional[Dict[str, Any]]
    
    # Phase 3: Human-in-the-Loop
    interview_question: Optional[str]
    bridge_story: Optional[str]
    
    # Phase 4: Adaptive Generation
    resume_optimizations: Optional[List[Dict[str, str]]]
    optimized_resume_markdown: Optional[str]
    essay_draft: Optional[str]
    strategy_note: Optional[str]
    
    # Workflow control
    current_phase: str
    errors: Optional[List[str]]

class ScholarshipWorkflow:
    """LangGraph-based workflow orchestrator for ScholarFit AI"""
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Construct the LangGraph state machine"""
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
        workflow.set_entry_point("scout")
        workflow.add_edge("scout", "profiler")
        workflow.add_edge("profiler", "decoder")
        workflow.add_edge("decoder", "matchmaker")
        
        workflow.add_conditional_edges(
            "matchmaker",
            self.should_interview,
            {
                "interviewer": "interviewer",
                "optimizer": "optimizer"
            }
        )
        
        workflow.add_edge("interviewer", "optimizer")
        workflow.add_edge("optimizer", "ghostwriter")
        workflow.add_edge("ghostwriter", END)
        
        return workflow.compile(interrupt_after=["matchmaker"])
    
    def _validate_state(self, state: Dict[str, Any], phase: str) -> bool:
        """Validate state has required fields for given phase"""
        validation_rules = {
            "decoder": ["scholarship_intelligence", "resume_text"],
            "matchmaker": ["decoder_analysis", "resume_text"],
            "optimizer": ["resume_text", "decoder_analysis"],
            "ghostwriter": ["resume_text", "decoder_analysis"]
        }
        
        required = validation_rules.get(phase, [])
        missing = [k for k in required if not state.get(k)]
        
        if missing:
            print(f"  ⚠ State validation failed for {phase}: missing {missing}")
            return False
        
        return True
    
    async def scout_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Scout Agent - Phase 1"""
        print("\n🔵 NODE: Scout Agent")
        print(f"  → Scraping scholarship URL: {state['scholarship_url']}")
        
        try:
            result = await self.agents["scout"].run(state["scholarship_url"])
            
            print(f"  ✓ Scout completed successfully")
            print(f"  → Intelligence keys: {list(result.get('scholarship_intelligence', {}).keys())}")
            
            return {
                "scholarship_intelligence": result["scholarship_intelligence"],
                "current_phase": "ingestion"
            }
        except Exception as e:
            print(f"  ❌ Scout failed: {e}")
            return {
                "errors": state.get("errors", []) + [f"Scout error: {str(e)}"],
                "current_phase": "error"
            }
    
    async def profiler_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Profiler Agent - Phase 1"""
        print("\n🔵 NODE: Profiler Agent")
        
        session_id = state.get("session_id")
        resume_pdf_path = state.get("resume_pdf_path")
        
        print(f"  → Resume path: {resume_pdf_path}")
        print(f"  → Session ID: {session_id}")
        
        try:
            # ✅ HANDLE SESSION-BASED RESUMES
            if resume_pdf_path == "session_based":
                print("  → Mode: Session-based (retrieving from ChromaDB)")
                
                # Retrieve existing resume data from ChromaDB
                result = await self.agents["profiler"].retrieve_from_session(session_id)
                
                if not result.get("success"):
                    raise ValueError(f"Failed to retrieve resume from session: {result.get('error')}")
                
                resume_text = result.get("resume_text", "")
                
                # Validate retrieved text
                if not resume_text or len(resume_text) < 100:
                    raise ValueError(f"Retrieved resume text too short or empty ({len(resume_text)} chars)")
                
                print(f"  ✓ Retrieved {len(resume_text)} characters from session")
                print(f"  → Found {result.get('chunks_count', 0)} chunks in ChromaDB")
                
                return {
                    "resume_processed": True,
                    "resume_text": resume_text,
                    "current_phase": "ingestion"
                }
                
            else:
                # ✅ HANDLE FILE UPLOAD MODE
                print("  → Mode: File upload (processing PDF)")
                
                # FILE VALIDATION
                if not Path(resume_pdf_path).exists():
                    raise FileNotFoundError(f"Resume file not found: {resume_pdf_path}")
                
                # Run profiler with session isolation
                result = await self.agents["profiler"].run(
                    resume_pdf_path,
                    session_id=session_id
                )
                
                # RESULT VALIDATION
                if not result.get("success"):
                    raise ValueError(f"Profiler failed: {result.get('error', 'Unknown error')}")
                
                resume_text = result.get("resume_text", "")
                
                # TEXT LENGTH VALIDATION
                if not resume_text or len(resume_text) < 100:
                    raise ValueError(f"Resume text too short or empty ({len(resume_text)} chars)")
                
                print(f"  ✓ Profiler completed successfully")
                print(f"  → Extracted {len(resume_text)} characters")
                print(f"  → Stored {result.get('chunks_stored', 0)} chunks in ChromaDB")
                
                return {
                    "resume_processed": True,
                    "resume_text": resume_text,
                    "current_phase": "ingestion"
                }
            
        except Exception as e:
            print(f"  ❌ Profiler failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "resume_processed": False,
                "resume_text": "",
                "errors": state.get("errors", []) + [f"Profiler error: {str(e)}"],
                "current_phase": "error"
            }
    
    async def decoder_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Decoder Agent - Phase 2"""
        print("\n🔵 NODE: Decoder Agent")
        
        # ✅ STATE VALIDATION (from Code 1)
        if not self._validate_state(state, "decoder"):
            return {
                "errors": state.get("errors", []) + ["Invalid state for decoder"],
                "current_phase": "error"
            }
        
        try:
            scout_data = state.get("scholarship_intelligence", {})
            combined_text = scout_data.get("combined_text", "")
            
            if not combined_text:
                print("  ⚠ No combined_text found, using raw intelligence")
                combined_text = str(scout_data)
            
            print(f"  → Analyzing {len(combined_text)} characters")
            
            analysis = await self.agents["decoder"].run(combined_text)
            
            print(f"  ✓ Decoder completed successfully")
            print(f"  → Primary values: {analysis.get('primary_values', [])}")
            
            return {
                "decoder_analysis": analysis,
                "current_phase": "analysis"
            }
        except Exception as e:
            print(f"  ❌ Decoder failed: {e}")
            return {
                "errors": state.get("errors", []) + [f"Decoder error: {str(e)}"],
                "current_phase": "error"
            }
    
    async def matchmaker_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Matchmaker Agent - Phase 2"""
        print("\n🔵 NODE: Matchmaker Agent")
        
        # ✅ STATE VALIDATION (from Code 1)
        if not self._validate_state(state, "matchmaker"):
            return {
                "errors": state.get("errors", []) + ["Invalid state for matchmaker"],
                "current_phase": "error"
            }
        
        session_id = state.get("session_id")
        print(f"  → Session ID: {session_id}")
        
        try:
            analysis = state.get("decoder_analysis", {})
            result = await self.agents["matchmaker"].run(
                analysis,
                session_id=session_id
            )
            
            print(f"  ✓ Matchmaker completed successfully")
            print(f"  → Match score: {result['match_score']:.0%}")
            print(f"  → Trigger interview: {result['trigger_interview']}")
            
            return {
                "match_score": result["match_score"],
                "trigger_interview": result["trigger_interview"],
                "identified_gaps": result["gaps"],
                "matchmaker_results": result,
                "current_phase": "matching"
            }
        except Exception as e:
            print(f"  ❌ Matchmaker failed: {e}")
            return {
                "errors": state.get("errors", []) + [f"Matchmaker error: {str(e)}"],
                "current_phase": "error"
            }
    
    def should_interview(self, state: ScholarshipState) -> str:
        """Conditional routing after matchmaker"""
        if state.get("trigger_interview", False):
            print("  🔀 Routing to: Interviewer (Gap detected)")
            return "interviewer"
        else:
            print("  🔀 Routing to: Optimizer (No significant gaps)")
            return "optimizer"
    
    async def interviewer_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Interviewer Agent - Phase 3"""
        print("\n🔵 NODE: Interviewer Agent")
        
        if state.get("bridge_story"):
            print("  ✓ Bridge story present, proceeding...")
            return {"current_phase": "interview_complete"}
        
        try:
            resume_text = state.get("resume_text", "")
            gaps = state.get("identified_gaps", [])
            weights = state.get("decoder_analysis", {}).get("hidden_weights", {})
            
            print(f"  → Generating question for gaps: {gaps}")
            
            result = await self.agents["interviewer"].run(resume_text, gaps, weights)
            
            print(f"  ✓ Interviewer generated question")
            
            return {
                "interview_question": result["question"],
                "current_phase": "interview"
            }
        except Exception as e:
            print(f"  ❌ Interviewer failed: {e}")
            return {
                "errors": state.get("errors", []) + [f"Interviewer error: {str(e)}"],
                "current_phase": "error"
            }
    
    async def optimizer_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Optimizer Agent - Phase 4"""
        print("\n🔵 NODE: Optimizer Agent")
        
        # ✅ STATE VALIDATION (from Code 1)
        if not self._validate_state(state, "optimizer"):
            return {
                "errors": state.get("errors", []) + ["Invalid state for optimizer"],
                "current_phase": "error"
            }
        
        try:
            resume_text = state.get("resume_text", "")
            decoder_output = state.get("decoder_analysis", {})
            
            # ✅ ADDITIONAL TEXT VALIDATION (from Code 1)
            if not resume_text or len(resume_text) < 100:
                print(f"  ⚠ WARNING: Resume text is empty or too short ({len(resume_text)} chars)")
                return {
                    "errors": state.get("errors", []) + ["Resume text not available for optimization"],
                    "current_phase": "error"
                }
            
            print(f"  → Optimizing resume ({len(resume_text)} chars)")
            
            result = await self.agents["optimizer"].run(resume_text, decoder_output)
            
            markdown = result.get("optimized_resume_markdown", "")
            
            print(f"  ✓ Optimizer completed successfully")
            print(f"  → Generated markdown: {len(markdown)} chars")
            
            if not markdown:
                print(f"  ⚠ WARNING: No markdown generated!")
            
            return {
                "resume_optimizations": result["optimizations"],
                "optimized_resume_markdown": markdown,
                "current_phase": "generation"
            }
        except Exception as e:
            print(f"  ❌ Optimizer failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "errors": state.get("errors", []) + [f"Optimizer error: {str(e)}"],
                "current_phase": "error"
            }
    
    async def ghostwriter_node(self, state: ScholarshipState) -> ScholarshipState:
        """Execute Ghostwriter Agent - Phase 4"""
        print("\n🔵 NODE: Ghostwriter Agent")
        
        # ✅ STATE VALIDATION (from Code 1)
        if not self._validate_state(state, "ghostwriter"):
            return {
                "errors": state.get("errors", []) + ["Invalid state for ghostwriter"],
                "current_phase": "error"
            }
        
        try:
            decoder_output = state.get("decoder_analysis", {})
            resume_text = state.get("resume_text", "")
            bridge_story = state.get("bridge_story")
            
            print(f"  → Writing essay with bridge story: {bool(bridge_story)}")
            
            result = await self.agents["ghostwriter"].run(
                decoder_output=decoder_output,
                resume_text=resume_text,
                bridge_story=bridge_story
            )
            
            essay = result.get("essay", "")
            
            print(f"  ✓ Ghostwriter completed successfully")
            print(f"  → Essay length: {len(essay)} chars")
            
            return {
                "essay_draft": essay,
                "strategy_note": result["strategy_note"],
                "current_phase": "complete"
            }
        except Exception as e:
            print(f"  ❌ Ghostwriter failed: {e}")
            return {
                "errors": state.get("errors", []) + [f"Ghostwriter error: {str(e)}"],
                "current_phase": "error"
            }
    
    async def run(
        self,
        scholarship_url: str,
        resume_pdf_path: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Execute the full workflow"""
        print("=" * 80)
        print(f"🚀 Starting Scholarship Workflow")
        print(f"  → Session: {session_id}")
        print(f"  → Scholarship: {scholarship_url}")
        print(f"  → Resume: {resume_pdf_path}")
        print("=" * 80)
        
        initial_state = ScholarshipState(
            scholarship_url=scholarship_url,
            resume_pdf_path=resume_pdf_path,
            session_id=session_id,
            current_phase="start",
            errors=[]
        )
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            print("\n" + "=" * 80)
            print(f"✅ Workflow execution complete")
            print(f"  → Final phase: {final_state.get('current_phase')}")
            print(f"  → Errors: {len(final_state.get('errors', []))}")
            print("=" * 80)
            
            return final_state
            
        except Exception as e:
            print(f"\n❌ Workflow execution failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                **initial_state,
                "errors": [f"Workflow error: {str(e)}"],
                "current_phase": "error"
            }
    
    async def resume_after_interview(
        self,
        bridge_story: str,
        checkpoint_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resume workflow after receiving student's bridge story"""
        print("=" * 80)
        print("🔄 Resuming workflow with bridge story")
        print("=" * 80)
        
        # ✅ CHECKPOINT VALIDATION (from Code 1)
        required_keys = ["resume_text", "decoder_analysis"]
        missing_keys = [k for k in required_keys if not checkpoint_state.get(k)]
        
        if missing_keys:
            print(f"  ⚠ WARNING: Missing required state keys: {missing_keys}")
            return {
                **checkpoint_state,
                "errors": checkpoint_state.get("errors", []) + [f"Missing state: {missing_keys}"],
                "current_phase": "error"
            }
        
        checkpoint_state["bridge_story"] = bridge_story
        
        print(f"  → Bridge story length: {len(bridge_story)} chars")
        
        # Execute remaining phases
        print("\n[Manual Execution] Running Optimizer...")
        opt_state = await self.optimizer_node(checkpoint_state)
        
        if opt_state.get("current_phase") == "error":
            print("  ❌ Optimizer failed, stopping workflow")
            return {**checkpoint_state, **opt_state}
        
        checkpoint_state = {**checkpoint_state, **opt_state}
        
        print("\n[Manual Execution] Running Ghostwriter...")
        gw_state = await self.ghostwriter_node(checkpoint_state)
        
        if gw_state.get("current_phase") == "error":
            print("  ❌ Ghostwriter failed, stopping workflow")
            return {**checkpoint_state, **gw_state}
        
        checkpoint_state = {**checkpoint_state, **gw_state}
        
        print("\n" + "=" * 80)
        print(f"✅ Workflow resume complete")
        print(f"  → Has optimized resume: {bool(checkpoint_state.get('optimized_resume_markdown'))}")
        print(f"  → Has essay draft: {bool(checkpoint_state.get('essay_draft'))}")
        print("=" * 80)
        
        return checkpoint_state