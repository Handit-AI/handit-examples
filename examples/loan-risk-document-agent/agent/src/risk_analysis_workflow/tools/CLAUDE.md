# Document Processing Tools

## Purpose
Utility functions for preparing documents for AI processing.

## Key Tools

### document_tools.py
- `pdf_to_image_base64()` - Convert PDF pages to base64 images
- `pdf_to_text()` - Extract text from PDFs
- `image_to_base64()` - Convert images to base64
- `csv_to_text_preview()` - Create readable CSV preview
- `prepare_document_for_ai()` - Main preparation function

### openai_tools.py
- `call_openai_structured()` - Get JSON response from OpenAI
- `call_openai_text()` - Get text response from OpenAI
- `get_llm()` - Get LangChain ChatOpenAI instance

## Document Preparation Flow
1. Identify file type (PDF, image, CSV)
2. Convert to appropriate format:
   - PDFs → Image (page 1) + extracted text
   - Images → Base64 encoding
   - CSVs → Text preview with structure
3. Return prepared content for AI

## Key Patterns
- PDFs processed as both image and text
- CSVs converted to readable text format
- Images encoded as base64 for GPT-4 Vision
- All content prepared for OpenAI API

## Common Tasks
- **Add file type**: Update prepare_document_for_ai()
- **Change DPI**: Modify pdf_to_image_base64() dpi parameter
- **Adjust CSV preview**: Change max_rows in csv_to_text_preview()

## Important Notes
- Uses pdf2image for PDF rendering
- Pandas for CSV processing
- PIL for image handling
- All tools are synchronous