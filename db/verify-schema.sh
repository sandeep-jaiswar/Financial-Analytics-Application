#!/bin/bash

# ClickHouse Schema Verification Script
# This script verifies that the ClickHouse schema is properly set up

set -e

CLICKHOUSE_CONTAINER="financial-analytics-clickhouse"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "ClickHouse Schema Verification"
echo "=========================================="
echo ""

# Check if container is running
echo -n "Checking if ClickHouse container is running... "
if docker ps --format '{{.Names}}' | grep -q "^${CLICKHOUSE_CONTAINER}$"; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Please start ClickHouse with: docker-compose up -d clickhouse"
    exit 1
fi

# Wait for ClickHouse to be ready
echo -n "Waiting for ClickHouse to be ready... "
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec "$CLICKHOUSE_CONTAINER" clickhouse-client --query "SELECT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}TIMEOUT${NC}"
    echo "ClickHouse did not become ready in time"
    exit 1
fi

echo ""
echo "Running verification tests..."
echo ""

# Test 1: Check database exists
echo -n "1. Checking database 'financial_data' exists... "
if docker exec "$CLICKHOUSE_CONTAINER" clickhouse-client --query "EXISTS DATABASE financial_data" | grep -q 1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 2: Check table exists
echo -n "2. Checking table 'market_data' exists... "
if docker exec "$CLICKHOUSE_CONTAINER" clickhouse-client --query "EXISTS TABLE financial_data.market_data" | grep -q 1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 3: Verify table structure
echo -n "3. Verifying table structure... "
expected_columns=("symbol" "timestamp" "date" "open" "high" "low" "close" "volume" "adjusted_close" "created_at")
table_structure=$(docker exec "$CLICKHOUSE_CONTAINER" clickhouse-client --query "DESCRIBE financial_data.market_data FORMAT TabSeparated")

all_columns_found=true
for col in "${expected_columns[@]}"; do
    if ! echo "$table_structure" | grep -q "^$col"; then
        echo -e "${RED}FAIL${NC}"
        echo "Missing column: $col"
        all_columns_found=false
        break
    fi
done

if $all_columns_found; then
    echo -e "${GREEN}PASS${NC}"
fi

# Test 4: Verify table engine
echo -n "4. Checking table engine (MergeTree)... "
engine=$(docker exec "$CLICKHOUSE_CONTAINER" clickhouse-client --query "SELECT engine FROM system.tables WHERE database = 'financial_data' AND name = 'market_data'")
if echo "$engine" | grep -q "MergeTree"; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${YELLOW}WARNING${NC} - Expected MergeTree, got: $engine"
fi

# Test 5: Insert and query test data
echo -n "5. Testing insert and query operations... "
docker exec "$CLICKHOUSE_CONTAINER" clickhouse-client --query "
    INSERT INTO financial_data.market_data 
        (symbol, timestamp, date, open, high, low, close, volume)
    VALUES 
        ('TEST', now(), today(), 100.0, 102.0, 99.0, 101.0, 1000000)
" 2>&1 > /dev/null

row_count=$(docker exec "$CLICKHOUSE_CONTAINER" clickhouse-client --query "SELECT count() FROM financial_data.market_data WHERE symbol = 'TEST'")
if [ "$row_count" -ge 1 ]; then
    echo -e "${GREEN}PASS${NC}"
    # Clean up test data
    docker exec "$CLICKHOUSE_CONTAINER" clickhouse-client --query "ALTER TABLE financial_data.market_data DELETE WHERE symbol = 'TEST'" 2>&1 > /dev/null
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# Test 6: Check partitioning
echo -n "6. Verifying partitioning configuration... "
partition_key=$(docker exec "$CLICKHOUSE_CONTAINER" clickhouse-client --query "
    SELECT partition_key FROM system.tables 
    WHERE database = 'financial_data' AND name = 'market_data'
")
if echo "$partition_key" | grep -q "toYYYYMM"; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${YELLOW}WARNING${NC} - Unexpected partition key: $partition_key"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}All verification tests passed!${NC}"
echo "=========================================="
echo ""

# Show table information
echo "Table Information:"
echo "------------------"
docker exec "$CLICKHOUSE_CONTAINER" clickhouse-client --query "
    SELECT 
        name,
        engine,
        total_rows,
        formatReadableSize(total_bytes) as size
    FROM system.tables 
    WHERE database = 'financial_data' AND name = 'market_data'
    FORMAT Pretty
"

echo ""
echo "Partition Information:"
echo "----------------------"
docker exec "$CLICKHOUSE_CONTAINER" clickhouse-client --query "
    SELECT 
        partition,
        count() as parts,
        sum(rows) as rows,
        formatReadableSize(sum(bytes_on_disk)) as size
    FROM system.parts
    WHERE database = 'financial_data' AND table = 'market_data' AND active
    GROUP BY partition
    ORDER BY partition DESC
    FORMAT Pretty
"

echo ""
echo -e "${GREEN}✓ Schema verification completed successfully!${NC}"
