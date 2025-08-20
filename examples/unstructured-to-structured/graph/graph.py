"""
LangGraph Workflow for Document Processing Pipeline

This module defines the main workflow graph that orchestrates the complete document
processing pipeline from unstructured documents to structured CSV outputs.

The workflow consists of three main stages:
1. Schema Inference: AI analyzes documents to create a unified JSON schema
2. Data Capture: Documents are mapped to the inferred schema using AI extraction
3. CSV Generation: Structured data is converted to organized CSV tables

The graph uses LangGraph's StateGraph to manage state transitions and ensure
proper data flow between processing stages. Each node maintains and updates
the shared GraphState, allowing for seamless data passing and error handling.

Architecture:
- StateGraph: Manages workflow state and transitions
- MemorySaver: Provides checkpointing for workflow persistence
- Nodes: Individual processing units with specific responsibilities
- Edges: Define the flow and dependencies between processing stages
"""

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
# from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph

from graph.consts import INFERENCE_SCHEMA, DOCUMENT_DATA_CAPTURE, GENERATE_CSV
from graph.nodes.inference_schema import inference_schema
from graph.nodes.document_data_capture import document_data_capture
from graph.nodes.generate_csv import generate_csv
from graph.state import GraphState


# Load environment variables (API keys, configuration)
load_dotenv()


# Initialize the main workflow graph using StateGraph
# StateGraph manages the state transitions and data flow between nodes
workflow = StateGraph(GraphState)


# Add processing nodes to the workflow
# Each node represents a distinct stage in the document processing pipeline
workflow.add_node(INFERENCE_SCHEMA, inference_schema)        # Stage 1: Schema generation
workflow.add_node(DOCUMENT_DATA_CAPTURE, document_data_capture)  # Stage 2: Data extraction
workflow.add_node(GENERATE_CSV, generate_csv)                # Stage 3: CSV output

# Set the entry point for the workflow
# All processing begins with schema inference to establish the data structure
workflow.set_entry_point(INFERENCE_SCHEMA)

# Define the workflow edges (processing flow)
# Each edge represents the data flow and dependencies between processing stages
workflow.add_edge(INFERENCE_SCHEMA, DOCUMENT_DATA_CAPTURE)  # Schema → Data extraction
workflow.add_edge(DOCUMENT_DATA_CAPTURE, GENERATE_CSV)      # Data extraction → CSV generation
workflow.add_edge(GENERATE_CSV, END)                       # CSV generation → Workflow completion

# Compile the workflow into an executable application
# This creates the final workflow that can be invoked with input data
app = workflow.compile()

# Optional: Generate a visual representation of the workflow graph
# Uncomment to create a Mermaid diagram showing the workflow structure
# app.get_graph().draw_mermaid_png(output_file_path="graph.png")
