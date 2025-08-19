"""
CSV Generation Node for LangGraph
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

        # App name for tracing
        agent_name = state.get("agent_name")

        # Execution id for tracing
        execution_id = state.get("execution_id")
        
        if not structured_json_paths:
            return {
                **state,
                'csv_generation_status': 'skipped',
                'csv_generation_message': 'No JSON files to process'
            }
        
        logger.info(f"📊 Processing {len(structured_json_paths)} JSON files")
        
        # Step 1: Load all JSON files completely for LLM
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
        try:
            logger.info("🤖 Getting structured tables from LLM with complete JSON data...")
            llm_response = csv_generation_planner.invoke({
                "documents_inventory": all_json_data
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
        
        # Step 3: Print tables len to console
        tables = plan.get("tables", [])
        logger.info(f"📊 Found {len(tables)} tables to display")
        
        print(f"\n🚀 GENERATING STRUCTURED TABLES FOR SESSION: {session_id}")
        print(f"📁 Processing {len(structured_json_paths)} documents")
        print(f"📊 LLM generated {len(tables)} tables\n")
        
        # Step 4: Save tables to CSV files
        output_dir = Path(f"assets/csv/{session_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"💾 Output directory: {output_dir}")
        
        generated_files = _save_tables_to_csv(tables, output_dir)
        logger.info(f"💾 Generated {len(generated_files)} CSV files")
        
        # Step 5: Track and return results
        
        # Prepare tracking input with complete JSON data
        tracking_input = {
            "systemPrompt": get_system_prompt(),
            "userPrompt": get_user_prompt(),
            "documents_inventory": all_json_data
        }
        
        tracker.track_node(
            input=tracking_input,
            output={"tables": tables, "plan": plan, "generated_files": generated_files},
            node_name="generate_csv",
            agent_name=agent_name,
            node_type="llm",
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
