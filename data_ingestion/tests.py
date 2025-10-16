from django.test import TestCase
from data_ingestion.models import MarketData
from data_ingestion.service import DataIngestionService
from datetime import datetime, date


class MarketDataModelTest(TestCase):
    """Test MarketData model"""
    
    def test_market_data_creation(self):
        """Test creating a MarketData instance"""
        now = datetime.now()
        today = date.today()
        
        data = MarketData(
            symbol='AAPL',
            timestamp=now,
            date=today,
            open_price=145.0,
            high=152.0,
            low=144.0,
            close=150.0,
            volume=1000000,
            adjusted_close=150.0
        )
        
        self.assertEqual(data.symbol, 'AAPL')
        self.assertEqual(data.open, 145.0)
        self.assertEqual(data.high, 152.0)
        self.assertEqual(data.low, 144.0)
        self.assertEqual(data.close, 150.0)
        self.assertEqual(data.volume, 1000000)
    
    def test_market_data_repr(self):
        """Test MarketData string representation"""
        today = date.today()
        data = MarketData(symbol='AAPL', date=today, close=150.0)
        repr_str = repr(data)
        self.assertIn('AAPL', repr_str)
        self.assertIn('150.0', repr_str)


class DataIngestionServiceTest(TestCase):
    """Test DataIngestionService"""
    
    def test_service_creation(self):
        """Test creating DataIngestionService"""
        service = DataIngestionService()
        self.assertIsNotNone(service)
        self.assertIsNotNone(service.repository)
    
    def test_service_has_symbols(self):
        """Test that service has configured symbols"""
        service = DataIngestionService()
        self.assertIsInstance(service.symbols, list)
        self.assertGreater(len(service.symbols), 0)
    
    def test_service_has_history_days(self):
        """Test that service has history days configured"""
        service = DataIngestionService()
        self.assertIsInstance(service.history_days, int)
        self.assertGreater(service.history_days, 0)

