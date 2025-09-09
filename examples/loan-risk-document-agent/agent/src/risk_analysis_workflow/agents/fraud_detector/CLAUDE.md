# Fraud Detector Agent

## Purpose
Detects fraud signals and financial risks through deep analysis of financial documents.

## Fraud Checks
1. **BALANCE_MATH** - Verify balance calculations
2. **INCOME_PLAUSIBILITY** - Check if income is realistic
3. **INCOME_STABILITY** - Assess income volatility
4. **NSF_OVERDRAFT** - Check for insufficient funds
5. **GAMBLING_EXPOSURE** - Detect gambling transactions
6. **DEBT_BURDEN** - Assess debt-to-income ratio
7. **CASH_BUFFER** - Check emergency fund adequacy
8. **ROUND_NUMBER_PATTERN** - Detect suspicious patterns
9. **DOCUMENT_AUTHENTICITY** - Check for tampering signs

## Risk Thresholds
- Gambling: >5% of spending is high risk
- Debt burden: >30% of income is high
- Cash buffer: <15 days is risky
- Income volatility: >60% is unstable

## Input/Output
**Input**: Payslip, bank statements, cross-doc analysis  
**Output**: Fraud analysis + checks + risk assessment

## Key Files
- `agent.py` - FraudDetectorAgent with detect_fraud()
- `prompts.py` - Fraud detection rules and thresholds

## Prompts Strategy
- Mathematical verification rules
- Pattern recognition guidelines
- Risk threshold definitions
- Document authenticity checks

## Common Modifications
- **Adjust thresholds**: Change percentage limits
- **Add pattern**: Update suspicious_patterns
- **New check**: Add to fraud_checks list

## Testing
```python
from agents.fraud_detector.agent import FraudDetectorAgent

agent = FraudDetectorAgent()
fraud_result = agent.detect_fraud(payslip, bank_statements, cross_doc)
print(f"Fraud probability: {fraud_result['risk_assessment']['fraud_probability']}")
```

## Important Notes
- Balance math must reconcile exactly
- All round number salaries are suspicious
- Multiple signals increase fraud probability