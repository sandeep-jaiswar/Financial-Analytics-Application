package com.financial.analytics.api.service;

import com.financial.analytics.api.exception.RateLimitExceededException;
import com.financial.analytics.api.model.StockQuote;
import io.github.resilience4j.ratelimiter.RateLimiter;
import io.github.resilience4j.ratelimiter.RateLimiterConfig;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Duration;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for YahooFinanceService
 * Note: These tests may require network access to Yahoo Finance API
 */
class YahooFinanceServiceTest {
    
    private YahooFinanceService service;
    private RateLimiter rateLimiter;
    
    @BeforeEach
    void setUp() {
        // Create a rate limiter with generous limits for testing
        RateLimiterConfig config = RateLimiterConfig.custom()
                .limitForPeriod(10)
                .limitRefreshPeriod(Duration.ofSeconds(1))
                .timeoutDuration(Duration.ofSeconds(5))
                .build();
        
        rateLimiter = RateLimiter.of("test", config);
        service = new YahooFinanceService(rateLimiter);
    }
    
    @Test
    void testServiceInitialization() {
        // Test that service is properly initialized
        assertNotNull(service);
        assertNotNull(rateLimiter);
    }
    
    @Test
    void testStockQuoteModel() {
        // Test StockQuote model creation
        StockQuote quote = new StockQuote();
        quote.setSymbol("AAPL");
        quote.setName("Apple Inc.");
        
        assertEquals("AAPL", quote.getSymbol());
        assertEquals("Apple Inc.", quote.getName());
    }
    
    @Test
    void testRateLimiterConfiguration() {
        // Create a strict rate limiter for testing
        RateLimiterConfig strictConfig = RateLimiterConfig.custom()
                .limitForPeriod(1)
                .limitRefreshPeriod(Duration.ofSeconds(10))
                .timeoutDuration(Duration.ofMillis(100))
                .build();
        
        RateLimiter strictLimiter = RateLimiter.of("strict", strictConfig);
        
        // Verify rate limiter is configured correctly
        assertNotNull(strictLimiter);
        assertEquals("strict", strictLimiter.getName());
    }
}
