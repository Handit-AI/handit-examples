# Legacy Utilities (Deprecated)

## ⚠️ IMPORTANT
This folder contains legacy code from the initial implementation that used code-based extraction and checks. The current system uses pure AI agents instead.

**These utilities are NOT used in the current workflow.**

## Legacy Files
- `pdf_utils.py` - PDF processing utilities
- `csv_utils.py` - CSV parsing and transaction categorization  
- `openai_client.py` - Direct OpenAI client wrapper

## Why Deprecated?
The project was refactored to use:
- Pure AI agents for all logic
- LangGraph for orchestration
- Agents make all decisions via prompts
- No hardcoded business rules

## Current Alternative
All functionality has been moved to:
- `risk-analysis-workflow/tools/` - Document preparation
- `risk-analysis-workflow/agents/` - AI-powered processing

## Migration Path
If you need similar functionality:
1. Use agents instead of code logic
2. Put rules in prompts, not Python
3. Let AI handle extraction and validation

## DO NOT USE
These utilities are kept for reference only. The active codebase uses the pure AI approach in risk-analysis-workflow/.