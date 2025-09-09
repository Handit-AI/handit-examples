# Identity Validator Agent

## Purpose
Validates identity documents and creates comprehensive identity profiles with risk checks.

## Validation Checks
1. **ID_PRESENT** - Document has name and ID number
2. **ID_EXPIRY** - Check if document is expired
3. **AGE_VERIFICATION** - Applicant is 18+ years old
4. **DATA_COMPLETENESS** - Required fields present
5. **DOCUMENT_INTEGRITY** - Suspicious patterns check

## Input/Output
**Input**: Extracted ID data (or None if missing)  
**Output**: Identity profile + validation checks + risk indicators

## Key Components
- Identity profile creation
- Validation check execution
- Risk indicator assessment
- Rejection reason determination

## Key Files
- `agent.py` - IdentityValidatorAgent with validate_identity()
- `prompts.py` - Validation rules and check definitions

## Prompts Strategy
- Includes today's date for expiry checks
- Detailed validation rules in system prompt
- Separate handling for missing ID case

## Common Modifications
- **Add validation**: Update validation_checks in prompts
- **Change age limit**: Modify AGE_VERIFICATION rules
- **Add risk indicator**: Update risk_indicators section

## Testing
```python
from agents.identity_validator.agent import IdentityValidatorAgent

agent = IdentityValidatorAgent()
validation = agent.validate_identity(id_data)
print(f"Valid: {validation['validation_summary']['is_valid']}")
```

## Important Notes
- All checks have severity levels (high/medium/low)
- Creates profile even with partial data
- Flags suspicious patterns (recent issue dates, etc.)