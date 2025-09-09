"""Cross-document analyzer agent."""

import json
from typing import Dict, Any
from src.risk_analysis_workflow.tools.openai_tools import call_openai_structured
from .prompts import SYSTEM_PROMPT, USER_PROMPT


class CrossDocAnalyzerAgent:
    """Agent responsible for analyzing consistency across multiple documents."""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0):
        """Initialize the cross-document analyzer agent.
        
        Args:
            model: OpenAI model to use
            temperature: Temperature for the model
        """
        self.model = model
        self.temperature = temperature
    
    def analyze_documents(self, id_data: Any, payslip_data: Any, bank_data: Any) -> Dict[str, Any]:
        """Analyze documents for cross-document consistency.
        
        Args:
            id_data: Extracted ID document data
            payslip_data: Extracted payslip data
            bank_data: List of extracted bank statement data
        
        Returns:
            Cross-document analysis results
        """
        # Prepare user prompt with document data
        user_prompt = USER_PROMPT.format(
            id_data=json.dumps(id_data, indent=2, default=str) if id_data else "No ID document provided",
            payslip_data=json.dumps(payslip_data, indent=2, default=str) if payslip_data else "No payslip provided",
            bank_data=json.dumps(bank_data, indent=2, default=str) if bank_data else "No bank statements provided"
        )
        
        # Call OpenAI for analysis
        result = call_openai_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=self.model,
            temperature=self.temperature
        )
        
        return result
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run cross-document analysis on extracted data.
        
        Args:
            state: Workflow state with extracted data
        
        Returns:
            Updated state with cross-document analysis
        """
        print("Analyzing cross-document consistency...")
        
        # Get extracted data
        extracted_data = state.get("extracted_data", {})
        id_data = extracted_data.get("ID")
        payslip_data = extracted_data.get("PAYSLIP")
        bank_data = extracted_data.get("BANK_STATEMENTS", [])
        
        # Also get identity profile if available
        identity_profile = state.get("identity_profile", {})
        
        # Perform analysis
        analysis_result = self.analyze_documents(
            id_data=id_data or identity_profile,
            payslip_data=payslip_data,
            bank_data=bank_data
        )
        
        if analysis_result:
            # Extract components
            cross_doc_analysis = analysis_result.get("cross_document_analysis", {})
            consistency_checks = analysis_result.get("consistency_checks", [])
            fraud_indicators = analysis_result.get("fraud_indicators", {})
            verification_summary = analysis_result.get("verification_summary", {})
            
            # Print analysis results
            for check in consistency_checks:
                status = "✓" if check["passed"] else "✗"
                print(f"  {status} {check['check_id']}: {check['details']}")
            
            # Print fraud indicators if any
            if fraud_indicators.get("suspicious_patterns"):
                print(f"  ⚠ Suspicious patterns detected:")
                for pattern in fraud_indicators["suspicious_patterns"]:
                    print(f"     - {pattern}")
            
            # Print summary
            if verification_summary.get("documents_consistent"):
                print(f"  → Documents are CONSISTENT")
            else:
                print(f"  → Documents have INCONSISTENCIES")
                if verification_summary.get("major_discrepancies"):
                    for disc in verification_summary["major_discrepancies"]:
                        print(f"     Major: {disc}")
            
            # Add consistency checks to state checks list
            existing_checks = state.get("checks", [])
            existing_checks.extend(consistency_checks)
            
            # Update state
            return {
                **state,
                "cross_doc_analysis": cross_doc_analysis,
                "consistency_verification": {
                    "fraud_indicators": fraud_indicators,
                    "summary": verification_summary
                },
                "checks": existing_checks
            }
        else:
            print("  ⚠ Cross-document analysis failed")
            return state