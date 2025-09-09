"""Workflow nodes that orchestrate agent calls."""

from typing import Dict, Any

# Import all agents
from src.risk_analysis_workflow.agents.classifier.agent import ClassifierAgent
from src.risk_analysis_workflow.agents.extractor.agent import ExtractorAgent
from src.risk_analysis_workflow.agents.identity_validator.agent import IdentityValidatorAgent
from src.risk_analysis_workflow.agents.crossdoc_analyzer.agent import CrossDocAnalyzerAgent
from src.risk_analysis_workflow.agents.fraud_detector.agent import FraudDetectorAgent
from src.risk_analysis_workflow.agents.risk_scorer.agent import RiskScorerAgent
from src.risk_analysis_workflow.agents.assistant_composer.agent import AssistantComposerAgent


def node_intake_and_classify(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 1: Intake and classify documents."""
    print("\n" + "="*50)
    print("NODE 1: INTAKE AND CLASSIFY")
    print("="*50)
    
    agent = ClassifierAgent()
    return agent.run(state)


def node_extract_per_type(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 2: Extract data per document type."""
    print("\n" + "="*50)
    print("NODE 2: EXTRACT PER TYPE")
    print("="*50)
    
    agent = ExtractorAgent()
    return agent.run(state)


def node_get_identity(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 3: Get and validate identity."""
    print("\n" + "="*50)
    print("NODE 3: GET IDENTITY")
    print("="*50)
    
    agent = IdentityValidatorAgent()
    return agent.run(state)


def node_check_crossdoc(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 4: Check cross-document consistency."""
    print("\n" + "="*50)
    print("NODE 4: CHECK CROSS-DOCUMENT")
    print("="*50)
    
    agent = CrossDocAnalyzerAgent()
    return agent.run(state)


def node_check_fraud_signals(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 5: Check for fraud signals."""
    print("\n" + "="*50)
    print("NODE 5: CHECK FRAUD SIGNALS")
    print("="*50)
    
    agent = FraudDetectorAgent()
    return agent.run(state)


def node_score_and_reasons(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 6: Calculate risk score and determine reasons."""
    print("\n" + "="*50)
    print("NODE 6: SCORE AND REASONS")
    print("="*50)
    
    agent = RiskScorerAgent()
    return agent.run(state)


def node_compose_assistant_reply(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node 7: Compose assistant reply."""
    print("\n" + "="*50)
    print("NODE 7: COMPOSE ASSISTANT REPLY")
    print("="*50)
    
    agent = AssistantComposerAgent()
    return agent.run(state)


# Export all nodes
__all__ = [
    "node_intake_and_classify",
    "node_extract_per_type",
    "node_get_identity",
    "node_check_crossdoc",
    "node_check_fraud_signals",
    "node_score_and_reasons",
    "node_compose_assistant_reply"
]