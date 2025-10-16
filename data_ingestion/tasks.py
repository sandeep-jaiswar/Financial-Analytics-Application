import logging
from celery import shared_task
from data_ingestion.service import DataIngestionService

logger = logging.getLogger('data_ingestion')
alert_logger = logging.getLogger('ALERT')


@shared_task(bind=True, max_retries=3, default_retry_delay=2)
def ingest_daily_historical(self):
    """
    Daily scheduled task to ingest historical market data
    Runs at 6 PM daily (after market close)
    """
    logger.info("Starting daily historical data ingestion task")
    
    try:
        service = DataIngestionService()
        # Fetch last 7 days to catch up on any missed data
        total_saved = service.ingest_historical_data_batch(days=7)
        
        logger.info(f"Daily historical ingestion completed. Total records saved: {total_saved}")
        return {'status': 'success', 'records_saved': total_saved}
        
    except Exception as e:
        logger.error(f"Daily historical ingestion failed: {str(e)}")
        alert_logger.error(f"ALERT: Daily historical ingestion failed: {str(e)}")
        
        # Retry the task
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            alert_logger.error("ALERT: Daily historical ingestion failed after max retries")
            return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True, max_retries=3, default_retry_delay=2)
def ingest_intraday_quotes(self):
    """
    Intraday scheduled task to fetch current quotes
    Runs every 15 minutes during market hours (9:30 AM - 4:00 PM EST, Mon-Fri)
    """
    logger.info("Starting intraday quote ingestion task")
    
    try:
        service = DataIngestionService()
        success_count = service.ingest_current_quotes_batch()
        
        logger.info(f"Intraday quote ingestion completed. Successfully saved: {success_count}")
        
        # Alert if high failure rate (>50%)
        total_symbols = len(service.symbols)
        if success_count < total_symbols * 0.5:
            alert_logger.error(
                f"ALERT: High failure rate in intraday ingestion. "
                f"Only {success_count}/{total_symbols} symbols succeeded"
            )
        
        return {'status': 'success', 'quotes_saved': success_count}
        
    except Exception as e:
        logger.error(f"Intraday quote ingestion failed: {str(e)}")
        
        # Retry the task
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            alert_logger.error("ALERT: Intraday quote ingestion failed after max retries")
            return {'status': 'failed', 'error': str(e)}


@shared_task
def ingest_symbol_historical(symbol, days=30):
    """
    Task to ingest historical data for a single symbol
    Can be called programmatically
    
    Args:
        symbol: Stock symbol
        days: Number of days of history
    """
    logger.info(f"Starting historical ingestion for {symbol}")
    
    try:
        service = DataIngestionService()
        saved_count = service.ingest_historical_data(symbol, days)
        
        logger.info(f"Historical ingestion for {symbol} completed. Records saved: {saved_count}")
        return {'status': 'success', 'symbol': symbol, 'records_saved': saved_count}
        
    except Exception as e:
        logger.error(f"Historical ingestion for {symbol} failed: {str(e)}")
        return {'status': 'failed', 'symbol': symbol, 'error': str(e)}


@shared_task
def ingest_symbol_current(symbol):
    """
    Task to ingest current quote for a single symbol
    Can be called programmatically
    
    Args:
        symbol: Stock symbol
    """
    logger.info(f"Starting current quote ingestion for {symbol}")
    
    try:
        service = DataIngestionService()
        success = service.ingest_current_quote(symbol)
        
        if success:
            logger.info(f"Current quote ingestion for {symbol} completed successfully")
            return {'status': 'success', 'symbol': symbol}
        else:
            logger.warning(f"Current quote ingestion for {symbol} returned no data")
            return {'status': 'no_data', 'symbol': symbol}
        
    except Exception as e:
        logger.error(f"Current quote ingestion for {symbol} failed: {str(e)}")
        return {'status': 'failed', 'symbol': symbol, 'error': str(e)}
