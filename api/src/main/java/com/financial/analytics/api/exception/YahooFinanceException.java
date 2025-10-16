package com.financial.analytics.api.exception;

/**
 * Exception thrown when Yahoo Finance API fails
 */
public class YahooFinanceException extends RuntimeException {
    
    public YahooFinanceException(String message) {
        super(message);
    }
    
    public YahooFinanceException(String message, Throwable cause) {
        super(message, cause);
    }
}
