package com.financial.analytics.api.config;

import io.github.resilience4j.ratelimiter.RateLimiter;
import io.github.resilience4j.ratelimiter.RateLimiterConfig;
import io.github.resilience4j.ratelimiter.RateLimiterRegistry;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

/**
 * Configuration for rate limiting
 */
@Configuration
public class RateLimiterConfiguration {
    
    @Bean
    public RateLimiterRegistry rateLimiterRegistry() {
        return RateLimiterRegistry.ofDefaults();
    }
    
    @Bean
    public RateLimiter yahooFinanceRateLimiter(RateLimiterRegistry registry) {
        RateLimiterConfig config = RateLimiterConfig.custom()
                .limitForPeriod(5) // 5 requests
                .limitRefreshPeriod(Duration.ofSeconds(1)) // per second
                .timeoutDuration(Duration.ofSeconds(10)) // wait up to 10 seconds
                .build();
        
        return registry.rateLimiter("yahooFinance", config);
    }
}
