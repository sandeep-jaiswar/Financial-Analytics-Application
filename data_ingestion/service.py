import logging
import time
from datetime import datetime, timedelta
import yfinance as yf
from django.conf import settings
from data_ingestion.models import MarketData
from data_ingestion.repository import ClickHouseRepository


logger = logging.getLogger('data_ingestion')


class DataIngestionService:
    """
    Service for ingesting market data from Yahoo Finance and storing in ClickHouse
    """
    
    def __init__(self):
        self.repository = ClickHouseRepository()
        self.symbols = getattr(settings, 'INGESTION_SYMBOLS', ['AAPL', 'GOOGL', 'MSFT'])
        self.history_days = getattr(settings, 'INGESTION_HISTORY_DAYS', 30)
    
    def ingest_historical_data(self, symbol, days=None):
        """
        Ingest historical data for a single symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days of history to fetch (default from settings)
            
        Returns:
            Number of records saved
        """
        if days is None:
            days = self.history_days
            
        logger.info(f"Starting historical data ingestion for {symbol} ({days} days)")
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date, interval='1d')
            
            if hist.empty:
                logger.warning(f"No historical data available for {symbol}")
                return 0
            
            market_data_list = []
            
            for index, row in hist.iterrows():
                market_data = MarketData(
                    symbol=symbol,
                    timestamp=index.to_pydatetime(),
                    date=index.date(),
                    open_price=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=int(row['Volume']),
                    adjusted_close=row['Close']
                )
                market_data_list.append(market_data)
            
            saved_count = self.repository.save_batch(market_data_list)
            logger.info(f"Ingested {saved_count} historical records for {symbol}")
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return 0
    
    def ingest_historical_data_batch(self, symbols=None, days=None):
        """
        Ingest historical data for multiple symbols
        
        Args:
            symbols: List of stock symbols (default from settings)
            days: Number of days of history
            
        Returns:
            Total number of records saved
        """
        if symbols is None:
            symbols = self.symbols
        
        if days is None:
            days = self.history_days
            
        logger.info(f"Starting batch historical data ingestion for {len(symbols)} symbols")
        
        total_saved = 0
        
        for symbol in symbols:
            try:
                saved = self.ingest_historical_data(symbol, days)
                total_saved += saved
                
                # Sleep to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"Ingestion failed for {symbol}: {str(e)}")
                continue
        
        logger.info(f"Batch ingestion complete. Total records saved: {total_saved}")
        return total_saved
    
    def ingest_current_quote(self, symbol):
        """
        Ingest current/live quote for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            True if saved successfully
        """
        logger.info(f"Fetching current quote for {symbol}")
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                logger.warning(f"No quote available for {symbol}")
                return False
            
            # Get the latest price data
            hist = ticker.history(period='1d')
            if hist.empty:
                logger.warning(f"No recent data available for {symbol}")
                return False
            
            latest = hist.iloc[-1]
            latest_date = hist.index[-1]
            
            market_data = MarketData(
                symbol=symbol,
                timestamp=latest_date.to_pydatetime(),
                date=latest_date.date(),
                open_price=latest['Open'],
                high=latest['High'],
                low=latest['Low'],
                close=latest['Close'],
                volume=int(latest['Volume']),
                adjusted_close=latest['Close']
            )
            
            self.repository.save(market_data)
            logger.info(f"Successfully saved current quote for {symbol}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error fetching current quote for {symbol}: {str(e)}")
            return False
    
    def ingest_current_quotes_batch(self, symbols=None):
        """
        Ingest current quotes for multiple symbols
        
        Args:
            symbols: List of stock symbols (default from settings)
            
        Returns:
            Number of successfully saved quotes
        """
        if symbols is None:
            symbols = self.symbols
            
        logger.info(f"Starting batch current quote ingestion for {len(symbols)} symbols")
        
        success_count = 0
        
        for symbol in symbols:
            try:
                if self.ingest_current_quote(symbol):
                    success_count += 1
                
                # Sleep to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"Failed to ingest current quote for {symbol}: {str(e)}")
                continue
        
        logger.info(f"Batch current quote ingestion complete. Successfully saved: {success_count}/{len(symbols)}")
        return success_count
