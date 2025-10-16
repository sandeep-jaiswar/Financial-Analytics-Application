import logging
from clickhouse_driver import Client
from django.conf import settings
from data_ingestion.models import MarketData


logger = logging.getLogger('data_ingestion')


class ClickHouseRepository:
    """
    Repository for storing market data in ClickHouse
    Uses clickhouse-driver for data persistence
    """
    
    INSERT_SQL = """
        INSERT INTO market_data 
        (symbol, timestamp, date, open, high, low, close, volume, adjusted_close, created_at)
        VALUES
    """
    
    def __init__(self):
        self.client = None
        
    def get_client(self):
        """Get or create ClickHouse client connection"""
        if self.client is None:
            self.client = Client(
                host=settings.CLICKHOUSE_HOST,
                port=settings.CLICKHOUSE_PORT,
                database=settings.CLICKHOUSE_DATABASE,
                user=settings.CLICKHOUSE_USER,
                password=settings.CLICKHOUSE_PASSWORD
            )
        return self.client
    
    def save(self, market_data):
        """
        Save a single market data record
        
        Args:
            market_data: MarketData object to save
        """
        logger.debug(f"Saving market data for symbol: {market_data.symbol}")
        
        try:
            client = self.get_client()
            
            client.execute(
                """
                INSERT INTO market_data 
                (symbol, timestamp, date, open, high, low, close, volume, adjusted_close, created_at)
                VALUES
                """,
                [(
                    market_data.symbol,
                    market_data.timestamp,
                    market_data.date,
                    float(market_data.open) if market_data.open else 0,
                    float(market_data.high) if market_data.high else 0,
                    float(market_data.low) if market_data.low else 0,
                    float(market_data.close) if market_data.close else 0,
                    int(market_data.volume) if market_data.volume else 0,
                    float(market_data.adjusted_close) if market_data.adjusted_close else 0,
                    market_data.created_at
                )]
            )
            
            logger.info(f"Successfully saved market data for {market_data.symbol}")
            
        except Exception as e:
            logger.error(f"Error saving market data for {market_data.symbol}: {str(e)}")
            raise
    
    def save_batch(self, market_data_list):
        """
        Save multiple market data records in batch
        
        Args:
            market_data_list: List of MarketData objects to save
            
        Returns:
            Number of records saved
        """
        if not market_data_list:
            logger.warning("No market data to save")
            return 0
        
        logger.info(f"Saving batch of {len(market_data_list)} market data records")
        
        saved_count = 0
        
        try:
            client = self.get_client()
            
            data = []
            for market_data in market_data_list:
                try:
                    data.append((
                        market_data.symbol,
                        market_data.timestamp,
                        market_data.date,
                        float(market_data.open) if market_data.open else 0,
                        float(market_data.high) if market_data.high else 0,
                        float(market_data.low) if market_data.low else 0,
                        float(market_data.close) if market_data.close else 0,
                        int(market_data.volume) if market_data.volume else 0,
                        float(market_data.adjusted_close) if market_data.adjusted_close else 0,
                        market_data.created_at
                    ))
                except Exception as e:
                    logger.error(f"Error preparing batch for {market_data.symbol}: {str(e)}")
            
            if data:
                client.execute(
                    """
                    INSERT INTO market_data 
                    (symbol, timestamp, date, open, high, low, close, volume, adjusted_close, created_at)
                    VALUES
                    """,
                    data
                )
                saved_count = len(data)
                logger.info(f"Successfully saved {saved_count} market data records")
            
        except Exception as e:
            logger.error(f"Error executing batch save: {str(e)}")
        
        return saved_count
    
    def exists(self, symbol, date):
        """
        Check if market data exists for a symbol and date
        
        Args:
            symbol: Stock symbol
            date: Date to check (datetime.date)
            
        Returns:
            True if data exists
        """
        try:
            client = self.get_client()
            
            result = client.execute(
                "SELECT COUNT(*) FROM market_data WHERE symbol = %(symbol)s AND date = %(date)s",
                {'symbol': symbol, 'date': date}
            )
            
            return result[0][0] > 0
            
        except Exception as e:
            logger.error(f"Error checking existence for {symbol} on {date}: {str(e)}")
            return False
    
    def find_by_symbol_and_date_range(self, symbol, from_date, to_date):
        """
        Get market data for a symbol within a date range
        
        Args:
            symbol: Stock symbol
            from_date: Start date
            to_date: End date
            
        Returns:
            List of MarketData objects
        """
        try:
            client = self.get_client()
            
            results = client.execute(
                """
                SELECT symbol, timestamp, date, open, high, low, close, volume, adjusted_close, created_at
                FROM market_data 
                WHERE symbol = %(symbol)s AND date BETWEEN %(from_date)s AND %(to_date)s 
                ORDER BY date
                """,
                {'symbol': symbol, 'from_date': from_date, 'to_date': to_date}
            )
            
            market_data_list = []
            for row in results:
                market_data = MarketData(
                    symbol=row[0],
                    timestamp=row[1],
                    date=row[2],
                    open_price=row[3],
                    high=row[4],
                    low=row[5],
                    close=row[6],
                    volume=row[7],
                    adjusted_close=row[8]
                )
                market_data.created_at = row[9]
                market_data_list.append(market_data)
            
            return market_data_list
            
        except Exception as e:
            logger.error(f"Error querying market data: {str(e)}")
            return []
