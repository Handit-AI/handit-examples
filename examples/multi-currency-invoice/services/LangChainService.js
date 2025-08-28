const { ChatOpenAI } = require('langchain/chat_models/openai');
const { PromptTemplate } = require('langchain/prompts');
const { StructuredOutputParser } = require('langchain/output_parsers');
const { HumanMessage } = require('langchain/schema');
const fs = require('fs').promises;
const path = require('path');

class LangChainService {
    constructor() {

        // VLLM-compatible configuration for gpt-5-mini-2025-08-07
        this.llm = new ChatOpenAI({
            openAIApiKey: process.env.OPENAI_API_KEY,
            modelName: process.env.OPENAI_MODEL || 'gpt-5-mini-2025-08-07',
            // temperature: 0,  // Removed - this model only supports default value (1)
            maxCompletionTokens: 4000,  // VLLM-compatible parameter
            // Additional VLLM-compatible parameters (uncomment if needed)
            // topK: 40,  // For diversity control
            // repetitionPenalty: 1.1,  // To avoid repetitions
        });

        // Use a more flexible parser that lets the LLM define the structure
        this.parser = StructuredOutputParser.fromNamesAndDescriptions({
            // Core fields that are commonly found in financial documents
            documentType: "The type of document (invoice, receipt, purchase order, contract, statement, etc.)",
            vendor: "The vendor or company name that issued the document",
            vendorAddress: "The vendor's address information",
            vendorContact: "The vendor's contact information",
            customer: "The customer or client name if present",
            invoiceNumber: "The invoice or document number",
            invoiceDate: "The date when the invoice was issued",
            dueDate: "The due date for payment if present",
            headerCurrency: "The header currency used in the document, in Currency code ISO 4217 format",
            totalAmount: "The total amount including all taxes and charges",
            lineItems: "Array of line items with their details",
            paymentTerms: "The payment terms and conditions",
            notes: "Any additional notes or comments",
            confidence: "Confidence level of the extraction (0-1)",
            extractedText: "The raw text extracted from the document",

            // Dynamic fields - let the LLM add any additional fields it finds
            additionalFields: "Any other relevant fields or data found in the document that don't fit the above categories",
            customFields: "Object containing any custom or document-specific fields discovered during extraction"
        });
    }

    /**
     * Process uploaded files using LangChain for data extraction in parallel
     * @param {Array} files - Array of file information from FileService
     * @param {string} sessionId - Session identifier
     * @returns {Object} Processing results with extracted data
     */
    async processFilesWithLangChain(files, sessionId) {
        try {
            console.log(`Starting LangChain processing for session: ${sessionId}`);

            // Process all files in parallel for better performance
            const processingPromises = files.map(file =>
                this.processSingleFile(file, sessionId)
            );

            const processingResults = await Promise.all(processingPromises);

            // Save structured data to JSON files
            await this.saveStructuredData(sessionId, processingResults);

            return {
                sessionId: sessionId,
                totalFiles: files.length,
                processedFiles: processingResults.length,
                results: processingResults,
                processingCompletedAt: new Date().toISOString(),
                structuredDataPath: `assets/${sessionId}/structured/`
            };

        } catch (error) {
            console.error('LangChain processing error:', error);
            throw new Error(`Failed to process files with LangChain: ${error.message}`);
        }
    }

    /**
     * Process a single file with LangChain
     * @param {Object} file - File information
     * @param {string} sessionId - Session identifier
     * @returns {Object} Processing result for the file
     */
    async processSingleFile(file, sessionId) {
        try {
            console.log(`Processing file: ${file.originalName}`);

            // Read actual file content
            const fileContent = await this.readFileContent(file.path, file.mimetype);

            // Process with LangChain using real file content
            const extractedData = await this.extractDataWithLangChain(fileContent, file.originalName, file.path);

            return {
                file: file.originalName,
                success: true,
                extractedData: extractedData,
                processingTime: new Date().toISOString(),
                filePath: file.path,
                fileSize: file.size,
                mimeType: file.mimetype
            };

        } catch (error) {
            console.error(`Error processing file ${file.originalName}:`, error);
            return {
                file: file.originalName,
                success: false,
                error: error.message,
                processingTime: new Date().toISOString(),
                filePath: file.path,
                fileSize: file.size,
                mimeType: file.mimetype
            };
        }
    }

    /**
     * Save structured data to JSON files in assets/{session_id}/structured/
     * @param {string} sessionId - Session identifier
     * @param {Array} processingResults - Results from file processing
     */
    async saveStructuredData(sessionId, processingResults) {
        try {
            const structuredDir = path.join(__dirname, '../assets', sessionId, 'structured');

            // Ensure structured directory exists
            await fs.mkdir(structuredDir, { recursive: true });

            // Save each file's extracted data to a separate JSON file
            for (const result of processingResults) {
                if (result.success && result.extractedData) {
                    const fileName = path.basename(result.file, path.extname(result.file));
                    const jsonFileName = `${fileName}_extracted_data.json`;
                    const jsonFilePath = path.join(structuredDir, jsonFileName);

                    const jsonData = {
                        metadata: {
                            originalFile: result.file,
                            processingTime: result.processingTime,
                            fileSize: result.fileSize,
                            mimeType: result.mimeType,
                            sessionId: sessionId,
                            extractedAt: new Date().toISOString()
                        },
                        extractedData: result.extractedData
                    };

                    await fs.writeFile(jsonFilePath, JSON.stringify(jsonData, null, 2), 'utf-8');
                    console.log(`Saved structured data for ${result.file} to ${jsonFilePath}`);
                }
            }

            // Save a summary file with all results
            const summaryFileName = `session_summary_${sessionId}.json`;
            const summaryFilePath = path.join(structuredDir, summaryFileName);

            const summaryData = {
                sessionId: sessionId,
                processingSummary: {
                    totalFiles: processingResults.length,
                    successfulExtractions: processingResults.filter(r => r.success).length,
                    failedExtractions: processingResults.filter(r => !r.success).length,
                    processingCompletedAt: new Date().toISOString()
                },
                fileResults: processingResults.map(result => ({
                    file: result.file,
                    success: result.success,
                    processingTime: result.processingTime,
                    error: result.error || null
                }))
            };

            await fs.writeFile(summaryFilePath, JSON.stringify(summaryData, null, 2), 'utf-8');
            console.log(`Saved session summary to ${summaryFilePath}`);

        } catch (error) {
            console.error('Error saving structured data:', error);
            throw new Error(`Failed to save structured data: ${error.message}`);
        }
    }

    /**
     * Read actual file content based on file type
     * @param {string} filePath - Path to the file
     * @param {string} mimeType - MIME type of the file
     * @returns {string} File content or description
     */
    async readFileContent(filePath, mimeType) {
        try {
            if (mimeType.startsWith('text/')) {
                // For text files, read directly
                return await fs.readFile(filePath, 'utf-8');
            } else if (mimeType.startsWith('image/')) {
                // For images, convert to base64 so LLM can process them
                const imageBuffer = await fs.readFile(filePath);
                const base64Image = imageBuffer.toString('base64');
                // Create proper data URL format that LangChain can process
                const dataUrl = `data:${mimeType};base64,${base64Image}`;
                return `[IMAGE_BASE64:${dataUrl}]`;
            } else if (mimeType === 'application/pdf') {
                // For PDFs, try to read as text first
                try {
                    return await fs.readFile(filePath, 'utf-8');
                } catch (error) {
                    // If PDF can't be read as text, convert to base64
                    const pdfBuffer = await fs.readFile(filePath);
                    const base64Pdf = pdfBuffer.toString('base64');
                    const dataUrl = `data:${mimeType};base64,${base64Pdf}`;
                    return `[PDF_BASE64:${dataUrl}]`;
                }
            } else if (mimeType.includes('word') || mimeType.includes('excel') || mimeType.includes('powerpoint')) {
                // For Office documents, convert to base64
                const docBuffer = await fs.readFile(filePath);
                const base64Doc = docBuffer.toString('base64');
                const dataUrl = `data:${mimeType};base64,${base64Doc}`;
                return `[OFFICE_DOC_BASE64:${dataUrl}]`;
            } else {
                // For other file types, try to read as text first
                try {
                    return await fs.readFile(filePath, 'utf-8');
                } catch (error) {
                    // If can't read as text, convert to base64
                    const fileBuffer = await fs.readFile(filePath);
                    const base64File = fileBuffer.toString('base64');
                    const dataUrl = `data:${mimeType};base64,${base64File}`;
                    return `[FILE_BASE64:${dataUrl}]`;
                }
            }
        } catch (error) {
            throw new Error(`Failed to read file content: ${error.message}`);
        }
    }

    /**
     * Extract data using LangChain with flexible prompts that let the LLM define the structure
     * @param {string} fileContent - Content of the file to process
     * @param {string} fileName - Name of the file being processed
     * @param {string} filePath - Path to the file for reference
     * @returns {Object} Extracted structured data
     */
    async extractDataWithLangChain(fileContent, fileName, filePath) {
        try {
            // Flexible system prompt that encourages the LLM to discover and define fields
            const systemPrompt = `You are an expert OCR and data extraction specialist with years of experience in processing financial documents. Your expertise includes:

1. **Document Analysis**: Analyze any type of financial document and identify its structure
2. **Dynamic Field Discovery**: Discover and extract ALL relevant fields, not just predefined ones
3. **Table and Structure Detection**: Identify tables, grids, line items, and any structured layouts
4. **Multi-Format Support**: Handle invoices, receipts, POs, contracts, statements, and any financial document
5. **Flexible Extraction**: Adapt your extraction to the specific document type and format
6. **Comprehensive Coverage**: Extract every piece of information you can find
7. **Base64 File Processing**: You can process base64-encoded images, PDFs, and documents directly

IMPORTANT FILE PROCESSING NOTES:
- Images are provided as base64 data URLs: [IMAGE_BASE64:data:image/png;base64,...]
- PDFs are provided as base64 data URLs: [PDF_BASE64:data:application/pdf;base64,...]
- Office documents are provided as base64 data URLs: [OFFICE_DOC_BASE64:data:application/...;base64,...]
- You can directly analyze and extract text from these base64-encoded files
- For images, perform OCR to extract all visible text, numbers, and structured data
- For PDFs and Office docs, extract all text content and structured information

Your task is to analyze the provided document and extract structured information. You are NOT limited to predefined fields - discover and create fields based on what you find in the document. Be creative and thorough in identifying all relevant data.

IMPORTANT: 
- Extract ALL information you can find, even if it doesn't fit standard categories
- Create custom fields for document-specific information
- Focus on tables, line items, and structured data
- Be flexible and adaptive to different document formats
- Process base64 files directly - don't just report that you can't access them`;

            // User prompt that encourages field discovery
            const userPrompt = `Please analyze the following document and extract ALL data you can find:

**Document Name**: ${fileName}
**File Path**: ${filePath}

**Document Content**:
${fileContent}

Please extract information in a structured format. You are NOT limited to predefined fields. Discover and create fields based on what you find in the document.

**Required Fields** (these should always be present):
- documentType: What type of document is this?
- headerCurrency: Analyze the document and determine the header currency as an ISO 4217 code (e.g., USD, EUR, COP)
- invoiceDate: The date when the invoice was issued, in this format: DD-MM-YYYY
- confidence: Your confidence level (0-1)
- extractedText: The raw text or content you extracted

**Standard Fields** (extract if present):
- vendor, customer, invoiceNumber, dates, amounts, headerCurrency, lineItems, etc.

**Custom Fields** (create these based on what you discover):
- Any additional fields, tables, or structured data you find
- Document-specific information that doesn't fit standard categories
- Special fields, codes, references, or metadata

**Guidelines**:
1. Be extremely thorough - extract every piece of information
2. Create custom fields for unique document features
3. Focus on tables, line items, and structured layouts
4. Don't limit yourself to predefined fields
5. Adapt to the specific document type and format

Provide your analysis with maximum detail and flexibility.`;

            // Create the prompt template
            const promptTemplate = PromptTemplate.fromTemplate(`
${systemPrompt}

${userPrompt}

{format_instructions}
`);

            // Get format instructions from the parser
            const formatInstructions = this.parser.getFormatInstructions();

            // Create the final prompt
            const finalPrompt = await promptTemplate.format({
                format_instructions: formatInstructions
            });

            // Check if this is an image file and create proper multimodal message
            let messages;
            
            if (fileContent.startsWith('[IMAGE_BASE64:')) {
                // Extract the base64 data from the content
                const base64Match = fileContent.match(/\[IMAGE_BASE64:(.+)\]/);
                if (base64Match) {
                    const base64Data = base64Match[1];
                    
                    // Create multimodal message for images using proper LangChain HumanMessage format
                    messages = [
                        new HumanMessage({
                            content: [
                                {
                                    type: 'text',
                                    text: finalPrompt
                                },
                                {
                                    type: 'image_url',
                                    image_url: {
                                        url: base64Data
                                    }
                                }
                            ]
                        })
                    ];
                    
                    console.log(`🖼️ Created multimodal message for image: ${fileName}`);
                } else {
                    // Fallback to text-only if base64 extraction fails
                    messages = [new HumanMessage(finalPrompt)];
                    console.log(`⚠️ Failed to extract base64, using text-only message for: ${fileName}`);
                }
            } else if (fileContent.startsWith('[PDF_BASE64:') || fileContent.startsWith('[OFFICE_DOC_BASE64:') || fileContent.startsWith('[FILE_BASE64:')) {
                // For other base64 files, use text-only for now (can be enhanced later)
                messages = [new HumanMessage(finalPrompt)];
                console.log(`📄 Using text-only message for base64 file: ${fileName}`);
            } else {
                // For text files, use standard text message
                messages = [new HumanMessage(finalPrompt)];
                console.log(`📝 Using text-only message for text file: ${fileName}`);
            }

            // Call the actual LLM for real processing
            const response = await this.llm.call(messages);
            const extractedData = await this.parser.parse(response.content);

            return extractedData;

        } catch (error) {
            console.error('LangChain extraction error:', error);
            throw new Error(`Failed to extract data with LangChain: ${error.message}`);
        }
    }

    /**
     * Get processing status for a session
     * @param {string} sessionId - Session identifier
     * @returns {Object} Processing status
     */
    async getProcessingStatus(sessionId) {
        try {
            const structuredDir = path.join(__dirname, '../assets', sessionId, 'structured');
            const summaryFile = path.join(structuredDir, `session_summary_${sessionId}.json`);

            try {
                const summaryData = await fs.readFile(summaryFile, 'utf-8');
                return JSON.parse(summaryData);
            } catch (error) {
                return {
                    sessionId: sessionId,
                    status: 'processing',
                    lastUpdated: new Date().toISOString(),
                    note: 'Summary file not found - processing may still be in progress'
                };
            }
        } catch (error) {
            throw new Error(`Failed to get processing status: ${error.message}`);
        }
    }
}

module.exports = LangChainService;