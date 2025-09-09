# Document Classifier Agent

## Purpose
Identifies document types from raw files using GPT-4 vision and text analysis.

## Capabilities
- Vision analysis for PDFs and images
- Text analysis for CSVs and text documents
- Confidence scoring for classification accuracy
- Multi-page PDF handling (checks page 2 if confidence low)

## Input/Output
**Input**: File with content (bytes), type (extension), name  
**Output**: Classification with label, confidence, reasoning

## Classification Categories
- **ID**: Government IDs, passports, driver's licenses
- **PAYSLIP**: Pay stubs, salary slips, wage statements
- **BANK_STATEMENT**: Bank statements, transaction histories
- **OTHER**: Anything that doesn't fit above

## Key Files
- `agent.py` - ClassifierAgent class with classify_document()
- `prompts.py` - Classification prompts for different content types

## Prompts Strategy
- System prompt defines categories and output format
- Different user prompts for images vs text vs CSV
- Requests reasoning to improve accuracy

## Common Modifications
- **Add document type**: Update SYSTEM_PROMPT categories
- **Improve accuracy**: Add examples to prompts
- **Change confidence threshold**: Modify agent.py logic

## Testing
```python
from agents.classifier.agent import ClassifierAgent

agent = ClassifierAgent()
result = agent.classify_document(file_data)
print(f"Type: {result['label']}, Confidence: {result['confidence']}")
```

## Important Notes
- Uses gpt-4o-mini for cost efficiency
- Falls back to "OTHER" if classification fails
- Confidence < 0.7 triggers re-classification for PDFs