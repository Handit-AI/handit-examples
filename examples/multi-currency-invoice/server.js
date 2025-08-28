// Load environment variables first
require('dotenv').config();

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

// Import routes
const healthRoutes = require('./routes/healthRoutes');
const fileRoutes = require('./routes/fileRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/health', healthRoutes);
app.use('/api/files', fileRoutes);

// Root route
app.get('/', (req, res) => {
  res.json({
    message: 'Multi-Currency Invoice API',
    version: '1.0.0',
    endpoints: {
      health: '/api/health',
      files: '/api/files'
    },
    features: {
      healthChecks: 'Comprehensive health monitoring',
      fileUpload: 'Bulk file upload and storage'
    }
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    message: 'The requested endpoint does not exist'
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Internal Server Error',
    message: 'Something went wrong on the server'
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📊 Health check available at: http://localhost:${PORT}/api/health`);
  console.log(`📁 File upload available at: http://localhost:${PORT}/api/files/upload`);
  
  // Log environment configuration
  console.log(`🔑 OpenAI API Key configured: ${process.env.OPENAI_API_KEY ? 'Yes' : 'No'}`);
  console.log(`🤖 OpenAI Model: ${process.env.OPENAI_MODEL || 'gpt-5-mini-2025-08-07'}`);
});

module.exports = app;
