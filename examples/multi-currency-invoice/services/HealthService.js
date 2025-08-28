const os = require('os');

class HealthService {
  /**
   * Get basic health status
   * @returns {Object} Basic health information
   */
  static async getBasicHealth() {
    return {
      status: 'healthy',
      service: 'multi-currency-invoice-api',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development'
    };
  }

  /**
   * Get detailed health status
   * @returns {Object} Detailed health information
   */
  static async getDetailedHealth() {
    const basicHealth = await this.getBasicHealth();
    
    return {
      ...basicHealth,
      system: {
        platform: os.platform(),
        arch: os.arch(),
        nodeVersion: process.version,
        memory: {
          used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
          total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024),
          external: Math.round(process.memoryUsage().external / 1024 / 1024)
        },
        cpu: {
          loadAverage: os.loadavg(),
          cores: os.cpus().length
        }
      },
      dependencies: {
        express: '4.18.2',
        cors: '2.8.5',
        helmet: '7.1.0',
        morgan: '1.10.0'
      }
    };
  }

  /**
   * Check health with custom parameters
   * @param {string} include - What to include in the check
   * @param {number} timeout - Timeout for the check
   * @returns {Object} Custom health check result
   */
  static async checkHealthWithParams(include = 'basic', timeout = 5000) {
    const startTime = Date.now();
    
    try {
      // Simulate some health checks based on parameters
      const checks = {};
      
      if (include.includes('basic')) {
        checks.basic = await this.getBasicHealth();
      }
      
      if (include.includes('detailed')) {
        checks.detailed = await this.getDetailedHealth();
      }
      
      if (include.includes('performance')) {
        checks.performance = {
          responseTime: Date.now() - startTime,
          memoryUsage: process.memoryUsage(),
          cpuUsage: process.cpuUsage()
        };
      }
      
      const totalTime = Date.now() - startTime;
      
      return {
        status: 'healthy',
        checks,
        responseTime: totalTime,
        timestamp: new Date().toISOString(),
        parameters: { include, timeout }
      };
      
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message,
        responseTime: Date.now() - startTime,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Check if the service is ready to handle requests
   * @returns {boolean} Service readiness status
   */
  static isReady() {
    return process.uptime() > 0;
  }

  /**
   * Check if the service is alive
   * @returns {boolean} Service liveness status
   */
  static isAlive() {
    return true;
  }
}

module.exports = HealthService;
