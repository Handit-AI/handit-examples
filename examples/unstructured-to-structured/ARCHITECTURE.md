# System Architecture

This document explains the technical architecture of the Unstructured to Structured Data Converter.

## 🏗️ High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   LangGraph      │    │   OpenAI        │
│   Server        │    │   Workflow       │    │   LLM Models    │
│                 │    │                  │    │                 │
│ • File Upload   │───▶│ • Schema         │───▶│ • GPT-4o-mini   │
│ • Session Mgmt  │    │   Inference      │    │ • Vision        │
│ • API Endpoints │    │ • Data Capture   │    │ • Text          │
└─────────────────┘    │ • CSV Generation │    └─────────────────┘
                       └──────────────────┘
```

## 🔄 Workflow Flow

### 1. Document Upload (FastAPI)
- **Endpoint**: `POST /bulk-unstructured-to-structured`
- **Input**: Multiple files + session_id
- **Output**: Files saved to session directory
- **Next**: Triggers LangGraph workflow

### 2. Schema Inference (Node 1)
- **Input**: All uploaded documents (images, PDFs, text)
- **Process**: Multimodal LLM analysis
- **Output**: Unified JSON schema
- **Key**: Works with any document type

### 3. Data Extraction (Node 2)
- **Input**: Documents + inferred schema
- **Process**: Field mapping with confidence scoring
- **Output**: Structured JSON files
- **Key**: Strict schema adherence

### 4. CSV Generation (Node 3)
- **Input**: Structured JSON files
- **Process**: LLM table planning + pandas
- **Output**: Organized CSV tables
- **Key**: Automatic table design

## 📊 Data Flow

```
Documents → Schema → Structured JSON → CSV Tables
    ↓           ↓           ↓            ↓
  Upload    Inference   Extraction   Generation
```

## 🧩 Component Details

### FastAPI Server (`main.py`)
- **Purpose**: HTTP API interface
- **Features**: File upload, session management, CORS
- **Integration**: Calls LangGraph workflow

### LangGraph Workflow (`graph/graph.py`)
- **Purpose**: Orchestrates the 3-step process
- **State Management**: Passes data between nodes
- **Error Handling**: Graceful failure recovery

### Processing Nodes
Each node is a Python function that:
- Receives state from previous node
- Processes data using LLM chains
- Updates state for next node
- Handles errors gracefully

### LLM Chains (`graph/chains/`)
- **document_inference**: Schema creation
- **invoice_data_extraction**: Field mapping
- **generation**: CSV table planning

## 🔧 State Management

The `GraphState` class manages data flow:

```python
class GraphState(TypedDict, total=False):
    session_id: str                    # Unique session identifier
    unstructured_paths: List[str]      # Input file paths
    inferred_schema: Dict[str, Any]   # Generated schema
    structured_json_paths: List[str]   # Output JSON files
    generated_csv_paths: List[str]     # Output CSV files
    errors: List[str]                  # Error tracking
    execution_id: str                  # Tracing ID
```

## 🚀 Performance Considerations

### Scalability
- **Session-based processing**: Each upload creates isolated session
- **File batching**: Process multiple documents together
- **Memory management**: Files processed sequentially

### Optimization Opportunities
- **Parallel processing**: Process documents concurrently
- **Caching**: Cache schemas for similar document types
- **Streaming**: Handle large files without loading into memory

## 🔒 Security & Privacy

### File Handling
- Files saved to session-specific directories
- No cross-session data leakage
- Temporary storage (consider cleanup policies)

### API Security
- CORS configuration for web clients
- Session isolation
- Input validation and sanitization

## 🧪 Testing Strategy

### Unit Testing
- Test individual nodes in isolation
- Mock LLM responses
- Validate state transitions

### Integration Testing
- End-to-end workflow testing
- Sample document processing
- Error scenario validation

### Performance Testing
- Large document set processing
- Memory usage monitoring
- Response time benchmarking

## 🔮 Future Enhancements

### Planned Features
- **Better PDF support**: Page-by-page image extraction
- **Schema validation**: Confidence scoring for schemas
- **Custom field mapping**: User-defined field rules
- **Batch processing**: Queue-based processing for large sets

### Technical Improvements
- **Async processing**: Non-blocking file processing
- **Database integration**: Persistent schema storage
- **API rate limiting**: Prevent abuse
- **Monitoring**: Metrics and alerting

## 📚 Related Documentation

- [LangGraph Concepts](https://langchain-ai.github.io/langgraph/concepts/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/best-practices/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

---

This architecture provides a solid foundation for document processing while maintaining flexibility for future enhancements.
