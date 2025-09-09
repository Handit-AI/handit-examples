# Assistant Composer Agent

## Purpose
Generates friendly, professional responses to applicants based on assessment results.

## Response Types
- **APPROVE**: Congratulatory with next steps
- **APPROVE_WITH_CONDITIONS**: Clear about conditions
- **MANUAL_REVIEW**: Explains review process
- **DECLINE**: Respectful with improvement suggestions
- **MISSING DOCUMENTS**: Specific about what's needed

## Response Guidelines
- 2-4 sentences maximum
- Friendly, professional tone
- No technical jargon
- Specific, actionable next steps
- Never mention internal scores or calculations

## Input/Output
**Input**: User message, decision, risk tier, concerns, missing docs  
**Output**: Brief friendly message string

## Key Files
- `agent.py` - AssistantComposerAgent with compose_response()
- `prompts.py` - Response templates and guidelines

## Prompts Strategy
- Template examples for each decision type
- Clear communication rules
- Prohibited topics (scores, fraud suspicions)
- Emphasis on helpfulness

## Common Modifications
- **Change tone**: Adjust prompts for formality
- **Add language**: Include response variations
- **Customize messages**: Update templates

## Testing
```python
from agents.assistant_composer.agent import AssistantComposerAgent

agent = AssistantComposerAgent()
message = agent.compose_response(
    user_message="Check my application",
    decision="APPROVE",
    risk_tier="LOW",
    ...
)
print(message)
```

## Important Notes
- Uses higher temperature (0.7) for natural language
- Never reveals risk scores or calculations
- Focuses on what applicant needs to do
- Avoids legal/financial advice

## Response Examples
- ✅ "Great news! Your application has been approved..."
- ⚠️ "Your application needs review. Please upload..."
- ❌ "Unfortunately, we cannot approve at this time..."