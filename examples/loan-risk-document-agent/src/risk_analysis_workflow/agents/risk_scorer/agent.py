"""Risk scorer agent."""

import json
from typing import Dict, Any
from src.risk_analysis_workflow.tools.openai_tools import call_openai_structured
from .prompts import SYSTEM_PROMPT, USER_PROMPT


class RiskScorerAgent:
    """Agent responsible for calculating final risk score and recommendation."""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0):
        """Initialize the risk scorer agent.
        
        Args:
            model: OpenAI model to use
            temperature: Temperature for the model
        """
        self.model = model
        self.temperature = temperature
    
    def calculate_risk_score(
        self,
        all_checks: Any,
        identity_validation: Any,
        consistency_verification: Any,
        fraud_signals: Any,
        doc_types: Any
    ) -> Dict[str, Any]:
        """Calculate final risk score and tier.
        
        Args:
            all_checks: All validation checks performed
            identity_validation: Identity validation summary
            consistency_verification: Cross-doc verification summary
            fraud_signals: Fraud detection summary
            doc_types: Document types provided
        
        Returns:
            Risk scoring results
        """
        # Prepare user prompt with all data
        user_prompt = USER_PROMPT.format(
            all_checks=json.dumps(all_checks, indent=2, default=str) if all_checks else "No checks performed",
            identity_validation=json.dumps(identity_validation, indent=2, default=str) if identity_validation else "No identity validation",
            consistency_verification=json.dumps(consistency_verification, indent=2, default=str) if consistency_verification else "No consistency verification",
            fraud_signals=json.dumps(fraud_signals, indent=2, default=str) if fraud_signals else "No fraud analysis",
            doc_types=json.dumps(doc_types, indent=2, default=str) if doc_types else "No documents"
        )
        
        # Call OpenAI for risk scoring
        result = call_openai_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=self.model,
            temperature=self.temperature
        )
        
        return result
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run risk scoring on all collected data.
        
        Args:
            state: Workflow state with all checks and analyses
        
        Returns:
            Updated state with risk score and recommendation
        """
        print("Calculating risk score...")
        
        # Get all relevant data from state
        all_checks = state.get("checks", [])
        identity_validation = state.get("identity_validation", {})
        consistency_verification = state.get("consistency_verification", {})
        fraud_signals = state.get("fraud_signals", {})
        doc_types = state.get("doc_types", {})
        
        # Calculate risk score
        scoring_result = self.calculate_risk_score(
            all_checks=all_checks,
            identity_validation=identity_validation,
            consistency_verification=consistency_verification,
            fraud_signals=fraud_signals,
            doc_types=doc_types
        )
        
        if scoring_result:
            # Extract components
            risk_calculation = scoring_result.get("risk_calculation", {})
            risk_assessment = scoring_result.get("risk_assessment", {})
            top_risk_factors = scoring_result.get("top_risk_factors", [])
            top_positive_factors = scoring_result.get("top_positive_factors", [])
            final_recommendation = scoring_result.get("final_recommendation", {})
            risk_summary = scoring_result.get("risk_summary", {})
            
            # Get key values
            risk_score = risk_assessment.get("risk_score", 0)
            risk_tier = risk_assessment.get("risk_tier", "INVALID")
            decision = final_recommendation.get("decision", "DECLINE")
            
            # Print scoring breakdown
            print(f"\n  Risk Calculation:")
            print(f"  → Base score: {risk_calculation.get('base_score', 0)}")
            
            # Print check contributions
            contributions = risk_calculation.get("check_contributions", [])[:5]
            for contrib in contributions:
                if not contrib["passed"]:
                    print(f"     + {contrib['points_added']} pts: {contrib['check_id']} ({contrib['reason']})")
            
            print(f"  → Final score: {risk_score}")
            print(f"  → Risk tier: {risk_tier}")
            
            # Print top risk factors
            if top_risk_factors:
                print(f"\n  Top Risk Factors:")
                for factor in top_risk_factors[:3]:
                    print(f"  • {factor['factor']}: {factor['description']}")
            
            # Print positive factors
            if top_positive_factors:
                print(f"\n  Positive Factors:")
                for factor in top_positive_factors[:2]:
                    print(f"  • {factor['factor']}: {factor['description']}")
            
            # Print recommendation
            print(f"\n  → Final Decision: {decision}")
            print(f"     {final_recommendation.get('reasoning', '')}")
            
            # Extract top reasons for state
            reasons = []
            if risk_summary.get("primary_concerns"):
                reasons = risk_summary["primary_concerns"][:5]
            
            # Update state
            return {
                **state,
                "risk_score": risk_score,
                "risk_tier": risk_tier,
                "reasons": reasons,
                "risk_calculation": risk_calculation,
                "risk_assessment": risk_assessment,
                "final_recommendation": final_recommendation,
                "risk_summary": risk_summary
            }
        else:
            print("  ⚠ Risk scoring failed")
            # Provide defaults
            return {
                **state,
                "risk_score": 100,
                "risk_tier": "INVALID",
                "reasons": ["Risk scoring failed"],
                "final_recommendation": {"decision": "DECLINE"}
            }