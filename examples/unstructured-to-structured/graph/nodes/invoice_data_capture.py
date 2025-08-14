from typing import Any, Dict
import os
import json
from pathlib import Path
import base64
from langchain_core.messages import HumanMessage
from graph.chains.invoice_data_extraction import invoice_data_extractor
from graph.state import GraphState
from services.handit_service import tracker

def read_document_content(file_path: str) -> str:
    """Read document content for vLLM processing"""
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    if extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
        # For images, read as base64 for vLLM
        try:
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
                # Encode as base64 string
                base64_string = base64.b64encode(image_bytes).decode('utf-8')
                return f"data:image/{extension[1:]};base64,{base64_string}"
        except Exception as e:
            print(f"❌ Error reading image file {file_path}: {str(e)}")
            return f"[ERROR_READING_IMAGE: {file_path.name}] - {str(e)}"
    
    elif extension == '.pdf':
        # For PDFs, you might need to convert to images first
        return f"[PDF_FILE: {file_path.name}] - PDF processing required"
    
    else:
        # For text files, read directly
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Try binary mode for other binary files
                with open(file_path, 'rb') as f:
                    return f"[BINARY_FILE: {file_path.name}] - Binary file, cannot extract text"
            except Exception as e:
                return f"[ERROR_READING_FILE: {file_path.name}] - {str(e)}"

def invoice_data_capture(state: GraphState) -> Dict[str, Any]:
    """Node to capture invoice data using the invoice data extraction chain"""
    print("🔄 Starting invoice data capture...")
    
    session_id = state.get("session_id")
    invoices_paths = state.get("unstructured_paths", [])
    execution_id = state.get("execution_id")
    
    if not invoices_paths:
        print("⚠️ No documents found to process")
        return {
            **state,
            "structured_json_paths": [],
            "errors": state.get("errors", []) + ["No documents found to process"],
        }
    
    # Create structured output directory
    structured_dir = Path(f"assets/structured/{session_id}")
    structured_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created structured directory: {structured_dir}")
    
    structured_json_paths = []
    processing_errors = []
    
    # Required inferred schema to drive mapping
    inferred_schema = state.get("inferred_schema")
    if not inferred_schema:
        print("❌ Missing inferred_schema in state; cannot perform mapping.")
        return {
            **state,
            "structured_json_paths": [],
            "errors": state.get("errors", []) + ["Missing inferred_schema in state"],
        }
    # Ensure schema is JSON-serializable for the mapping prompt
    try:
        schema_json = inferred_schema.model_dump() if hasattr(inferred_schema, "model_dump") else inferred_schema
    except Exception:
        schema_json = inferred_schema
    schema_json_text = json.dumps(schema_json, ensure_ascii=False)

    for i, invoice_path in enumerate(invoices_paths):
        try:
            print(f"\n🔄 Processing invoice {i+1}/{len(invoices_paths)}: {Path(invoice_path).name}")
            
            # Check if file exists
            if not os.path.exists(invoice_path):
                error_msg = f"File not found: {invoice_path}"
                print(f"❌ {error_msg}")
                processing_errors.append(error_msg)
                continue
            
            # Read file content and create multimodal input
            file_path = Path(invoice_path)
            extension = file_path.suffix.lower()
            
            preface = "Map the document to the provided schema. Analyze layout first, use synonyms/semantic similarity; include reasons."
            if extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                # For images, create multimodal input similar to openai_client.py
                try:
                    with open(invoice_path, 'rb') as f:
                        image_bytes = f.read()
                    
                    # Build LangChain multimodal message
                    messages = [
                        HumanMessage(content=[
                            {"type": "text", "text": preface},
                            {"type": "image_url", "image_url": {"url": f"data:image/{extension[1:]};base64,{base64.b64encode(image_bytes).decode('utf-8')}"}},
                        ])
                    ]
                    print(f"🖼️ Image file detected: {extension}")
                    
                except Exception as e:
                    error_msg = f"Error reading image file {invoice_path}: {str(e)}"
                    print(f"❌ {error_msg}")
                    processing_errors.append(error_msg)
                    continue
                    
            elif extension == '.pdf':
                # PDFs: pass as a marker; recommend page rendering in future
                messages = [HumanMessage(content=f"{preface}\n\n[PDF_FILE] {file_path.name}")]
                print(f"📄 PDF file detected: {extension}")
            else:
                # For text files, read directly
                try:
                    with open(invoice_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    # Build text message
                    messages = [HumanMessage(content=f"{preface}\n\nDocument name: {file_path.name}\n\nContent:\n{text}")]
                    print(f"📄 Text file detected: {extension}")
                    
                except UnicodeDecodeError:
                    try:
                        # Try binary mode for other binary files
                        with open(invoice_path, 'rb') as f:
                            text = f"[BINARY_FILE: {file_path.name}] - Binary file, cannot extract text"
                        messages = [HumanMessage(content=f"Extract invoice data using the system rules and schema.\n\nDocument name: {file_path.name}\n\nContent:\n{text}")]
                    except Exception as e:
                        error_msg = f"Error reading file {invoice_path}: {str(e)}"
                        print(f"❌ {error_msg}")
                        processing_errors.append(error_msg)
                        continue
            
            print(f"📄 Prepared document content for processing")
            
            print("🤖 Invoking invoice data extractor...")
            
            # Call the invoice data extraction chain with multimodal messages
            extraction_result = invoice_data_extractor.invoke({"messages": messages, "schema_json": schema_json_text})
            
            print("✅ Invoice data extraction completed successfully!")
            
            # Convert to dictionary for JSON serialization
            result_dict = extraction_result if isinstance(extraction_result, dict) else getattr(extraction_result, "model_dump", lambda: {} )()
            
            # Create output filename
            original_filename = Path(invoice_path).stem  # Remove extension
            output_filename = f"{original_filename}.json"
            output_path = structured_dir / output_filename
            
            # Save structured data to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            
            structured_json_paths.append(str(output_path))
            print(f"💾 Saved structured data to: {output_path}")
            
            # Log some key extracted information
            if result_dict.get("invoice_id", {}).get("value"):
                invoice_id = result_dict["invoice_id"]["value"]
                print(f"📋 Extracted Invoice ID: {invoice_id}")
            
            if result_dict.get("grand_total", {}).get("value"):
                total = result_dict["grand_total"]["value"]
                currency = result_dict["grand_total"].get("currency", "Unknown")
                print(f"💰 Grand Total: {total} {currency}")
            
            # Track the LLM call
            tracker.track_node(
                 input="hola",
                 output=result_dict,
                 node_name="invoice_data_capture",
                 agent_name="unstructured_to_structured",
                 node_type="llm",
                 execution_id=execution_id
            )    
            
        except Exception as e:
            error_msg = f"Error processing invoice {i+1}: {str(e)}"
            print(f"❌ {error_msg}")
            processing_errors.append(error_msg)
            continue
    
    # Summary
    print(f"\n📊 Processing Summary:")
    print(f"✅ Successfully processed: {len(structured_json_paths)} invoices")
    print(f"❌ Errors encountered: {len(processing_errors)}")
    print(f"📁 Structured JSON files saved to: {structured_dir}")
    
    # Add any processing errors to state errors
    all_errors = state.get("errors", []) + processing_errors
    
    # Return updated state with structured JSON paths
    return {
        **state,
        "structured_json_paths": structured_json_paths,
        "errors": all_errors
    }
