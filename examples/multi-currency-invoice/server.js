// Load environment variables first
require('dotenv').config();

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');

// Import Handit.ai for validation
const { config} = require('@handit.ai/node');

// Import routes
const healthRoutes = require('./routes/healthRoutes');
const fileRoutes = require('./routes/fileRoutes');
const currencyRoutes = require('./routes/currencyRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

/**
 * Validate that Handit.ai API key is present in environment variables.
 * 
 * This function checks if the HANDIT_API_KEY is configured before allowing
 * server startup. It's a simple validation that ensures the basic
 * configuration is in place.
 * 
 * @throws {Error} If HANDIT_API_KEY is not found
 */
function validateHanditConfiguration() {
    console.log("🔍 Validating Handit.ai configuration...");
    
    // Check if Handit.ai API key is present in environment variables
    const handitApiKey = process.env.HANDIT_API_KEY;
    if (!handitApiKey) {
        console.error("❌ HANDIT_API_KEY not found in environment variables");
        console.log("\n" + "=".repeat(80));
        console.log("🚨 HANDIT.AI CONFIGURATION REQUIRED");
        console.log("=".repeat(80));
        console.log("❌ Server cannot start: Handit.ai is not properly configured");
        console.log("\n📋 Follow these steps to set up Handit.ai:");
        console.log("1. Visit Handit.ai");
        console.log("2. Create an account");
        console.log("3. Get API key from dashboard");
        console.log("4. Add HANDIT_API_KEY to .env file");
        console.log("\n❓ Questions? Need help?");
        console.log("   📅 Schedule a call: https://calendly.com/cristhian-handit/30min");
        console.log("   📚 Documentation: https://docs.handit.ai/");
        console.log("\n" + "=".repeat(80));
        throw new Error("Handit.ai configuration required");
    }
    
    // Configure Handit.ai with the API key
    config({ apiKey: handitApiKey });
    
    console.log("✅ Handit.ai configuration validation completed successfully");
}

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/health', healthRoutes);
app.use('/api/files', fileRoutes);
app.use('/api/currency', currencyRoutes);

// Root route
app.get('/', (req, res) => {
  res.json({
    message: 'Multi-Currency Invoice API',
    version: '1.0.0',
    endpoints: {
      health: '/api/health',
      files: '/api/files',
      currency: '/api/currency'
    },
    features: {
      healthChecks: 'Comprehensive health monitoring',
      fileUpload: 'Bulk file upload and storage',
      currencyConversion: 'Historical currency conversion with exchange rates'
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

// Start server with Handit.ai validation
try {
    // Validate Handit.ai configuration before starting server
    // This ensures the server only runs with proper observability setup
    validateHanditConfiguration();
    
    // Start the Express server with comprehensive configuration
    // The server will only start if all validation passes
    app.listen(PORT, () => {
        console.log(`🚀 Server running on port ${PORT}`);
        console.log(`📊 Health check available at: http://localhost:${PORT}/api/health`);
        console.log(`📁 File upload available at: http://localhost:${PORT}/api/files/upload`);
        console.log(`💱 Currency conversion available at: http://localhost:${PORT}/api/currency`);
        
        // Log environment configuration
        console.log(`🔑 OpenAI API Key configured: ${process.env.OPENAI_API_KEY ? 'Yes' : 'No'}`);
        console.log(`🤖 OpenAI Model: ${process.env.OPENAI_MODEL || 'gpt-5-mini-2025-08-07'}`);
        console.log(`🔍 Handit.ai configured: Yes`);
    });
    
} catch (error) {
    // Exit gracefully if validation fails
    // This prevents server startup without proper Handit.ai configuration
    console.error(`💥 Server startup failed: ${error.message}`);
    process.exit(1);
}

module.exports = app;
