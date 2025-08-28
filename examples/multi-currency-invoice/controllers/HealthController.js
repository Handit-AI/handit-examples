const HealthService = require('../services/HealthService');

class HealthController {
  /**
   * Basic health check endpoint
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async getHealth(req, res) {
    try {
      const healthStatus = await HealthService.getBasicHealth();
      res.status(200).json(healthStatus);
    } catch (error) {
      console.error('Health check error:', error);
      res.status(500).json({
        status: 'unhealthy',
        error: 'Failed to perform health check',
        timestamp: new Date().toISOString()
      });
    }
  }

  /**
   * Detailed health check endpoint
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async getDetailedHealth(req, res) {
    try {
      const detailedHealth = await HealthService.getDetailedHealth();
      res.status(200).json(detailedHealth);
    } catch (error) {
      console.error('Detailed health check error:', error);
      res.status(500).json({
        status: 'unhealthy',
        error: 'Failed to perform detailed health check',
        timestamp: new Date().toISOString()
      });
    }
  }

  /**
   * Custom health check with parameters
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async checkHealth(req, res) {
    try {
      const { include = 'basic', timeout = 5000 } = req.query;
      const healthCheck = await HealthService.checkHealthWithParams(include, timeout);
      res.status(200).json(healthCheck);
    } catch (error) {
      console.error('Custom health check error:', error);
      res.status(500).json({
        status: 'unhealthy',
        error: 'Failed to perform custom health check',
        timestamp: new Date().toISOString()
      });
    }
  }
}

module.exports = HealthController;
