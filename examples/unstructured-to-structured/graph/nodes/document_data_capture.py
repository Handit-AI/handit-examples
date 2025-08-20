"""
Document Data Capture Node for LangGraph

This node processes any type of unstructured documents and extracts structured data
using AI-powered data extraction. It can handle invoices, contracts, reports,
medical documents, or any other document types.

The node uses the inferred schema to map document content to structured fields,
supporting both text and image-based documents through multimodal processing.

Key Features:
- Multimodal document processing (images, PDFs, text files)
- AI-powered data extraction using inferred schemas
- Structured JSON output with field mapping and validation
- Comprehensive error handling and logging
- Integration with Handit.ai for tracking and monitoring
- Support for various file formats and encodings

Processing Flow:
1. Document validation and file existence checks
2. Content reading based on file type (image, PDF, text)
3. Multimodal message construction for AI processing
4. Schema-based data extraction using AI models
5. Structured JSON output generation and storage
6. Tracking and monitoring integration
"""

from typing import Any, Dict
import os
import json
from pathlib import Path
import base64
from langchain_core.messages import HumanMessage
from graph.chains.document_data_extraction import document_data_extractor
from graph.state import GraphState

# Get system and user prompts from the chain
from graph.chains.document_data_extraction import get_system_prompt, get_user_prompt

# Handit.ai
from services.handit_service import tracker

def read_document_content(file_path: str) -> str:
    """
    Read document content for vLLM processing.
    
    This function handles different file types and converts them to appropriate
    formats for AI processing. Images are converted to base64 data URLs,
    PDFs are marked for future processing, and text files are read directly.
    
    Args:
        file_path: Path to the document file to be processed
        
    Returns:
        str: Processed content ready for AI analysis
        
    Supported Formats:
        - Images: PNG, JPG, JPEG, GIF, BMP (converted to base64)
        - PDFs: Marked for future processing
        - Text: Direct content reading with encoding fallbacks
        - Binary: Error markers for unsupported formats
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    if extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
        # For images, read as base64 for vLLM vision processing
        try:
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
                # Encode as base64 string for AI vision models
                base64_string = base64.b64encode(image_bytes).decode('utf-8')
                return f"data:image/{extension[1:]};base64,{base64_string}"
        except Exception as e:
            print(f"❌ Error reading image file {file_path}: {str(e)}")
            return f"[ERROR_READING_IMAGE: {file_path.name}] - {str(e)}"
    
    elif extension == '.pdf':
        # For PDFs, mark for future processing (could be extended to convert pages to images)
        return f"[PDF_FILE: {file_path.name}] - PDF processing required"
    
    else:
        # For text files, read directly with encoding fallbacks
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

def document_data_capture(state: GraphState) -> Dict[str, Any]:
    """
    Main node function to capture structured data from any type of documents.
    
    This function orchestrates the complete document processing pipeline:
    1. Validates input documents and creates output directories
    2. Processes each document using AI-powered extraction
    3. Maps document content to the inferred schema
    4. Generates structured JSON outputs
    5. Integrates with tracking and monitoring systems
    
    The function handles various document types including images, PDFs, and text
    files, ensuring robust processing with comprehensive error handling.
    
    Args:
        state: GraphState containing session information, document paths, and inferred schema
        
    Returns:
        Dict[str, Any]: Updated state with structured JSON paths and any processing errors
        
    Raises:
        Exception: Various exceptions during file processing or AI extraction
                 (all caught and handled gracefully with error logging)
    """
    print("🔄 Starting document data capture...")
    
    # Extract session and document information from state
    session_id = state.get("session_id")
    document_paths = state.get("unstructured_paths", [])

    # App name and execution ID for Handit.ai Observability
    agent_name = state.get("agent_name")
    execution_id = state.get("execution_id")
    
    # Validate that documents are provided for processing
    if not document_paths:
        print("⚠️ No documents found to process")
        return {
            **state,
            "structured_json_paths": [],
            "errors": state.get("errors", []) + ["No documents found to process"],
        }
    
    # Create structured output directory for this session
    # This organizes outputs by session for better file management
    structured_dir = Path(f"assets/structured/{session_id}")
    structured_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created structured directory: {structured_dir}")
    
    # Initialize tracking variables for processing results
    structured_json_paths = []
    processing_errors = []
    
    # Retrieve and validate the inferred schema from previous processing stage
    # The schema is required to drive the field mapping process
    inferred_schema = state.get("inferred_schema")
    if not inferred_schema:
        print("❌ Missing inferred_schema in state; cannot perform mapping.")
        return {
            **state,
            "structured_json_paths": [],
            "errors": state.get("errors", []) + ["Missing inferred_schema in state"],
        }
    
    # Ensure schema is JSON-serializable for the mapping prompt
    # This handles both Pydantic models and raw dictionaries
    try:
        schema_json = inferred_schema.model_dump() if hasattr(inferred_schema, "model_dump") else inferred_schema
    except Exception:
        schema_json = inferred_schema
    schema_json_text = json.dumps(schema_json, ensure_ascii=False)

    # Process each document in the provided list
    for i, document_path in enumerate(document_paths):
        try:
            print(f"\n🔄 Processing document {i+1}/{len(document_paths)}: {Path(document_path).name}")
            
            # Validate file existence before processing
            if not os.path.exists(document_path):
                error_msg = f"File not found: {document_path}"
                print(f"❌ {error_msg}")
                processing_errors.append(error_msg)
                continue
            
            # Read file content and create multimodal input for AI processing
            file_path = Path(document_path)
            extension = file_path.suffix.lower()
            
            # Common instruction for all document types
            preface = "Map the document to the provided schema. Analyze layout first, use synonyms/semantic similarity; include reasons."
            
            if extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                # For images, create multimodal input combining text instructions with image data
                try:
                    with open(document_path, 'rb') as f:
                        image_bytes = f.read()
                    
                    # Build LangChain multimodal message with text and image content
                    messages = [
                        HumanMessage(content=[
                            {"type": "text", "text": preface},
                            {"type": "image_url", "image_url": {"url": f"data:image/{extension[1:]};base64,{base64.b64encode(image_bytes).decode('utf-8')}"}},
                        ])
                    ]
                    print(f"🖼️ Image file detected: {extension}")
                    
                except Exception as e:
                    error_msg = f"Error reading image file {document_path}: {str(e)}"
                    print(f"❌ {error_msg}")
                    processing_errors.append(error_msg)
                    continue
                    
            elif extension == '.pdf':
                # PDFs: pass as a marker for future processing
                # Future enhancement: convert PDF pages to images for processing
                messages = [HumanMessage(content=f"{preface}\n\n[PDF_FILE] {file_path.name}")]
                print(f"📄 PDF file detected: {extension}")
            else:
                # For text files, read content directly and create text-based messages
                try:
                    with open(document_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    # Build text message with document content
                    messages = [HumanMessage(content=f"{preface}\n\nDocument name: {file_path.name}\n\nContent:\n{text}")]
                    print(f"📄 Text file detected: {extension}")
                    
                except UnicodeDecodeError:
                    try:
                        # Try binary mode for other binary files
                        with open(document_path, 'rb') as f:
                            text = f"[BINARY_FILE: {file_path.name}] - Binary file, cannot extract text"
                        messages = [HumanMessage(content=f"Extract data using the system rules and schema.\n\nDocument name: {file_path.name}\n\nContent:\n{text}")]
                    except Exception as e:
                        error_msg = f"Error reading file {document_path}: {str(e)}"
                        print(f"❌ {error_msg}")
                        processing_errors.append(error_msg)
                        continue
            
            print(f"📄 Prepared document content for processing")
            
            print("🤖 Invoking document data extractor...")
            
            # Call the document data extraction chain with multimodal messages and schema
            # This is the core AI processing step that maps document content to structured fields
            extraction_result = document_data_extractor.invoke({"messages": messages, "schema_json": schema_json_text})
            
            print("✅ Document data extraction completed successfully!")
            
            # Convert extraction result to dictionary for JSON serialization
            # Handle both raw dictionaries and Pydantic model outputs
            result_dict = extraction_result if isinstance(extraction_result, dict) else getattr(extraction_result, "model_dump", lambda: {} )()
            
            # Create output filename and path for structured data
            original_filename = Path(document_path).stem  # Remove extension
            output_filename = f"{original_filename}.json"
            output_path = structured_dir / output_filename
            
            # Save structured data to JSON file with proper formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            
            structured_json_paths.append(str(output_path))
            print(f"💾 Saved structured data to: {output_path}")
            
            # Process images for tracking and monitoring purposes
            # This prepares image data for Handit.ai integration
            image_attachments = []
            print(f"🔍 Processing images for document: {Path(document_path).name} (extension: {extension})")
            
            if extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                try:
                    with open(document_path, 'rb') as f:
                        image_bytes = f.read()
                    
                    # Convert to base64 and create data URL (format that Handit.ai expects)
                    base64_data = base64.b64encode(image_bytes).decode('utf-8')
                    mime_type = f"image/{extension[1:]}" if extension[1:] != "jpg" else "image/jpeg"
                    data_url = f"data:{mime_type};base64,{base64_data}"
                    
                    image_attachments.append(data_url)
                    print(f"📸 Added image for tracking: {Path(document_path).name} ({len(data_url)} chars)")
                    print(f"📸 Image MIME type: {mime_type}")
                    print(f"📸 Base64 length: {len(base64_data)}")
                    
                except Exception as e:
                    print(f"❌ Error processing image for tracking: {str(e)}")
            else:
                print(f"📄 No image processing needed for file type: {extension}")
            
            print(f"🖼️ Total images in this cycle: {len(image_attachments)}")
            print(f"🖼️ Total len of this document: {len(data_url)}")
            
            # Prepare tracking input in the correct Handit.ai format
            # This includes system prompts, user prompts, schema, and document data
            tracking_input = {
                "systemPrompt": get_system_prompt(),
                "userPrompt": get_user_prompt(),
                "schema_json": schema_json_text,
                "document": data_url,
            }
            
            print(f"📤 Sending tracking data to Handit.ai:")
            print(f"   - Document: {Path(document_path).name}")
            
            # Track the processing operation with Handit.ai for monitoring and debugging
            tracker.track_node(
                 input=tracking_input,
                 output=result_dict,
                 node_name="document_data_capture",
                 agent_name=agent_name,
                 node_type="llm",
                 execution_id=execution_id
            )
            
        except Exception as e:
            # Comprehensive error handling for any processing failures
            error_msg = f"Error processing document {i+1}: {str(e)}"
            print(f"❌ {error_msg}")
            processing_errors.append(error_msg)
            continue
    
    # Generate processing summary and statistics
    print(f"\n📊 Processing Summary:")
    print(f"✅ Successfully processed: {len(structured_json_paths)} documents")
    print(f"❌ Errors encountered: {len(processing_errors)}")
    print(f"📁 Structured JSON files saved to: {structured_dir}")
    
    # Aggregate all processing errors for state management
    all_errors = state.get("errors", []) + processing_errors
    
    # Return updated state with structured JSON paths and error information
    # This allows subsequent nodes to access the processing results
    return {
        **state,
        "structured_json_paths": structured_json_paths,
        "errors": all_errors
    }
