// Import FileService and move files to session directory
const FileService = require('../services/FileService');
const LangChainService = require('../services/LangChainService');

class FileController {
  /**
   * Handle bulk file upload
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async uploadFiles(req, res) {
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
      
      const movedFiles = await fileService.moveFilesToSession(req.files, sessionId);

      // Process files with LangChain for data extraction
      const langChainService = new LangChainService();
      const extractionResults = await langChainService.processFilesWithLangChain(movedFiles, sessionId);

      res.status(200).json({
        success: true,
        message: 'Files uploaded and processed successfully',
        sessionId: sessionId,
        totalFiles: movedFiles.length,
        files: movedFiles,
        storagePath: `assets/${sessionId}/files/`,
        langChainProcessing: {
          status: 'completed',
          extractedData: extractionResults,
          processingCompletedAt: extractionResults.processingCompletedAt
        }
      });

    } catch (error) {
      console.error('File upload error:', error);
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
      const langChainService = new LangChainService();
      
      const processingStatus = await langChainService.getProcessingStatus(sessionId);
      
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
}

module.exports = FileController;
