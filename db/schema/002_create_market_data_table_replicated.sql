-- ClickHouse replicated schema for financial time-series market data
-- This version uses ReplicatedMergeTree for high availability and data replication
-- Use this schema in production environments with ClickHouse Keeper or ZooKeeper

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS financial_data;

-- Use the financial_data database
USE financial_data;

-- Create replicated market_data table with ReplicatedMergeTree engine
-- Replication path includes shard and replica identifiers for distributed setups
-- Adjust {shard} and {replica} macros based on your cluster configuration
CREATE TABLE IF NOT EXISTS market_data_replicated
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
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/financial_data/market_data', '{replica}')
PARTITION BY toYYYYMM(date)
ORDER BY (symbol, date, timestamp)
PRIMARY KEY (symbol, date)
SETTINGS 
    index_granularity = 8192,
    -- Replication settings
    replicated_deduplication_window = 100,
    replicated_deduplication_window_seconds = 604800,
    -- Enable TTL for data older than 10 years (can be adjusted)
    merge_with_ttl_timeout = 86400,
    -- Performance optimization for replicated tables
    max_replicated_mutations_in_queue = 16,
    max_replicated_merges_in_queue = 16
COMMENT 'Replicated market data table storing OHLCV time-series data with monthly partitioning';

-- Create index for faster symbol lookups
CREATE INDEX IF NOT EXISTS idx_symbol_replicated ON market_data_replicated (symbol) TYPE bloom_filter GRANULARITY 1;

-- Create index for timestamp range queries
CREATE INDEX IF NOT EXISTS idx_timestamp_replicated ON market_data_replicated (timestamp) TYPE minmax GRANULARITY 1;
