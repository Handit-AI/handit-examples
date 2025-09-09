# Loan Risk Document Agent

An AI-powered document analysis system for loan risk assessment using LangGraph and OpenAI. This agent processes identity documents, payslips, and bank statements to provide comprehensive risk scoring and recommendations.

## 🏗️ Architecture

This project demonstrates a **pure AI agent-based architecture** where every step is handled by specialized AI agents using OpenAI's GPT-4:

```
┌─────────────┐
│   CLIENT    │
└──────┬──────┘
       │ POST /v1/chat/messages
       ▼
┌─────────────────────────────────────────────┐
│            LANGGRAPH WORKFLOW               │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ Node 1: Document Classifier Agent    │  │
│  └────────────┬─────────────────────────┘  │
│               ▼                             │
│  ┌──────────────────────────────────────┐  │
│  │ Node 2: Document Extractor Agent     │  │
│  └────────────┬─────────────────────────┘  │
│               ▼                             │
│  ┌──────────────────────────────────────┐  │
│  │ Node 3: Identity Validator Agent     │  │
│  └────────────┬─────────────────────────┘  │
│               ▼                             │
│  ┌──────────────────────────────────────┐  │
│  │ Node 4: Cross-Doc Analyzer Agent     │  │
│  └────────────┬─────────────────────────┘  │
│               ▼                             │
│  ┌──────────────────────────────────────┐  │
│  │ Node 5: Fraud Detector Agent         │  │
│  └────────────┬─────────────────────────┘  │
│               ▼                             │
│  ┌──────────────────────────────────────┐  │
│  │ Node 6: Risk Scorer Agent            │  │
│  └────────────┬─────────────────────────┘  │
│               ▼                             │
│  ┌──────────────────────────────────────┐  │
│  │ Node 7: Assistant Composer Agent     │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## 🤖 AI Agents

Each agent is a specialized AI system with its own prompts and logic:

1. **Classifier Agent** - Identifies document types (ID, payslip, bank statement)
2. **Extractor Agent** - Extracts structured data from each document type
3. **Identity Validator** - Validates ID documents and creates identity profiles
4. **CrossDoc Analyzer** - Checks consistency across multiple documents
5. **Fraud Detector** - Identifies fraud signals and financial risks
6. **Risk Scorer** - Calculates final risk score and tier
7. **Assistant Composer** - Generates friendly responses to applicants

## 📁 Project Structure

```
src/
├── risk-analysis-workflow/
│   ├── agents/              # AI Agents (7 specialized agents)
│   │   ├── classifier/
│   │   │   ├── agent.py     # Agent implementation
│   │   │   └── prompts.py   # Agent-specific prompts
│   │   ├── extractor/
│   │   ├── identity_validator/
│   │   ├── crossdoc_analyzer/
│   │   ├── fraud_detector/
│   │   ├── risk_scorer/
│   │   └── assistant_composer/
│   ├── nodes/               # Workflow nodes that call agents
│   ├── tools/               # Document processing utilities
│   ├── state.py             # Workflow state definition
│   └── workflow.py          # Main LangGraph orchestration
├── schemas/                 # Data models (Pydantic)
├── config.py               # Configuration
└── app.py                  # Flask API
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
cp .env.example .env
# Edit .env with your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key"
```

### 3. Run the Test

```bash
python test_workflow.py
```

### 4. Start the API Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 📡 API Usage

### Main Endpoint

**POST** `/v1/chat/messages`

Send documents for risk assessment:

```bash
curl -X POST http://localhost:5000/v1/chat/messages \
  -F "messages=[{\"role\":\"user\",\"content\":\"Please assess my loan application\"}]" \
  -F "files[]=@drivers_license.pdf" \
  -F "files[]=@payslip.pdf" \
  -F "files[]=@bank_statement.csv" \
  -F "options={\"country\":\"US\",\"currency\":\"USD\"}"
```

### Response Format

```json
{
  "assistant_message": "Your application has been conditionally approved...",
  "assessment": {
    "risk_score": 45.0,
    "risk_tier": "MEDIUM",
    "reasons": [
      "Recent ID expiry date approaching",
      "Minor income variance detected"
    ],
    "checks": [
      {
        "check_id": "ID_EXPIRY",
        "passed": false,
        "severity": "medium",
        "details": "ID expires in 25 days"
      }
    ],
    "doc_types": {
      "0": "ID",
      "1": "PAYSLIP",
      "2": "BANK_STATEMENT"
    }
  }
}
```

## 🔍 Risk Assessment Process

### 1. Document Classification
- AI analyzes each uploaded file
- Classifies as ID, PAYSLIP, BANK_STATEMENT, or OTHER
- Uses visual and text analysis

### 2. Data Extraction
- Specialized extraction for each document type
- Handles PDFs, images, and CSVs
- Extracts all relevant fields

### 3. Identity Validation
- Verifies ID document completeness
- Checks expiry dates
- Validates age requirements

### 4. Cross-Document Analysis
- Name matching across documents
- Employer verification
- Income consistency checks
- Currency alignment

### 5. Fraud Detection
- Mathematical verification (balance calculations)
- Income plausibility analysis
- Spending pattern analysis
- Document authenticity checks

### 6. Risk Scoring
- Failed HIGH severity checks: +40 points
- Failed MEDIUM severity checks: +20 points
- Failed LOW severity checks: +10 points
- Risk tiers: LOW (0-39), MEDIUM (40-69), HIGH (70+)

### 7. Response Generation
- Friendly, actionable feedback
- Clear next steps
- Document requests if needed

## 🛠️ Configuration

Edit `.env` file for customization:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_key_here

# Models (can use gpt-4o-mini for cost savings)
CLASSIFICATION_MODEL=gpt-4o-mini
EXTRACTION_MODEL=gpt-4o
ASSISTANT_MODEL=gpt-4o-mini

# Risk Thresholds
LOW_RISK_THRESHOLD=40
HIGH_RISK_THRESHOLD=70

# File Limits
MAX_FILE_SIZE_MB=10
MAX_FILES_PER_REQUEST=6
```

## 📊 Supported Documents

### Identity Documents
- Passports
- Driver's licenses
- National ID cards

### Income Documents
- Payslips/pay stubs
- Salary statements

### Financial Documents
- Bank statements (PDF or CSV)
- Transaction histories

## 🔒 Security & Privacy

- No document storage - all processing is ephemeral
- PII masking in logs
- Configurable to disable PII logging
- All AI processing via OpenAI's secure APIs

## 🧪 Testing

Run the included test script:

```bash
python test_workflow.py
```

This will:
1. Create mock test documents
2. Run the complete workflow
3. Display results
4. Save detailed output to `test_results.json`

## 🎯 Use Cases

- **Fintech Applications** - Automated loan application processing
- **KYC/AML Compliance** - Identity verification and risk assessment
- **Credit Decisioning** - Data-driven credit risk evaluation
- **Document Verification** - Multi-document consistency checking

## 🔧 Extending the System

### Adding New Document Types

1. Update the classifier agent prompts in `agents/classifier/prompts.py`
2. Add extraction prompts in `agents/extractor/prompts.py`
3. Update relevant analysis agents

### Adding New Risk Checks

1. Modify the fraud detector prompts in `agents/fraud_detector/prompts.py`
2. Update risk scorer logic in `agents/risk_scorer/prompts.py`

### Customizing Responses

Edit prompts in `agents/assistant_composer/prompts.py` to change response style and tone.

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

This is a demonstration system for educational purposes. In production:
- Implement proper authentication and authorization
- Add comprehensive error handling
- Consider GDPR/privacy compliance
- Implement audit logging
- Add monitoring and alerting
- Consider using dedicated document processing services
- Implement retry logic and failover
- Add rate limiting and request validation

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - For workflow orchestration
- [OpenAI GPT-4](https://openai.com) - For AI processing
- [Flask](https://flask.palletsprojects.com/) - For API framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - For data validation