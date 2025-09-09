# Cross-Document Analyzer Agent

## Purpose
Analyzes consistency across multiple documents to detect discrepancies and potential fraud.

## Consistency Checks
1. **NAME_MATCH** - Names consistent across documents
2. **EMPLOYER_MATCH** - Employer in payslip matches bank deposits
3. **INCOME_CONSISTENCY** - Stated vs observed income
4. **CURRENCY_CONSISTENCY** - Same currency used
5. **TIMELINE_CONSISTENCY** - Dates align logically

## Analysis Areas
- Name matching with fuzzy logic
- Employer verification in deposits
- Income variance analysis (20% tolerance)
- Timeline gap detection
- Deposit pattern recognition

## Input/Output
**Input**: ID data, payslip data, bank statements  
**Output**: Cross-doc analysis + consistency checks + fraud indicators

## Key Files
- `agent.py` - CrossDocAnalyzerAgent with analyze_documents()
- `prompts.py` - Cross-reference rules and patterns

## Prompts Strategy
- Detailed consistency rules in system prompt
- Fraud pattern detection guidelines
- Tolerance thresholds specified

## Common Modifications
- **Adjust tolerance**: Change variance percentages
- **Add check**: Update consistency_checks section
- **New pattern**: Add to fraud_indicators

## Testing
```python
from agents.crossdoc_analyzer.agent import CrossDocAnalyzerAgent

agent = CrossDocAnalyzerAgent()
analysis = agent.analyze_documents(id_data, payslip_data, bank_data)
print(f"Consistent: {analysis['verification_summary']['documents_consistent']}")
```

## Important Notes
- Considers name variations (nicknames, middle names)
- 20% income variance is acceptable
- Flags suspicious patterns for manual review