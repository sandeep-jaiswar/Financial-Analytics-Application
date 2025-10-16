#!/bin/bash

# ClickHouse Schema Initialization Script
# This script initializes the ClickHouse database schema for the Financial Analytics Application

set -e

# Configuration
CLICKHOUSE_HOST="${CLICKHOUSE_HOST:-localhost}"
CLICKHOUSE_PORT="${CLICKHOUSE_PORT:-9000}"
CLICKHOUSE_USER="${CLICKHOUSE_USER:-default}"
CLICKHOUSE_PASSWORD="${CLICKHOUSE_PASSWORD:-}"
SCHEMA_DIR="$(dirname "$0")/schema"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "ClickHouse Schema Initialization"
echo "=========================================="
echo ""

# Function to check if ClickHouse is available
check_clickhouse() {
    echo -n "Checking ClickHouse connection... "
    if clickhouse-client --host "$CLICKHOUSE_HOST" --port "$CLICKHOUSE_PORT" --user "$CLICKHOUSE_USER" ${CLICKHOUSE_PASSWORD:+--password "$CLICKHOUSE_PASSWORD"} --query "SELECT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        return 1
    fi
}

# Function to run SQL file
run_sql_file() {
    local file=$1
    local filename=$(basename "$file")
    
    echo -n "Running $filename... "
    if clickhouse-client --host "$CLICKHOUSE_HOST" --port "$CLICKHOUSE_PORT" --user "$CLICKHOUSE_USER" ${CLICKHOUSE_PASSWORD:+--password "$CLICKHOUSE_PASSWORD"} --multiquery < "$file" > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        return 1
    fi
}

# Function to verify schema
verify_schema() {
    echo ""
    echo "Verifying schema..."
    echo ""
    
    # Check database
    echo -n "  - Database 'financial_data': "
    if clickhouse-client --host "$CLICKHOUSE_HOST" --port "$CLICKHOUSE_PORT" --user "$CLICKHOUSE_USER" ${CLICKHOUSE_PASSWORD:+--password "$CLICKHOUSE_PASSWORD"} --query "EXISTS DATABASE financial_data" | grep -q 1; then
        echo -e "${GREEN}EXISTS${NC}"
    else
        echo -e "${RED}NOT FOUND${NC}"
        return 1
    fi
    
    # Check market_data table
    echo -n "  - Table 'market_data': "
    if clickhouse-client --host "$CLICKHOUSE_HOST" --port "$CLICKHOUSE_PORT" --user "$CLICKHOUSE_USER" ${CLICKHOUSE_PASSWORD:+--password "$CLICKHOUSE_PASSWORD"} --query "EXISTS TABLE financial_data.market_data" | grep -q 1; then
        echo -e "${GREEN}EXISTS${NC}"
    else
        echo -e "${RED}NOT FOUND${NC}"
        return 1
    fi
    
    echo ""
    echo "Schema verification completed successfully!"
    return 0
}

# Function to show table info
show_table_info() {
    echo ""
    echo "=========================================="
    echo "Table Information"
    echo "=========================================="
    echo ""
    
    echo "Structure of market_data table:"
    clickhouse-client --host "$CLICKHOUSE_HOST" --port "$CLICKHOUSE_PORT" --user "$CLICKHOUSE_USER" ${CLICKHOUSE_PASSWORD:+--password "$CLICKHOUSE_PASSWORD"} --query "DESCRIBE financial_data.market_data" --format PrettyCompact
    
    echo ""
    echo "Table engine and settings:"
    clickhouse-client --host "$CLICKHOUSE_HOST" --port "$CLICKHOUSE_PORT" --user "$CLICKHOUSE_USER" ${CLICKHOUSE_PASSWORD:+--password "$CLICKHOUSE_PASSWORD"} --query "SHOW CREATE TABLE financial_data.market_data" --format PrettyCompact
}

# Main execution
main() {
    # Check if ClickHouse is available
    if ! check_clickhouse; then
        echo -e "${RED}Error: Cannot connect to ClickHouse at $CLICKHOUSE_HOST:$CLICKHOUSE_PORT${NC}"
        echo "Please ensure ClickHouse is running and accessible."
        exit 1
    fi
    
    echo ""
    echo "Initializing schema..."
    echo ""
    
    # Run migration scripts in order
    if [ -d "$SCHEMA_DIR" ]; then
        for sql_file in "$SCHEMA_DIR"/*.sql; do
            if [ -f "$sql_file" ]; then
                # Skip replicated schema by default (use environment variable to enable)
                if [[ "$sql_file" == *"replicated"* ]] && [ "${USE_REPLICATION:-false}" != "true" ]; then
                    echo -e "Skipping $(basename "$sql_file") ${YELLOW}(replication disabled)${NC}"
                    continue
                fi
                
                if ! run_sql_file "$sql_file"; then
                    echo -e "${RED}Error running $sql_file${NC}"
                    exit 1
                fi
            fi
        done
    else
        echo -e "${RED}Error: Schema directory not found: $SCHEMA_DIR${NC}"
        exit 1
    fi
    
    # Verify schema
    if verify_schema; then
        echo ""
        echo -e "${GREEN}✓ Schema initialization completed successfully!${NC}"
        
        # Show table info
        show_table_info
    else
        echo -e "${RED}✗ Schema verification failed!${NC}"
        exit 1
    fi
}

# Run main function
main
