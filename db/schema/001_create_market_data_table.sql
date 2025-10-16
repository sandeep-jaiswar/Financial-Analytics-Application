-- ClickHouse schema for financial time-series market data
-- This table stores OHLCV (Open, High, Low, Close, Volume) data for financial instruments

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS financial_data;

-- Use the financial_data database
USE financial_data;

-- Create market_data table with MergeTree engine for optimal time-series analytics
-- The table uses monthly partitioning for efficient data management and query performance
CREATE TABLE IF NOT EXISTS market_data
(
    symbol String COMMENT 'Stock ticker symbol (e.g., AAPL, GOOGL)',
    timestamp DateTime COMMENT 'Trading timestamp in UTC',
    date Date COMMENT 'Trading date for partitioning',
    open Decimal64(8) COMMENT 'Opening price',
    high Decimal64(8) COMMENT 'Highest price during the period',
    low Decimal64(8) COMMENT 'Lowest price during the period',
    close Decimal64(8) COMMENT 'Closing price',
    volume UInt64 COMMENT 'Trading volume',
    adjusted_close Nullable(Decimal64(8)) COMMENT 'Adjusted closing price (accounts for splits, dividends)',
    created_at DateTime DEFAULT now() COMMENT 'Record creation timestamp'
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (symbol, date, timestamp)
PRIMARY KEY (symbol, date)
SETTINGS 
    index_granularity = 8192,
    -- Enable TTL for data older than 10 years (can be adjusted)
    merge_with_ttl_timeout = 86400
COMMENT 'Market data table storing OHLCV time-series data with monthly partitioning';

-- Create index for faster symbol lookups
CREATE INDEX IF NOT EXISTS idx_symbol ON market_data (symbol) TYPE bloom_filter GRANULARITY 1;

-- Create index for timestamp range queries
CREATE INDEX IF NOT EXISTS idx_timestamp ON market_data (timestamp) TYPE minmax GRANULARITY 1;
