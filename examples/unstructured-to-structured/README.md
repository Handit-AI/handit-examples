# Unstructured to Structured Data Converter

An AI-powered tool that automatically converts messy, unstructured documents into clean, structured data and CSV tables. Perfect for processing invoices, purchase orders, contracts, medical reports, and any other document types.

## 🚀 What This Tool Does

**The Problem:** You have a bunch of documents sitting around - invoices, purchase orders, contracts, medical reports, whatever - and you want to actually use that data. But right now it's just sitting there in PDFs and images, completely useless.

**The Solution:** This tool takes all those documents and spits out structured data and CSV tables. Now you can actually visualize and work with your data instead of staring at PDFs all day.

## 🏗️ How It Works

The system uses a **3-step LangGraph workflow** to process your documents:

### Step 1: Schema Inference (`inference_schema`)
- A vLLM model analyzes your documents and suggests the best JSON structure
- Works with any document type - it figures out the right format automatically
- Creates a unified schema that all documents will follow

### Step 2: Data Extraction (`invoice_data_capture`)
- A specialized LLM maps fields from your documents to the inferred schema
- Strictly follows the schema - every document gets the same structure
- Handles images, PDFs, and text files
- Outputs structured JSON with confidence scores and reasoning

### Step 3: CSV Generation (`generate_csv`)
- Another LLM designs CSV tables to present all your data clearly
- Uses pandas to create organized, readable spreadsheets
- Automatically handles arrays and nested data

## 📁 Project Structure

```
unstructured-to-structured/
├── main.py                 # FastAPI server entry point
├── requirements.txt        # Python dependencies
├── graph/                 # LangGraph workflow components
│   ├── graph.py          # Main workflow definition
│   ├── state.py          # Data structure definitions
│   ├── consts.py         # Workflow constants
│   ├── nodes/            # Individual workflow nodes
│   │   ├── inference_schema.py
│   │   ├── invoice_data_capture.py
│   │   └── generate_csv.py
│   └── chains/           # LangChain processing chains
│       ├── document_inference.py
│       ├── invoice_data_extraction.py
│       └── generation.py
├── services/              # External service integrations
│   └── handit_service.py
└── assets/               # Input/output directories
    ├── outputs/          # Session-based outputs
    ├── structured/       # JSON outputs
    └── csv/             # CSV table outputs
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (or compatible LLM provider)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd handit-examples/examples/unstructured-to-structured
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
   echo "OPENAI_MODEL=gpt-4o-mini" >> .env
   ```

5. **Run the server**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

**📖 Need more help?** Check out our [Getting Started Guide](GETTING_STARTED.md) for detailed step-by-step instructions!

## 📖 API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Process Documents
```bash
curl -X POST "http://localhost:8000/bulk-unstructured-to-structured" \
  -F "session_id=test_session_123" \
  -F "files=@invoice1.pdf" \
  -F "files=@invoice2.jpg"
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: gpt-4o-mini)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

### Supported File Types
- **Images**: PNG, JPG, JPEG, GIF, BMP
- **Documents**: PDF (basic support)
- **Text**: Any text-based format

## 🧪 Testing

The project includes sample data in the `assets/` directory:

- **Test documents**: Various invoice and document samples
- **Expected outputs**: JSON and CSV examples
- **Validation data**: For testing the workflow

## 🔍 How the Workflow Works

### 1. Schema Inference Node
```python
# Analyzes all uploaded documents
# Creates a unified JSON schema
# Handles multilingual and mixed document types
```

### 2. Data Capture Node
```python
# Maps document content to the inferred schema
# Extracts structured data with confidence scores
# Handles multimodal input (images + text)
```

### 3. CSV Generation Node
```python
# Plans optimal table structure
# Generates CSV files using pandas
# Handles nested data and arrays
```

## 🚧 Development

### Adding New Document Types
1. The system automatically detects document types
2. No manual configuration needed
3. Schema adapts to your data

### Customizing the Workflow
1. Modify nodes in `graph/nodes/`
2. Adjust chains in `graph/chains/`
3. Update the workflow in `graph/graph.py`

### Extending the Schema
1. The inference system learns from your documents
2. Add custom fields by including examples
3. Schema evolves with your data

## 🤝 Contributing

We welcome contributions! Here's how to help:

### Areas for Improvement
- **PDF Processing**: Better PDF text extraction
- **Image Quality**: Handle low-quality scans
- **Schema Validation**: More robust schema inference
- **Performance**: Optimize for large document sets
- **Testing**: Add comprehensive test coverage

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- Follow PEP 8
- Add type hints
- Include docstrings
- Use meaningful variable names

## 📊 Example Output

### Structured JSON
```json
{
  "header": {
    "document_title": {
      "value": "Invoice",
      "normalized_value": "Invoice",
      "reason": "Large prominent text at top of document labeled 'Invoice'",
      "confidence": 0.99
    },
    "vendor_name": {
      "value": "Craigs' Landscaping",
      "normalized_value": "Craigs' Landscaping",
      "reason": "Top-left block under document title",
      "confidence": 0.98
    }
  }
}
```

### Generated CSV
- `general.csv`: Document-level information
- `line_items.csv`: Itemized details
- Custom tables based on your data structure

## 🐛 Troubleshooting

### Common Issues
1. **API Key Error**: Check your `.env` file
2. **File Upload Fails**: Verify file size and format
3. **Schema Inference Errors**: Check document quality
4. **Memory Issues**: Process documents in smaller batches

### Debug Mode
Enable detailed logging by setting log level to DEBUG in `main.py`.

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

## 📋 Additional Documentation

- **[Getting Started Guide](GETTING_STARTED.md)** - Step-by-step setup instructions
- **[Architecture Guide](ARCHITECTURE.md)** - Technical system design and components

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

- Built with LangGraph and LangChain
- Powered by OpenAI's language models
- Community contributors and feedback

---

**Questions?** Open an issue or start a discussion. We're here to help!
