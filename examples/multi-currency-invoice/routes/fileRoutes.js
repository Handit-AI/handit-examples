const express = require('express');
const router = express.Router();
const FileController = require('../controllers/FileController');
const FileService = require('../services/FileService');

// Initialize file service
const fileService = new FileService();

// Bulk file upload endpoint
router.post('/upload', 
  fileService.createMulterInstance().array('files', 10), // Allow up to 10 files
  FileController.uploadFiles
);

// Get session files endpoint
router.get('/session/:sessionId', FileController.getSessionFiles);

// Get LangChain processing results endpoint
router.get('/langchain/:sessionId', FileController.getLangChainResults);

// Get currency normalization results endpoint
router.get('/normalization/:sessionId', FileController.getCurrencyNormalizationResults);

// Health check for file service
router.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'file-upload-service',
    timestamp: new Date().toISOString(),
    endpoints: {
      upload: 'POST /api/files/upload',
      getSession: 'GET /api/files/session/:sessionId',
      getLangChainResults: 'GET /api/files/langchain/:sessionId',
      getNormalizationResults: 'GET /api/files/normalization/:sessionId'
    }
  });
});

module.exports = router;
