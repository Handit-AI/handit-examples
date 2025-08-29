const { ChatOpenAI } = require('langchain/chat_models/openai');
const { PromptTemplate } = require('langchain/prompts');
const { HumanMessage } = require('langchain/schema');
const fs = require('fs').promises;
const path = require('path');

//Handit.ai
const { trackNode } = require('@handit.ai/node');

class ExtractionService {
    constructor(executionId) {
        // Store the execution ID for Handit.ai tracking
        this.executionId = executionId;
        
        // VLLM-compatible configuration for gpt-5-mini-2025-08-07
        this.llm = new ChatOpenAI({
            openAIApiKey: process.env.OPENAI_API_KEY,
            modelName: process.env.OPENAI_MODEL || 'gpt-5-mini-2025-08-07',
            maxCompletionTokens: 4000,  // VLLM-compatible parameter
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
            console.log(`🚀 Starting LangChain processing for session: ${sessionId}`);
            console.log(`📁 Total files to process: ${files.length}`);
            console.log(`📋 Files:`, files.map(f => f.originalName));

            // Process all files in parallel for better performance
            console.log(`⚡ Starting parallel processing of ${files.length} files...`);
            const processingPromises = files.map(file =>
                this.processSingleFile(file, sessionId)
            );

            const processingResults = await Promise.all(processingPromises);
            console.log(`✅ Parallel processing completed for session: ${sessionId}`);
            console.log(`📊 Processing results:`, processingResults.map(r => ({
                file: r.file,
                success: r.success,
                hasData: !!r.extractedData,
                error: r.error || null
            })));

            // Save structured data to JSON files
            console.log(`💾 Starting to save structured data for session: ${sessionId}`);
            await this.saveStructuredData(sessionId, processingResults);
            console.log(`✅ Structured data saved successfully for session: ${sessionId}`);

            const finalResult = {
                sessionId: sessionId,
                totalFiles: files.length,
                processedFiles: processingResults.length,
                results: processingResults,
                processingCompletedAt: new Date().toISOString(),
                structuredDataPath: `assets/${sessionId}/structured/`
            };

            console.log(`🎉 LangChain processing completed successfully for session: ${sessionId}`);
            console.log(`📊 Final result:`, finalResult);

            return finalResult;

        } catch (error) {
            console.error('❌ LangChain processing error:', error);
            console.error('❌ Error stack:', error.stack);
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
            console.log(`🔄 Processing file: ${file.originalName}`);
            console.log(`📁 File path: ${file.path}`);
            console.log(`📏 File size: ${file.size} bytes`);
            console.log(`🔤 MIME type: ${file.mimetype}`);

            // Read actual file content
            console.log(`📖 Reading file content for: ${file.originalName}`);
            const fileContent = await this.readFileContent(file.path, file.mimetype);
            console.log(`📄 File content type: ${typeof fileContent}`);
            console.log(`📏 File content length: ${fileContent.length} characters`);

            // Process with LangChain using real file content
            console.log(`🤖 Starting LangChain extraction for: ${file.originalName}`);
            const extractedData = await this.extractDataWithLangChain(fileContent, file.originalName, file.path);
            console.log(`✅ LangChain extraction completed for: ${file.originalName}`);
            console.log(`📊 Extracted data type: ${typeof extractedData}`);
            console.log(`📊 Extracted data keys:`, extractedData ? Object.keys(extractedData) : 'NULL');

            const result = {
                file: file.originalName,
                success: true,
                extractedData: extractedData,
                processingTime: new Date().toISOString(),
                filePath: file.path,
                fileSize: file.size,
                mimeType: file.mimetype
            };

            console.log(`✅ Successfully processed file: ${file.originalName}`);
            return result;

        } catch (error) {
            console.error(`❌ Error processing file ${file.originalName}:`, error);
            console.error(`❌ Error stack:`, error.stack);

            const errorResult = {
                file: file.originalName,
                success: false,
                error: error.message,
                processingTime: new Date().toISOString(),
                filePath: file.path,
                fileSize: file.size,
                mimeType: file.mimetype
            };

            console.log(`⚠️ Returning error result for: ${file.originalName}`);
            return errorResult;
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
            console.log(`💾 Starting to save structured data for ${processingResults.length} files...`);

            for (const result of processingResults) {
                console.log(`📁 Processing result for file: ${result.file}`);
                console.log(`✅ Success status: ${result.success}`);
                console.log(`📊 Has extractedData: ${!!result.extractedData}`);

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

                    console.log(`💾 Saving JSON data for ${result.file} to: ${jsonFilePath}`);
                    console.log(`📊 JSON data structure:`, Object.keys(jsonData));
                    console.log(`📊 Extracted data structure:`, Object.keys(result.extractedData));

                    await fs.writeFile(jsonFilePath, JSON.stringify(jsonData, null, 2), 'utf-8');
                    console.log(`✅ Successfully saved structured data for ${result.file} to ${jsonFilePath}`);
                } else {
                    console.log(`⚠️ Skipping file ${result.file} - success: ${result.success}, has data: ${!!result.extractedData}`);
                    if (result.error) {
                        console.log(`❌ Error details: ${result.error}`);
                    }
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
- Process base64 files directly - don't just report that you can't access them
- ALWAYS return valid JSON format with proper structure`;

            // User prompt that encourages field discovery
            const userPrompt = `Please analyze the following document and extract ALL data you can find:

**Document Name**: ${fileName}
**File Path**: ${filePath}

**Document Content**:
${fileContent}

Please extract information in a structured JSON format. You are NOT limited to predefined fields. Discover and create fields based on what you find in the document.

**CRITICAL FORMAT REQUIREMENTS**:
- Return ONLY valid JSON format
- For tables and line items, use proper JSON arrays with objects
- Each field should have its own confidence level (0-1)
- Make the JSON structure clean and readable

**Required Fields** (these should always be present):
- documentType: What type of document is this?
- headerCurrency: Analyze the document and determine the header currency as an ISO 4217 code (e.g., USD, EUR, COP)
- invoiceDate: The date when the invoice was issued, in this format: DD-MM-YYYY

**Standard Fields** (extract if present with individual confidence):
- vendor, customer, invoiceNumber, totalAmount, etc.
- Each field should be an object with "value", "confidence", and "reason" properties
- lineItems should be an array of objects with reason for each item

**Custom Fields** (create these based on what you discover):
- Any additional fields, tables, or structured data you find
- Document-specific information that doesn't fit standard categories
- Special fields, codes, references, or metadata
- Each with individual confidence levels and reason for extraction

**Guidelines**:
1. Be extremely thorough - extract every piece of information
2. Create custom fields for unique document features
3. Focus on tables, line items, and structured layouts
4. Don't limit yourself to predefined fields
5. Adapt to the specific document type and format
6. ALWAYS return valid, well-structured JSON
7. Use proper arrays for tables and line items
8. Include confidence for each field individually
9. Provide a short reason for each field explaining how/where it was extracted

Provide your analysis with maximum detail and flexibility in clean, readable JSON format.

**IMPORTANT**: Your response must be valid JSON. Here's the expected structure:

Example structure:
- documentType: object with "value" and "confidence" properties
- vendor: object with "value" and "confidence" properties  
- lineItems: array of objects with description, quantity, rate, amount, and confidence
Each field should follow this pattern:
"fieldName": {{
  "value": "actual value here",
  "confidence": 0.95,
  "reason": "short explanation of why this value was extracted"
}}

Example JSON structure:
{{
  "documentType": {{
    "value": "invoice",
    "confidence": 0.95,
    "reason": "Found 'Invoice' header at top of document"
  }},
  "vendor": {{
    "value": "Company Name",
    "confidence": 0.90,
    "reason": "Company name found in top-left corner with logo"
  }},
  "lineItems": [
    {{
      "description": "Service Description",
      "quantity": "1",
      "rate": "$50.00",
      "amount": "$50.00",
      "confidence": 0.95,
      "reason": "Extracted from itemized table row"
    }}
  ],
}}`;

            // Create the prompt template
            console.log(`🔧 Creating prompt template for: ${fileName}`);
            console.log(`📝 System prompt length: ${systemPrompt.length} characters`);
            console.log(`📝 User prompt length: ${userPrompt.length} characters`);

            let promptTemplate;
            try {
                promptTemplate = PromptTemplate.fromTemplate(`
${systemPrompt}

${userPrompt}
`);
                console.log(`✅ Prompt template created successfully for: ${fileName}`);
            } catch (templateError) {
                console.error(`❌ Failed to create prompt template for ${fileName}:`, templateError);
                console.error(`❌ Template error details:`, templateError.message);
                throw new Error(`Failed to create prompt template: ${templateError.message}`);
            }

            // Create the final prompt
            console.log(`🔧 Formatting final prompt for: ${fileName}`);
            let finalPrompt;
            try {
                finalPrompt = await promptTemplate.format({});
                console.log(`✅ Final prompt formatted successfully for: ${fileName}`);
                console.log(`📏 Final prompt length: ${finalPrompt.length} characters`);
            } catch (formatError) {
                console.error(`❌ Failed to format final prompt for ${fileName}:`, formatError);
                console.error(`❌ Format error details:`, formatError.message);
                throw new Error(`Failed to format final prompt: ${formatError.message}`);
            }

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
            console.log(`🤖 Calling LLM for file: ${fileName}`);
            console.log(`📤 Sending prompt to LLM (first 500 chars):`, finalPrompt.substring(0, 500) + '...');

            const response = await this.llm.call(messages);
            console.log(`📝 LLM response received for: ${fileName}`);
            console.log(`📄 Response content length: ${response.content.length} characters`);
            console.log(`📄 FULL LLM RESPONSE for ${fileName}:`, response.content);

            // Track the LLM call with Handit.ai
            let trackingInput = {
                systemPrompt: systemPrompt,
                userPrompt: userPrompt
            };

            // Add image data if this is an image file
            if (fileContent.startsWith('[IMAGE_BASE64:')) {
                const base64Match = fileContent.match(/\[IMAGE_BASE64:(.+)\]/);
                if (base64Match) {
                    const base64Data = base64Match[1];
                    
                    trackingInput.image = `${base64Data}`;
                }
            }

            await trackNode({
                input: trackingInput,
                output: response.content,
                nodeName: 'extraction_data',
                agentName: 'multi_currency',
                nodeType: 'llm',
                executionId: this.executionId
            });

            // Parse the JSON response from the LLM
            try {
                console.log(`🔍 Attempting to parse LLM response as JSON for: ${fileName}`);
                const extractedData = JSON.parse(response.content);
                console.log(`✅ Successfully parsed JSON for: ${fileName}`);
                console.log(`📊 Extracted data keys:`, Object.keys(extractedData));
                return extractedData;
            } catch (parseError) {
                console.error(`❌ Failed to parse LLM response as JSON for ${fileName}:`, parseError);
                console.log(`📄 Raw LLM response for ${fileName}:`, response.content);

                // Try to extract JSON from the response if it's wrapped in markdown
                const jsonMatch = response.content.match(/```json\s*([\s\S]*?)\s*```/);
                if (jsonMatch) {
                    console.log(`🔍 Found JSON wrapped in markdown for: ${fileName}`);
                    try {
                        const extractedData = JSON.parse(jsonMatch[1]);
                        console.log(`✅ Successfully parsed extracted JSON for: ${fileName}`);
                        return extractedData;
                    } catch (secondParseError) {
                        console.error(`❌ Failed to parse extracted JSON for ${fileName}:`, secondParseError);
                        throw new Error(`LLM response could not be parsed as valid JSON for ${fileName}`);
                    }
                }

                // Try to find any JSON-like content in the response
                const jsonLikeMatch = response.content.match(/\{[\s\S]*\}/);
                if (jsonLikeMatch) {
                    console.log(`🔍 Found JSON-like content for: ${fileName}`);
                    try {
                        const extractedData = JSON.parse(jsonLikeMatch[0]);
                        console.log(`✅ Successfully parsed JSON-like content for: ${fileName}`);
                        return extractedData;
                    } catch (thirdParseError) {
                        console.error(`❌ Failed to parse JSON-like content for ${fileName}:`, thirdParseError);
                    }
                }

                throw new Error(`LLM response could not be parsed as valid JSON for ${fileName}. FULL Response: ${response.content}`);
            }

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

module.exports = ExtractionService;