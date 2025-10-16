# ClickHouse Quick Reference for Financial Analytics

## Starting ClickHouse

```bash
# Start ClickHouse
docker compose up -d clickhouse

# Check status
docker compose ps

# View logs
docker compose logs -f clickhouse
```

## Connecting to ClickHouse

```bash
# Connect via command line
docker exec -it financial-analytics-clickhouse clickhouse-client

# Connect to specific database
docker exec -it financial-analytics-clickhouse clickhouse-client --database financial_data

# HTTP interface
curl http://localhost:8123/ping
```

## Common Operations

### Database and Schema

```sql
-- Show databases
SHOW DATABASES;

-- Use database
USE financial_data;

-- Show tables
SHOW TABLES;

-- Describe table
DESCRIBE market_data;

-- Show create statement
SHOW CREATE TABLE market_data;
```

### Data Operations

```sql
-- Insert data
INSERT INTO market_data 
    (symbol, timestamp, date, open, high, low, close, volume)
VALUES 
    ('AAPL', now(), today(), 180.50, 182.30, 179.80, 181.90, 50000000);

-- Query latest prices
SELECT * FROM market_data
WHERE symbol = 'AAPL'
ORDER BY timestamp DESC
LIMIT 10;

-- Get daily aggregates
SELECT 
    symbol,
    date,
    min(low) as day_low,
    max(high) as day_high,
    argMin(open, timestamp) as open,
    argMax(close, timestamp) as close,
    sum(volume) as total_volume
FROM market_data
WHERE date >= today() - INTERVAL 7 DAY
GROUP BY symbol, date
ORDER BY date DESC, symbol;

-- Calculate daily returns
SELECT 
    symbol,
    date,
    close,
    round((close - lag(close) OVER (PARTITION BY symbol ORDER BY date)) / lag(close) OVER (PARTITION BY symbol ORDER BY date) * 100, 2) as daily_return_pct
FROM (
    SELECT 
        symbol, 
        date, 
        argMax(close, timestamp) as close
    FROM market_data
    GROUP BY symbol, date
)
ORDER BY symbol, date DESC
LIMIT 20;
```

### Performance Analysis

```sql
-- Check table size and rows
SELECT 
    name,
    total_rows,
    formatReadableSize(total_bytes) as size
FROM system.tables 
WHERE database = 'financial_data';

-- View partitions
SELECT 
    partition,
    count() as parts,
    sum(rows) as rows,
    formatReadableSize(sum(bytes_on_disk)) as size
FROM system.parts
WHERE database = 'financial_data' AND table = 'market_data' AND active
GROUP BY partition
ORDER BY partition DESC;

-- View recent queries
SELECT 
    type,
    query_start_time,
    query_duration_ms,
    formatReadableSize(memory_usage) as memory,
    query
FROM system.query_log
WHERE type = 'QueryFinish' AND query NOT LIKE '%system%'
ORDER BY query_start_time DESC
LIMIT 10;
```

### Maintenance

```sql
-- Optimize table (merge parts)
OPTIMIZE TABLE market_data FINAL;

-- Optimize specific partition
OPTIMIZE TABLE market_data PARTITION '202410' FINAL;

-- Drop old partition (be careful!)
ALTER TABLE market_data DROP PARTITION '202301';

-- Check for broken parts
SELECT * FROM system.detached_parts
WHERE database = 'financial_data' AND table = 'market_data';
```

## Useful System Tables

```sql
-- Active processes
SELECT * FROM system.processes;

-- Metrics
SELECT * FROM system.metrics;

-- Table information
SELECT * FROM system.tables WHERE database = 'financial_data';

-- Column information
SELECT * FROM system.columns WHERE database = 'financial_data' AND table = 'market_data';
```

## Performance Tips

1. **Use appropriate data types**: Decimal64 for prices, UInt64 for volume
2. **Leverage partitioning**: Query specific partitions when possible
3. **Use primary key in WHERE clauses**: Queries on (symbol, date) are fastest
4. **Avoid SELECT ***: Select only needed columns
5. **Batch inserts**: Insert in batches of 10k-100k rows for best performance
6. **Use materialized views**: Pre-aggregate common queries

## Environment Variables

```bash
# Set in .env file
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_DB=financial_data
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
```

## JDBC Connection String

```
jdbc:clickhouse://localhost:8123/financial_data
```

## Troubleshooting

### Container not starting
```bash
# Check logs
docker compose logs clickhouse

# Remove and restart
docker compose down -v
docker compose up -d clickhouse
```

### Connection refused
```bash
# Check if container is running
docker compose ps clickhouse

# Test HTTP interface
curl http://localhost:8123/ping

# Check port binding
netstat -tuln | grep -E '8123|9000'
```

### Slow queries
```sql
-- Enable query profiling
SET query_profiler_cpu_time_period_ns = 10000000;
SET query_profiler_real_time_period_ns = 10000000;

-- Check query log
SELECT * FROM system.query_log
WHERE type = 'QueryFinish' 
ORDER BY query_duration_ms DESC
LIMIT 10;
```

## Additional Resources

- [ClickHouse Documentation](https://clickhouse.com/docs/)
- [SQL Reference](https://clickhouse.com/docs/en/sql-reference/)
- [Functions](https://clickhouse.com/docs/en/sql-reference/functions/)
- [Aggregate Functions](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/)
