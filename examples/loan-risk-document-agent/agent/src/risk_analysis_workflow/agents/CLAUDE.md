# AI Agents Directory

## Overview
7 specialized AI agents that power the loan risk assessment. Each agent is a complete AI system with its own prompts and logic.

## Agent Structure
Each agent folder contains:
- `agent.py` - Agent class with run() method
- `prompts.py` - System and user prompts for OpenAI

## The 7 Agents

### 1. classifier/
**Purpose**: Identify document types  
**Input**: Raw file bytes  
**Output**: Document classification (ID, PAYSLIP, BANK_STATEMENT, OTHER)

### 2. extractor/
**Purpose**: Extract structured data from documents  
**Input**: Classified documents  
**Output**: JSON structured data per document type

### 3. identity_validator/
**Purpose**: Validate ID documents and create identity profile  
**Input**: Extracted ID data  
**Output**: Identity profile + validation checks

### 4. crossdoc_analyzer/
**Purpose**: Check consistency across documents  
**Input**: All extracted documents  
**Output**: Consistency checks + fraud indicators

### 5. fraud_detector/
**Purpose**: Detect fraud signals and financial risks  
**Input**: Payslip + bank statements + cross-doc analysis  
**Output**: Fraud checks + risk assessment

### 6. risk_scorer/
**Purpose**: Calculate final risk score and tier  
**Input**: All checks and analyses  
**Output**: Risk score (0-100), tier, recommendation

### 7. assistant_composer/
**Purpose**: Generate user-friendly responses  
**Input**: Assessment results  
**Output**: 2-4 sentence friendly message

## Agent Pattern
```python
class AgentName:
    def __init__(self, model="gpt-4o", temperature=0):
        self.model = model
        self.temperature = temperature
    
    def run(self, state: Dict) -> Dict:
        # Process state
        # Call OpenAI with prompts
        # Update state
        return state
```

## Modifying Agents
1. **Change logic**: Edit prompts.py (ALL logic is here)
2. **Change structure**: Edit agent.py run() method
3. **Test individually**: Import and call agent directly

## Key Principles
- **Stateless**: Agents don't maintain state between calls
- **Defensive**: Handle missing/invalid input gracefully
- **Explicit**: Prompts specify exact output format
- **Independent**: Each agent works standalone

## Common Modifications
- **Stricter checks**: Add emphasis in prompts (IMPORTANT, MUST)
- **New fields**: Update JSON schema in prompts
- **Different model**: Change model parameter in __init__
- **More reasoning**: Increase temperature for creativity

## Testing an Agent
```python
from agents.classifier.agent import ClassifierAgent

agent = ClassifierAgent()
result = agent.classify_document({
    "content": file_bytes,
    "type": "pdf",
    "name": "document.pdf"
})
```

## IMPORTANT
- Agents are the ONLY source of business logic
- All decisions flow through OpenAI
- Prompts are the "code" - tune them carefully
- Agent code is just orchestration