from django.test import TestCase, Client
from django.urls import reverse
from api_service.models import StockQuote, HistoricalQuote
from api_service.services import YahooFinanceService, RateLimitExceededException
from datetime import datetime
import json


class StockQuoteModelTest(TestCase):
    """Test StockQuote model"""
    
    def test_stock_quote_creation(self):
        quote = StockQuote(symbol='AAPL', name='Apple Inc.', price=150.0)
        self.assertEqual(quote.symbol, 'AAPL')
        self.assertEqual(quote.name, 'Apple Inc.')
        self.assertEqual(quote.price, 150.0)
    
    def test_stock_quote_to_dict(self):
        quote = StockQuote(symbol='AAPL', name='Apple Inc.', price=150.0)
        quote.change = 2.5
        quote.volume = 100000
        
        data = quote.to_dict()
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertEqual(data['name'], 'Apple Inc.')
        self.assertEqual(data['price'], 150.0)
        self.assertEqual(data['change'], 2.5)
        self.assertEqual(data['volume'], 100000)


class HistoricalQuoteModelTest(TestCase):
    """Test HistoricalQuote model"""
    
    def test_historical_quote_creation(self):
        timestamp = datetime.now()
        quote = HistoricalQuote(
            symbol='AAPL',
            timestamp=timestamp,
            open_price=145.0,
            high=152.0,
            low=144.0,
            close=150.0,
            volume=1000000,
            adjusted_close=150.0
        )
        self.assertEqual(quote.symbol, 'AAPL')
        self.assertEqual(quote.open, 145.0)
        self.assertEqual(quote.high, 152.0)
    
    def test_historical_quote_to_dict(self):
        timestamp = datetime.now()
        quote = HistoricalQuote(
            symbol='AAPL',
            timestamp=timestamp,
            open_price=145.0,
            high=152.0,
            low=144.0,
            close=150.0,
            volume=1000000,
            adjusted_close=150.0
        )
        
        data = quote.to_dict()
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertEqual(data['open'], 145.0)
        self.assertEqual(data['close'], 150.0)


class APIEndpointsTest(TestCase):
    """Test API endpoints"""
    
    def setUp(self):
        self.client = Client()
    
    def test_quote_endpoint_returns_error_without_network(self):
        """Test that quote endpoint returns error when network is unavailable"""
        response = self.client.get('/api/stocks/AAPL/quote/')
        # Should return 500 because Yahoo Finance API is not accessible
        self.assertIn(response.status_code, [500, 429])
    
    def test_history_endpoint_requires_dates(self):
        """Test that history endpoint requires date parameters"""
        response = self.client.get('/api/stocks/AAPL/history/')
        self.assertEqual(response.status_code, 400)
    
    def test_multiple_quotes_endpoint_requires_symbols(self):
        """Test that multiple quotes endpoint requires symbols"""
        response = self.client.post(
            '/api/stocks/quotes/',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_multiple_quotes_with_valid_data(self):
        """Test multiple quotes endpoint with valid data"""
        response = self.client.post(
            '/api/stocks/quotes/',
            data=json.dumps({'symbols': ['AAPL', 'GOOGL']}),
            content_type='application/json'
        )
        # Should return 200 with empty list (network not available)
        self.assertEqual(response.status_code, 200)


class RateLimiterTest(TestCase):
    """Test rate limiter functionality"""
    
    def test_rate_limiter_creation(self):
        """Test that rate limiter can be created"""
        from api_service.services import RateLimiter
        limiter = RateLimiter(max_calls=5, period=1.0)
        self.assertEqual(limiter.max_calls, 5)
        self.assertEqual(limiter.period, 1.0)

