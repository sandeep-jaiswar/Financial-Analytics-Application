package com.financial.analytics.ingestion.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Recover;
import org.springframework.retry.annotation.Retryable;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Service for scheduling periodic data ingestion tasks
 * Implements daily and intraday data updates with retry strategy and alert logging
 */
@Service
public class SchedulerService {
    
    private static final Logger logger = LoggerFactory.getLogger(SchedulerService.class);
    private static final Logger alertLogger = LoggerFactory.getLogger("ALERT." + SchedulerService.class.getName());
    
    private final DataIngestionService dataIngestionService;
    
    @Value("${ingestion.symbols:AAPL,GOOGL,MSFT,AMZN,TSLA}")
    private String[] symbols;
    
    @Value("${ingestion.history.days:7}")
    private int historyDays;
    
    @Value("${ingestion.alert.enabled:true}")
    private boolean alertEnabled;
    
    @Value("${ingestion.alert.threshold:3}")
    private int alertThreshold;
    
    private int consecutiveFailures = 0;
    
    public SchedulerService(DataIngestionService dataIngestionService) {
        this.dataIngestionService = dataIngestionService;
    }
    
    /**
     * Daily scheduled task for end-of-day data ingestion
     * Runs at 6 PM by default (after market close)
     * Fetches last 7 days to catch up on any missed data
     */
    @Scheduled(cron = "${ingestion.schedule.daily.cron:0 0 18 * * ?}")
    @ConditionalOnProperty(name = "ingestion.schedule.daily.enabled", havingValue = "true", matchIfMissing = true)
    @Retryable(
        retryFor = {Exception.class},
        maxAttemptsExpression = "${ingestion.retry.maxAttempts:3}",
        backoff = @Backoff(
            delayExpression = "${ingestion.retry.backoffDelay:2000}",
            maxDelayExpression = "${ingestion.retry.maxBackoffDelay:10000}",
            multiplierExpression = "${ingestion.retry.multiplier:2.0}"
        )
    )
    public void scheduledDailyIngestion() {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        logger.info("[DAILY INGESTION] Starting daily data ingestion at {}", timestamp);
        
        try {
            int totalRecords = dataIngestionService.ingestHistoricalDataBatch(symbols, historyDays);
            
            logger.info("[DAILY INGESTION] Successfully completed. Total records ingested: {}", totalRecords);
            
            // Reset consecutive failures on success
            if (consecutiveFailures > 0) {
                logger.info("[DAILY INGESTION] Service recovered after {} consecutive failures", consecutiveFailures);
                consecutiveFailures = 0;
            }
            
        } catch (Exception e) {
            consecutiveFailures++;
            logger.error("[DAILY INGESTION] Failed at {}: {}", timestamp, e.getMessage(), e);
            
            // Alert if threshold is reached
            if (alertEnabled && consecutiveFailures >= alertThreshold) {
                alertLogger.error("ALERT: Daily ingestion has failed {} consecutive times. Last error: {}", 
                    consecutiveFailures, e.getMessage());
            }
            
            throw e; // Re-throw for retry mechanism
        }
    }
    
    /**
     * Intraday scheduled task for real-time quote ingestion
     * Runs every 15 minutes during market hours (9:30 AM - 4:00 PM EST)
     * Fetches current quotes for configured symbols
     */
    @Scheduled(cron = "${ingestion.schedule.intraday.cron:0 */15 9-16 * * MON-FRI}")
    @ConditionalOnProperty(name = "ingestion.schedule.intraday.enabled", havingValue = "true", matchIfMissing = true)
    @Retryable(
        retryFor = {Exception.class},
        maxAttemptsExpression = "${ingestion.retry.maxAttempts:3}",
        backoff = @Backoff(
            delayExpression = "${ingestion.retry.backoffDelay:2000}",
            maxDelayExpression = "${ingestion.retry.maxBackoffDelay:10000}",
            multiplierExpression = "${ingestion.retry.multiplier:2.0}"
        )
    )
    public void scheduledIntradayIngestion() {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        logger.info("[INTRADAY INGESTION] Starting intraday quote ingestion at {}", timestamp);
        
        try {
            int successCount = 0;
            int failureCount = 0;
            
            for (String symbol : symbols) {
                try {
                    boolean success = dataIngestionService.ingestCurrentQuote(symbol.trim());
                    if (success) {
                        successCount++;
                    } else {
                        failureCount++;
                    }
                    
                    // Brief delay to avoid rate limiting
                    Thread.sleep(200);
                    
                } catch (InterruptedException e) {
                    logger.warn("[INTRADAY INGESTION] Interrupted while ingesting {}", symbol);
                    Thread.currentThread().interrupt();
                    break;
                } catch (Exception e) {
                    logger.warn("[INTRADAY INGESTION] Error ingesting quote for {}: {}", symbol, e.getMessage());
                    failureCount++;
                }
            }
            
            logger.info("[INTRADAY INGESTION] Completed. Success: {}, Failures: {}", successCount, failureCount);
            
            // Alert if too many failures
            if (alertEnabled && failureCount > symbols.length / 2) {
                alertLogger.warn("ALERT: Intraday ingestion had high failure rate: {}/{} symbols failed", 
                    failureCount, symbols.length);
            }
            
        } catch (Exception e) {
            logger.error("[INTRADAY INGESTION] Failed at {}: {}", timestamp, e.getMessage(), e);
            
            if (alertEnabled) {
                alertLogger.error("ALERT: Intraday ingestion failed completely: {}", e.getMessage());
            }
            
            throw e; // Re-throw for retry mechanism
        }
    }
    
    /**
     * Recovery method called when all retry attempts are exhausted for daily ingestion
     */
    @Recover
    public void recoverDailyIngestion(Exception e) {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        logger.error("[DAILY INGESTION RECOVERY] All retry attempts exhausted at {}", timestamp);
        
        if (alertEnabled) {
            alertLogger.error("CRITICAL ALERT: Daily ingestion failed after all retry attempts. Error: {}", 
                e.getMessage());
        }
    }
    
    /**
     * Recovery method called when all retry attempts are exhausted for intraday ingestion
     */
    @Recover
    public void recoverIntradayIngestion(Exception e) {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        logger.error("[INTRADAY INGESTION RECOVERY] All retry attempts exhausted at {}", timestamp);
        
        if (alertEnabled) {
            alertLogger.error("CRITICAL ALERT: Intraday ingestion failed after all retry attempts. Error: {}", 
                e.getMessage());
        }
    }
    
    /**
     * Get the current count of consecutive failures
     * Useful for monitoring and health checks
     */
    public int getConsecutiveFailures() {
        return consecutiveFailures;
    }
    
    /**
     * Reset consecutive failure counter
     * Can be called after manual intervention
     */
    public void resetConsecutiveFailures() {
        logger.info("Resetting consecutive failures counter from {}", consecutiveFailures);
        consecutiveFailures = 0;
    }
}
