#!/bin/bash

# Market Data API Testing Script (NSE/nsemine version)
# This script demonstrates how to test the market data API endpoints
# Prerequisites: Django server running and ClickHouse populated with NSE data

BASE_URL="http://localhost:8000"
API_URL="${BASE_URL}/api/marketdata"

echo "========================================"
echo "Market Data API Testing Script (NSE)"
echo "========================================"
echo ""

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test an endpoint
test_endpoint() {
    local name=$1
    local endpoint=$2
    echo -e "${BLUE}Testing: ${name}${NC}"
    echo -e "${YELLOW}curl ${endpoint}${NC}"
    curl -s "${endpoint}" | jq '.' || echo "Failed or no data"
    echo ""
    echo "----------------------------------------"
    echo ""
}

# 1. Test symbols endpoint (NSE tickers)
echo -e "${GREEN}1. Get All Symbols (NSE Tickers)${NC}"
test_endpoint "List all NSE symbols" "${API_URL}/symbols/"

# 2. Test symbols with pagination
echo -e "${GREEN}2. Get Symbols with Pagination${NC}"
test_endpoint "Symbols page 1, 5 per page" "${API_URL}/symbols/?page=1&per_page=5"

# 3. Test market data for a specific symbol (default date range) - Use NSE ticker
echo -e "${GREEN}3. Get Market Data for Symbol (Default Dates)${NC}"
test_endpoint "INFY market data (last 30 days)" "${API_URL}/INFY/"

# 4. Test market data with date range
echo -e "${GREEN}4. Get Market Data with Date Range${NC}"
FROM_DATE=$(date -d "30 days ago" +%Y-%m-%d)
TO_DATE=$(date +%Y-%m-%d)
test_endpoint "TCS from ${FROM_DATE} to ${TO_DATE}" "${API_URL}/TCS/?from=${FROM_DATE}&to=${TO_DATE}"

# 5. Test market data with pagination
echo -e "${GREEN}5. Get Market Data with Pagination${NC}"
test_endpoint "INFY page 1, 10 per page" "${API_URL}/INFY/?from=${FROM_DATE}&to=${TO_DATE}&page=1&per_page=10"

# 6. Test latest market data for all symbols
echo -e "${GREEN}6. Get Latest Market Data (All Symbols)${NC}"
test_endpoint "Latest data for all symbols" "${API_URL}/latest/"

# 7. Test latest market data for specific symbols (NSE tickers)
echo -e "${GREEN}7. Get Latest Market Data (Specific Symbols)${NC}"
test_endpoint "Latest data for INFY,TCS,RELIANCE" "${API_URL}/latest/?symbols=INFY,TCS,RELIANCE"

# 8. Test latest market data with pagination
echo -e "${GREEN}8. Get Latest Market Data with Pagination${NC}"
test_endpoint "Latest data page 1, 3 per page" "${API_URL}/latest/?page=1&per_page=3"

# 9. Test parallel processing (new feature)
echo -e "${GREEN}9. Test Parallel Processing for Latest Data${NC}"
test_endpoint "Latest data with parallel=true" "${API_URL}/latest/?symbols=INFY,TCS,RELIANCE,HDFCBANK,ICICIBANK&parallel=true"

# 10. Test error handling - invalid date format
echo -e "${GREEN}10. Test Error Handling - Invalid Date${NC}"
echo -e "${BLUE}Testing: Invalid date format${NC}"
echo -e "${YELLOW}curl ${API_URL}/INFY/?from=invalid-date${NC}"
RESPONSE=$(curl -s "${API_URL}/INFY/?from=invalid-date")
echo "$RESPONSE" | jq '.'
if echo "$RESPONSE" | grep -q "error"; then
    echo -e "${GREEN}✓ Error handling works correctly${NC}"
else
    echo -e "${YELLOW}⚠ Unexpected response${NC}"
fi
echo ""
echo "----------------------------------------"
echo ""

# 11. Test error handling - invalid date range
echo -e "${GREEN}11. Test Error Handling - Invalid Date Range${NC}"
echo -e "${BLUE}Testing: From date after to date${NC}"
echo -e "${YELLOW}curl ${API_URL}/INFY/?from=2024-12-31&to=2024-01-01${NC}"
RESPONSE=$(curl -s "${API_URL}/INFY/?from=2024-12-31&to=2024-01-01")
echo "$RESPONSE" | jq '.'
if echo "$RESPONSE" | grep -q "Invalid date range"; then
    echo -e "${GREEN}✓ Date range validation works correctly${NC}"
else
    echo -e "${YELLOW}⚠ Unexpected response${NC}"
fi
echo ""
echo "----------------------------------------"
echo ""

echo -e "${GREEN}Testing Complete!${NC}"
echo ""
echo "Summary:"
echo "- Symbols endpoint: GET /api/marketdata/symbols/ (NSE tickers from eq_masters)"
echo "- Market data by ticker: GET /api/marketdata/:ticker/ (OHLCV from eq_ohlcv)"
echo "- Latest market data: GET /api/marketdata/latest/ (with parallel processing support)"
echo ""
echo "All endpoints support pagination with 'page' and 'per_page' parameters"
echo "Symbol endpoint supports date filtering with 'from' and 'to' parameters"
echo "Latest endpoint supports 'parallel' parameter for concurrent fetching"
echo ""
echo "For complete documentation, see MARKETDATA_API.md"
