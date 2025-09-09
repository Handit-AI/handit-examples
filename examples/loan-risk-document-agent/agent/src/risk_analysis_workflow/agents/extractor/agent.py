"""Document extractor agent."""

from typing import Dict, Any, Optional
from src.risk_analysis_workflow.tools.document_tools import prepare_document_for_ai
from src.risk_analysis_workflow.tools.openai_tools import call_openai_structured
from .prompts import (
    ID_SYSTEM_PROMPT,
    PAYSLIP_SYSTEM_PROMPT,
    BANK_STATEMENT_SYSTEM_PROMPT,
    EXTRACTION_USER_PROMPT
)


class ExtractorAgent:
    """Agent responsible for extracting structured data from documents."""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0):
        """Initialize the extractor agent.
        
        Args:
            model: OpenAI model to use for extraction
            temperature: Temperature for the model (0 for deterministic)
        """
        self.model = model
        self.temperature = temperature
    
    def extract_document(self, file_data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Extract structured data from a single document.
        
        Args:
            file_data: Dictionary with document content
            doc_type: Type of document (ID, PAYSLIP, BANK_STATEMENT)
        
        Returns:
            Extracted data in structured format
        """
        # Select appropriate prompt based on document type
        if doc_type == "ID":
            system_prompt = ID_SYSTEM_PROMPT
            doc_type_name = "identity"
        elif doc_type == "PAYSLIP":
            system_prompt = PAYSLIP_SYSTEM_PROMPT
            doc_type_name = "payslip"
        elif doc_type == "BANK_STATEMENT":
            system_prompt = BANK_STATEMENT_SYSTEM_PROMPT
            doc_type_name = "bank statement"
        else:
            return None
        
        # Prepare document for AI
        prepared = prepare_document_for_ai(file_data)
        
        # Create user prompt
        user_prompt = EXTRACTION_USER_PROMPT.format(doc_type=doc_type_name)
        
        # Handle different content types
        if prepared["content_type"] == "images":
            result = call_openai_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                images_base64=prepared["content"],  # Now always a list
                model=self.model,
                temperature=self.temperature
            )
        else:
            # For text content, append the actual text
            if prepared.get("text_content"):
                # PDF with extracted text
                full_prompt = f"{user_prompt}\n\nDocument text:\n{prepared['text_content']}"
            else:
                # Pure text document
                full_prompt = f"{user_prompt}\n\nDocument content:\n{prepared['content']}"
            
            result = call_openai_structured(
                system_prompt=system_prompt,
                user_prompt=full_prompt,
                model=self.model,
                temperature=self.temperature
            )
        
        return result
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run extraction on all classified documents.
        
        Args:
            state: Workflow state with classified documents
        
        Returns:
            Updated state with extracted data
        """
        extracted_data = {
            "ID": None,
            "PAYSLIP": None,
            "BANK_STATEMENTS": []
        }
        extraction_details = {}
        
        doc_types = state.get("doc_types", {})
        files = state.get("files", [])
        
        for idx, file_data in enumerate(files):
            doc_type = doc_types.get(str(idx), "OTHER")
            
            if doc_type == "OTHER":
                continue
            
            file_name = file_data.get("name", f"file_{idx}")
            print(f"Extracting from {file_name} ({doc_type})...")
            
            # Extract data from document
            extracted = self.extract_document(file_data, doc_type)
            
            if extracted:
                # Store extraction details
                extraction_details[str(idx)] = {
                    "doc_type": doc_type,
                    "confidence": extracted.get("extraction_confidence", {}).get("overall", 0),
                    "extracted_fields": extracted.get("extraction_confidence", {}).get("fields_extracted", [])
                }
                
                # Store extracted data by type
                if doc_type == "ID" and not extracted_data["ID"]:
                    extracted_data["ID"] = extracted
                    name = extracted.get("personal_info", {}).get("full_name", "Unknown")
                    print(f"  → Extracted ID for: {name}")
                    
                elif doc_type == "PAYSLIP" and not extracted_data["PAYSLIP"]:
                    extracted_data["PAYSLIP"] = extracted
                    employer = extracted.get("employer", {}).get("name", "Unknown")
                    amount = extracted.get("net_pay", {}).get("amount", 0)
                    print(f"  → Extracted payslip: {employer} - ${amount:,.2f}")
                    
                elif doc_type == "BANK_STATEMENT":
                    extracted_data["BANK_STATEMENTS"].append(extracted)
                    period = extracted.get("statement_period", {})
                    start = period.get("start_date", "")
                    end = period.get("end_date", "")
                    print(f"  → Extracted statement: {start} to {end}")
            else:
                print(f"  ⚠ Failed to extract data from {doc_type}")
                
        # Update state
        return {
            **state,
            "extracted_data": extracted_data,
            "extraction_details": extraction_details
        }