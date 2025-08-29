// Import FileService and move files to session directory
const FileService = require('../services/FileService');
const ExtractionService = require('../services/ExtractionService');
const CurrencyNormalizationService = require('../services/CurrencyNormalizationService');
const { config, startTracing, endTracing } = require('@handit.ai/node');

// Configure Handit.ai API KEY
config({ apiKey: process.env.HANDIT_API_KEY });

class FileController {
  /**
   * Handle bulk file upload
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async uploadFiles(req, res) {

    // Start a new trace session
    const tracingResponse = await startTracing({
      agentName: 'multi_currency_test'  // Identifies this agent in the Handit.ai dashboard
    });
    const executionId = tracingResponse.executionId;  // Unique ID for this trace session

    console.log('🔄 Starting trace session with execution_id: ', executionId);

    try {
      if (!req.files || req.files.length === 0) {
        return res.status(400).json({
          success: false,
          error: 'No files provided',
          message: 'Please upload at least one file'
        });
      }

      // Get session_id from request body or generate one
      const sessionId = req.body.session_id || `session_${Date.now()}`;

      // Import FileService and move files to session directory
      const fileService = new FileService();

      const movedFiles = await fileService.moveFilesToSession(req.files, sessionId, executionId);

      // Process files with LangChain for data extraction
      const extractionService = new ExtractionService(executionId);
      const extractionResults = await extractionService.processFilesWithLangChain(movedFiles, sessionId);

      // Normalize currencies in extracted JSONs
      console.log('🔄 Starting currency normalization process...');
      const currencyNormalizationService = new CurrencyNormalizationService(executionId);
      const normalizationResults = await currencyNormalizationService.normalizeSessionCurrencies(sessionId);

      // End the trace session
      await endTracing({
        executionId,                         // The ID of the trace session to end
        agentName: 'multi_currency_test'  // Must match the name used in startTracing
      });

      res.status(200).json({
        success: true,
        message: 'Files uploaded, processed, and currencies normalized successfully',
        sessionId: sessionId,
        totalFiles: movedFiles.length,
        files: movedFiles,
        storagePath: `assets/${sessionId}/files/`,
        langChainProcessing: {
          status: 'completed',
          extractedData: extractionResults,
          processingCompletedAt: extractionResults.processingCompletedAt
        },
        currencyNormalization: {
          status: 'completed',
          results: normalizationResults,
          outputDirectory: normalizationResults.outputDirectory,
          completedAt: normalizationResults.completedAt
        }
      });

    } catch (error) {
      console.error('File upload error:', error);
      // End the trace session
      await endTracing({
        executionId,                         // The ID of the trace session to end
        agentName: 'multi_currency_test'  // Must match the name used in startTracing
      });
      res.status(500).json({
        success: false,
        error: 'Failed to upload files',
        message: error.message
      });
    }
  }

  /**
   * Get session files
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async getSessionFiles(req, res) {
    try {
      const { sessionId } = req.params;
      const FileService = require('../services/FileService');
      const fileService = new FileService();

      const sessionInfo = await fileService.getSessionFiles(sessionId);

      res.status(200).json({
        success: true,
        sessionInfo
      });

    } catch (error) {
      console.error('Get session files error:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get session files',
        message: error.message
      });
    }
  }

  /**
   * Get LangChain processing results for a session
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async getLangChainResults(req, res) {
    try {
      const { sessionId } = req.params;
      const extractionService = new ExtractionService();

      const processingStatus = await extractionService.getProcessingStatus(sessionId);

      res.status(200).json({
        success: true,
        sessionId: sessionId,
        langChainStatus: processingStatus
      });

    } catch (error) {
      console.error('Get LangChain results error:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get LangChain results',
        message: error.message
      });
    }
  }

  /**
   * Get currency normalization results for a session
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async getCurrencyNormalizationResults(req, res) {
    try {
      const { sessionId } = req.params;
      const currencyNormalizationService = new CurrencyNormalizationService();

      // Get the output directory path
      const outputDir = `assets/${sessionId}/output`;

      // Check if output directory exists and get files
      const fs = require('fs').promises;
      const path = require('path');

      try {
        const files = await fs.readdir(outputDir);
        const jsonFiles = files.filter(file => file.endsWith('.json'));

        const results = [];
        for (const file of jsonFiles) {
          const filePath = path.join(outputDir, file);
          const content = await fs.readFile(filePath, 'utf8');
          const data = JSON.parse(content);

          results.push({
            file: file,
            path: filePath,
            data: data
          });
        }

        res.status(200).json({
          success: true,
          sessionId: sessionId,
          outputDirectory: outputDir,
          totalFiles: jsonFiles.length,
          files: results
        });

      } catch (dirError) {
        res.status(404).json({
          success: false,
          error: 'Output directory not found',
          message: 'Currency normalization has not been completed for this session yet'
        });
      }

    } catch (error) {
      console.error('Get currency normalization results error:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get currency normalization results',
        message: error.message
      });
    }
  }
}

module.exports = FileController;
