from __future__ import annotations

from typing import Dict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from graph.state import GraphState
from graph.nodes.generate_csv import generate_csv
from graph.nodes.save_csv import save_csv


load_dotenv()


def collect_json_paths(state: GraphState) -> GraphState:
    """No-op node that ensures json_paths are present in the state.

    This node simply passes through the state; useful to test wiring.
    """

    json_paths = state.get("json_paths") or []
    # Ensure list type
    state["json_paths"] = list(json_paths)
    return state


# Initialize the graph
workflow = StateGraph(GraphState)

workflow.add_node("collect", collect_json_paths)

# Entry point
workflow.set_entry_point("collect")

# Direct edge to END
workflow.add_edge("collect", END)

app = workflow.compile()


def run_test_graph(json_paths: list[str]) -> Dict:
    """Helper to run the simple graph with provided json paths."""
    initial: GraphState = {"json_paths": json_paths}
    return app.invoke(initial)


def run_csv_graph(session_id: str, json_paths: list[str]) -> Dict:
    """Run a minimal graph that executes generate_csv then save_csv and returns state."""
    import logging
    logger = logging.getLogger("graph.csv_workflow")
    
    logger.info("🚀 Creating CSV workflow with session_id=%s, json_paths=%d", session_id, len(json_paths))
    
    csv_workflow = StateGraph(GraphState)
    csv_workflow.add_node("generate_csv", generate_csv)
    csv_workflow.add_node("save_csv", save_csv)
    csv_workflow.set_entry_point("generate_csv")
    csv_workflow.add_edge("generate_csv", "save_csv")
    csv_workflow.add_edge("save_csv", END)
    csv_app = csv_workflow.compile()
    
    initial: GraphState = {"session_id": session_id, "json_paths": json_paths}
    logger.info("📤 Initial state: %s", list(initial.keys()))
    
    result = csv_app.invoke(initial)
    logger.info("📥 Final state: %s", list(result.keys()))
    
    return result
