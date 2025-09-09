"""Document classifier agent."""

from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.risk_analysis_workflow.tools.document_tools import prepare_document_for_ai
from src.risk_analysis_workflow.tools.openai_tools import call_openai_structured
from .prompts import SYSTEM_PROMPT, IMAGE_USER_PROMPT, TEXT_USER_PROMPT, CSV_USER_PROMPT


class ClassifierAgent:
    """Agent responsible for classifying documents into categories."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """Initialize the classifier agent.
        
        Args:
            model: OpenAI model to use for classification
            temperature: Temperature for the model (0 for deterministic)
        """
        self.model = model
        self.temperature = temperature
    
    def classify_document(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a single document.
        
        Args:
            file_data: Dictionary with 'content' (bytes), 'type' (str), and 'name' (str)
        
        Returns:
            Classification result with label, confidence, and reasoning
        """
        # Prepare document for AI processing
        prepared = prepare_document_for_ai(file_data)
        
        # Select appropriate prompt based on content type
        if prepared["content_type"] == "images":
            user_prompt = IMAGE_USER_PROMPT
            result = call_openai_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                images_base64=prepared["content"],  # Now always a list
                model=self.model,
                temperature=self.temperature
            )
        elif prepared["type"] == "csv":
            # For CSV, include structure information
            import pandas as pd
            import io
            
            try:
                csv_content = file_data["content"].decode('utf-8')
            except:
                csv_content = file_data["content"].decode('latin-1')
            
            df = pd.read_csv(io.StringIO(csv_content))
            
            user_prompt = CSV_USER_PROMPT.format(
                columns=", ".join(df.columns[:20]),
                row_count=len(df),
                preview=df.head(5).to_string(index=False) if len(df) > 0 else "No data"
            )
            
            result = call_openai_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                model=self.model,
                temperature=self.temperature
            )
        else:
            # Text-based classification
            user_prompt = TEXT_USER_PROMPT.format(
                content=prepared["content"][:3000]  # Limit content length
            )
            
            result = call_openai_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                model=self.model,
                temperature=self.temperature
            )
        
        # Ensure we have a valid result
        if not result:
            result = {
                "label": "OTHER",
                "confidence": 0.0,
                "reasoning": "Classification failed",
                "document_details": {}
            }
        
        return result
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run classification on all files in the state.
        
        Args:
            state: Workflow state containing files to classify
        
        Returns:
            Updated state with doc_types mapping
        """
        doc_types = {}
        classification_details = {}
        
        for idx, file_data in enumerate(state.get("files", [])):
            file_name = file_data.get("name", f"file_{idx}")
            print(f"Classifying {file_name}...")
            
            # Classify the document
            result = self.classify_document(file_data)
            
            # Store results
            doc_types[str(idx)] = result["label"]
            classification_details[str(idx)] = result
            
            print(f"  → {result['label']} (confidence: {result.get('confidence', 0):.2f})")
            if result.get("reasoning"):
                print(f"     {result['reasoning']}")
        
        # Update state
        return {
            **state,
            "doc_types": doc_types,
            "classification_details": classification_details
        }