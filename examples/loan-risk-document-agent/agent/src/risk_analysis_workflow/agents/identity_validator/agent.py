"""Identity validator agent."""

import json
from datetime import date
from typing import Dict, Any
from src.risk_analysis_workflow.tools.openai_tools import call_openai_structured
from .prompts import SYSTEM_PROMPT, USER_PROMPT_WITH_ID, USER_PROMPT_NO_ID


class IdentityValidatorAgent:
    """Agent responsible for validating identity documents and creating identity profiles."""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0):
        """Initialize the identity validator agent.
        
        Args:
            model: OpenAI model to use
            temperature: Temperature for the model
        """
        self.model = model
        self.temperature = temperature
    
    def validate_identity(self, id_data: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            """Validate identity document and create profile.
        
            Args:
                id_data: Extracted ID document data
            
            Returns:
                Identity profile and validation results
            """
            # Prepare system prompt with today's date
            print(f"Validating identity with data: {id_data}")
            system_prompt = SYSTEM_PROMPT.format(today_date=date.today().isoformat())
            print(f"System prompt: {system_prompt}")
            # Prepare user prompt based on whether ID is present
            if id_data:
                user_prompt = USER_PROMPT_WITH_ID.format(
                    id_data=json.dumps(id_data, indent=2, default=str)
                )
            else:
                user_prompt = USER_PROMPT_NO_ID
            
            # Call OpenAI for validation
            result = call_openai_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=self.model,
                temperature=self.temperature
            )
            
            return result
        except Exception as e:
            print(f"Error validating identity: {e}")
            return None
        
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run identity validation on extracted data.
        
        Args:
            state: Workflow state with extracted data
        
        Returns:
            Updated state with identity profile and validation checks
        """
        print("Validating identity...")
        
        # Get extracted ID data
        extracted_data = state.get("extracted_data", {})
        id_data = extracted_data.get("ID")
        
        # Validate identity
        validation_result = self.validate_identity(id_data)
        
        if validation_result:
            # Extract components
            identity_profile = validation_result.get("identity_profile", {})
            validation_checks = validation_result.get("validation_checks", [])
            risk_indicators = validation_result.get("risk_indicators", {})
            validation_summary = validation_result.get("validation_summary", {})
            
            # Print summary
            if identity_profile:
                name = identity_profile.get("verified_name", "Unknown")
                print(f"  → Identity: {name}")
                
            # Print validation results
            for check in validation_checks:
                status = "✓" if check["passed"] else "✗"
                print(f"  {status} {check['check_id']}: {check['details']}")
            
            # Print overall validation
            if validation_summary.get("is_valid"):
                print(f"  → Validation: PASSED")
            else:
                print(f"  → Validation: FAILED")
                if validation_summary.get("rejection_reasons"):
                    for reason in validation_summary["rejection_reasons"]:
                        print(f"     - {reason}")
            
            # Add validation checks to state checks list
            existing_checks = state.get("checks", [])
            existing_checks.extend(validation_checks)
            
            # Update state
            return {
                **state,
                "identity_profile": identity_profile,
                "identity_validation": {
                    "risk_indicators": risk_indicators,
                    "summary": validation_summary
                },
                "checks": existing_checks
            }
        else:
            print("  ⚠ Identity validation failed")
            return state