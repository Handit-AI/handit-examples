from typing import Any, Dict, List
import os
import base64
from pathlib import Path
from langchain_core.messages import HumanMessage

from graph.chains.document_inference import schema_inferencer, get_system_prompt
from graph.state import GraphState

from services.handit_service import tracker


def _build_multimodal_human_message(file_paths: List[str]) -> HumanMessage:
    """Build a single HumanMessage with multimodal content covering all documents.

    - Images are passed as base64 data URLs to enable vision + layout analysis
    - PDFs are referenced (could be extended later to images per page)
    - Text files include full content (up to a practical size)
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

            if ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
                with open(p, "rb") as f:
                    b = f.read()
                data_url = f"data:image/{ext[1:]};base64,{base64.b64encode(b).decode('utf-8')}"
                content.append({"type": "image_url", "image_url": {"url": data_url}})
                continue

            if ext == ".pdf":
                content.append({"type": "text", "text": f"[PDF_FILE] {p.name}"})
                continue

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

    Returns updated state with key 'inferred_schema'.
    """
    print("---SCHEMA INFERENCE STARTED---")

    session_id = state["session_id"]
    unstructured_paths = state.get("unstructured_paths", [])

    # App name for tracing
    agent_name = state.get("agent_name")

    # Execution id for tracing
    execution_id = state.get("execution_id")

    print(f"Session ID: {session_id}")
    print(f"Documents provided: {len(unstructured_paths)}")

    try:
        if not unstructured_paths:
            print("No documents provided for schema inference")
            return {
                **state,
                "inferred_schema": {},
                "errors": state.get("errors", []) + ["No documents provided for schema inference"],
            }

        human_message = _build_multimodal_human_message(unstructured_paths)
        print("Invoking schema inferencer (multimodal)…")

        schema_result = schema_inferencer.invoke({"messages": [human_message]})

        print("Schema inference completed successfully!")

      
   
        print(f"🔍 Schema result: {schema_result}")
        # Return updated state with inferred schema
        # Ensure we store plain JSON in state
        inferred_schema = schema_result.model_dump() if hasattr(schema_result, "model_dump") else schema_result


        # Track the LLM call
        system_prompt = get_system_prompt()
        
        # Create a clean version of user prompt for tracking (without heavy base64 data)
        clean_user_prompt = []
        for item in human_message.content:
            if item["type"] == "text":
                clean_user_prompt.append(item["text"])
            # Remove image processing since images are sent separately
        
        user_prompt_summary = " | ".join(clean_user_prompt)
        
        # Print both prompts for debugging
        print("🔧 SYSTEM PROMPT:")
        print(system_prompt)
        print("\n👤 USER PROMPT (CLEAN):")
        print(user_prompt_summary)
        print("\n" + "="*50)
        
        # Prepare input with images in the correct Handit.ai format
        tracking_input = {
            "systemPrompt": system_prompt,
            "userPrompt": user_prompt_summary,
            "images": []  # Will contain data URLs for each image
        }
        
        # Add images as data URLs in the correct format
        for file_path in unstructured_paths:
            try:
                if not os.path.exists(file_path):
                    continue
                    
                p = Path(file_path)
                ext = p.suffix.lower()
                
                # Only process image files
                if ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
                    with open(p, "rb") as f:
                        image_bytes = f.read()
                    
                    # Convert to base64 and create data URL (format that Handit.ai expects)
                    base64_data = base64.b64encode(image_bytes).decode('utf-8')
                    mime_type = f"image/{ext[1:]}" if ext[1:] != "jpg" else "image/jpeg"
                    data_url = f"data:{mime_type};base64,{base64_data}"
                    
                    tracking_input["images"].append(data_url)
                    print(f"📸 Added image: {p.name} ({len(data_url)} chars)")
                    
            except Exception as e:
                print(f"❌ Error processing image {file_path}: {str(e)}")
                continue
        
        print(f"🖼️ Total images in input: {len(tracking_input['images'])}")
        
        tracker.track_node(
            input=tracking_input,
            output= inferred_schema,
            node_name="inference_schema",
            agent_name= agent_name,
            node_type="llm",
            execution_id=execution_id,
        )
        print(f"🔍 Schema JSON result: {schema_result}")
        return {**state, "inferred_schema": inferred_schema}

    except Exception as e:
        error_msg = f"Error during schema inference: {str(e)}"
        print(f"❌ {error_msg}")

        return {
            **state,
            "inferred_schema": {},
            "errors": state.get("errors", []) + [error_msg],
        }
