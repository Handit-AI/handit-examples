# Data Schemas (Pydantic Models)

## Purpose
Type-safe data models for documents and assessments using Pydantic.

## Schema Files

### documents.py
- `IDRecord` - Identity document structure
- `PayslipRecord` - Payslip/wage statement structure
- `BankStatementRecord` - Bank statement with transactions
- `Transaction` - Individual transaction
- `ComputedMetrics` - Calculated financial metrics

### assessment.py
- `Identity` - Normalized identity profile
- `Employment` - Employment information
- `Banking` - Banking and financial profile
- `ApplicantFinancialProfile` - Complete profile
- `Check` - Risk check result
- `Assessment` - Complete risk assessment
- `ChatRequest` - API request format
- `ChatResponse` - API response format

## Key Patterns
- All models inherit from Pydantic BaseModel
- Optional fields use Optional[Type]
- Dates use date type
- Enums for constrained values (Literal)
- Nested models for complex structures

## Usage
```python
from schemas import IDRecord, Assessment

# Create model instance
id_doc = IDRecord(
    id_type="passport",
    full_name="John Smith",
    id_number="123456"
)

# Serialize to dict/JSON
data = id_doc.model_dump()
json_str = id_doc.model_dump_json()
```

## Common Modifications
- **Add field**: Add to model with type annotation
- **Make required**: Remove Optional wrapper
- **Add validation**: Use Pydantic validators
- **Change constraints**: Update Field() parameters

## Important Notes
- Used for API request/response validation
- NOT used in workflow (uses Dict instead)
- Provides automatic JSON serialization
- Type hints improve IDE support