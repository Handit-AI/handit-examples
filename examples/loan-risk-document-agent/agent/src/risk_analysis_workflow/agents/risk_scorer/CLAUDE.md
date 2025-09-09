# Risk Scorer Agent

## Purpose
Calculates final risk score, determines tier, and provides recommendation based on all checks.

## Scoring Methodology
- Failed HIGH severity: +40 points
- Failed MEDIUM severity: +20 points
- Failed LOW severity: +10 points
- Exceptional passes: -5 points

## Risk Tiers
- **LOW** (0-39): Generally approvable
- **MEDIUM** (40-69): Requires review
- **HIGH** (70+): Likely decline
- **INVALID**: Missing critical documents

## Decision Types
- **APPROVE**: Low risk, all docs present
- **APPROVE_WITH_CONDITIONS**: Medium risk, conditions apply
- **MANUAL_REVIEW**: Requires human review
- **DECLINE**: High risk or missing critical docs

## Input/Output
**Input**: All checks, validations, analyses, doc types  
**Output**: Risk score, tier, recommendation, top reasons

## Key Files
- `agent.py` - RiskScorerAgent with calculate_risk_score()
- `prompts.py` - Scoring rules and decision guidelines

## Prompts Strategy
- Explicit point calculations
- Decision matrix based on tier
- Holistic assessment guidance
- Clear reasoning requirements

## Common Modifications
- **Adjust weights**: Change point values in prompts
- **Change thresholds**: Modify tier boundaries
- **Add factor**: Include in risk_calculation

## Testing
```python
from agents.risk_scorer.agent import RiskScorerAgent

agent = RiskScorerAgent()
scoring = agent.calculate_risk_score(checks, validations, ...)
print(f"Score: {scoring['risk_assessment']['risk_score']}")
print(f"Decision: {scoring['final_recommendation']['decision']}")
```

## Important Notes
- Score is cumulative from all failed checks
- Missing critical docs = automatic INVALID
- Considers both negative and positive factors
- Provides detailed calculation breakdown