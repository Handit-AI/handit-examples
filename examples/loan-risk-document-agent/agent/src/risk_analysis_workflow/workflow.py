"""Main LangGraph workflow for loan risk analysis."""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.risk_analysis_workflow.state import WorkflowState
from src.risk_analysis_workflow.nodes import (
    node_intake_and_classify,
    node_extract_per_type,
    node_get_identity,
    node_check_crossdoc,
    node_check_fraud_signals,
    node_score_and_reasons,
    node_compose_assistant_reply
)


def create_workflow() -> StateGraph:
    """Create the loan risk analysis workflow.
    
    Returns:
        Configured LangGraph workflow
    """
    # Create workflow with state schema
    workflow = StateGraph(WorkflowState)
    
    # Add all nodes
    workflow.add_node("classify", node_intake_and_classify)
    workflow.add_node("extract", node_extract_per_type)
    workflow.add_node("identity", node_get_identity)
    workflow.add_node("crossdoc", node_check_crossdoc)
    workflow.add_node("fraud", node_check_fraud_signals)
    workflow.add_node("score", node_score_and_reasons)
    workflow.add_node("compose", node_compose_assistant_reply)
    
    # Define the flow
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "identity")
    workflow.add_edge("identity", "crossdoc")
    workflow.add_edge("crossdoc", "fraud")
    workflow.add_edge("fraud", "score")
    workflow.add_edge("score", "compose")
    workflow.add_edge("compose", END)
    
    return workflow


def compile_workflow(workflow: StateGraph):
    """Compile the workflow with checkpointing.
    
    Args:
        workflow: The workflow to compile
    
    Returns:
        Compiled workflow ready for execution
    """
    # Create memory checkpointer for state persistence
    memory = MemorySaver()
    
    # Compile the workflow
    app = workflow.compile(checkpointer=memory)
    
    return app


def run_workflow(files: list, messages: list = None, options: dict = None) -> Dict[str, Any]:
    """Run the complete loan risk analysis workflow.
    
    Args:
        files: List of file dictionaries with 'content', 'type', and 'name'
        messages: Optional chat messages
        options: Optional processing options
    
    Returns:
        Complete assessment results
    """
    # Create and compile workflow
    workflow = create_workflow()
    app = compile_workflow(workflow)
    
    # Prepare initial state
    initial_state = {
        "files": files,
        "messages": messages or [],
        "options": options or {},
        "errors": [],
        "warnings": [],
        "checks": []
    }
    
    # Run the workflow
    config = {"configurable": {"thread_id": "loan-risk-analysis"}}
    
    print("\n" + "="*70)
    print(" STARTING LOAN RISK ANALYSIS WORKFLOW")
    print("="*70)
    print(f"Processing {len(files)} document(s)...")
    
    # Execute workflow
    final_state = None
    for state in app.stream(initial_state, config):
        # The state is returned as {node_name: state_data}
        for node_name, state_data in state.items():
            final_state = state_data
    
    print("\n" + "="*70)
    print(" WORKFLOW COMPLETED")
    print("="*70)
    
    return final_state


# Export main components
__all__ = [
    "create_workflow",
    "compile_workflow",
    "run_workflow"
]