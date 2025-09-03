"""
Inference Schema Node for LangGraph

This module handles the automatic inference of JSON schemas from unstructured documents.
It processes multimodal content including images, PDFs, and text files to generate
a unified schema that can represent all provided documents.

The node uses LLM capabilities to analyze document layouts and content,
then generates a structured JSON schema with field definitions and synonyms.
"""

from typing import Any, Dict, List
import os
import base64
from pathlib import Path
from langchain_core.messages import HumanMessage

from graph.chains.document_inference import schema_inferencer, get_system_prompt
from graph.state import GraphState




def _build_multimodal_human_message(file_paths: List[str]) -> HumanMessage:
    """Build a single HumanMessage with multimodal content covering all documents.

    This function creates a comprehensive message that includes:
    - Text instructions for schema inference
    - Image content as base64 data URLs for vision analysis
    - PDF file references (for future extension)
    - Full text content from text files
    - Error handling for missing or corrupted files

    Args:
        file_paths: List of file paths to process for schema inference

    Returns:
        HumanMessage: A multimodal message containing all document content and instructions

    Note:
        Images are converted to base64 data URLs to enable the LLM's vision capabilities
        for analyzing document layouts and extracting structured information.
    """
    content: List[Dict[str, Any]] = []

    # Keep instruction neutral and general
    content.append({
        "type": "text",
        "text": (
            "Infer a general JSON schema that can represent the following documents (any types, any languages). "
            "For each field, always provide synonyms derived from the documents, and do not include confidence fields. "
            "When later mapping, values must use normalized_value when present, else value."
        ),
    })

    for file_path in file_paths:
        try:
            if not os.path.exists(file_path):
                content.append({"type": "text", "text": f"[MISSING_FILE] {file_path}"})
                continue

            p = Path(file_path)
            ext = p.suffix.lower()

            content.append({"type": "text", "text": f"[DOCUMENT] {p.name}"})

            # Process image files by converting to base64 data URLs
            if ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
                with open(p, "rb") as f:
                    b = f.read()
                data_url = f"data:image/{ext[1:]};base64,{base64.b64encode(b).decode('utf-8')}"
                content.append({"type": "image_url", "image_url": {"url": data_url}})
                continue

            # Handle PDF files (currently just referenced, could be extended later)
            if ext == ".pdf":
                content.append({"type": "text", "text": f"[PDF_FILE] {p.name}"})
                continue

            # Process text files by reading full content
            try:
                with open(p, "r", encoding="utf-8") as f:
                    content_text = f.read()
                content.append({"type": "text", "text": content_text})
            except Exception:
                content.append({"type": "text", "text": f"[BINARY_FILE] {p.name}"})

        except Exception as e:
            content.append({"type": "text", "text": f"[ERROR] {file_path}: {str(e)}"})

    return HumanMessage(content=content)


def inference_schema(state: GraphState) -> Dict[str, Any]:
    """Infer a robust, unified schema from all provided documents and attach it to state.

    This is the main entry point for schema inference. It processes all documents
    in the state, builds a multimodal message, and invokes the LLM for schema generation.

    The function handles:
    - Document validation and preprocessing
    - Multimodal message construction
    - LLM invocation for schema inference
    - Result processing and state updates
    - Comprehensive error handling

    Args:
        state: GraphState containing session information and document paths

    Returns:
        Dict[str, Any]: Updated state with 'inferred_schema' key containing the generated schema

    Raises:
        Exception: Various exceptions during file processing or LLM invocation
                 (all caught and handled gracefully)

    Example:
        >>> state = {"session_id": "123", "unstructured_paths": ["doc1.pdf", "doc2.jpg"]}
        >>> result = inference_schema(state)
        >>> "inferred_schema" in result
        True
    """
    print("---SCHEMA INFERENCE STARTED---")

    session_id = state["session_id"]
    unstructured_paths = state.get("unstructured_paths", [])



    print(f"Session ID: {session_id}")
    print(f"Documents provided: {len(unstructured_paths)}")

    try:
        # Validate that documents are provided
        if not unstructured_paths:
            print("No documents provided for schema inference")
            return {
                **state,
                "inferred_schema": {},
                "errors": state.get("errors", []) + ["No documents provided for schema inference"],
            }

        # Build multimodal message containing all document content
        human_message = _build_multimodal_human_message(unstructured_paths)
        print("Invoking schema inferencer (multimodal)…")

        # Invoke the LLM to generate the schema
        schema_result = schema_inferencer.invoke({"messages": [human_message]})

        print("Schema inference completed successfully!")

        # Process and display the schema result
        print(f"🔍 Schema result: {schema_result}")
        
        # Return updated state with inferred schema
        # Ensure we store plain JSON in state
        inferred_schema = schema_result.model_dump() if hasattr(schema_result, "model_dump") else schema_result


        
        # Display final schema result and return updated state
        print(f"🔍 Schema JSON result: {schema_result}")
        return {**state, "inferred_schema": inferred_schema}

    except Exception as e:
        # Comprehensive error handling with detailed error messages
        error_msg = f"Error during schema inference: {str(e)}"
        print(f"❌ {error_msg}")

        # Return state with error information for debugging
        return {
            **state,
            "inferred_schema": {},
            "errors": state.get("errors", []) + [error_msg],
        }
