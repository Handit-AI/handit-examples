const express = require('express');
const router = express.Router();
const HealthController = require('../controllers/HealthController');

// Health check endpoint
router.get('/', HealthController.getHealth);

// Detailed health check
router.get('/detailed', HealthController.getDetailedHealth);

// Health check with custom parameters
router.get('/check', HealthController.checkHealth);

module.exports = router;
