const fs = require('fs').promises;
const path = require('path');
const { ChatOpenAI } = require('@langchain/openai');
const { tool } = require('@langchain/core/tools');
const { z } = require('zod');
const CurrencyConverterService = require('./CurrencyConverterService');

//Handit.ai
const { trackNode } = require('@handit.ai/node');

/**
 * Currency Normalization Service using LangChain with Tools
 * 
 * This service uses an LLM with currency conversion tools to intelligently
 * normalize monetary values in extracted JSON data.
 */
class CurrencyNormalizationService {
    constructor(executionId) {
        // Store the execution ID for Handit.ai tracking
        this.executionId = executionId;
        // Initialize the LLM
        this.llm = new ChatOpenAI({
            model: "gpt-4o-mini",
            temperature: 0,
            openAIApiKey: process.env.OPENAI_API_KEY
        });

        // Initialize the real currency converter service
        this.currencyConverter = new CurrencyConverterService();

        // Create the currency conversion tool
        this.currencyTool = this.createCurrencyTool();
        
        // Bind the tool to the LLM
        this.llmWithTools = this.llm.bindTools([this.currencyTool]);
    }

    /**
     * Create the currency conversion tool
     * @returns {Object} LangChain tool object
     */
    createCurrencyTool() {
        return tool(
            async ({ amount, fromCurrency, toCurrency, date }) => {
                try {
                    console.log(`🔄 Tool called: Converting ${amount} ${fromCurrency} to ${toCurrency}${date ? ` for date ${date}` : ''}`);
                    
                    const conversionResult = await this.performCurrencyConversion(amount, fromCurrency, toCurrency, date);
                    
                    return JSON.stringify(conversionResult);
                } catch (error) {
                    console.error(`❌ Tool error: ${error.message}`);
                    return JSON.stringify({
                        error: error.message,
                        amount: amount,
                        fromCurrency: fromCurrency,
                        toCurrency: toCurrency
                    });
                }
            },
            {
                name: "convert_currency",
                description: "Convert an amount from one currency to another. Use this tool whenever you need to convert monetary values to the target currency.",
                schema: z.object({
                    amount: z.number().describe("The amount to convert"),
                    fromCurrency: z.string().describe("The source currency code (e.g., USD, EUR, GBP)"),
                    toCurrency: z.string().describe("The target currency code to convert to"),
                    date: z.string().optional().describe("Optional date for historical conversion (YYYY-MM-DD format)")
                })
            }
        );
    }

    /**
     * Perform actual currency conversion using the real CurrencyConverterService
     * @param {number} amount - Amount to convert
     * @param {string} fromCurrency - Source currency
     * @param {string} toCurrency - Target currency
     * @param {string} date - Optional date
     * @returns {Promise<Object>} Conversion result
     */
    async performCurrencyConversion(amount, fromCurrency, toCurrency, date) {
        try {
            console.log(`💱 Converting ${amount} ${fromCurrency} to ${toCurrency}${date ? ` for date ${date}` : ''}`);
            
            if (fromCurrency.toUpperCase() === toCurrency.toUpperCase()) {
                return {
                    convertedAmount: amount,
                    originalAmount: amount,
                    fromCurrency: fromCurrency,
                    toCurrency: toCurrency,
                    exchangeRate: 1.0,
                    conversionDate: date || new Date().toISOString().split('T')[0],
                    method: "same_currency"
                };
            }

            // Use the real currency converter service
            const conversionResult = await this.currencyConverter.convertCurrency(amount, fromCurrency, toCurrency, date);
            
            // Format the result to match our expected structure
            return {
                convertedAmount: conversionResult.convertedAmount || conversionResult.amount,
                originalAmount: amount,
                fromCurrency: fromCurrency,
                toCurrency: toCurrency,
                exchangeRate: conversionResult.exchangeRate || conversionResult.rate,
                conversionDate: date || new Date().toISOString().split('T')[0],
                method: "api_conversion",
                apiResponse: conversionResult
            };
            
        } catch (error) {
            console.error(`❌ Currency conversion failed: ${error.message}`);
            throw new Error(`Failed to convert ${amount} ${fromCurrency} to ${toCurrency}: ${error.message}`);
        }
    }

    /**
     * Process all JSON files in a session using LLM with tools
     * @param {string} sessionId - Session ID to process
     * @returns {Promise<Object>} Processing results
     */
    async normalizeSessionCurrencies(sessionId) {
        try {
            console.log(`🔄 Starting LLM-based currency normalization for session: ${sessionId}`);
            
            const structuredDir = path.join('assets', sessionId, 'structured');
            const outputDir = path.join('assets', sessionId, 'output');
            
            // Ensure output directory exists
            await this.ensureDirectoryExists(outputDir);
            
            // Get all JSON files in structured directory (excluding session_summary)
            const jsonFiles = await this.getJsonFiles(structuredDir);
            
            console.log(`📁 Found ${jsonFiles.length} JSON files to process with LLM`);
            
            const results = [];
            let filesProcessed = 0;
            let filesSkipped = 0;
            let filesNormalized = 0;
            
            for (const filePath of jsonFiles) {
                try {
                    console.log(`📄 Processing with LLM: ${path.basename(filePath)}`);
                    
                    const normalizedData = await this.normalizeFileWithLLM(filePath);
                    
                    // Save normalized data to output directory
                    const outputPath = path.join(outputDir, path.basename(filePath));
                    await fs.writeFile(outputPath, JSON.stringify(normalizedData, null, 2));
                    
                    // Check if the data was actually normalized or just copied
                    const wasNormalized = this.wasDataNormalized(normalizedData);
                    
                    if (wasNormalized) {
                        filesNormalized++;
                        console.log(`✅ Normalized: ${path.basename(filePath)}`);
                    } else {
                        filesSkipped++;
                        console.log(`⏭️ Skipped (no changes needed): ${path.basename(filePath)}`);
                    }
                    
                    results.push({
                        file: path.basename(filePath),
                        status: 'success',
                        outputPath: outputPath,
                        originalPath: filePath,
                        wasNormalized: wasNormalized,
                        reason: wasNormalized ? 'Currency values converted' : 'No conversion needed'
                    });
                    
                    filesProcessed++;
                    
                } catch (error) {
                    console.error(`❌ Error processing ${path.basename(filePath)}:`, error.message);
                    results.push({
                        file: path.basename(filePath),
                        status: 'error',
                        error: error.message,
                        originalPath: filePath,
                        wasNormalized: false,
                        reason: 'Processing failed'
                    });
                }
            }
            
            console.log(`🎉 LLM-based currency normalization completed for session: ${sessionId}`);
            console.log(`📊 Summary: ${filesProcessed} processed, ${filesNormalized} normalized, ${filesSkipped} skipped`);
            
            return {
                sessionId,
                status: 'completed',
                totalFiles: jsonFiles.length,
                processedFiles: filesProcessed,
                normalizedFiles: filesNormalized,
                skippedFiles: filesSkipped,
                results: results,
                outputDirectory: outputDir,
                completedAt: new Date().toISOString(),
                method: 'llm_with_tools',
                summary: {
                    totalFiles: jsonFiles.length,
                    processedFiles: filesProcessed,
                    normalizedFiles: filesNormalized,
                    skippedFiles: filesSkipped,
                    efficiency: filesSkipped > 0 ? `${Math.round((filesSkipped / jsonFiles.length) * 100)}% of files didn't need normalization` : 'All files required normalization'
                }
            };
            
        } catch (error) {
            console.error(`❌ LLM-based currency normalization failed for session ${sessionId}:`, error);
            throw new Error(`Failed to normalize currencies with LLM for session ${sessionId}: ${error.message}`);
        }
    }

    /**
     * Normalize a single JSON file using LLM with tools
     * @param {string} filePath - Path to the JSON file
     * @returns {Promise<Object>} Normalized data
     */
    async normalizeFileWithLLM(filePath) {
        try {
            // Read the JSON file
            const fileContent = await fs.readFile(filePath, 'utf8');
            const data = JSON.parse(fileContent);
            
            // Extract header currency
            const headerCurrency = this.extractHeaderCurrency(data);
            
            if (!headerCurrency) {
                console.log(`⚠️ No header currency found in ${path.basename(filePath)}, skipping normalization`);
                return data;
            }
            
            console.log(`💰 Header currency: ${headerCurrency}`);
            
            // Check if normalization is needed BEFORE calling the LLM
            const needsNormalization = this.checkIfNormalizationNeeded(data, headerCurrency);
            
            if (!needsNormalization) {
                console.log(`✅ No normalization needed - all values already in ${headerCurrency}, returning original data`);
                return data;
            }
            
            // Create the prompt for the LLM
            const prompt = this.createNormalizationPrompt(data, headerCurrency);
            
            console.log(`🤖 Sending to LLM for intelligent normalization...`);
            
            // Get LLM response with tool calls
            const llmResponse = await this.llmWithTools.invoke(prompt);
            
            console.log(`📝 LLM Response:`, llmResponse);
            
            // Process tool calls if any
            if (llmResponse.tool_calls && llmResponse.tool_calls.length > 0) {
                console.log(`🔧 Processing ${llmResponse.tool_calls.length} tool calls...`);
                
                for (const toolCall of llmResponse.tool_calls) {
                    if (toolCall.name === 'convert_currency') {
                        console.log(`💱 Tool call args:`, toolCall.args);
                        
                        // Execute the tool
                        const toolResult = await this.currencyTool.func(toolCall.args);
                        console.log(`✅ Tool result:`, toolResult);
                        
                        // Parse the result and apply to the data
                        try {
                            const conversionResult = JSON.parse(toolResult);
                            if (!conversionResult.error) {
                                // Find and update the corresponding field in the data
                                await this.applyConversionToData(data, toolCall.args, conversionResult);
                            }
                        } catch (parseError) {
                            console.error(`❌ Failed to parse tool result:`, parseError);
                        }
                    }
                }
            } else {
                console.log(`ℹ️ No tool calls made by LLM`);
            }

            // Track the LLM call with Handit.ai
            let trackingInput = {
                systemPrompt: prompt,
                userPrompt: "Convert all monetary values to " + headerCurrency,
                jsonData: JSON.stringify(data, null, 2)  // Send the JSON data
            };

            await trackNode({
                input: trackingInput,
                output: JSON.stringify(data, null, 2),
                nodeName: 'currency_normalization',
                agentName: 'multi_currency_test',
                nodeType: 'llm',
                executionId: this.executionId
            });

            console.log(`📊 Handit.ai tracking completed for currency normalization`);
            
            return data;
            
        } catch (error) {
            throw new Error(`Failed to normalize file with LLM ${filePath}: ${error.message}`);
        }
    }

    /**
     * Create prompt for the LLM to normalize currencies
     * @param {Object} data - Data to normalize
     * @param {string} targetCurrency - Target currency
     * @returns {string} Prompt for the LLM
     */
    createNormalizationPrompt(data, targetCurrency) {
        return `You are a financial data processor. Your task is to normalize all monetary values in the following JSON data to ${targetCurrency}.

IMPORTANT: Use the convert_currency tool whenever you encounter a monetary value that needs to be converted to ${targetCurrency}.

The data structure follows this pattern:
- Each field has a "value" property containing the actual data
- Monetary values may be in various currencies (USD, EUR, GBP, etc.)
- You need to identify monetary values and convert them to ${targetCurrency}
- Use the convert_currency tool for each conversion needed

JSON Data to process:
${JSON.stringify(data, null, 2)}

Instructions:
1. Analyze the JSON data to identify all monetary values
2. For each monetary value that is NOT in ${targetCurrency}, use the convert_currency tool
3. The tool will return conversion results that you should use to add a "normalizedValue" field
4. Preserve the original structure completely - only add the normalizedValue field
5. If a value is already in ${targetCurrency}, you can skip conversion but still add a normalizedValue field with the same values

Remember: Always use the convert_currency tool for conversions. Do not attempt to convert currencies manually.`;
    }

    /**
     * Apply conversion result to the data structure
     * @param {Object} data - Data to update
     * @param {Object} toolArgs - Tool arguments used
     * @param {Object} conversionResult - Result from the tool
     */
    async applyConversionToData(data, toolArgs, conversionResult) {
        console.log(`🔄 Applying conversion result to data structure...`);
        console.log(`📊 Tool args:`, toolArgs);
        console.log(`📊 Conversion result:`, conversionResult);
        
        try {
            // Parse the conversion result if it's a string
            let result;
            if (typeof conversionResult === 'string') {
                result = JSON.parse(conversionResult);
            } else {
                result = conversionResult;
            }
            
            if (result.error) {
                console.error(`❌ Conversion failed: ${result.error}`);
                return;
            }
            
            // Find the monetary field that corresponds to this conversion
            // We need to identify which field in the data this conversion belongs to
            const monetaryFields = this.findMonetaryFields(data);
            console.log(`🔍 Found ${monetaryFields.length} monetary fields to check`);
            
            // Try to match the conversion with a field based on the tool arguments
            let conversionApplied = false;
            
            for (const field of monetaryFields) {
                const fieldValue = this.getFieldValue(data, field.path);
                if (fieldValue && fieldValue.value) {
                    const extractedAmount = this.extractAmountFromValue(fieldValue.value);
                    const extractedCurrency = this.extractCurrencyFromValue(fieldValue.value);
                    
                    console.log(`🔍 Checking field ${field.path}: amount=${extractedAmount}, currency=${extractedCurrency}`);
                    
                    // Check if this field matches the conversion
                    if (extractedAmount === toolArgs.amount && 
                        extractedCurrency === toolArgs.fromCurrency) {
                        
                        // Apply the normalizedValue to this field
                        fieldValue.normalizedValue = {
                            amount: result.convertedAmount,
                            currency: result.toCurrency,
                            originalAmount: result.originalAmount,
                            originalCurrency: result.fromCurrency,
                            exchangeRate: result.exchangeRate,
                            conversionDate: result.conversionDate,
                            method: result.method
                        };
                        
                        console.log(`✅ Applied conversion to field: ${field.path}`);
                        conversionApplied = true;
                        break;
                    }
                }
            }
            
            // If we can't find a direct match, try to find by amount only
            if (!conversionApplied) {
                console.log(`⚠️ No exact match found, trying to find by amount only...`);
                
                for (const field of monetaryFields) {
                    const fieldValue = this.getFieldValue(data, field.path);
                    if (fieldValue && fieldValue.value) {
                        const extractedAmount = this.extractAmountFromValue(fieldValue.value);
                        
                        if (extractedAmount === toolArgs.amount) {
                            console.log(`🎯 Found field by amount: ${field.path}`);
                            
                            // Apply the normalizedValue to this field
                            fieldValue.normalizedValue = {
                                amount: result.convertedAmount,
                                currency: result.toCurrency,
                                originalAmount: result.originalAmount,
                                originalCurrency: result.fromCurrency,
                                exchangeRate: result.exchangeRate,
                                conversionDate: result.conversionDate,
                                method: result.method
                            };
                            
                            console.log(`✅ Applied conversion to field: ${field.path}`);
                            conversionApplied = true;
                            break;
                        }
                    }
                }
            }
            
            // If still no match, add to conversions metadata
            if (!conversionApplied) {
                console.log(`⚠️ Could not find field match, adding to conversions metadata`);
                if (!data._conversions) {
                    data._conversions = [];
                }
                
                data._conversions.push({
                    originalArgs: toolArgs,
                    result: result,
                    timestamp: new Date().toISOString(),
                    status: 'unmatched'
                });
            }
            
        } catch (error) {
            console.error(`❌ Error applying conversion:`, error.message);
        }
    }

    /**
     * Find all monetary fields in the data structure
     * @param {Object} data - Data to search
     * @returns {Array} Array of field objects with path and value
     */
    findMonetaryFields(data) {
        const fields = [];
        
        const findFields = (obj, path = '') => {
            if (Array.isArray(obj)) {
                obj.forEach((item, index) => findFields(item, `${path}[${index}]`));
            } else if (obj && typeof obj === 'object') {
                for (const [key, value] of Object.entries(obj)) {
                    const currentPath = path ? `${path}.${key}` : key;
                    
                    if (this.isMonetaryValue(value)) {
                        fields.push({
                            path: currentPath,
                            value: value.value,
                            currency: this.extractCurrencyFromValue(value.value),
                            amount: this.extractAmountFromValue(value.value)
                        });
                    } else if (typeof value === 'object' && value !== null) {
                        findFields(value, currentPath);
                    }
                }
            }
        };
        
        findFields(data);
        return fields;
    }

    /**
     * Get field value from data using path
     * @param {Object} data - Data object
     * @param {string} path - Field path (e.g., "totalAmount" or "lineItems[0].amount")
     * @returns {any} Field value or null if not found
     */
    getFieldValue(data, path) {
        try {
            const pathParts = path.split('.');
            let current = data;
            
            for (const part of pathParts) {
                if (part.includes('[')) {
                    // Handle array indices
                    const match = part.match(/(\w+)\[(\d+)\]/);
                    if (match) {
                        const [, arrayName, index] = match;
                        current = current[arrayName][parseInt(index)];
                    }
                } else {
                    current = current[part];
                }
                
                if (current === undefined || current === null) {
                    return null;
                }
            }
            
            return current;
        } catch (error) {
            console.error(`❌ Error getting field value for path ${path}:`, error.message);
            return null;
        }
    }

    /**
     * Check if normalization is needed for a given data and target currency
     * @param {Object} data - The JSON data to check
     * @param {string} targetCurrency - The target currency to normalize to
     * @returns {boolean} True if normalization is needed, false otherwise
     */
    checkIfNormalizationNeeded(data, targetCurrency) {
        const analysis = this.analyzeJsonStructure(data, targetCurrency);
        return analysis.needsConversion;
    }

    /**
     * Analyze JSON structure to identify monetary values
     * @param {Object} data - JSON data object
     * @param {string} targetCurrency - Target currency
     * @returns {Object} Analysis result
     */
    analyzeJsonStructure(data, targetCurrency) {
        const analysis = {
            targetCurrency: targetCurrency,
            monetaryFields: [],
            totalFields: 0,
            needsConversion: false
        };

        const analyzeObject = (obj, path = '') => {
            if (Array.isArray(obj)) {
                obj.forEach((item, index) => analyzeObject(item, `${path}[${index}]`));
            } else if (obj && typeof obj === 'object') {
                for (const [key, value] of Object.entries(obj)) {
                    const currentPath = path ? `${path}.${key}` : key;
                    analysis.totalFields++;
                    
                    if (this.isMonetaryValue(value)) {
                        const originalCurrency = this.extractCurrencyFromValue(value.value);
                        const needsConversion = originalCurrency && originalCurrency.toUpperCase() !== targetCurrency.toUpperCase();
                        
                        analysis.monetaryFields.push({
                            path: currentPath,
                            value: value.value,
                            currency: originalCurrency,
                            needsConversion: needsConversion,
                            targetCurrency: targetCurrency
                        });
                        
                        if (needsConversion) {
                            analysis.needsConversion = true;
                        }
                    } else if (typeof value === 'object' && value !== null) {
                        analyzeObject(value, currentPath);
                    }
                }
            }
        };

        // Start analysis from extractedData if it exists, otherwise from root
        if (data.extractedData) {
            console.log(`🔍 Analyzing extractedData structure...`);
            analyzeObject(data.extractedData, 'extractedData');
        } else {
            console.log(`🔍 Analyzing root structure...`);
            analyzeObject(data);
        }
        
        console.log(`🔍 Analysis: Found ${analysis.monetaryFields.length} monetary fields, ${analysis.needsConversion ? 'conversion needed' : 'no conversion needed'}`);
        
        return analysis;
    }

    /**
     * Extract header currency from the data
     * @param {Object} data - Data object
     * @returns {string|null} Currency code or null if not found
     */
    extractHeaderCurrency(data) {
        console.log(`🔍 Extracting header currency from data structure...`);
        
        // First, check if we have extractedData structure
        if (data.extractedData) {
            console.log(`📁 Found extractedData structure, searching there...`);
            
            // Look for common currency fields in extractedData
            const currencyFields = ['currency', 'headerCurrency', 'baseCurrency', 'documentCurrency'];
            
            for (const field of currencyFields) {
                if (data.extractedData[field] && data.extractedData[field].value) {
                    const currency = data.extractedData[field].value.toUpperCase();
                    console.log(`✅ Found header currency: ${currency} in field: ${field}`);
                    return currency;
                }
            }
            
            // Look for currency in nested structures within extractedData
            if (data.extractedData.header && data.extractedData.header.currency && data.extractedData.header.currency.value) {
                const currency = data.extractedData.header.currency.value.toUpperCase();
                console.log(`✅ Found header currency: ${currency} in extractedData.header.currency`);
                return currency;
            }
            
            // Look for currency in document metadata within extractedData
            if (data.extractedData.documentMetadata && data.extractedData.documentMetadata.currency && data.extractedData.documentMetadata.currency.value) {
                const currency = data.extractedData.documentMetadata.currency.value.toUpperCase();
                console.log(`✅ Found header currency: ${currency} in extractedData.documentMetadata.currency`);
                return currency;
            }
        }
        
        // Fallback: look in the root level (for backward compatibility)
        console.log(`🔍 Checking root level for currency fields...`);
        const currencyFields = ['currency', 'headerCurrency', 'baseCurrency', 'documentCurrency'];
        
        for (const field of currencyFields) {
            if (data[field] && data[field].value) {
                const currency = data[field].value.toUpperCase();
                console.log(`✅ Found header currency: ${currency} in root field: ${field}`);
                return currency;
            }
        }
        
        // Look for currency in nested structures at root level
        if (data.header && data.header.currency && data.header.currency.value) {
            const currency = data.header.currency.value.toUpperCase();
            console.log(`✅ Found header currency: ${currency} in root header.currency`);
            return currency;
        }
        
        // Look for currency in document metadata at root level
        if (data.documentMetadata && data.documentMetadata.currency && data.documentMetadata.currency.value) {
            const currency = data.documentMetadata.currency.value.toUpperCase();
            console.log(`✅ Found header currency: ${currency} in root documentMetadata.currency`);
            return currency;
        }
        
        console.log(`❌ No header currency found in any location`);
        return null;
    }

    /**
     * Check if a value represents a monetary amount
     * @param {any} value - Value to check
     * @returns {boolean} True if it's a monetary value
     */
    isMonetaryValue(value) {
        if (!value || typeof value !== 'object') return false;
        
        // Check if it has a value field that looks like money
        if (value.value !== undefined) {
            const strValue = String(value.value);
            
            // Look for currency symbols or patterns
            const moneyPatterns = [
                /\$[\d,]+\.?\d*/,           // $123.45, $1,234
                /[\d,]+\.?\d*\s*[A-Z]{3}/, // 123.45 USD, 1,234 EUR
                /[A-Z]{3}\s*[\d,]+\.?\d*/, // USD 123.45, EUR 1,234
                /[\d,]+\.?\d*/,             // 123.45, 1,234 (if context suggests money)
            ];
            
            return moneyPatterns.some(pattern => pattern.test(strValue));
        }
        
        return false;
    }

    /**
     * Extract currency code from a monetary value string
     * @param {string} value - Monetary value string
     * @returns {string|null} Currency code or null if not found
     */
    extractCurrencyFromValue(value) {
        if (typeof value !== 'string') return null;
        
        // Look for 3-letter currency codes
        const currencyMatch = value.match(/\b([A-Z]{3})\b/);
        if (currencyMatch) {
            return currencyMatch[1];
        }
        
        // Look for currency symbols and map them
        const symbolMap = {
            '$': 'USD',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'JPY',
            '₹': 'INR',
            '₽': 'RUB',
            '₩': 'KRW',
            '₺': 'TRY',
            '₪': 'ILS',
            '₦': 'NGN',
            '₨': 'PKR',
            '₫': 'VND',
            '₱': 'PHP',
            '₴': 'UAH',
            '₸': 'KZT',
            '₼': 'AZN',
            '₾': 'GEL',
            '₿': 'BTC'
        };
        
        for (const [symbol, currency] of Object.entries(symbolMap)) {
            if (value.includes(symbol)) {
                return currency;
            }
        }
        
        return null;
    }

    /**
     * Extract numeric amount from a monetary value string
     * @param {string} value - Monetary value string
     * @returns {number|null} Numeric amount or null if not found
     */
    extractAmountFromValue(value) {
        if (typeof value !== 'string') return null;
        
        // Remove currency symbols and codes, keep only numbers, commas, and dots
        const cleanValue = value
            .replace(/[A-Z]{3}/g, '')  // Remove currency codes
            .replace(/[^\d,.-]/g, '')  // Keep only numbers, commas, dots, and minus
            .replace(/,/g, '')         // Remove commas
            .trim();
        
        const amount = parseFloat(cleanValue);
        return isNaN(amount) ? null : amount;
    }

    /**
     * Check if the data was actually normalized (has normalizedValue fields)
     * @param {Object} data - Data to check
     * @returns {boolean} True if data contains normalizedValue fields
     */
    wasDataNormalized(data) {
        let hasNormalizedValues = false;
        
        const checkForNormalizedValues = (obj) => {
            if (Array.isArray(obj)) {
                obj.forEach(checkForNormalizedValues);
            } else if (obj && typeof obj === 'object') {
                for (const [key, value] of Object.entries(obj)) {
                    if (key === 'normalizedValue' && value && typeof value === 'object') {
                        hasNormalizedValues = true;
                        return; // Early exit if we find any normalizedValue
                    } else if (typeof value === 'object' && value !== null) {
                        checkForNormalizedValues(value);
                    }
                }
            }
        };
        
        checkForNormalizedValues(data);
        return hasNormalizedValues;
    }

    /**
     * Get all JSON files in a directory (excluding session_summary)
     * @param {string} directory - Directory to scan
     * @returns {Promise<string[]>} Array of file paths
     */
    async getJsonFiles(directory) {
        try {
            const files = await fs.readdir(directory);
            const jsonFiles = files
                .filter(file => file.endsWith('.json') && !file.includes('session_summary'))
                .map(file => path.join(directory, file));
            
            return jsonFiles;
        } catch (error) {
            throw new Error(`Failed to read directory ${directory}: ${error.message}`);
        }
    }

    /**
     * Ensure a directory exists, create if it doesn't
     * @param {string} directory - Directory path
     */
    async ensureDirectoryExists(directory) {
        try {
            await fs.access(directory);
        } catch {
            await fs.mkdir(directory, { recursive: true });
            console.log(`📁 Created directory: ${directory}`);
        }
    }
}

module.exports = CurrencyNormalizationService;
