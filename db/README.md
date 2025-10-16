# Database Configuration

This directory contains database schemas and configuration for the Financial Analytics Application.

## Structure

```
db/
├── schema/                      # SQL migration scripts
│   ├── README.md               # Schema documentation
│   ├── 001_create_market_data_table.sql
│   └── 002_create_market_data_table_replicated.sql
└── init-schema.sh              # Schema initialization script
```

## Quick Start

### 1. Start ClickHouse with Docker

```bash
# From the project root directory
docker-compose up -d clickhouse

# Wait for ClickHouse to be ready
docker-compose ps
```

### 2. Initialize Schema

The schema is automatically initialized when the Docker container starts. To manually initialize or update:

```bash
# Using the initialization script (requires clickhouse-client installed)
./db/init-schema.sh

# Or manually via Docker
docker exec -it financial-analytics-clickhouse clickhouse-client --multiquery < db/schema/001_create_market_data_table.sql
```

### 3. Verify Setup

```bash
# Connect to ClickHouse
docker exec -it financial-analytics-clickhouse clickhouse-client

# Check the schema
SHOW DATABASES;
USE financial_data;
SHOW TABLES;
DESCRIBE market_data;
```

## Schema Files

- **001_create_market_data_table.sql**: Creates the basic `market_data` table using MergeTree engine. Suitable for local development and single-node deployments.

- **002_create_market_data_table_replicated.sql**: Creates a replicated version using ReplicatedMergeTree engine. Use this for production clusters with high availability requirements.

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Configuration options:
- `CLICKHOUSE_PASSWORD`: Password for ClickHouse (optional for local dev)
- `CLICKHOUSE_HOST`: ClickHouse host (default: localhost)
- `CLICKHOUSE_PORT`: ClickHouse native protocol port (default: 9000)
- `CLICKHOUSE_DB`: Database name (default: financial_data)
- `USE_REPLICATION`: Enable replicated schema (default: false)

## Testing the Schema

### Insert Sample Data

```sql
INSERT INTO financial_data.market_data 
    (symbol, timestamp, date, open, high, low, close, volume)
VALUES 
    ('AAPL', now(), today(), 180.50, 182.30, 179.80, 181.90, 50000000),
    ('GOOGL', now(), today(), 140.20, 141.50, 139.90, 141.00, 25000000),
    ('MSFT', now(), today(), 380.00, 382.50, 379.50, 381.80, 35000000);
```

### Query Examples

```sql
-- Get all data for a symbol
SELECT * FROM financial_data.market_data
WHERE symbol = 'AAPL'
ORDER BY timestamp DESC
LIMIT 10;

-- Calculate daily statistics
SELECT 
    symbol,
    date,
    min(low) as day_low,
    max(high) as day_high,
    argMin(open, timestamp) as open,
    argMax(close, timestamp) as close,
    sum(volume) as total_volume
FROM financial_data.market_data
WHERE date >= today() - INTERVAL 7 DAY
GROUP BY symbol, date
ORDER BY date DESC, symbol;
```

## Maintenance

### View Partitions

```sql
SELECT 
    partition,
    count() as parts,
    sum(rows) as rows,
    formatReadableSize(sum(bytes_on_disk)) as size
FROM system.parts
WHERE table = 'market_data' AND active
GROUP BY partition
ORDER BY partition DESC;
```

### Optimize Table

```sql
-- Optimize all partitions
OPTIMIZE TABLE financial_data.market_data FINAL;

-- Optimize specific partition
OPTIMIZE TABLE financial_data.market_data PARTITION '202410' FINAL;
```

## Troubleshooting

### ClickHouse Not Starting

```bash
# Check logs
docker-compose logs clickhouse

# Restart service
docker-compose restart clickhouse
```

### Schema Initialization Failed

```bash
# Verify ClickHouse is running
curl http://localhost:8123/ping

# Check if port is accessible
docker-compose port clickhouse 8123

# Try manual initialization
docker exec -it financial-analytics-clickhouse clickhouse-client
```

### Connection Refused

Ensure ports 8123 (HTTP) and 9000 (Native) are not blocked:

```bash
# Check if ports are listening
netstat -tuln | grep -E '8123|9000'

# Or with Docker
docker-compose ps
```

## For More Information

See [schema/README.md](schema/README.md) for detailed schema documentation, query examples, and production deployment guidance.
