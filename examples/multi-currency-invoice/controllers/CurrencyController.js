const CurrencyConverterService = require('../services/CurrencyConverterService');

class CurrencyController {
    constructor() {
        // Initialize service with API key from environment if available
        const apiKey = process.env.EXCHANGE_RATE_API_KEY || null;
        this.currencyService = new CurrencyConverterService(apiKey);
        
        if (apiKey) {
            console.log('🔑 Historical exchange rates enabled with API key');
        } else {
            console.log('💡 Historical exchange rates disabled. Set EXCHANGE_RATE_API_KEY for full access');
        }
    }

    /**
     * Convert currency using latest rates or historical rates if date provided
     * POST /api/currency/convert
     */
    async convertCurrency(req, res) {
        try {
            const { amount, fromCurrency, toCurrency, date } = req.body;

            // Validate required fields
            if (!amount || !fromCurrency || !toCurrency) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required fields: amount, fromCurrency, toCurrency'
                });
            }

            // Validate amount
            if (isNaN(amount) || amount <= 0) {
                return res.status(400).json({
                    success: false,
                    error: 'Amount must be a positive number'
                });
            }

            // Validate date format if provided
            if (date && !/^\d{4}-\d{2}-\d{2}$/.test(date)) {
                return res.status(400).json({
                    success: false,
                    error: 'Date must be in YYYY-MM-DD format'
                });
            }

            console.log(`🔄 Currency conversion request: ${amount} ${fromCurrency} to ${toCurrency}${date ? ` for ${date}` : ''}`);

            const result = await this.currencyService.convertCurrency(
                parseFloat(amount),
                fromCurrency.toUpperCase(),
                toCurrency.toUpperCase(),
                date || null
            );

            res.json({
                success: true,
                data: result
            });

        } catch (error) {
            console.error('❌ Currency conversion error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Convert currency using historical rates (requires API key)
     * POST /api/currency/convert/historical
     */
    async convertCurrencyHistorical(req, res) {
        try {
            const { amount, fromCurrency, toCurrency, date } = req.body;

            // Validate required fields
            if (!amount || !fromCurrency || !toCurrency || !date) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required fields: amount, fromCurrency, toCurrency, date'
                });
            }

            // Validate amount
            if (isNaN(amount) || amount <= 0) {
                return res.status(400).json({
                    success: false,
                    error: 'Amount must be a positive number'
                });
            }

            // Validate date format
            if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
                return res.status(400).json({
                    success: false,
                    error: 'Date must be in YYYY-MM-DD format'
                });
            }

            // Check if historical access is available
            if (!this.currencyService.hasHistoricalAccess()) {
                return res.status(403).json({
                    success: false,
                    error: 'Historical rates require API key. Set EXCHANGE_RATE_API_KEY environment variable.'
                });
            }

            console.log(`🔄 Historical currency conversion request: ${amount} ${fromCurrency} to ${toCurrency} for ${date}`);

            const result = await this.currencyService.convertCurrencyHistorical(
                parseFloat(amount),
                fromCurrency.toUpperCase(),
                toCurrency.toUpperCase(),
                date
            );

            res.json({
                success: true,
                data: result
            });

        } catch (error) {
            console.error('❌ Historical currency conversion error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Get latest exchange rate between two currencies
     * GET /api/currency/rate
     */
    async getExchangeRate(req, res) {
        try {
            const { fromCurrency, toCurrency } = req.query;

            // Validate required fields
            if (!fromCurrency || !toCurrency) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required query parameters: fromCurrency, toCurrency'
                });
            }

            console.log(`📊 Exchange rate request: ${fromCurrency} to ${toCurrency}`);

            const result = await this.currencyService.getExchangeRate(
                fromCurrency.toUpperCase(),
                toCurrency.toUpperCase()
            );

            res.json({
                success: true,
                data: result
            });

        } catch (error) {
            console.error('❌ Get exchange rate error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Get historical exchange rate (requires API key)
     * GET /api/currency/rate/historical
     */
    async getExchangeRateHistorical(req, res) {
        try {
            const { fromCurrency, toCurrency, date } = req.query;

            // Validate required fields
            if (!fromCurrency || !toCurrency || !date) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required query parameters: fromCurrency, toCurrency, date'
                });
            }

            // Validate date format
            if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
                return res.status(400).json({
                    success: false,
                    error: 'Date must be in YYYY-MM-DD format'
                });
            }

            // Check if historical access is available
            if (!this.currencyService.hasHistoricalAccess()) {
                return res.status(403).json({
                    success: false,
                    error: 'Historical rates require API key. Set EXCHANGE_RATE_API_KEY environment variable.'
                });
            }

            console.log(`📊 Historical exchange rate request: ${fromCurrency} to ${toCurrency} for ${date}`);

            const result = await this.currencyService.getExchangeRateHistorical(
                fromCurrency.toUpperCase(),
                toCurrency.toUpperCase(),
                date
            );

            res.json({
                success: true,
                data: result
            });

        } catch (error) {
            console.error('❌ Get historical exchange rate error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Get all latest exchange rates for a base currency
     * GET /api/currency/rates
     */
    async getAllRates(req, res) {
        try {
            const { baseCurrency, symbols } = req.query;

            // Validate required fields
            if (!baseCurrency) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required query parameter: baseCurrency'
                });
            }

            // Parse symbols if provided
            let symbolsArray = null;
            if (symbols) {
                try {
                    symbolsArray = JSON.parse(symbols);
                    if (!Array.isArray(symbolsArray)) {
                        throw new Error('Symbols must be an array');
                    }
                } catch (parseError) {
                    return res.status(400).json({
                        success: false,
                        error: 'Invalid symbols format. Must be a valid JSON array'
                    });
                }
            }

            console.log(`📊 All rates request for base currency: ${baseCurrency}`);

            const result = await this.currencyService.getAllRates(
                baseCurrency.toUpperCase(),
                symbolsArray
            );

            res.json({
                success: true,
                data: result
            });

        } catch (error) {
            console.error('❌ Get all rates error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Get all historical exchange rates for a base currency (requires API key)
     * GET /api/currency/rates/historical
     */
    async getAllRatesHistorical(req, res) {
        try {
            const { baseCurrency, date } = req.query;

            // Validate required fields
            if (!baseCurrency || !date) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required query parameters: baseCurrency, date'
                });
            }

            // Validate date format
            if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
                return res.status(400).json({
                    success: false,
                    error: 'Date must be in YYYY-MM-DD format'
                });
            }

            // Check if historical access is available
            if (!this.currencyService.hasHistoricalAccess()) {
                return res.status(403).json({
                    success: false,
                    error: 'Historical rates require API key. Set EXCHANGE_RATE_API_KEY environment variable.'
                });
            }

            console.log(`📊 Historical all rates request for base currency: ${baseCurrency} on ${date}`);

            const result = await this.currencyService.getAllRatesHistorical(
                baseCurrency.toUpperCase(),
                date
            );

            res.json({
                success: true,
                data: result
            });

        } catch (error) {
            console.error('❌ Get historical all rates error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Get list of supported currencies
     * GET /api/currency/supported
     */
    async getSupportedCurrencies(req, res) {
        try {
            console.log('📋 Supported currencies request');

            const result = await this.currencyService.getSupportedCurrencies();

            res.json({
                success: true,
                data: result
            });

        } catch (error) {
            console.error('❌ Get supported currencies error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Check if a currency is supported
     * GET /api/currency/supported/:currency
     */
    async checkCurrencySupport(req, res) {
        try {
            const { currency } = req.params;

            if (!currency) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing currency parameter'
                });
            }

            console.log(`🔍 Currency support check for: ${currency}`);

            const isSupported = await this.currencyService.isCurrencySupported(currency);
            const currencyInfo = this.currencyService.getCurrencyInfo(currency);
            
            // Update the supported status based on API response
            currencyInfo.supported = isSupported;

            res.json({
                success: true,
                data: {
                    currency: currency.toUpperCase(),
                    supported: isSupported,
                    info: currencyInfo
                }
            });

        } catch (error) {
            console.error('❌ Check currency support error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Format currency amount
     * POST /api/currency/format
     */
    async formatCurrency(req, res) {
        try {
            const { amount, currency, locale } = req.body;

            // Validate required fields
            if (!amount || !currency) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required fields: amount, currency'
                });
            }

            // Validate amount
            if (isNaN(amount)) {
                return res.status(400).json({
                    success: false,
                    error: 'Amount must be a valid number'
                });
            }

            console.log(`💰 Format currency request: ${amount} ${currency}`);

            const formatted = this.currencyService.formatCurrency(
                parseFloat(amount),
                currency.toUpperCase(),
                locale || 'en-US'
            );

            res.json({
                success: true,
                data: {
                    originalAmount: amount,
                    currency: currency.toUpperCase(),
                    formatted: formatted,
                    locale: locale || 'en-US'
                }
            });

        } catch (error) {
            console.error('❌ Format currency error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Set API key for historical data access
     * POST /api/currency/set-api-key
     */
    async setApiKey(req, res) {
        try {
            const { apiKey } = req.body;

            if (!apiKey) {
                return res.status(400).json({
                    success: false,
                    error: 'Missing required field: apiKey'
                });
            }

            console.log('🔑 Setting API key for historical data access');

            this.currencyService.setApiKey(apiKey);

            res.json({
                success: true,
                message: 'API key set successfully. Historical data access enabled.',
                hasHistoricalAccess: this.currencyService.hasHistoricalAccess()
            });

        } catch (error) {
            console.error('❌ Set API key error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    /**
     * Get service status and capabilities
     * GET /api/currency/status
     */
    async getStatus(req, res) {
        try {
            console.log('📊 Currency service status request');

            const supportedCurrencies = await this.currencyService.getSupportedCurrencies();
            const status = {
                service: 'Currency Converter Service',
                version: '2.0.0',
                hasHistoricalAccess: this.currencyService.hasHistoricalAccess(),
                supportedCurrenciesCount: supportedCurrencies.count || 0,
                apiEndpoints: {
                    v4: 'Free tier - Latest exchange rates',
                    v6: this.currencyService.hasHistoricalAccess() ? 'Enabled - Historical rates' : 'Disabled - Requires API key'
                },
                features: [
                    'Latest exchange rates (free)',
                    'Currency conversion',
                    'Exchange rate queries',
                    'All rates for base currency',
                    'Currency validation',
                    'Currency formatting',
                    'Supported currencies list'
                ]
            };

            if (this.currencyService.hasHistoricalAccess()) {
                status.features.push('Historical exchange rates');
                status.features.push('Historical currency conversion');
            }

            res.json({
                success: true,
                data: status
            });

        } catch (error) {
            console.error('❌ Get status error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }
}

module.exports = CurrencyController;
