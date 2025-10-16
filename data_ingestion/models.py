from django.db import models
from datetime import datetime
from decimal import Decimal


class MarketData:
    """
    Represents market data for storage in ClickHouse
    """
    def __init__(self, symbol=None, timestamp=None, date=None,
                 open_price=None, high=None, low=None, close=None,
                 volume=None, adjusted_close=None):
        self.symbol = symbol
        self.timestamp = timestamp
        self.date = date
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.adjusted_close = adjusted_close
        self.created_at = datetime.now()

    def __repr__(self):
        return f"MarketData(symbol={self.symbol}, date={self.date}, close={self.close})"

