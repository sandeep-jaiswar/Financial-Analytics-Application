# Market Data REST API Documentation

This document provides information about the REST API endpoints for retrieving financial market data from ClickHouse.

## Base URL

All endpoints are prefixed with: `http://localhost:8000/api/marketdata/`

## Endpoints

### 1. Get All Symbols

Retrieves a list of all available stock symbols with metadata.

**Endpoint:** `GET /api/marketdata/symbols/`

**Query Parameters:**
- `page` (optional, default: 1): Page number for pagination
- `per_page` (optional, default: 50, max: 100): Number of items per page

**Response:**
```json
{
  "symbols": [
    {
      "symbol": "AAPL",
      "recordCount": 250,
      "firstDate": "2024-01-01",
      "lastDate": "2024-10-15"
    },
    {
      "symbol": "GOOGL",
      "recordCount": 250,
      "firstDate": "2024-01-01",
      "lastDate": "2024-10-15"
    }
  ],
  "pagination": {
    "page": 1,
    "perPage": 50,
    "totalItems": 8,
    "totalPages": 1,
    "hasNext": false,
    "hasPrev": false
  }
}
```

**Sample curl commands:**

```bash
# Get all symbols (first page, default pagination)
curl http://localhost:8000/api/marketdata/symbols/

# Get symbols with custom pagination
curl "http://localhost:8000/api/marketdata/symbols/?page=2&per_page=10"

# Get first page with 5 symbols per page
curl "http://localhost:8000/api/marketdata/symbols/?per_page=5"
```

---

### 2. Get Market Data by Symbol

Retrieves historical market data for a specific stock symbol.

**Endpoint:** `GET /api/marketdata/:symbol/`

**Path Parameters:**
- `symbol`: Stock ticker symbol (e.g., AAPL, GOOGL)

**Query Parameters:**
- `from` (optional, default: 30 days ago): Start date in YYYY-MM-DD format
- `to` (optional, default: today): End date in YYYY-MM-DD format
- `page` (optional, default: 1): Page number for pagination
- `per_page` (optional, default: 100, max: 1000): Number of items per page

**Response:**
```json
{
  "symbol": "AAPL",
  "data": [
    {
      "symbol": "AAPL",
      "timestamp": "2024-10-15T16:00:00",
      "date": "2024-10-15",
      "open": 150.25,
      "high": 152.50,
      "low": 149.80,
      "close": 151.75,
      "volume": 50000000,
      "adjustedClose": 151.75
    },
    {
      "symbol": "AAPL",
      "timestamp": "2024-10-14T16:00:00",
      "date": "2024-10-14",
      "open": 148.50,
      "high": 150.75,
      "low": 147.90,
      "close": 150.25,
      "volume": 48000000,
      "adjustedClose": 150.25
    }
  ],
  "dateRange": {
    "from": "2024-10-01",
    "to": "2024-10-31"
  },
  "pagination": {
    "page": 1,
    "perPage": 100,
    "totalItems": 22,
    "totalPages": 1,
    "hasNext": false,
    "hasPrev": false
  }
}
```

**Sample curl commands:**

```bash
# Get market data for AAPL (last 30 days by default)
curl http://localhost:8000/api/marketdata/AAPL/

# Get market data for specific date range
curl "http://localhost:8000/api/marketdata/AAPL/?from=2024-01-01&to=2024-01-31"

# Get market data with custom pagination
curl "http://localhost:8000/api/marketdata/AAPL/?from=2024-01-01&to=2024-12-31&page=1&per_page=50"

# Get recent data for GOOGL
curl "http://localhost:8000/api/marketdata/GOOGL/?from=2024-10-01&to=2024-10-15"

# Get market data for MSFT with pagination
curl "http://localhost:8000/api/marketdata/MSFT/?page=2&per_page=25"
```

---

### 3. Get Latest Market Data

Retrieves the most recent market data for all symbols or a specific set of symbols.

**Endpoint:** `GET /api/marketdata/latest/`

**Query Parameters:**
- `symbols` (optional): Comma-separated list of stock symbols (e.g., AAPL,GOOGL,MSFT)
- `page` (optional, default: 1): Page number for pagination
- `per_page` (optional, default: 50, max: 100): Number of items per page

**Response:**
```json
{
  "data": [
    {
      "symbol": "AAPL",
      "timestamp": "2024-10-15T16:00:00",
      "date": "2024-10-15",
      "open": 150.25,
      "high": 152.50,
      "low": 149.80,
      "close": 151.75,
      "volume": 50000000,
      "adjustedClose": 151.75
    },
    {
      "symbol": "GOOGL",
      "timestamp": "2024-10-15T16:00:00",
      "date": "2024-10-15",
      "open": 2800.00,
      "high": 2850.00,
      "low": 2790.00,
      "close": 2820.00,
      "volume": 2000000,
      "adjustedClose": 2820.00
    }
  ],
  "pagination": {
    "page": 1,
    "perPage": 50,
    "totalItems": 8,
    "totalPages": 1,
    "hasNext": false,
    "hasPrev": false
  }
}
```

**Sample curl commands:**

```bash
# Get latest data for all symbols
curl http://localhost:8000/api/marketdata/latest/

# Get latest data for specific symbols
curl "http://localhost:8000/api/marketdata/latest/?symbols=AAPL,GOOGL,MSFT"

# Get latest data for a single symbol
curl "http://localhost:8000/api/marketdata/latest/?symbols=AAPL"

# Get latest data with pagination
curl "http://localhost:8000/api/marketdata/latest/?page=1&per_page=10"

# Get latest data for multiple symbols with pagination
curl "http://localhost:8000/api/marketdata/latest/?symbols=AAPL,GOOGL,MSFT,AMZN,TSLA&per_page=3"
```

---

## Error Responses

All endpoints return standardized error responses:

**400 Bad Request:**
```json
{
  "error": "Invalid parameter",
  "message": "Use YYYY-MM-DD format for dates"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error",
  "message": "Connection to database failed"
}
```

---

## Pagination

All endpoints support pagination with consistent parameters:

- `page`: Page number (starts at 1)
- `per_page`: Number of items per page

Response includes a `pagination` object with:
- `page`: Current page number
- `perPage`: Items per page
- `totalItems`: Total number of items
- `totalPages`: Total number of pages
- `hasNext`: Boolean indicating if there's a next page
- `hasPrev`: Boolean indicating if there's a previous page

---

## Date Range Filtering

The `/api/marketdata/:symbol/` endpoint supports date range filtering:

- Dates must be in `YYYY-MM-DD` format
- `from` date must be before or equal to `to` date
- If not specified, defaults to the last 30 days

---

## Usage Examples

### Complete Workflow Example

```bash
# 1. Get all available symbols
curl http://localhost:8000/api/marketdata/symbols/

# 2. Get historical data for a specific symbol
curl "http://localhost:8000/api/marketdata/AAPL/?from=2024-09-01&to=2024-10-15"

# 3. Get latest quotes for a watchlist
curl "http://localhost:8000/api/marketdata/latest/?symbols=AAPL,GOOGL,MSFT,AMZN,TSLA"

# 4. Paginate through large result sets
curl "http://localhost:8000/api/marketdata/AAPL/?from=2024-01-01&to=2024-12-31&page=1&per_page=100"
curl "http://localhost:8000/api/marketdata/AAPL/?from=2024-01-01&to=2024-12-31&page=2&per_page=100"
```

### Scripting Example

```bash
#!/bin/bash

# Get latest prices for multiple symbols and save to file
SYMBOLS="AAPL,GOOGL,MSFT,AMZN,TSLA,META,NVDA,NFLX"
curl -s "http://localhost:8000/api/marketdata/latest/?symbols=${SYMBOLS}" | jq '.' > latest_prices.json

# Extract specific data using jq
curl -s "http://localhost:8000/api/marketdata/AAPL/?from=2024-10-01&to=2024-10-15" | \
  jq '.data[] | {date: .date, close: .close, volume: .volume}'
```

---

## Notes

- All timestamps are in UTC
- The API uses ClickHouse as the data source, optimized for analytical queries
- Data is stored with daily granularity by default
- Volume is returned as an integer
- Price fields (open, high, low, close, adjustedClose) are returned as floats
- Symbol lookups are case-insensitive but responses always return uppercase symbols

---

## Testing the API

Before using the API in production, ensure:

1. ClickHouse is running and accessible
2. The `market_data` table is created and populated
3. Environment variables are properly configured

You can verify the setup by:

```bash
# Check if the API is accessible
curl http://localhost:8000/api/marketdata/symbols/

# Verify data exists
curl "http://localhost:8000/api/marketdata/latest/?per_page=1"
```
