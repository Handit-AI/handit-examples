# Risk Analysis Workflow - LangGraph Implementation

## Overview
This is the core LangGraph workflow that orchestrates 7 AI agents in sequence to assess loan risk.

## Structure
```
workflow.py         # Main LangGraph workflow definition
state.py           # WorkflowState TypedDict
agents/            # 7 specialized AI agents
├── classifier/    # Document type identification
├── extractor/     # Data extraction from documents
├── identity_validator/  # ID verification
├── crossdoc_analyzer/   # Cross-document consistency
├── fraud_detector/      # Fraud signal detection
├── risk_scorer/         # Risk scoring and tier
└── assistant_composer/  # User-friendly responses
nodes/             # Thin wrappers that call agents
tools/             # Document processing utilities
```

## Workflow Sequence
1. **Classify** → Identify document types (ID, PAYSLIP, BANK_STATEMENT)
2. **Extract** → Pull structured data from each document
3. **Identity** → Validate ID and create profile
4. **CrossDoc** → Check consistency across documents
5. **Fraud** → Detect fraud signals and risks
6. **Score** → Calculate risk score (0-100) and tier
7. **Compose** → Generate friendly response

## Key Patterns
- **State passing**: Single WorkflowState flows through all nodes
- **Agent isolation**: Each agent is independent and stateless
- **Error accumulation**: Errors/warnings collected in state
- **Check aggregation**: All checks accumulated in state.checks[]

## Working with Workflow
```python
# Create and run workflow
from workflow import run_workflow

result = run_workflow(
    files=[...],      # Document bytes
    messages=[...],   # Chat history
    options={...}     # Config options
)
```

## Modifying the Workflow
1. **Add node**: Update workflow.py add_node() and add_edge()
2. **Change flow**: Modify edges in create_workflow()
3. **Add agent**: Create new folder in agents/ with agent.py + prompts.py
4. **Update state**: Modify WorkflowState in state.py

## Important Concepts
- **Checkpointing**: Uses MemorySaver for state persistence
- **Streaming**: Each node yields state updates
- **Thread ID**: Groups related workflow executions

## Testing
```bash
# Test full workflow
python test_workflow.py

# Test individual agent
from agents.classifier.agent import ClassifierAgent
agent = ClassifierAgent()
result = agent.classify_document(file_data)
```

## CRITICAL
- All logic is in agent prompts, not in code
- Nodes are just thin wrappers calling agents
- State flows sequentially through all 7 nodes
- Each agent must handle missing data gracefully