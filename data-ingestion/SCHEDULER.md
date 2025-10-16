# Data Ingestion Scheduler Service

## Overview

The Data Ingestion Scheduler Service is a comprehensive solution for automated, reliable financial data ingestion from Yahoo Finance into ClickHouse. It provides configurable scheduling, retry strategies, and alert mechanisms for robust data pipeline operations.

## Features

### 1. Dual Schedule Support
- **Daily Ingestion**: End-of-day data updates (default: 6 PM after market close)
- **Intraday Ingestion**: Real-time quote updates during market hours (default: every 15 minutes)

### 2. Intelligent Retry Strategy
- Automatic retry on transient failures
- Exponential backoff to handle rate limiting
- Configurable retry attempts, delays, and multipliers
- Recovery methods when all retries are exhausted

### 3. Alert Logging
- Separate alert logger for critical failures
- Tracks consecutive failures across runs
- Configurable threshold for alerting
- Integration-ready for external monitoring systems

### 4. Configuration-Driven Design
All aspects of the scheduler are configurable via `application.yml`:
- Schedule timing (cron expressions)
- Enable/disable individual schedules
- Retry parameters
- Alert thresholds
- Symbol lists

## Architecture

```
SchedulerService
├── scheduledDailyIngestion()      - Daily historical data updates
├── scheduledIntradayIngestion()   - Intraday quote updates
├── recoverDailyIngestion()        - Recovery handler for daily failures
└── recoverIntradayIngestion()     - Recovery handler for intraday failures

DataIngestionService
├── ingestHistoricalDataBatch()    - Batch historical data ingestion
└── ingestCurrentQuote()           - Current quote ingestion
```

## Configuration

### Basic Configuration

```yaml
ingestion:
  symbols: AAPL,GOOGL,MSFT,AMZN,TSLA,META,NVDA,NFLX
  history:
    days: 30
```

### Schedule Configuration

```yaml
ingestion:
  schedule:
    daily:
      cron: "0 0 18 * * ?"        # Daily at 6 PM
      enabled: true
    intraday:
      cron: "0 */15 9-16 * * MON-FRI"  # Every 15 min, 9 AM-4 PM, Mon-Fri
      enabled: true
```

#### Common Cron Expressions

| Expression | Description |
|-----------|-------------|
| `0 0 18 * * ?` | Daily at 6:00 PM |
| `0 0 9 * * MON-FRI` | Weekdays at 9:00 AM |
| `0 */15 9-16 * * MON-FRI` | Every 15 min, 9 AM-4 PM, Mon-Fri |
| `0 0 */4 * * ?` | Every 4 hours |
| `0 30 9,15 * * MON-FRI` | Weekdays at 9:30 AM and 3:30 PM |

### Retry Configuration

```yaml
ingestion:
  retry:
    maxAttempts: 3              # Maximum retry attempts per failure
    backoffDelay: 2000          # Initial backoff delay (ms)
    maxBackoffDelay: 10000      # Maximum backoff delay (ms)
    multiplier: 2.0             # Backoff multiplier
```

**Retry Behavior Example:**
- Attempt 1: Immediate
- Attempt 2: After 2 seconds
- Attempt 3: After 4 seconds (2s × 2.0)
- Failure: After 8 seconds (4s × 2.0, capped at 10s)

### Alert Configuration

```yaml
ingestion:
  alert:
    enabled: true
    threshold: 3  # Alert after N consecutive failures
```

## Usage Examples

### Enabling/Disabling Schedules

Disable intraday updates outside of market hours:
```yaml
ingestion:
  schedule:
    daily:
      enabled: true
    intraday:
      enabled: false  # Disable intraday updates
```

### Adjusting for Different Time Zones

For a different market (e.g., LSE - London Stock Exchange):
```yaml
ingestion:
  schedule:
    daily:
      cron: "0 30 16 * * MON-FRI"  # 4:30 PM GMT (LSE close)
    intraday:
      cron: "0 */10 8-16 * * MON-FRI"  # Every 10 min, 8 AM-4 PM GMT
```

### Conservative Retry Settings

For less aggressive retries:
```yaml
ingestion:
  retry:
    maxAttempts: 2
    backoffDelay: 5000
    maxBackoffDelay: 30000
    multiplier: 3.0
```

## Monitoring

### Log Levels

The service produces logs at different levels:

- **INFO**: Normal operations
  ```
  [DAILY INGESTION] Starting daily data ingestion at 2025-10-16T18:00:00
  [DAILY INGESTION] Successfully completed. Total records ingested: 560
  ```

- **WARN**: Partial failures
  ```
  [INTRADAY INGESTION] Error ingesting quote for AAPL: Connection timeout
  ```

- **ERROR**: Complete failures
  ```
  [DAILY INGESTION] Failed at 2025-10-16T18:00:00: Network error
  ```

- **ALERT.ERROR**: Critical failures
  ```
  ALERT: Daily ingestion has failed 3 consecutive times. Last error: Database unavailable
  CRITICAL ALERT: Daily ingestion failed after all retry attempts. Error: Network timeout
  ```

### Monitoring Endpoints

The service exposes health monitoring methods:

```java
@Autowired
private SchedulerService schedulerService;

// Get consecutive failure count
int failures = schedulerService.getConsecutiveFailures();

// Reset after manual intervention
schedulerService.resetConsecutiveFailures();
```

These can be exposed via Spring Boot Actuator:

```java
@RestController
@RequestMapping("/actuator/scheduler")
public class SchedulerHealthController {
    
    @Autowired
    private SchedulerService schedulerService;
    
    @GetMapping("/health")
    public Map<String, Object> health() {
        return Map.of(
            "consecutiveFailures", schedulerService.getConsecutiveFailures(),
            "status", schedulerService.getConsecutiveFailures() > 0 ? "DEGRADED" : "UP"
        );
    }
    
    @PostMapping("/reset")
    public void reset() {
        schedulerService.resetConsecutiveFailures();
    }
}
```

### Alert Integration

Configure the ALERT logger to send notifications:

**Logback Configuration (logback-spring.xml):**
```xml
<!-- Alert appender for Slack/email/monitoring system -->
<appender name="ALERT" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <file>logs/alerts.log</file>
    <encoder>
        <pattern>%d{yyyy-MM-dd HH:mm:ss} [ALERT] %msg%n</pattern>
    </encoder>
</appender>

<logger name="ALERT" level="ERROR" additivity="false">
    <appender-ref ref="ALERT" />
    <appender-ref ref="CONSOLE" />
</logger>
```

## Troubleshooting

### Issue: Scheduler not running

**Symptoms:** No log entries for scheduled tasks

**Solutions:**
1. Verify `@EnableScheduling` is present in `DataIngestionApplication`
2. Check schedule configuration:
   ```yaml
   ingestion:
     schedule:
       daily:
         enabled: true  # Must be true
   ```
3. Verify cron expression syntax
4. Check application logs for startup errors

### Issue: Frequent failures and retries

**Symptoms:** High number of retry attempts, alert logs

**Solutions:**
1. Check network connectivity to Yahoo Finance
2. Verify ClickHouse database is running and accessible
3. Review rate limiting settings
4. Adjust retry parameters:
   ```yaml
   ingestion:
     retry:
       maxAttempts: 5  # Increase attempts
       backoffDelay: 5000  # Longer initial delay
   ```

### Issue: Missing data for specific symbols

**Symptoms:** Some symbols succeed, others consistently fail

**Solutions:**
1. Check symbol validity on Yahoo Finance
2. Review logs for specific symbol errors
3. Update symbol list in configuration:
   ```yaml
   ingestion:
     symbols: AAPL,GOOGL,MSFT  # Remove invalid symbols
   ```

### Issue: Intraday updates during off-market hours

**Symptoms:** Intraday ingestion running outside market hours

**Solutions:**
1. Adjust cron expression to match market hours:
   ```yaml
   ingestion:
     schedule:
       intraday:
         cron: "0 */15 9-16 * * MON-FRI"  # 9 AM - 4 PM, Mon-Fri
   ```
2. Consider time zones if running on servers in different regions

## Testing

The service includes comprehensive unit tests:

```bash
./gradlew :data-ingestion:test --tests SchedulerServiceTest
```

**Test Coverage:**
- ✅ Daily ingestion success and failure scenarios
- ✅ Intraday ingestion with partial/complete failures
- ✅ Retry behavior and consecutive failure tracking
- ✅ Recovery methods
- ✅ Alert threshold handling

## Performance Considerations

### Batch Size
For large symbol lists, consider:
- Breaking into smaller batches
- Adjusting delays between symbol ingestions
- Using separate schedules for different symbol groups

### Database Load
- Daily ingestion: ~7 days × symbols count × 1 record = moderate load
- Intraday ingestion: symbols count × 1 record every 15 min = continuous low load

### Rate Limiting
- Built-in 1-second delay between symbols in daily ingestion
- 200ms delay between symbols in intraday ingestion
- Yahoo Finance API rate limits apply

## Best Practices

1. **Start Conservative**: Begin with fewer symbols and longer intervals
2. **Monitor Alerts**: Set up proper alert routing for ALERT logs
3. **Regular Reviews**: Check logs weekly for patterns
4. **Backup Schedules**: Keep daily ingestion even with intraday updates
5. **Test Configuration**: Use `@ConditionalOnProperty` to test in non-prod environments
6. **Time Zone Awareness**: Configure schedules according to target market hours

## Version History

### v1.0.0 (Current)
- ✅ Daily and intraday scheduling
- ✅ Retry strategy with exponential backoff
- ✅ Alert logging with thresholds
- ✅ Configurable via application properties
- ✅ Comprehensive test coverage
- ✅ Java 21 support
- ✅ Gradle 8.10.2 support

## Future Enhancements

- [ ] Dynamic symbol list updates without restart
- [ ] Per-symbol retry configuration
- [ ] Historical backfill on-demand triggers
- [ ] Webhook integration for alerts
- [ ] Metrics export (Prometheus/Micrometer)
- [ ] Circuit breaker pattern for external service calls
- [ ] Distributed scheduling (Quartz/ShedLock) for multi-instance deployments
