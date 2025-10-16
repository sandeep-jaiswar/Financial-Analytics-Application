# Yahoo Finance Data Connector Implementation

This implementation provides a complete data ingestion pipeline for fetching stock market data from Yahoo Finance API and storing it in ClickHouse.

## Features

### 1. Yahoo Finance Integration
- Real-time stock quotes
- Historical market data (OHLCV)
- Multi-symbol batch queries
- Support for daily, weekly, and monthly intervals

### 2. Rate Limiting
- Resilience4j rate limiter integration
- Configurable limits (default: 5 requests per second)
- Automatic rate limit enforcement
- Graceful handling of rate limit exceptions

### 3. Error Handling
- Custom exceptions: `YahooFinanceException`, `RateLimitExceededException`
- Comprehensive logging at all levels
- Retry logic through rate limiter
- Network failure handling

### 4. ClickHouse Persistence
- JDBC-based data storage
- Batch insert support
- Duplicate checking
- Date range queries
- Optimized for time-series data

### 5. Scheduled Ingestion
- Automatic daily data ingestion (6 PM by default)
- Intraday quote updates (every 15 minutes during market hours)
- Configurable symbols and history period
- Incremental updates
- Independent enable/disable for daily and intraday schedules

### 6. Retry Strategy
- Automatic retry on failures with exponential backoff
- Configurable retry attempts and delays
- Recovery methods for exhausted retries
- Alert logging for critical failures

### 7. Alert Logging
- Separate ALERT logger for critical issues
- Tracks consecutive failures
- Configurable failure threshold
- Proactive notification of service degradation

## Architecture

### API Module (`api`)
**Purpose**: REST API for Yahoo Finance integration

**Components**:
- `ApiApplication.java` - Spring Boot main class
- `YahooFinanceService.java` - Core service with rate limiting
- `StockController.java` - REST endpoints
- `StockQuote.java`, `HistoricalQuote.java` - Data models
- `RateLimiterConfiguration.java` - Rate limiter setup

**Endpoints**:
- `GET /api/stocks/{symbol}/quote` - Get real-time quote
- `GET /api/stocks/{symbol}/history?from=YYYY-MM-DD&to=YYYY-MM-DD&interval=DAILY` - Get historical data
- `POST /api/stocks/quotes` - Get multiple quotes (body: `{"symbols": ["AAPL", "GOOGL"]}`)

### Data Ingestion Module (`data-ingestion`)
**Purpose**: Fetch data from Yahoo Finance and persist to ClickHouse

**Components**:
- `DataIngestionApplication.java` - Spring Boot main class with scheduling and retry enabled
- `DataIngestionService.java` - Data fetching and ingestion logic
- `SchedulerService.java` - Scheduled task orchestration with retry and alerting
- `ClickHouseRepository.java` - Database operations
- `MarketData.java` - Entity model

**Features**:
- Scheduled ingestion (daily and intraday)
- Historical data backfill
- Current quote ingestion
- Batch processing
- Retry strategy with exponential backoff
- Alert logging for failures

## Configuration

### API Module (`api/src/main/resources/application.yml`)
```yaml
server:
  port: 8080

resilience4j:
  ratelimiter:
    instances:
      yahooFinance:
        limitForPeriod: 5
        limitRefreshPeriod: 1s
        timeoutDuration: 10s
```

### Data Ingestion Module (`data-ingestion/src/main/resources/application.yml`)
```yaml
server:
  port: 8081

clickhouse:
  url: jdbc:clickhouse://localhost:8123/financial_data
  username: default
  password: ""

ingestion:
  symbols: AAPL,GOOGL,MSFT,AMZN,TSLA,META,NVDA,NFLX
  history:
    days: 30
  schedule:
    # Daily update at 6 PM (after market close)
    daily:
      cron: "0 0 18 * * ?"
      enabled: true
    # Intraday updates every 15 minutes during market hours (9:30 AM - 4:00 PM EST)
    intraday:
      cron: "0 */15 9-16 * * MON-FRI"
      enabled: true
  retry:
    maxAttempts: 3
    backoffDelay: 2000  # milliseconds
    maxBackoffDelay: 10000  # milliseconds
    multiplier: 2.0
  alert:
    enabled: true
    threshold: 3  # Number of consecutive failures before alert
```

## Usage

### 1. Start ClickHouse
```bash
docker compose up -d clickhouse
```

### 2. Initialize Database Schema
```bash
./db/init-schema.sh
```

### 3. Run API Service
```bash
./gradlew :api:bootRun
```

### 4. Run Data Ingestion Service
```bash
./gradlew :data-ingestion:bootRun
```

### 5. Test API Endpoints

**Get real-time quote**:
```bash
curl http://localhost:8080/api/stocks/AAPL/quote
```

**Get historical data**:
```bash
curl "http://localhost:8080/api/stocks/AAPL/history?from=2024-01-01&to=2024-01-31&interval=DAILY"
```

**Get multiple quotes**:
```bash
curl -X POST http://localhost:8080/api/stocks/quotes \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "GOOGL", "MSFT"]}'
```

## Manual Data Ingestion

You can programmatically trigger data ingestion:

```java
@Autowired
private DataIngestionService ingestionService;

// Ingest historical data for a single symbol
ingestionService.ingestHistoricalData("AAPL", 30);

// Ingest current quote
ingestionService.ingestCurrentQuote("AAPL");

// Batch ingestion
String[] symbols = {"AAPL", "GOOGL", "MSFT"};
ingestionService.ingestHistoricalDataBatch(symbols, 30);
```

## Scheduler Configuration

The `SchedulerService` provides two types of scheduled ingestion:

### Daily Ingestion
- **Purpose**: Fetch end-of-day historical data
- **Default Schedule**: Daily at 6:00 PM (after market close)
- **Configuration**:
  ```yaml
  ingestion:
    schedule:
      daily:
        cron: "0 0 18 * * ?"  # Customize as needed
        enabled: true
  ```
- **Behavior**: Fetches last 7 days of data to catch up on any missed data

### Intraday Ingestion
- **Purpose**: Fetch real-time quotes during market hours
- **Default Schedule**: Every 15 minutes, Monday-Friday, 9:00 AM - 4:00 PM EST
- **Configuration**:
  ```yaml
  ingestion:
    schedule:
      intraday:
        cron: "0 */15 9-16 * * MON-FRI"  # Customize as needed
        enabled: true
  ```
- **Behavior**: Fetches current quotes for all configured symbols

### Retry Configuration
Both schedulers support automatic retry with exponential backoff:

```yaml
ingestion:
  retry:
    maxAttempts: 3              # Maximum retry attempts
    backoffDelay: 2000          # Initial delay in milliseconds
    maxBackoffDelay: 10000      # Maximum delay in milliseconds
    multiplier: 2.0             # Backoff multiplier
```

### Alert Configuration
Configure when alerts are triggered:

```yaml
ingestion:
  alert:
    enabled: true
    threshold: 3  # Alert after N consecutive failures
```

## Error Handling

The implementation includes comprehensive error handling:

1. **Network Failures**: Caught and logged with detailed error messages
2. **Invalid Symbols**: Returns `YahooFinanceException` with informative message
3. **Rate Limiting**: Returns HTTP 429 (Too Many Requests) when rate limit exceeded
4. **Database Errors**: Logged with context, operations continue for remaining records
5. **Retry Logic**: Automatic retry with exponential backoff for transient failures
6. **Alert Logging**: Critical failures are logged to a separate ALERT logger

### Alert Logger
A separate logger (`ALERT.SchedulerService`) is used for critical failures:
- Daily ingestion failures after threshold reached
- Intraday ingestion high failure rates (>50% symbols failed)
- Complete failures after all retry attempts exhausted

Configure alert logging in `logback.xml` or similar:
```xml
<logger name="ALERT" level="ERROR">
  <appender-ref ref="ALERT_FILE" />
  <!-- Or send to monitoring system, email, Slack, etc. -->
</logger>
```

## Testing

### Run Unit Tests
```bash
./gradlew test
```

### Test Coverage
- `YahooFinanceServiceTest` - Service initialization and model tests
- `ClickHouseRepositoryTest` - Repository logic tests
- `SchedulerServiceTest` - Scheduler service with 14 comprehensive test cases
  - Success and failure scenarios
  - Retry behavior
  - Alert thresholds
  - Recovery methods

Note: Integration tests requiring network access are simplified to avoid dependencies on external services.

## Dependencies

### Key Libraries
- **yahoofinance-api** (3.17.0) - Yahoo Finance data fetching
- **resilience4j** (2.1.0) - Rate limiting
- **spring-retry** (2.0.4) - Retry mechanism with exponential backoff
- **spring-aspects** (6.1.3) - AOP support for retry annotations
- **clickhouse-jdbc** (0.6.0) - ClickHouse database driver
- **Spring Boot** (3.2.2) - Application framework

## Migration from Kotlin to Java

All code has been refactored from Kotlin to Java as required:
- ✅ `ApiApplication.kt` → `ApiApplication.java`
- ✅ `DataIngestionApplication.kt` → `DataIngestionApplication.java`
- ✅ All service classes implemented in Java
- ✅ All model classes implemented in Java
- ✅ All test classes implemented in Java

## Monitoring and Logging

All operations are logged with appropriate levels:
- `INFO` - Normal operations (fetching data, saving records, scheduler execution)
- `WARN` - Rate limiting, invalid symbols, partial failures
- `ERROR` - Network failures, database errors, ingestion failures
- `ALERT.ERROR` - Critical failures (consecutive failures, exhausted retries)

Configure logging level in `application.yml`:
```yaml
logging:
  level:
    com.financial.analytics: INFO
    yahoofinance: WARN
    ALERT: ERROR  # Ensure alert logs are captured
```

### Monitoring Scheduler Health
The `SchedulerService` provides methods for health monitoring:
- `getConsecutiveFailures()` - Get current failure count
- `resetConsecutiveFailures()` - Reset counter after manual intervention

These can be exposed via Spring Boot Actuator for external monitoring.

## Future Enhancements

1. Add WebSocket support for real-time streaming quotes
2. Implement caching layer (Redis) for frequently accessed data
3. Add more comprehensive integration tests
4. Support for additional data sources (Alpha Vantage, Polygon.io)
5. Metrics and monitoring with Micrometer/Prometheus
6. Data quality validation and anomaly detection
