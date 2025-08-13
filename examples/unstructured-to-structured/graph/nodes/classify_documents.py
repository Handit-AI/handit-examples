from typing import Any, Dict
import os
from pathlib import Path

from graph.chains.classification import document_classifier
from graph.state import GraphState

from services.handit_service import tracker


def classify_documents(state: GraphState) -> Dict[str, Any]:
    """
    Classifies uploaded documents by type using the classification chain.
    Analyzes each document and determines its type, language, and confidence level.

    Args:
        state (GraphState): The current graph state containing session_id and unstructured_paths

    Returns:
        Dict[str, Any]: Updated state with classification_results
    """

    print("---DOCUMENT CLASSIFICATION STARTED---")
    
    session_id = state["session_id"]
    unstructured_paths = state["unstructured_paths"]
    execution_id = state["execution_id"]
    
    print(f"Session ID: {session_id}")
    print(f"Documents to classify: {len(unstructured_paths)}")
    
    try:
        # Prepare file information for classification
        file_info = []
        for file_path in unstructured_paths:
            if os.path.exists(file_path):
                filename = Path(file_path).name
                file_info.append(f"File: {filename}, Path: {file_path}")
            else:
                print(f"Warning: File not found: {file_path}")
        
        if not file_info:
            print("No valid files found for classification")
            return {
                **state,
                "classification_results": {},
                "errors": state.get("errors", []) + ["No valid files found for classification"]
            }
        
        # Prepare input for the classification chain
        classification_input = {
            "unstructured_paths": "\n".join(file_info)
        }
        
        print("Invoking document classifier...")
        
        # Call the classification chain
        classification_result = document_classifier.invoke(classification_input)
        
        print("Classification completed successfully!")
        print(f"Classified {len(classification_result.classifications)} documents")
        
        # Convert classifications to a dictionary format for easier access
        classification_results = {}
        invoices_paths = []
        
        for classification in classification_result.classifications:
            filename = classification.filename
            classification_results[filename] = {
                "document_type": classification.document_type,
                "confidence": classification.confidence,
                "language": classification.language,
                "reason": classification.reason
            }
            
            # Check if this is an invoice and add to invoices_paths
            if classification.document_type.lower() == "invoice":
                # Find the corresponding file path from unstructured_paths
                for file_path in unstructured_paths:
                    if Path(file_path).name == filename:
                        invoices_paths.append(file_path)
                        break
            
            print(f"📄 {filename}: {classification.document_type} ({classification.language}) - Confidence: {classification.confidence}")
        
        print(f"Classification results: {classification_results}")
        print(f"Invoices found: {len(invoices_paths)} - Paths: {invoices_paths}")

         # Track the LLM call
        tracker.track_node(
            input={
                "classification_input": classification_input,
                
                }
            ,
            output={"llm_result": classification_result, "classification_results": classification_results, "invoices_paths": invoices_paths},
            node_name="classify_documents",
            agent_name="unstructured_to_structured",
            node_type="llm",
            execution_id=execution_id
        )
        
        # Return updated state with classification results and invoices paths
        return {
            "classification_results": classification_results,
            "invoices_paths": invoices_paths
        }
        
    except Exception as e:
        error_msg = f"Error during document classification: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            "classification_results": {},
            "errors": state.get("errors", []) + [error_msg]
        }
