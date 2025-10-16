# ClickHouse Database Schema

This directory contains SQL migration scripts for setting up the ClickHouse database schema optimized for financial time-series data.

## Schema Overview

The database schema is designed to efficiently store and query financial market data (OHLCV - Open, High, Low, Close, Volume) with the following characteristics:

- **Database**: `financial_data`
- **Primary Table**: `market_data`
- **Engine**: MergeTree (or ReplicatedMergeTree for production)
- **Partitioning**: Monthly partitions using `toYYYYMM(date)`
- **Ordering**: Optimized for queries by symbol and date

## Table Structure

### market_data

| Column | Type | Description |
|--------|------|-------------|
| symbol | String | Stock ticker symbol (e.g., AAPL, GOOGL) |
| timestamp | DateTime | Trading timestamp in UTC |
| date | Date | Trading date (used for partitioning) |
| open | Decimal64(8) | Opening price |
| high | Decimal64(8) | Highest price during the period |
| low | Decimal64(8) | Lowest price during the period |
| close | Decimal64(8) | Closing price |
| volume | UInt64 | Trading volume |
| adjusted_close | Nullable(Decimal64(8)) | Adjusted closing price |
| created_at | DateTime | Record creation timestamp |

## Migration Scripts

1. **001_create_market_data_table.sql** - Basic MergeTree table for local/single-node deployments
2. **002_create_market_data_table_replicated.sql** - ReplicatedMergeTree table for production clusters

## Features

- **Monthly Partitioning**: Data is partitioned by month for efficient data management and faster queries
- **Bloom Filter Index**: On symbol column for fast lookups
- **MinMax Index**: On timestamp for efficient range queries
- **Optimized Ordering**: Primary key on (symbol, date) for analytical workloads
- **TTL Support**: Configurable data retention (default: 10 years)

## Local Setup with Docker

### Prerequisites

- Docker and Docker Compose installed
- Ports 8123 and 9000 available

### Start ClickHouse

```bash
# Start ClickHouse server
docker-compose up -d clickhouse

# Check service health
docker-compose ps
```

### Initialize Schema

The schema is automatically initialized when the container starts. The SQL files in this directory are mounted to `/docker-entrypoint-initdb.d`.

Alternatively, you can manually run the migration scripts:

```bash
# Connect to ClickHouse
docker exec -it financial-analytics-clickhouse clickhouse-client

# Or from host machine if clickhouse-client is installed
clickhouse-client --host localhost --port 9000

# Run the schema creation script
USE financial_data;
SOURCE /docker-entrypoint-initdb.d/001_create_market_data_table.sql;
```

### Verify Schema

```bash
# Connect to ClickHouse client
docker exec -it financial-analytics-clickhouse clickhouse-client

# In the ClickHouse client:
SHOW DATABASES;
USE financial_data;
SHOW TABLES;
DESCRIBE market_data;
```

### Insert Test Data

```sql
INSERT INTO market_data (symbol, timestamp, date, open, high, low, close, volume)
VALUES 
    ('AAPL', '2024-01-15 09:30:00', '2024-01-15', 185.50, 187.20, 184.30, 186.80, 52000000),
    ('GOOGL', '2024-01-15 09:30:00', '2024-01-15', 142.30, 143.50, 141.80, 143.20, 28000000);
```

### Query Examples

```sql
-- Get latest prices for a symbol
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
WHERE symbol = 'AAPL' AND date >= '2024-01-01'
GROUP BY symbol, date
ORDER BY date DESC;

-- Check partition information
SELECT 
    partition,
    count() as rows,
    formatReadableSize(sum(bytes_on_disk)) as size
FROM system.parts
WHERE table = 'market_data' AND active
GROUP BY partition
ORDER BY partition DESC;
```

## Production Deployment

For production environments with high availability requirements:

1. Set up a ClickHouse cluster with ClickHouse Keeper or ZooKeeper
2. Use the replicated schema (`002_create_market_data_table_replicated.sql`)
3. Configure macros `{shard}` and `{replica}` in ClickHouse server configuration
4. Adjust replication and performance settings based on your workload

### Replication Configuration

Create `/etc/clickhouse-server/config.d/macros.xml`:

```xml
<clickhouse>
    <macros>
        <shard>01</shard>
        <replica>replica01</replica>
    </macros>
</clickhouse>
```

## Maintenance

### Check Table Size

```sql
SELECT 
    formatReadableSize(sum(bytes_on_disk)) as size,
    count() as rows
FROM system.parts
WHERE table = 'market_data' AND active;
```

### Optimize Partitions

```sql
-- Optimize recent partitions for better query performance
OPTIMIZE TABLE market_data PARTITION '202401' FINAL;
```

### Drop Old Partitions

```sql
-- Drop data older than required retention period
ALTER TABLE market_data DROP PARTITION '202001';
```

## Troubleshooting

### Connection Issues

```bash
# Check if ClickHouse is running
docker-compose ps clickhouse

# View logs
docker-compose logs clickhouse

# Test HTTP interface
curl http://localhost:8123/ping
```

### Performance Tuning

- Adjust `index_granularity` based on your query patterns
- Consider additional materialized views for common aggregations
- Monitor query performance with `system.query_log`

## References

- [ClickHouse Documentation](https://clickhouse.com/docs/)
- [MergeTree Engine](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree)
- [ReplicatedMergeTree Engine](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replication)
- [Partitioning](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/custom-partitioning-key)
