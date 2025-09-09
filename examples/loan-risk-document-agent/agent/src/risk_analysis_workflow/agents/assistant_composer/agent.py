"""Assistant composer agent."""

from typing import Dict, Any, List
from src.risk_analysis_workflow.tools.openai_tools import call_openai_text
from .prompts import SYSTEM_PROMPT, USER_PROMPT


class AssistantComposerAgent:
    """Agent responsible for composing friendly assistant responses."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        """Initialize the assistant composer agent.
        
        Args:
            model: OpenAI model to use
            temperature: Temperature for more natural responses
        """
        self.model = model
        self.temperature = temperature
    
    def compose_response(
        self,
        user_message: str,
        decision: str,
        risk_tier: str,
        primary_concerns: List[str],
        strengths: List[str],
        missing_docs: Dict[str, List[str]],
        conditions: List[str],
        documents_provided: List[str]
    ) -> str:
        """Compose a friendly response to the applicant.
        
        Args:
            user_message: The user's last message
            decision: Final decision (APPROVE, DECLINE, etc.)
            risk_tier: Risk tier (LOW, MEDIUM, HIGH, INVALID)
            primary_concerns: List of main concerns
            strengths: List of positive factors
            missing_docs: Dictionary of missing documents
            conditions: Any conditions for approval
            documents_provided: List of documents provided
        
        Returns:
            Composed assistant message
        """
        # Prepare user prompt with assessment data
        user_prompt = USER_PROMPT.format(
            user_message=user_message or "Please assess my loan application.",
            decision=decision,
            risk_tier=risk_tier,
            primary_concerns=", ".join(primary_concerns[:3]) if primary_concerns else "None",
            strengths=", ".join(strengths[:2]) if strengths else "None identified",
            missing_docs=", ".join(missing_docs.get("critical", [])) if missing_docs else "None",
            conditions=", ".join(conditions) if conditions else "None",
            documents_provided=", ".join(documents_provided) if documents_provided else "None"
        )
        
        # Generate response
        response = call_openai_text(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            model=self.model,
            temperature=self.temperature,
            max_tokens=150
        )
        
        return response
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run assistant response composition.
        
        Args:
            state: Workflow state with assessment results
        
        Returns:
            Updated state with assistant message
        """
        print("Composing assistant response...")
        
        # Get relevant data from state
        messages = state.get("messages", [])
        user_message = messages[-1]["content"] if messages else ""
        
        final_recommendation = state.get("final_recommendation", {})
        decision = final_recommendation.get("decision", "DECLINE")
        conditions = final_recommendation.get("conditions", [])
        
        risk_tier = state.get("risk_tier", "INVALID")
        risk_summary = state.get("risk_summary", {})
        primary_concerns = risk_summary.get("primary_concerns", [])
        strengths = risk_summary.get("strengths", [])
        
        # Get missing documents
        scoring_result = state.get("risk_assessment", {})
        missing_docs = state.get("missing_documents", {})
        
        # Get documents provided
        doc_types = state.get("doc_types", {})
        documents_provided = [doc_type for doc_type in doc_types.values() if doc_type != "OTHER"]
        
        # Compose response
        assistant_message = self.compose_response(
            user_message=user_message,
            decision=decision,
            risk_tier=risk_tier,
            primary_concerns=primary_concerns,
            strengths=strengths,
            missing_docs=missing_docs,
            conditions=conditions,
            documents_provided=documents_provided
        )
        
        if assistant_message:
            print(f"\n  Assistant Response:")
            print(f"  \"{assistant_message}\"")
            
            # Update state
            return {
                **state,
                "assistant_message": assistant_message
            }
        else:
            # Fallback message
            default_message = "Thank you for your submission. We've completed our initial assessment. Please review the detailed results above."
            
            return {
                **state,
                "assistant_message": default_message
            }