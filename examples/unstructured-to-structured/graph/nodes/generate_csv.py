"""
Simple CSV Generation Node for LangGraph - Prints structured tables to console
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
from graph.state import GraphState
from graph.chains.generation import csv_generation_planner
from services.handit_service import tracker

logger = logging.getLogger(__name__)


def _collect_documents_summary(structured_json_paths: List[str]) -> str:
    """Create a comprehensive summary of documents for the LLM to analyze."""
    summaries = []
    
    for json_path in structured_json_paths:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            filename = Path(json_path).name
            summary = f"=== DOCUMENT: {filename} ===\n"
            
            # Analyze document structure
            if isinstance(data, dict):
                summary += f"Type: Dictionary with {len(data)} top-level keys\n"
                summary += f"Top-level keys: {list(data.keys())}\n\n"
                
                # Show structure of each top-level key
                for key, value in data.items():
                    if key in ['reason', 'confidence']:
                        continue
                    
                    if isinstance(value, dict):
                        if "normalized_value" in value or "value" in value:
                            # This is a field object
                            nv = value.get("normalized_value")
                            v = value.get("value")
                            summary += f"  {key}: FIELD_OBJECT"
                            if nv is not None:
                                summary += f" (normalized_value: {nv}, type: {type(nv).__name__})"
                            elif v is not None:
                                summary += f" (value: {v}, type: {type(v).__name__})"
                            else:
                                summary += f" (empty field object)"
                            summary += "\n"
                        else:
                            # Regular nested object
                            summary += f"  {key}: NESTED_OBJECT with keys: {list(value.keys())}\n"
                    elif isinstance(value, list):
                        summary += f"  {key}: ARRAY with {len(value)} items"
                        if value:
                            first_item = value[0]
                            if isinstance(first_item, dict):
                                summary += f" (first item keys: {list(first_item.keys())})"
                            else:
                                summary += f" (first item: {first_item})"
                        summary += "\n"
                    else:
                        summary += f"  {key}: {type(value).__name__} = {value}\n"
                
                # Show some sample nested structures
                summary += "\nSample nested structures:\n"
                for key, value in data.items():
                    if key in ['reason', 'confidence']:
                        continue
                    
                    if isinstance(value, dict) and len(value) > 0:
                        sample_key = list(value.keys())[0]
                        sample_value = value[sample_key]
                        summary += f"  {key}.{sample_key}: {type(sample_value).__name__} = {sample_value}\n"
                    elif isinstance(value, list) and len(value) > 0:
                        first_item = value[0]
                        if isinstance(first_item, dict) and len(first_item) > 0:
                            sample_key = list(first_item.keys())[0]
                            sample_value = first_item[sample_key]
                            summary += f"  {key}[0].{sample_key}: {type(sample_value).__name__} = {sample_value}\n"
                
            elif isinstance(data, list):
                summary += f"Type: Array with {len(data)} items\n"
                if data:
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        summary += f"First item keys: {list(first_item.keys())}\n"
                    else:
                        summary += f"First item: {first_item}\n"
            else:
                summary += f"Type: {type(data).__name__} = {data}\n"
            
            summaries.append(summary)
            
        except Exception as e:
            summaries.append(f"File: {json_path} - Error: {e}")
    
    return "\n\n".join(summaries)


def _print_table_to_console(table: Dict[str, Any]) -> None:
    """Print a table to console in a nice format."""
    table_name = table.get("name", "unknown")
    description = table.get("description", "No description")
    data_dict = table.get("data_dict", {})
    
    print(f"\n{'='*60}")
    print(f"📊 TABLE: {table_name.upper()}")
    print(f"📝 Description: {description}")
    print(f"{'='*60}")
    
    if not data_dict:
        print("⚠️  No data found in table")
        return
    
    # Get column names and data
    columns = list(data_dict.keys())
    if not columns:
        print("⚠️  No columns found in table")
        return
    
    # Get the length of the longest list to determine number of rows
    max_rows = max(len(data_dict[col]) for col in columns if isinstance(data_dict[col], list))
    
    if max_rows == 0:
        print("⚠️  No data rows found in table")
        return
    
    # Print header
    header = " | ".join(f"{col:20}" for col in columns)
    print(header)
    print("-" * len(header))
    
    # Print data rows
    for i in range(max_rows):
        row_data = []
        for col in columns:
            if isinstance(data_dict[col], list) and i < len(data_dict[col]):
                value = str(data_dict[col][i])
                if len(value) > 18:
                    value = value[:15] + "..."
                row_data.append(f"{value:20}")
            else:
                row_data.append(f"{'N/A':20}")
        
        print(" | ".join(row_data))
    
    print(f"\n📊 Total rows: {max_rows}")
    print(f"📊 Total columns: {len(columns)}")
    print(f"{'='*60}\n")


def _save_tables_to_csv(tables: List[Dict[str, Any]], output_dir: Path) -> List[str]:
    """Save tables to CSV files and return list of generated file paths."""
    generated_files = []
    
    for table in tables:
        table_name = table.get("name", "unknown")
        data_dict = table.get("data_dict", {})
        
        if not data_dict:
            logger.warning(f"⚠️ No data_dict found for table {table_name}")
            continue
        
        try:
            # Convert data_dict to DataFrame
            df = pd.DataFrame(data_dict)
            
            # Save to CSV
            csv_path = output_dir / f"{table_name}.csv"
            df.to_csv(csv_path, index=False)
            generated_files.append(str(csv_path))
            
            logger.info(f"💾 Saved CSV: {csv_path} with {len(df)} rows and {len(df.columns)} columns")
            
        except Exception as e:
            logger.error(f"❌ Error saving table {table_name}: {e}")
    
    return generated_files


def generate_csv(state: GraphState) -> Dict[str, Any]:
    """
    Generate structured tables using LLM, print them to console, and save as CSVs.
    """
    logger.info("🔄 Starting table generation...")
    
    try:
        # Get data from state
        session_id = state.get("session_id")
        structured_json_paths = state.get("structured_json_paths", [])
        execution_id = state.get("execution_id")
        
        if not structured_json_paths:
            return {
                **state,
                'csv_generation_status': 'skipped',
                'csv_generation_message': 'No JSON files to process'
            }
        
        logger.info(f"📊 Processing {len(structured_json_paths)} JSON files")
        
        # Step 1: Create document summary for LLM
        documents_summary = _collect_documents_summary(structured_json_paths)
        logger.info("📋 Created document summary for LLM")
        
        # Step 2: Get structured tables from LLM
        try:
            logger.info("🤖 Getting structured tables from LLM...")
            llm_response = csv_generation_planner.invoke({
                "documents_inventory": documents_summary
            })
            
            logger.info(f"🤖 Raw LLM response: {llm_response}")
            logger.info(f"🤖 Response type: {type(llm_response)}")
            
            # Parse LLM response
            if hasattr(llm_response, 'content'):
                # This is an AIMessage, extract the content
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
                # Try to extract JSON from response
                try:
                    plan = json.loads(llm_response)
                    logger.info("✅ Successfully parsed JSON from LLM response")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse JSON from LLM response: {e}")
                    logger.info("📋 Using fallback plan")
                    plan = _create_simple_plan(structured_json_paths)
            else:
                plan = llm_response
                logger.info("✅ LLM returned structured response")
            
            logger.info(f"📋 Final plan: {json.dumps(plan, indent=2)}")
            
        except Exception as e:
            logger.error(f"❌ LLM planning failed: {e}")
            plan = _create_simple_plan(structured_json_paths)
            logger.info("📋 Using fallback plan")
        
        # Step 3: Print tables to console
        tables = plan.get("tables", [])
        logger.info(f"📊 Found {len(tables)} tables to display")
        
        print(f"\n🚀 GENERATING STRUCTURED TABLES FOR SESSION: {session_id}")
        print(f"📁 Processing {len(structured_json_paths)} documents")
        print(f"📊 LLM generated {len(tables)} tables\n")
        
        for table in tables:
            _print_table_to_console(table)
        
        # Step 4: Save tables to CSV files
        output_dir = Path(f"assets/csv/{session_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"💾 Output directory: {output_dir}")
        
        generated_files = _save_tables_to_csv(tables, output_dir)
        logger.info(f"💾 Generated {len(generated_files)} CSV files")
        
        # Step 5: Track and return results
        tracker.track_node(
            input="Table generation with LLM",
            output={"tables": tables, "plan": plan, "generated_files": generated_files},
            node_name="generate_csv",
            agent_name="unstructured_to_structured_csv",
            node_type="table_generation",
            execution_id=execution_id
        )
        
        logger.info("✅ Table generation completed")
        
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
        logger.error(f"❌ Table generation failed: {e}")
        return {
            **state,
            'csv_generation_status': 'error',
            'csv_generation_message': f'Error: {str(e)}'
        }


def _create_simple_plan(structured_json_paths: List[str]) -> Dict[str, Any]:
    """Create a simple fallback plan with basic structure."""
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
