"""
CSV Generation Node for LangGraph

This node processes structured JSON data from document extraction and generates
organized CSV tables for data analysis and visualization. It uses AI-powered
planning to create meaningful table structures from heterogeneous document data.

The node performs intelligent table generation by:
- Loading and analyzing structured JSON data from previous processing stages
- Using AI to plan optimal table structures and groupings
- Converting complex nested data into flat, tabular formats
- Generating CSV files with proper data organization
- Providing fallback plans when AI processing fails

Key Features:
- AI-powered table structure planning
- Automatic CSV file generation
- Fallback processing for robustness
- Comprehensive logging and error handling
- Integration with Handit.ai for tracking and monitoring
- Support for various data structures and formats

Processing Flow:
1. Load structured JSON data from previous processing stage
2. Use AI to plan optimal table structures
3. Parse and validate AI-generated plans
4. Convert data to tabular format
5. Generate and save CSV files
6. Track operations and return results
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
from graph.state import GraphState
from graph.chains.generation import csv_generation_planner
# Get system and user prompts from the chain
from graph.chains.generation import get_system_prompt, get_user_prompt
# Handit.ai
from services.handit_service import tracker

logger = logging.getLogger(__name__)


def _save_tables_to_csv(tables: List[Dict[str, Any]], output_dir: Path) -> List[str]:
    """
    Save tables to CSV files and return list of generated file paths.
    
    This function converts the AI-generated table plans into actual CSV files
    using pandas DataFrame operations. It handles various data structures and
    provides comprehensive error handling for each table.
    
    Args:
        tables: List of table dictionaries containing name, description, and data_dict
        output_dir: Directory path where CSV files will be saved
        
    Returns:
        List[str]: List of file paths for successfully generated CSV files
        
    Table Structure Expected:
        Each table should have:
        - name: Table identifier (used for filename)
        - description: Human-readable table description
        - data_dict: Dictionary where keys are column names and values are lists of data
    """
    generated_files = []
    
    for table in tables:
        table_name = table.get("name", "unknown")
        data_dict = table.get("data_dict", {})
        
        if not data_dict:
            logger.warning(f"⚠️ No data_dict found for table {table_name}")
            continue
        
        try:
            # Convert data_dict to pandas DataFrame for CSV generation
            # This handles the conversion from nested dictionary to tabular format
            df = pd.DataFrame(data_dict)
            
            # Save DataFrame to CSV file with table name as filename
            csv_path = output_dir / f"{table_name}.csv"
            df.to_csv(csv_path, index=False)
            generated_files.append(str(csv_path))
            
            logger.info(f"💾 Saved CSV: {csv_path} with {len(df)} rows and {len(df.columns)} columns")
            
        except Exception as e:
            logger.error(f"❌ Error saving table {table_name}: {e}")
    
    return generated_files


def generate_csv(state: GraphState) -> Dict[str, Any]:
    """
    Generate structured tables using LLM, process them, and save as CSV files.
    
    This is the main function that orchestrates the complete CSV generation pipeline.
    It loads structured JSON data, uses AI to plan table structures, converts data
    to tabular format, and generates CSV files for data analysis.
    
    The function includes robust error handling with fallback plans when AI processing
    fails, ensuring reliable CSV generation even in error conditions.
    
    Args:
        state: GraphState containing session information and structured JSON paths
        
    Returns:
        Dict[str, Any]: Updated state with CSV generation results, including:
            - csv_generation_status: 'completed', 'skipped', or 'error'
            - csv_generation_message: Human-readable status description
            - generated_tables: AI-generated table structures
            - llm_plan: Complete AI planning response
            - csv_output_dir: Directory containing generated CSV files
            - generated_csv_files: List of generated CSV file paths
            
    Processing Stages:
        1. Data Loading: Load structured JSON data from previous processing
        2. AI Planning: Use LLM to plan optimal table structures
        3. Response Parsing: Handle various LLM response formats
        4. Table Generation: Convert planned structures to actual tables
        5. CSV Export: Save tables as CSV files
        6. Tracking: Monitor operations with Handit.ai
    """
    logger.info("🔄 Starting table generation...")
    
    try:
        # Extract session and processing information from state
        session_id = state.get("session_id")
        structured_json_paths = state.get("structured_json_paths", [])

        # App name and execution ID for Handit.ai observability
        agent_name = state.get("agent_name")
        execution_id = state.get("execution_id")
        
        # Validate that structured JSON data is available for processing
        if not structured_json_paths:
            return {
                **state,
                'csv_generation_status': 'skipped',
                'csv_generation_message': 'No JSON files to process'
            }
        
        logger.info(f"📊 Processing {len(structured_json_paths)} JSON files")
        
        # Step 1: Load all JSON files completely for LLM processing
        # This ensures the AI has access to complete document data for planning
        all_json_data = []
        for json_path in structured_json_paths:
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                
                filename = Path(json_path).name
                all_json_data.append({
                    "filename": filename,
                    "data": json_data
                })
                logger.info(f"📄 Loaded complete JSON: {filename}")
                
            except Exception as e:
                logger.error(f"❌ Error loading JSON file {json_path}: {e}")
                continue
        
        logger.info(f"📋 Loaded {len(all_json_data)} complete JSON files for LLM")
        
        # Step 2: Get structured tables from LLM with complete data
        # This is the core AI processing step that plans optimal table structures
        try:
            logger.info("🤖 Getting structured tables from LLM with complete JSON data...")
            llm_response = csv_generation_planner.invoke({
                "documents_inventory": all_json_data
            })
            
            logger.info(f"🤖 Raw LLM response: {llm_response}")
            logger.info(f"🤖 Response type: {type(llm_response)}")
            
            # Parse LLM response with robust error handling
            # Handle different response formats (AIMessage, string, structured object)
            if hasattr(llm_response, 'content'):
                # This is an AIMessage, extract the content for JSON parsing
                response_content = llm_response.content
                logger.info(f"🤖 Extracted content from AIMessage: {response_content}")
                
                try:
                    plan = json.loads(response_content)
                    logger.info("✅ Successfully parsed JSON from LLM response content")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse JSON from LLM response content: {e}")
                    logger.info("📋 Using fallback plan")
                    plan = _create_simple_plan(structured_json_paths)
            elif isinstance(llm_response, str):
                # Try to extract JSON from string response
                try:
                    plan = json.loads(llm_response)
                    logger.info("✅ Successfully parsed JSON from LLM response")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse JSON from LLM response: {e}")
                    logger.info("📋 Using fallback plan")
                    plan = _create_simple_plan(structured_json_paths)
            else:
                # Assume structured response (dict, list, etc.)
                plan = llm_response
                logger.info("✅ LLM returned structured response")
            
            logger.info(f"📋 Final plan: {json.dumps(plan, indent=2)}")
            
        except Exception as e:
            # Comprehensive error handling for LLM processing failures
            logger.error(f"❌ LLM planning failed: {e}")
            plan = _create_simple_plan(structured_json_paths)
            logger.info("📋 Using fallback plan")
        
        # Step 3: Extract table information from the AI-generated plan
        tables = plan.get("tables", [])
        logger.info(f"📊 Found {len(tables)} tables to display")
        
        # Display processing summary to console
        print(f"\n🚀 GENERATING STRUCTURED TABLES FOR SESSION: {session_id}")
        print(f"📁 Processing {len(structured_json_paths)} documents")
        print(f"📊 LLM generated {len(tables)} tables\n")
        
        # Step 4: Save tables to CSV files in organized directory structure
        output_dir = Path(f"assets/csv/{session_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"💾 Output directory: {output_dir}")
        
        # Generate CSV files from the planned table structures
        generated_files = _save_tables_to_csv(tables, output_dir)
        logger.info(f"💾 Generated {len(generated_files)} CSV files")
        
        # Step 5: Track operations and prepare return results
        
        # Prepare tracking input with complete JSON data for Handit.ai monitoring
        tracking_input = {
            "systemPrompt": get_system_prompt(),
            "userPrompt": get_user_prompt(),
            "documents_inventory": all_json_data
        }
        
        # Track the CSV generation operation for observability and debugging
        tracker.track_node(
            input=tracking_input,
            output={"tables": tables, "plan": plan, "generated_files": generated_files},
            node_name="generate_csv",
            agent_name=agent_name,
            node_type="llm",
            execution_id=execution_id
        )

        logger.info("✅ Table generation completed")
        
        # Return comprehensive results including status, tables, and file information
        return {
            **state,
            'csv_generation_status': 'completed',
            'csv_generation_message': f'Generated and displayed {len(tables)} tables, saved {len(generated_files)} CSV files',
            'generated_tables': tables,
            'llm_plan': plan,
            'csv_output_dir': str(output_dir),
            'generated_csv_files': generated_files
        }
        
    except Exception as e:
        # Global error handling for any unexpected failures
        logger.error(f"❌ Table generation failed: {e}")
        return {
            **state,
            'csv_generation_status': 'error',
            'csv_generation_message': f'Error: {str(e)}'
        }


def _create_simple_plan(structured_json_paths: List[str]) -> Dict[str, Any]:
    """
    Create a simple fallback plan with basic structure when AI processing fails.
    
    This function provides a robust fallback mechanism that ensures CSV generation
    can continue even when the AI planning step encounters errors. It creates a
    basic table structure that provides useful information about the processed
    documents.
    
    Args:
        structured_json_paths: List of paths to structured JSON files
        
    Returns:
        Dict[str, Any]: Simple table plan with basic document overview
        
    Fallback Structure:
        Creates a single "general" table with:
        - source_file: Names of processed document files
        - document_count: Total count of processed documents
    """
    return {
        "tables": [
            {
                "name": "general",
                "description": "Basic document overview",
                "data_dict": {
                    "source_file": [Path(path).name for path in structured_json_paths],
                    "document_count": [len(structured_json_paths)] * len(structured_json_paths)
                }
            }
        ]
    }
