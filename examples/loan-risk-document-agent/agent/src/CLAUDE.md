# Source Code Structure

## Folders
- `risk-analysis-workflow/` - Core LangGraph workflow and agents
- `schemas/` - Pydantic models for data validation
- `utils/` - Document processing utilities
- `config.py` - Application configuration

## Key Concepts
This src/ folder contains the entire loan risk assessment engine. The main entry point is the workflow in `risk-analysis-workflow/workflow.py`.

## Architecture Flow
```
Files → Workflow → Agents → OpenAI → State Updates → Response
```

## Working with Code
- All business logic lives in agent prompts, not in Python code
- Python code is just plumbing for data flow
- State management uses TypedDict for LangGraph compatibility
- Pydantic schemas ensure data consistency

## Common Tasks
- **Add new agent**: Create in `risk-analysis-workflow/agents/`
- **Modify prompts**: Edit `prompts.py` in agent folder
- **Change workflow**: Update `risk-analysis-workflow/workflow.py`
- **Add schemas**: Edit files in `schemas/`

## Important Files
- `config.py` - All configuration settings
- `risk-analysis-workflow/state.py` - Workflow state definition
- `risk-analysis-workflow/workflow.py` - Main orchestration