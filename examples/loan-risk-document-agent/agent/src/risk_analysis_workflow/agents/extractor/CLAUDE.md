# Document Extractor Agent

## Purpose
Extracts structured data from classified documents using specialized prompts for each document type.

## Extraction Schemas
- **ID**: Personal info, document info, address, dates
- **PAYSLIP**: Employer, employee, earnings, deductions, YTD
- **BANK_STATEMENT**: Account info, balances, transactions, analysis

## Key Capabilities
- Vision-based extraction for images/PDFs
- Text parsing for readable documents
- CSV transaction processing
- Mathematical verification (gross - deductions = net)

## Input/Output
**Input**: Classified document with type  
**Output**: Structured JSON matching document schema

## Prompts Strategy
- Separate system prompts for each document type
- Detailed JSON schemas in prompts
- Extraction confidence tracking

## Key Files
- `agent.py` - ExtractorAgent with extract_document()
- `prompts.py` - Document-specific extraction prompts

## Common Modifications
- **Add fields**: Update JSON schema in prompts
- **Improve extraction**: Add field descriptions/examples
- **Handle new format**: Add document type prompts

## Testing
```python
from agents.extractor.agent import ExtractorAgent

agent = ExtractorAgent()
extracted = agent.extract_document(file_data, "PAYSLIP")
print(f"Employer: {extracted['employer']['name']}")
```

## Extraction Tips
- Uses gpt-4o for accuracy
- Prompts emphasize null for missing fields
- Includes validation rules (e.g., balance math)

## Important Notes
- Each document type has completely different schema
- Bank statements extract full transaction lists
- Payslips verify mathematical consistency