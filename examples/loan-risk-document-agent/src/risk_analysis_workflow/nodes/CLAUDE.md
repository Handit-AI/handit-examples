# Workflow Nodes

## Purpose
Thin wrapper functions that connect LangGraph workflow to AI agents.

## Node Pattern
```python
def node_name(state: Dict[str, Any]) -> Dict[str, Any]:
    print("NODE X: DESCRIPTION")
    agent = AgentClass()
    return agent.run(state)
```

## The 7 Nodes
1. `node_intake_and_classify` - Calls ClassifierAgent
2. `node_extract_per_type` - Calls ExtractorAgent
3. `node_get_identity` - Calls IdentityValidatorAgent
4. `node_check_crossdoc` - Calls CrossDocAnalyzerAgent
5. `node_check_fraud_signals` - Calls FraudDetectorAgent
6. `node_score_and_reasons` - Calls RiskScorerAgent
7. `node_compose_assistant_reply` - Calls AssistantComposerAgent

## Key Concepts
- Nodes are stateless functions
- Each node receives and returns state
- Nodes print progress for debugging
- Error handling happens in agents

## Workflow Integration
These nodes are registered in workflow.py:
```python
workflow.add_node("classify", node_intake_and_classify)
workflow.add_edge("classify", "extract")
```

## Important Notes
- Nodes don't contain business logic
- All intelligence is in the agents
- Nodes just orchestrate agent calls
- State flows through nodes sequentially