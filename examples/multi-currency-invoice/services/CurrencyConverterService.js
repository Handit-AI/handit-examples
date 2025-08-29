/**
 * Currency Converter Service
 * 
 * This service provides currency conversion functionality using exchange rates
 * from exchangerate-api.com.
 * 
 * Features:
 * - Convert between any supported currencies
 * - Use latest exchange rates (free tier)
 * - Support for 170+ currencies including major ones
 * - Historical rates support (requires API key for v6)
 * 
 * API Endpoints:
 * - v4 (free): https://api.exchangerate-api.com/v4/latest/{base_currency}
 * - v6 (paid): https://v6.exchangerate-api.com/v6/{api_key}/history/{base}/{year}/{month}/{day}
 */
class CurrencyConverterService {
    constructor(apiKey = null) {
        // API configuration
        this.apiKey = apiKey;
        this.baseUrlV4 = 'https://api.exchangerate-api.com/v4';
        this.baseUrlV6 = 'https://v6.exchangerate-api.com/v6';
    }

    /**
     * Convert amount from one currency to another using latest rates or historical rates if date provided
     * @param {number} amount - Amount to convert
     * @param {string} fromCurrency - Source currency (3-letter ISO code)
     * @param {string} toCurrency - Target currency (3-letter ISO code)
     * @param {string} date - Optional date in YYYY-MM-DD format for historical rates
     * @returns {Promise<Object>} Conversion result
     */
    async convertCurrency(amount, fromCurrency, toCurrency, date = null) {
        try {
            // Validate amount
            if (typeof amount !== 'number' || amount < 0) {
                throw new Error('Amount must be a positive number');
            }

            // If date is provided, use historical rates (requires API key)
            if (date) {
                if (!this.apiKey) {
                    throw new Error('Date provided but API key required for historical rates. Use convertCurrencyHistorical() or set EXCHANGE_RATE_API_KEY environment variable.');
                }

                console.log(`💱 Converting ${amount} ${fromCurrency} to ${toCurrency} for ${date} using historical rates`);

                // Parse date
                const dateObj = new Date(date);
                if (isNaN(dateObj.getTime())) {
                    throw new Error('Invalid date format. Use YYYY-MM-DD');
                }

                const year = dateObj.getFullYear();
                const month = dateObj.getMonth() + 1; // getMonth() returns 0-11
                const day = dateObj.getDate();

                // Use v6 API for historical rates
                const response = await fetch(`${this.baseUrlV6}/${this.apiKey}/history/${fromCurrency}/${year}/${month}/${day}/${amount}`);
                if (!response.ok) {
                    const errorData = await response.json();
                    if (errorData['error-type'] === 'unsupported-code') {
                        throw new Error(`Currency ${fromCurrency} is not supported by the API`);
                    }
                    throw new Error(`API request failed: ${response.status} - ${errorData['error-type'] || response.statusText}`);
                }
                
                const data = await response.json();
                const convertedAmount = data.conversion_amounts[toCurrency];
                if (!convertedAmount) {
                    throw new Error(`Currency ${toCurrency} is not supported by the API`);
                }

                console.log(`✅ Historical conversion successful: ${amount} ${fromCurrency} = ${convertedAmount} ${toCurrency}`);
                
                return {
                    originalAmount: amount,
                    originalCurrency: fromCurrency,
                    convertedAmount: convertedAmount,
                    targetCurrency: toCurrency,
                    date: date,
                    year: year,
                    month: month,
                    day: day,
                    success: true,
                    apiVersion: 'v6',
                    historical: true
                };
            }

            // Use latest rates (no date provided)
            console.log(`💱 Converting ${amount} ${fromCurrency} to ${toCurrency} using latest rates`);

            // Use v4 API (free tier) for latest rates
            const response = await fetch(`${this.baseUrlV4}/latest/${fromCurrency}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                if (errorData.error_type === 'unsupported-code') {
                    throw new Error(`Currency ${fromCurrency} is not supported by the API`);
                }
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            const exchangeRate = data.rates[toCurrency];
            if (!exchangeRate) {
                throw new Error(`Currency ${toCurrency} is not supported by the API`);
            }
            
            const convertedAmount = amount * exchangeRate;

            console.log(`✅ Conversion successful: ${amount} ${fromCurrency} = ${convertedAmount} ${toCurrency}`);
            
            return {
                originalAmount: amount,
                originalCurrency: fromCurrency,
                convertedAmount: convertedAmount,
                targetCurrency: toCurrency,
                exchangeRate: exchangeRate,
                date: data.date || new Date().toISOString().split('T')[0],
                success: true,
                apiVersion: 'v4',
                historical: false
            };

        } catch (error) {
            console.error(`❌ Currency conversion failed:`, error.message);
            throw new Error(`Failed to convert ${amount} ${fromCurrency} to ${toCurrency}: ${error.message}`);
        }
    }

    /**
     * Convert amount using historical rates (requires API key)
     * @param {number} amount - Amount to convert
     * @param {string} fromCurrency - Source currency (3-letter ISO code)
     * @param {string} toCurrency - Target currency (3-letter ISO code)
     * @param {string} date - Date in YYYY-MM-DD format
     * @returns {Promise<Object>} Conversion result
     */
    async convertCurrencyHistorical(amount, fromCurrency, toCurrency, date) {
        if (!this.apiKey) {
            throw new Error('API key required for historical rates. Use convertCurrency() for latest rates.');
        }

        try {
            if (typeof amount !== 'number' || amount < 0) {
                throw new Error('Amount must be a positive number');
            }

            // Parse date
            const dateObj = new Date(date);
            if (isNaN(dateObj.getTime())) {
                throw new Error('Invalid date format. Use YYYY-MM-DD');
            }

            const year = dateObj.getFullYear();
            const month = dateObj.getMonth() + 1; // getMonth() returns 0-11
            const day = dateObj.getDate();

            console.log(`💱 Converting ${amount} ${fromCurrency} to ${toCurrency} for ${date} using historical rates`);

            // Use v6 API for historical rates
            const response = await fetch(`${this.baseUrlV6}/${this.apiKey}/history/${fromCurrency}/${year}/${month}/${day}/${amount}`);
            if (!response.ok) {
                const errorData = await response.json();
                if (errorData['error-type'] === 'unsupported-code') {
                    throw new Error(`Currency ${fromCurrency} is not supported by the API`);
                }
                throw new Error(`API request failed: ${response.status} - ${errorData['error-type'] || response.statusText}`);
            }
            
            const data = await response.json();
            const convertedAmount = data.conversion_amounts[toCurrency];
            if (!convertedAmount) {
                throw new Error(`Currency ${toCurrency} is not supported by the API`);
            }

            console.log(`✅ Historical conversion successful: ${amount} ${fromCurrency} = ${convertedAmount} ${toCurrency}`);
            
            return {
                originalAmount: amount,
                originalCurrency: fromCurrency,
                convertedAmount: convertedAmount,
                targetCurrency: toCurrency,
                date: date,
                year: year,
                month: month,
                day: day,
                success: true,
                apiVersion: 'v6',
                historical: true
            };

        } catch (error) {
            console.error(`❌ Historical currency conversion failed:`, error.message);
            throw new Error(`Failed to convert ${amount} ${fromCurrency} to ${toCurrency} for ${date}: ${error.message}`);
        }
    }

    /**
     * Get latest exchange rate between two currencies
     * @param {string} fromCurrency - Source currency (3-letter ISO code)
     * @param {string} toCurrency - Target currency (3-letter ISO code)
     * @returns {Promise<Object>} Exchange rate result
     */
    async getExchangeRate(fromCurrency, toCurrency) {
        try {
            console.log(`📊 Getting latest exchange rate ${fromCurrency} to ${toCurrency}`);

            const response = await fetch(`${this.baseUrlV4}/latest/${fromCurrency}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                if (errorData.error_type === 'unsupported-code') {
                    throw new Error(`Currency ${fromCurrency} is not supported by the API`);
                }
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            const rate = data.rates[toCurrency];
            if (!rate) {
                throw new Error(`Currency ${toCurrency} is not supported by the API`);
            }

            console.log(`✅ Exchange rate: 1 ${fromCurrency} = ${rate} ${toCurrency}`);

            return {
                fromCurrency,
                toCurrency,
                rate,
                date: data.date || new Date().toISOString().split('T')[0],
                success: true,
                apiVersion: 'v4'
            };

        } catch (error) {
            console.error(`❌ Failed to get exchange rate:`, error.message);
            throw new Error(`Failed to get exchange rate ${fromCurrency} to ${toCurrency}: ${error.message}`);
        }
    }

    /**
     * Get historical exchange rate (requires API key)
     * @param {string} fromCurrency - Source currency (3-letter ISO code)
     * @param {string} toCurrency - Target currency (3-letter ISO code)
     * @param {string} date - Date in YYYY-MM-DD format
     * @returns {Promise<Object>} Exchange rate result
     */
    async getExchangeRateHistorical(fromCurrency, toCurrency, date) {
        if (!this.apiKey) {
            throw new Error('API key required for historical rates. Use getExchangeRate() for latest rates.');
        }

        try {
            const dateObj = new Date(date);
            if (isNaN(dateObj.getTime())) {
                throw new Error('Invalid date format. Use YYYY-MM-DD');
            }

            const year = dateObj.getFullYear();
            const month = dateObj.getMonth() + 1;
            const day = dateObj.getDate();

            console.log(`📊 Getting historical exchange rate ${fromCurrency} to ${toCurrency} for ${date}`);

            const response = await fetch(`${this.baseUrlV6}/${this.apiKey}/history/${fromCurrency}/${year}/${month}/${day}`);
            if (!response.ok) {
                const errorData = await response.json();
                if (errorData['error-type'] === 'unsupported-code') {
                    throw new Error(`Currency ${fromCurrency} is not supported by the API`);
                }
                throw new Error(`API request failed: ${response.status} - ${errorData['error-type'] || response.statusText}`);
            }
            
            const data = await response.json();
            const rate = data.conversion_rates[toCurrency];
            if (!rate) {
                throw new Error(`Currency ${toCurrency} is not supported by the API`);
            }

            console.log(`✅ Historical exchange rate: 1 ${fromCurrency} = ${rate} ${toCurrency}`);

            return {
                fromCurrency,
                toCurrency,
                rate,
                date: date,
                year: year,
                month: month,
                day: day,
                success: true,
                apiVersion: 'v6',
                historical: true
            };

        } catch (error) {
            console.error(`❌ Failed to get historical exchange rate:`, error.message);
            throw new Error(`Failed to get historical exchange rate ${fromCurrency} to ${toCurrency}: ${error.message}`);
        }
    }

    /**
     * Get all latest exchange rates for a base currency
     * @param {string} baseCurrency - Base currency (3-letter ISO code)
     * @param {string[]} symbols - Specific currencies to get (optional, gets all if not specified)
     * @returns {Promise<Object>} All exchange rates
     */
    async getAllRates(baseCurrency, symbols = null) {
        try {
            console.log(`📊 Getting all latest exchange rates for ${baseCurrency}`);

            const response = await fetch(`${this.baseUrlV4}/latest/${baseCurrency}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                if (errorData.error_type === 'unsupported-code') {
                    throw new Error(`Currency ${baseCurrency} is not supported by the API`);
                }
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            let rates = data.rates;

            // Filter by specific symbols if provided
            if (symbols && Array.isArray(symbols)) {
                const filteredRates = {};
                symbols.forEach(symbol => {
                    if (rates[symbol]) {
                        filteredRates[symbol] = rates[symbol];
                    }
                });
                rates = filteredRates;
            }

            console.log(`✅ Retrieved ${Object.keys(rates).length} exchange rates for ${baseCurrency}`);

            return {
                baseCurrency,
                rates,
                date: data.date || new Date().toISOString().split('T')[0],
                count: Object.keys(rates).length,
                success: true,
                apiVersion: 'v4'
            };

        } catch (error) {
            console.error(`❌ Failed to get all rates:`, error.message);
            throw new Error(`Failed to get exchange rates for ${baseCurrency}: ${error.message}`);
        }
    }

    /**
     * Get all historical exchange rates for a base currency (requires API key)
     * @param {string} baseCurrency - Base currency (3-letter ISO code)
     * @param {string} date - Date in YYYY-MM-DD format
     * @returns {Promise<Object>} All historical exchange rates
     */
    async getAllRatesHistorical(baseCurrency, date) {
        if (!this.apiKey) {
            throw new Error('API key required for historical rates. Use getAllRates() for latest rates.');
        }

        try {
            const dateObj = new Date(date);
            if (isNaN(dateObj.getTime())) {
                throw new Error('Invalid date format. Use YYYY-MM-DD');
            }

            const year = dateObj.getFullYear();
            const month = dateObj.getMonth() + 1;
            const day = dateObj.getDate();

            console.log(`📊 Getting all historical exchange rates for ${baseCurrency} on ${date}`);

            const response = await fetch(`${this.baseUrlV6}/${this.apiKey}/history/${baseCurrency}/${year}/${month}/${day}`);
            if (!response.ok) {
                const errorData = await response.json();
                if (errorData['error-type'] === 'unsupported-code') {
                    throw new Error(`Currency ${baseCurrency} is not supported by the API`);
                }
                throw new Error(`API request failed: ${response.status} - ${errorData['error-type'] || response.statusText}`);
            }

            const data = await response.json();
            const rates = data.conversion_rates;

            console.log(`✅ Retrieved ${Object.keys(rates).length} historical exchange rates for ${baseCurrency}`);

            return {
                baseCurrency,
                rates,
                date: date,
                year: year,
                month: month,
                day: day,
                count: Object.keys(rates).length,
                success: true,
                apiVersion: 'v6',
                historical: true
            };

        } catch (error) {
            console.error(`❌ Failed to get historical rates:`, error.message);
            throw new Error(`Failed to get historical exchange rates for ${baseCurrency}: ${error.message}`);
        }
    }

    /**
     * Set API key for historical data access
     * @param {string} apiKey - API key from exchangerate-api.com
     */
    setApiKey(apiKey) {
        if (apiKey && typeof apiKey === 'string') {
            this.apiKey = apiKey;
            console.log('✅ API key set successfully for historical data access');
        } else {
            throw new Error('Invalid API key. Must be a non-empty string.');
        }
    }

    /**
     * Check if historical data is available
     * @returns {boolean} True if API key is set, false otherwise
     */
    hasHistoricalAccess() {
        return !!this.apiKey;
    }

    /**
     * Get list of supported currencies dynamically from API
     * @returns {Promise<Object>} Supported currencies from API
     */
    async getSupportedCurrencies() {
        try {
            console.log('📋 Getting supported currencies from API');

            const response = await fetch(`${this.baseUrlV4}/latest/USD`);
            if (!response.ok) {
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            const currencies = Object.keys(data.rates);
            currencies.push('USD'); // Add USD as it's the base currency

            console.log(`✅ Retrieved ${currencies.length} supported currencies from API`);

            return {
                count: currencies.length,
                currencies: currencies.sort(),
                date: data.date || new Date().toISOString().split('T')[0],
                success: true
            };

        } catch (error) {
            console.error(`❌ Failed to get supported currencies:`, error.message);
            throw new Error(`Failed to get supported currencies: ${error.message}`);
        }
    }

    /**
     * Check if a currency is supported by querying the API
     * @param {string} currency - Currency code to check
     * @returns {Promise<boolean>} True if supported, false otherwise
     */
    async isCurrencySupported(currency) {
        try {
            if (!currency || typeof currency !== 'string') {
                return false;
            }

            const response = await fetch(`${this.baseUrlV4}/latest/${currency}`);
            return response.ok;

        } catch (error) {
            return false;
        }
    }

    /**
     * Format currency amount with proper formatting
     * @param {number} amount - Amount to convert
     * @param {string} currency - Currency code
     * @param {string} locale - Locale for formatting (default: 'en-US')
     * @returns {string} Formatted currency string
     */
    formatCurrency(amount, currency, locale = 'en-US') {
        try {
            return new Intl.NumberFormat(locale, {
                style: 'currency',
                currency: currency
            }).format(amount);
        } catch (error) {
            // Fallback formatting if Intl is not supported
            return `${amount.toFixed(2)} ${currency}`;
        }
    }

    /**
     * Get currency information and metadata
     * @param {string} currency - Currency code
     * @returns {Object} Currency information
     */
    getCurrencyInfo(currency) {
        const currencyNames = {
            'USD': 'US Dollar',
            'EUR': 'Euro',
            'GBP': 'British Pound',
            'JPY': 'Japanese Yen',
            'AUD': 'Australian Dollar',
            'CAD': 'Canadian Dollar',
            'CHF': 'Swiss Franc',
            'CNY': 'Chinese Yuan',
            'SEK': 'Swedish Krona',
            'NZD': 'New Zealand Dollar',
            'MXN': 'Mexican Peso',
            'SGD': 'Singapore Dollar',
            'HKD': 'Hong Kong Dollar',
            'NOK': 'Norwegian Krone',
            'KRW': 'South Korean Won',
            'TRY': 'Turkish Lira',
            'RUB': 'Russian Ruble',
            'INR': 'Indian Rupee',
            'BRL': 'Brazilian Real',
            'ZAR': 'South African Rand',
            'PLN': 'Polish Zloty',
            'THB': 'Thai Baht',
            'ILS': 'Israeli Shekel',
            'IDR': 'Indonesian Rupiah',
            'CZK': 'Czech Koruna',
            'AED': 'UAE Dirham',
            'CLP': 'Chilean Peso',
            'COP': 'Colombian Peso',
            'PEN': 'Peruvian Sol',
            'ARS': 'Argentine Peso'
        };

        return {
            code: currency.toUpperCase(),
            name: currencyNames[currency.toUpperCase()] || 'Unknown Currency',
            supported: null, // Will be determined dynamically by API
            symbol: this.getCurrencySymbol(currency)
        };
    }

    /**
     * Get currency symbol
     * @param {string} currency - Currency code
     * @returns {string} Currency symbol
     */
    getCurrencySymbol(currency) {
        const symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'AUD': 'A$',
            'CAD': 'C$',
            'CHF': 'CHF',
            'CNY': '¥',
            'SEK': 'kr',
            'NZD': 'NZ$',
            'MXN': '$',
            'SGD': 'S$',
            'HKD': 'HK$',
            'NOK': 'kr',
            'KRW': '₩',
            'TRY': '₺',
            'RUB': '₽',
            'INR': '₹',
            'BRL': 'R$',
            'ZAR': 'R',
            'PLN': 'zł',
            'THB': '฿',
            'ILS': '₪',
            'IDR': 'Rp',
            'CZK': 'Kč',
            'COP': '$'
        };

        return symbols[currency.toUpperCase()] || currency.toUpperCase();
    }
}

module.exports = CurrencyConverterService;
