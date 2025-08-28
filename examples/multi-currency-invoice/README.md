# Multi-Currency Invoice API

A simple Express.js API with MVC pattern design featuring health check endpoints, bulk file upload with session management, and AI-powered data extraction using LangChain with parallel processing, comprehensive data extraction, and VLLM support.

## 🏗️ Architecture

This project follows the **MVC (Model-View-Controller)** pattern:

- **Models**: Business logic and data handling (services)
- **Views**: API responses (JSON)
- **Controllers**: Request handling and response formatting
- **Routes**: URL endpoint definitions

## 📁 Project Structure

```
multi-currency-invoice/
├── controllers/
│   ├── HealthController.js    # Health check logic
│   └── FileController.js      # File upload and LangChain processing
├── routes/
│   ├── healthRoutes.js        # Health endpoint routes
│   └── fileRoutes.js          # File upload and LangChain routes
├── services/
│   ├── HealthService.js       # Business logic for health checks
│   ├── FileService.js         # File handling and storage
│   └── LangChainService.js    # AI-powered data extraction with VLLM support
├── assets/                    # File storage directory
│   └── {session_id}/         # Session-specific directories
│       ├── files/            # Uploaded files
│       └── structured/       # Extracted data in JSON format
├── server.js                  # Main application entry point
├── package.json               # Dependencies and scripts
├── config.env.example         # Environment variables template
└── README.md                  # This file
```

## 🚀 Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- OpenAI API key for LangChain integration OR VLLM endpoint for local models

### Installation

1. Navigate to the project directory:
   ```bash
   cd examples/multi-currency-invoice
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp config.env.example .env
   # Edit .env with your API keys and preferred model
   ```

4. Start the server:
   ```bash
   # Development mode with auto-reload
   npm run dev
   
   # Production mode
   npm start
   ```

The server will start on port 3000 by default.

## 🔍 API Endpoints

### Health Check Endpoints

#### 1. Basic Health Check
- **URL**: `GET /api/health`
- **Description**: Basic service health status

#### 2. Detailed Health Check
- **URL**: `GET /api/health/detailed`
- **Description**: Comprehensive health information including system metrics

#### 3. Custom Health Check
- **URL**: `GET /api/health/check?include=basic,detailed&timeout=5000`
- **Description**: Customizable health check with query parameters

### File Upload & AI Processing Endpoints

#### 1. Bulk File Upload with AI Processing
- **URL**: `POST /api/files/upload`
- **Description**: Upload multiple files and automatically process them with LangChain for comprehensive data extraction
- **Form Data**:
  - `files`: Array of files (max 10 files, 50MB each)
  - `session_id`: Optional session identifier (auto-generated if not provided)
- **Response**:
  ```json
  {
    "success": true,
    "message": "Files uploaded and processed successfully",
    "sessionId": "session_1234567890",
    "totalFiles": 3,
    "files": [...],
    "storagePath": "assets/session_1234567890/files/",
    "langChainProcessing": {
      "status": "completed",
      "extractedData": {...},
      "processingCompletedAt": "2024-01-01T00:00:00.000Z",
      "structuredDataPath": "assets/session_1234567890/structured/"
    }
  }
  ```

#### 2. Get Session Files
- **URL**: `GET /api/files/session/:sessionId`
- **Description**: Retrieve information about files in a specific session

#### 3. Get LangChain Processing Results
- **URL**: `GET /api/files/langchain/:sessionId`
- **Description**: Get AI processing results and extracted data for a session

### Root Endpoint
- **URL**: `GET /`
- **Description**: API information and available endpoints

## 🤖 AI-Powered Data Extraction

The API now includes an **enhanced LangChain service** that automatically processes uploaded documents with parallel processing, comprehensive data extraction, and VLLM support:

### **What LangChain Extracts:**
- **Document Type**: Invoice, receipt, purchase order, contract, statement, quote, estimate, etc.
- **Vendor Information**: Company name, address, contact details
- **Customer Information**: Client details, addresses, contact information
- **Financial Data**: Amounts, currencies, dates, payment terms
- **Line Items**: Detailed breakdown with quantities, prices, descriptions
- **Tax Information**: Tax amounts, rates, types
- **Additional Charges**: Shipping, handling, discounts, processing fees
- **Table Data**: Any structured information from tables, grids, or forms
- **Key-Value Pairs**: All important data fields from documents
- **Custom Fields**: Document-specific information discovered by the AI
- **Dynamic Fields**: Fields that the LLM discovers and creates based on content

### **Enhanced System Prompt:**
The AI is configured as an expert OCR and data extraction specialist with expertise in:
1. **Document Analysis**: Analyze any type of financial document and identify its structure
2. **Dynamic Field Discovery**: Discover and extract ALL relevant fields, not just predefined ones
3. **Table and Structure Detection**: Identify tables, grids, line items, and any structured layouts
4. **Multi-Format Support**: Handle invoices, receipts, POs, contracts, statements, and any financial document
5. **Flexible Extraction**: Adapt your extraction to the specific document type and format
6. **Comprehensive Coverage**: Extract every piece of information you can find

### **Processing Features:**
- **Parallel Processing**: All invoices processed simultaneously for faster results
- **Flexible Field Extraction**: AI discovers and creates fields based on document content
- **Comprehensive Extraction**: Captures every piece of information possible
- **Table Detection**: Automatically identifies and extracts table data
- **Multi-Currency Support**: Handles various currencies and exchange rates
- **High Confidence**: 85-100% confidence levels in extraction
- **Structured Output**: Consistent JSON format for all extractions
- **VLLM Support**: Works with local/self-hosted models for privacy and cost control

### **Processing Flow:**
1. **File Upload** → Files saved to session directory
2. **File Content Reading** → Actual file content extracted (text, base64 for images/PDFs)
3. **Parallel Processing** → All files processed simultaneously with LangChain
4. **Flexible Extraction** → AI discovers fields and creates custom structures
5. **JSON Storage** → Structured data saved to `assets/{session_id}/structured/`
6. **Response** → Complete results with extracted data and storage paths

## 📁 File Storage Structure

Files and extracted data are organized by session:

```
assets/
├── session_1234567890/
│   ├── files/                    # Original uploaded files
│   │   ├── invoice.pdf
│   │   ├── receipt.jpg
│   │   └── document.docx
│   └── structured/               # Extracted data in JSON format
│       ├── invoice_extracted_data.json
│       ├── receipt_extracted_data.json
│       ├── document_extracted_data.json
│       └── session_summary_session_1234567890.json
├── session_0987654321/
│   ├── files/
│   └── structured/
```

### **JSON File Structure:**
Each extracted document gets its own JSON file with:
- **Metadata**: File info, processing time, session details
- **Extracted Data**: All extracted information in structured format
- **Custom Fields**: Fields discovered by the AI that don't fit standard categories
- **Confidence Levels**: Processing confidence for each field
- **Processing Notes**: Details about the extraction process

## 🚀 VLLM Support

The API now supports **VLLM (Very Large Language Model)** for local model deployment:

### **Benefits of VLLM:**
- **Privacy**: Process documents locally without sending data to external APIs
- **Cost Control**: No per-token charges for external API calls
- **Custom Models**: Use your own fine-tuned models for specific document types
- **Offline Processing**: Work without internet connectivity
- **Customization**: Modify models for your specific use case

### **VLLM Configuration:**
```bash
# .env
VLLM_ENDPOINT=http://localhost:8000/v1
OPENAI_MODEL=your_local_model_name
```

### **VLLM Setup:**
1. **Install VLLM**: `pip install vllm`
2. **Start Server**: `python -m vllm.entrypoints.openai.api_server --model your_model_name`
3. **Configure API**: Set `VLLM_ENDPOINT` in your `.env` file

## 🛠️ Development

### Available Scripts

- `npm start`: Start the production server
- `npm run dev`: Start the development server with nodemon (auto-reload)

### Adding New Endpoints

1. **Create a Service** in the `services/` directory
2. **Create a Controller** in the `controllers/` directory
3. **Create Routes** in the `routes/` directory
4. **Register Routes** in `server.js`

### Example: Adding a New Service

```javascript
// services/ExampleService.js
class ExampleService {
  static async doSomething() {
    // Business logic here
    return { message: "Success" };
  }
}

module.exports = ExampleService;
```

## 🔧 Configuration

The application can be configured using environment variables:

- `PORT`: Server port (default: 3000)
- `NODE_ENV`: Environment (default: development)
- `OPENAI_API_KEY`: Your OpenAI API key for LangChain integration
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-5-mini-2025-08-07)
- `VLLM_ENDPOINT`: VLLM server endpoint for local models (optional)

## 📊 Monitoring

The health endpoints provide comprehensive monitoring capabilities:

- Service status and uptime
- System resource usage (memory, CPU)
- Response time metrics
- Environment information

## 🚨 Error Handling

The API includes comprehensive error handling:

- 404 for non-existent endpoints
- 500 for internal server errors
- Structured error responses with timestamps

## 🔒 Security

Built-in security features:

- Helmet.js for security headers
- CORS configuration
- Input validation and sanitization
- File type restrictions
- Local processing option with VLLM for sensitive documents

## 📝 License

MIT License - see LICENSE file for details.
