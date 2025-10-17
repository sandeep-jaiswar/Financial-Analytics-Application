from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import Mock, patch
from datetime import datetime, date, timedelta
import json


class MarketDataAPITest(TestCase):
    """Test market data API endpoints"""
    
    def setUp(self):
        self.client = Client()
    
    @patch('api_service.marketdata_views.ClickHouseRepository')
    def test_get_symbols_success(self, mock_repo_class):
        """Test successful retrieval of symbols"""
        mock_repo = Mock()
        mock_client = Mock()
        
        # Mock the client execute method for symbols query
        mock_client.execute.side_effect = [
            # First call - get symbols
            [
                ('AAPL', 100, date(2024, 1, 1), date(2024, 10, 15)),
                ('GOOGL', 150, date(2024, 1, 1), date(2024, 10, 15)),
            ],
            # Second call - get total count
            [(2,)]
        ]
        
        mock_repo.get_client.return_value = mock_client
        mock_repo_class.return_value = mock_repo
        
        response = self.client.get('/api/marketdata/symbols/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('symbols', data)
        self.assertIn('pagination', data)
        self.assertEqual(len(data['symbols']), 2)
        self.assertEqual(data['symbols'][0]['symbol'], 'AAPL')
        self.assertEqual(data['pagination']['totalItems'], 2)
    
    @patch('api_service.marketdata_views.ClickHouseRepository')
    def test_get_symbols_with_pagination(self, mock_repo_class):
        """Test symbols endpoint with pagination parameters"""
        mock_repo = Mock()
        mock_client = Mock()
        
        mock_client.execute.side_effect = [
            # First call - get symbols (page 2)
            [
                ('MSFT', 200, date(2024, 1, 1), date(2024, 10, 15)),
            ],
            # Second call - get total count
            [(5,)]
        ]
        
        mock_repo.get_client.return_value = mock_client
        mock_repo_class.return_value = mock_repo
        
        response = self.client.get('/api/marketdata/symbols/?page=2&per_page=1')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['pagination']['page'], 2)
        self.assertEqual(data['pagination']['perPage'], 1)
        self.assertEqual(data['pagination']['totalPages'], 5)
        self.assertTrue(data['pagination']['hasNext'])
        self.assertTrue(data['pagination']['hasPrev'])
    
    def test_get_symbols_invalid_page(self):
        """Test symbols endpoint with invalid page number"""
        response = self.client.get('/api/marketdata/symbols/?page=0')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('api_service.marketdata_views.ClickHouseRepository')
    def test_get_marketdata_by_symbol_success(self, mock_repo_class):
        """Test successful retrieval of market data by symbol"""
        mock_repo = Mock()
        mock_client = Mock()
        
        test_date = datetime(2024, 10, 15)
        
        mock_client.execute.side_effect = [
            # First call - get market data
            [
                ('AAPL', test_date, date(2024, 10, 15), 150.0, 152.0, 149.0, 151.0, 1000000, 151.0),
                ('AAPL', test_date, date(2024, 10, 14), 148.0, 150.5, 147.5, 150.0, 900000, 150.0),
            ],
            # Second call - get total count
            [(2,)]
        ]
        
        mock_repo.get_client.return_value = mock_client
        mock_repo_class.return_value = mock_repo
        
        response = self.client.get('/api/marketdata/AAPL/?from=2024-10-01&to=2024-10-31')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertIn('data', data)
        self.assertIn('dateRange', data)
        self.assertIn('pagination', data)
        self.assertEqual(len(data['data']), 2)
        self.assertEqual(data['data'][0]['close'], 151.0)
        self.assertEqual(data['dateRange']['from'], '2024-10-01')
        self.assertEqual(data['dateRange']['to'], '2024-10-31')
    
    @patch('api_service.marketdata_views.ClickHouseRepository')
    def test_get_marketdata_by_symbol_default_dates(self, mock_repo_class):
        """Test market data retrieval with default date range (last 30 days)"""
        mock_repo = Mock()
        mock_client = Mock()
        
        mock_client.execute.side_effect = [
            # First call - get market data
            [],
            # Second call - get total count
            [(0,)]
        ]
        
        mock_repo.get_client.return_value = mock_client
        mock_repo_class.return_value = mock_repo
        
        response = self.client.get('/api/marketdata/AAPL/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['symbol'], 'AAPL')
        self.assertIn('dateRange', data)
    
    def test_get_marketdata_by_symbol_invalid_dates(self):
        """Test market data endpoint with invalid date format"""
        response = self.client.get('/api/marketdata/AAPL/?from=invalid-date&to=2024-10-31')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_get_marketdata_by_symbol_invalid_date_range(self):
        """Test market data endpoint with from date after to date"""
        response = self.client.get('/api/marketdata/AAPL/?from=2024-10-31&to=2024-10-01')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('Invalid date range', data['error'])
    
    @patch('api_service.marketdata_views.ClickHouseRepository')
    def test_get_latest_marketdata_all_symbols(self, mock_repo_class):
        """Test retrieval of latest market data for all symbols"""
        mock_repo = Mock()
        mock_client = Mock()
        
        test_date = datetime(2024, 10, 15)
        
        mock_client.execute.side_effect = [
            # First call - get latest data
            [
                ('AAPL', test_date, date(2024, 10, 15), 150.0, 152.0, 149.0, 151.0, 1000000, 151.0),
                ('GOOGL', test_date, date(2024, 10, 15), 2800.0, 2850.0, 2790.0, 2820.0, 500000, 2820.0),
            ],
            # Second call - get total count
            [(2,)]
        ]
        
        mock_repo.get_client.return_value = mock_client
        mock_repo_class.return_value = mock_repo
        
        response = self.client.get('/api/marketdata/latest/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('pagination', data)
        self.assertEqual(len(data['data']), 2)
        self.assertEqual(data['data'][0]['symbol'], 'AAPL')
        self.assertEqual(data['data'][1]['symbol'], 'GOOGL')
    
    @patch('api_service.marketdata_views.ClickHouseRepository')
    def test_get_latest_marketdata_specific_symbols(self, mock_repo_class):
        """Test retrieval of latest market data for specific symbols"""
        mock_repo = Mock()
        mock_client = Mock()
        
        test_date = datetime(2024, 10, 15)
        
        mock_client.execute.side_effect = [
            # First call - get latest data
            [
                ('AAPL', test_date, date(2024, 10, 15), 150.0, 152.0, 149.0, 151.0, 1000000, 151.0),
            ],
            # Second call - get total count
            [(1,)]
        ]
        
        mock_repo.get_client.return_value = mock_client
        mock_repo_class.return_value = mock_repo
        
        response = self.client.get('/api/marketdata/latest/?symbols=AAPL')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['symbol'], 'AAPL')
    
    @patch('api_service.marketdata_views.ClickHouseRepository')
    def test_get_latest_marketdata_multiple_symbols(self, mock_repo_class):
        """Test retrieval of latest market data for multiple comma-separated symbols"""
        mock_repo = Mock()
        mock_client = Mock()
        
        test_date = datetime(2024, 10, 15)
        
        mock_client.execute.side_effect = [
            # First call - get latest data
            [
                ('AAPL', test_date, date(2024, 10, 15), 150.0, 152.0, 149.0, 151.0, 1000000, 151.0),
                ('MSFT', test_date, date(2024, 10, 15), 420.0, 425.0, 418.0, 422.0, 800000, 422.0),
            ],
            # Second call - get total count
            [(2,)]
        ]
        
        mock_repo.get_client.return_value = mock_client
        mock_repo_class.return_value = mock_repo
        
        response = self.client.get('/api/marketdata/latest/?symbols=AAPL,MSFT')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['data']), 2)
    
    @patch('api_service.marketdata_views.ClickHouseRepository')
    def test_get_latest_marketdata_with_pagination(self, mock_repo_class):
        """Test latest market data endpoint with pagination"""
        mock_repo = Mock()
        mock_client = Mock()
        
        mock_client.execute.side_effect = [
            # First call - get latest data (page 1, per_page 1)
            [
                ('AAPL', datetime(2024, 10, 15), date(2024, 10, 15), 150.0, 152.0, 149.0, 151.0, 1000000, 151.0),
            ],
            # Second call - get total count
            [(5,)]
        ]
        
        mock_repo.get_client.return_value = mock_client
        mock_repo_class.return_value = mock_repo
        
        response = self.client.get('/api/marketdata/latest/?page=1&per_page=1')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['pagination']['page'], 1)
        self.assertEqual(data['pagination']['perPage'], 1)
        self.assertEqual(data['pagination']['totalPages'], 5)
        self.assertTrue(data['pagination']['hasNext'])
    
    def test_get_latest_marketdata_invalid_page(self):
        """Test latest market data endpoint with invalid page number"""
        response = self.client.get('/api/marketdata/latest/?page=-1')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    @patch('api_service.marketdata_views.ClickHouseRepository')
    def test_clickhouse_connection_error(self, mock_repo_class):
        """Test handling of ClickHouse connection errors"""
        mock_repo = Mock()
        mock_repo.get_client.side_effect = Exception("Connection failed")
        mock_repo_class.return_value = mock_repo
        
        response = self.client.get('/api/marketdata/symbols/')
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Internal server error')
