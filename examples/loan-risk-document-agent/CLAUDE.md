# Loan Risk Document Agent - Claude Guide

## Overview
This is a pure AI-powered loan risk assessment system using LangGraph and OpenAI. Every decision is made by specialized AI agents - no hardcoded rules.

## Architecture
7-node sequential LangGraph workflow where each node calls a dedicated AI agent:
1. **Classifier** → Document type identification
2. **Extractor** → Structured data extraction  
3. **Identity Validator** → ID verification
4. **CrossDoc Analyzer** → Multi-document consistency
5. **Fraud Detector** → Risk signal detection
6. **Risk Scorer** → Final scoring
7. **Assistant Composer** → User responses

## Key Commands
```bash
# Development
python test_workflow.py    # Run test with mock documents
python app.py             # Start Flask API server (port 5000)
pip install -r requirements.txt

# Testing the API
curl -X POST http://localhost:5000/v1/chat/messages \
  -F "messages=[{\"role\":\"user\",\"content\":\"Please assess my loan\"}]" \
  -F "files[]=@test.pdf" \
  -F "options={\"country\":\"US\"}"
```

## Important Files
- `src/risk-analysis-workflow/workflow.py` - Main LangGraph orchestration
- `src/risk-analysis-workflow/agents/` - All 7 AI agents
- `app.py` - Flask API endpoint
- `.env` - Configuration (OPENAI_API_KEY required)

## Code Style & Patterns
- **Pure AI approach**: All logic in prompts, no business rules in code
- **Agent structure**: Each agent has `agent.py` + `prompts.py`
- **Node pattern**: Nodes are thin wrappers that call agents
- **State management**: Single WorkflowState passed between nodes
- **Error handling**: Graceful degradation with defaults

## Workflow Guidelines
- When modifying agents, update both `agent.py` and `prompts.py`
- Test changes with `test_workflow.py` before API testing
- Each agent should be independent and stateless
- Prompts should be detailed and explicit about output format

## Adding Features
1. **New document type**: Update classifier and extractor agents
2. **New risk check**: Modify fraud_detector prompts
3. **New agent**: Create folder in `agents/`, add to workflow.py
4. **API changes**: Update app.py and schemas/

## Environment Setup
```bash
export OPENAI_API_KEY="your-key"
cp .env.example .env
# Edit .env with your settings
```

## Testing Approach
- Use mock documents in `test_workflow.py`
- Each agent can be tested independently
- Full workflow test shows all 7 nodes executing

## IMPORTANT
- This is ALL AI - no hardcoded business logic
- Every decision flows through OpenAI GPT-4
- Agents are the source of truth for logic
- Code just orchestrates agent calls