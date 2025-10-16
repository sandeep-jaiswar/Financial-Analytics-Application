import logging
import time
from datetime import datetime, timedelta
import yfinance as yf
from django.conf import settings
from api_service.models import StockQuote, HistoricalQuote


logger = logging.getLogger('api_service')


class RateLimitExceededException(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


class YahooFinanceException(Exception):
    """Exception raised when Yahoo Finance API call fails"""
    pass


class RateLimiter:
    """Simple rate limiter implementation"""
    def __init__(self, max_calls, period=1.0):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside the window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.period]
            
            if len(self.calls) >= self.max_calls:
                raise RateLimitExceededException("Rate limit exceeded. Please try again later.")
            
            self.calls.append(now)
            return func(*args, **kwargs)
        return wrapper


class YahooFinanceService:
    """
    Service for fetching stock data from Yahoo Finance API
    Includes rate limiting and comprehensive error handling
    """
    def __init__(self):
        self.rate_limiter = RateLimiter(
            max_calls=getattr(settings, 'YAHOO_FINANCE_RATE_LIMIT', 5),
            period=1.0
        )

    def get_stock_quote(self, symbol):
        """
        Fetch real-time quote for a stock symbol
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            
        Returns:
            StockQuote with current data
            
        Raises:
            YahooFinanceException: if API call fails
            RateLimitExceededException: if rate limit is exceeded
        """
        logger.info(f"Fetching stock quote for symbol: {symbol}")
        
        @self.rate_limiter
        def fetch():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if not info or 'symbol' not in info:
                    raise YahooFinanceException(f"No data available for symbol: {symbol}")
                
                quote = StockQuote(
                    symbol=symbol,
                    name=info.get('longName', info.get('shortName', symbol)),
                    price=info.get('currentPrice', info.get('regularMarketPrice'))
                )
                
                quote.change = info.get('regularMarketChange')
                quote.change_in_percent = info.get('regularMarketChangePercent')
                quote.day_high = info.get('dayHigh', info.get('regularMarketDayHigh'))
                quote.day_low = info.get('dayLow', info.get('regularMarketDayLow'))
                quote.open = info.get('open', info.get('regularMarketOpen'))
                quote.previous_close = info.get('previousClose', info.get('regularMarketPreviousClose'))
                quote.volume = info.get('volume', info.get('regularMarketVolume'))
                
                # Get timestamp from recent data
                hist = ticker.history(period='1d')
                if not hist.empty:
                    quote.timestamp = hist.index[-1].to_pydatetime()
                else:
                    quote.timestamp = datetime.now()
                
                return quote
                
            except Exception as e:
                logger.error(f"Error fetching stock quote for {symbol}: {str(e)}")
                raise YahooFinanceException(f"Failed to fetch stock quote for {symbol}", e)
        
        return fetch()

    def get_historical_quotes(self, symbol, from_date, to_date, interval='1d'):
        """
        Fetch historical quotes for a stock symbol
        
        Args:
            symbol: Stock symbol
            from_date: Start date (datetime)
            to_date: End date (datetime)
            interval: Data interval ('1d', '1wk', '1mo')
            
        Returns:
            List of HistoricalQuote objects
            
        Raises:
            YahooFinanceException: if API call fails
            RateLimitExceededException: if rate limit is exceeded
        """
        logger.info(f"Fetching historical quotes for symbol: {symbol} from {from_date} to {to_date}")
        
        @self.rate_limiter
        def fetch():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=from_date, end=to_date, interval=interval)
                
                if hist.empty:
                    raise YahooFinanceException(f"No historical data available for symbol: {symbol}")
                
                quotes = []
                for index, row in hist.iterrows():
                    quote = HistoricalQuote(
                        symbol=symbol,
                        timestamp=index.to_pydatetime(),
                        open_price=row['Open'],
                        high=row['High'],
                        low=row['Low'],
                        close=row['Close'],
                        volume=int(row['Volume']),
                        adjusted_close=row['Close']  # yfinance already provides adjusted close
                    )
                    quotes.append(quote)
                
                return quotes
                
            except Exception as e:
                logger.error(f"Error fetching historical quotes for {symbol}: {str(e)}")
                raise YahooFinanceException(f"Failed to fetch historical quotes for {symbol}", e)
        
        return fetch()

    def get_multiple_quotes(self, symbols):
        """
        Fetch quotes for multiple symbols in one call
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            List of StockQuote objects
            
        Raises:
            YahooFinanceException: if API call fails
            RateLimitExceededException: if rate limit is exceeded
        """
        logger.info(f"Fetching quotes for {len(symbols)} symbols")
        
        quotes = []
        for symbol in symbols:
            try:
                quote = self.get_stock_quote(symbol)
                quotes.append(quote)
                # Small delay to avoid hammering the API
                time.sleep(0.1)
            except Exception as e:
                logger.warning(f"Failed to fetch quote for {symbol}: {str(e)}")
                continue
        
        return quotes
