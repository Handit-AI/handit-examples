"""Fraud detector agent."""

import json
from typing import Dict, Any
from src.risk_analysis_workflow.tools.openai_tools import call_openai_structured
from .prompts import SYSTEM_PROMPT, USER_PROMPT


class FraudDetectorAgent:
    """Agent responsible for detecting fraud signals and financial risks."""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0):
        """Initialize the fraud detector agent.
        
        Args:
            model: OpenAI model to use
            temperature: Temperature for the model
        """
        self.model = model
        self.temperature = temperature
    
    def detect_fraud(
        self,
        payslip_data: Any,
        bank_data: Any,
        cross_doc_analysis: Any
    ) -> Dict[str, Any]:
        """Analyze documents for fraud signals.
        
        Args:
            payslip_data: Extracted payslip data
            bank_data: List of extracted bank statement data
            cross_doc_analysis: Results from cross-document analysis
        
        Returns:
            Fraud detection results
        """
        # Prepare user prompt with document data
        user_prompt = USER_PROMPT.format(
            payslip_data=json.dumps(payslip_data, indent=2, default=str) if payslip_data else "No payslip provided",
            bank_data=json.dumps(bank_data, indent=2, default=str) if bank_data else "No bank statements provided",
            cross_doc_analysis=json.dumps(cross_doc_analysis, indent=2, default=str) if cross_doc_analysis else "No cross-document analysis available"
        )
        
        # Call OpenAI for fraud detection
        result = call_openai_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=self.model,
            temperature=self.temperature
        )
        
        return result
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run fraud detection on financial documents.
        
        Args:
            state: Workflow state with extracted and analyzed data
        
        Returns:
            Updated state with fraud detection results
        """
        print("Detecting fraud signals...")
        
        # Get relevant data from state
        extracted_data = state.get("extracted_data", {})
        payslip_data = extracted_data.get("PAYSLIP")
        bank_data = extracted_data.get("BANK_STATEMENTS", [])
        cross_doc_analysis = state.get("cross_doc_analysis", {})
        
        # Perform fraud detection
        fraud_result = self.detect_fraud(
            payslip_data=payslip_data,
            bank_data=bank_data,
            cross_doc_analysis=cross_doc_analysis
        )
        
        if fraud_result:
            # Extract components
            fraud_analysis = fraud_result.get("fraud_analysis", {})
            fraud_checks = fraud_result.get("fraud_checks", [])
            risk_assessment = fraud_result.get("risk_assessment", {})
            
            # Print fraud check results
            for check in fraud_checks:
                status = "✓" if check["passed"] else "✗"
                print(f"  {status} {check['check_id']}: {check['details']}")
            
            # Print risk assessment
            fraud_prob = risk_assessment.get("fraud_probability", "unknown")
            financial_risk = risk_assessment.get("financial_risk", "unknown")
            print(f"  → Fraud probability: {fraud_prob.upper()}")
            print(f"  → Financial risk: {financial_risk.upper()}")
            
            # Print key risk factors
            if risk_assessment.get("key_risk_factors"):
                print("  → Key risk factors:")
                for factor in risk_assessment["key_risk_factors"]:
                    print(f"     - {factor}")
            
            # Add fraud checks to state checks list
            existing_checks = state.get("checks", [])
            existing_checks.extend(fraud_checks)
            
            # Update state
            return {
                **state,
                "fraud_analysis": fraud_analysis,
                "fraud_signals": {
                    "risk_assessment": risk_assessment,
                    "financial_health": fraud_analysis.get("financial_health", {}),
                    "spending_patterns": fraud_analysis.get("spending_patterns", {})
                },
                "checks": existing_checks
            }
        else:
            print("  ⚠ Fraud detection failed")
            return state