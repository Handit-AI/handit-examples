const express = require('express');
const CurrencyController = require('../controllers/CurrencyController');

const router = express.Router();
const currencyController = new CurrencyController();

// Currency conversion endpoints
router.post('/convert', currencyController.convertCurrency.bind(currencyController));
router.post('/convert/historical', currencyController.convertCurrencyHistorical.bind(currencyController));

// Exchange rate endpoints
router.get('/rate', currencyController.getExchangeRate.bind(currencyController));
router.get('/rate/historical', currencyController.getExchangeRateHistorical.bind(currencyController));

// All rates endpoints
router.get('/rates', currencyController.getAllRates.bind(currencyController));
router.get('/rates/historical', currencyController.getAllRatesHistorical.bind(currencyController));

// Currency information endpoints
router.get('/supported', currencyController.getSupportedCurrencies.bind(currencyController));
router.get('/supported/:currency', currencyController.checkCurrencySupport.bind(currencyController));

// Utility endpoints
router.post('/format', currencyController.formatCurrency.bind(currencyController));
router.post('/set-api-key', currencyController.setApiKey.bind(currencyController));
router.get('/status', currencyController.getStatus.bind(currencyController));

module.exports = router;
