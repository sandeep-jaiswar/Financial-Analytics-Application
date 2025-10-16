from django.db import models
from decimal import Decimal
from datetime import datetime


class StockQuote:
    """
    Represents a real-time stock quote
    """
    def __init__(self, symbol=None, name=None, price=None):
        self.symbol = symbol
        self.name = name
        self.price = price
        self.change = None
        self.change_in_percent = None
        self.day_high = None
        self.day_low = None
        self.open = None
        self.previous_close = None
        self.volume = None
        self.timestamp = None

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'name': self.name,
            'price': float(self.price) if self.price else None,
            'change': float(self.change) if self.change else None,
            'changeInPercent': float(self.change_in_percent) if self.change_in_percent else None,
            'dayHigh': float(self.day_high) if self.day_high else None,
            'dayLow': float(self.day_low) if self.day_low else None,
            'open': float(self.open) if self.open else None,
            'previousClose': float(self.previous_close) if self.previous_close else None,
            'volume': self.volume,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class HistoricalQuote:
    """
    Represents a historical quote for a stock
    """
    def __init__(self, symbol=None, timestamp=None, open_price=None, 
                 high=None, low=None, close=None, volume=None, adjusted_close=None):
        self.symbol = symbol
        self.timestamp = timestamp
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.adjusted_close = adjusted_close

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume,
            'adjustedClose': float(self.adjusted_close) if self.adjusted_close else None,
        }

