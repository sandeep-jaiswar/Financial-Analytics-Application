package com.financial.analytics.api.controller;

import com.financial.analytics.api.exception.RateLimitExceededException;
import com.financial.analytics.api.exception.YahooFinanceException;
import com.financial.analytics.api.model.HistoricalQuote;
import com.financial.analytics.api.model.StockQuote;
import com.financial.analytics.api.service.YahooFinanceService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import yahoofinance.histquotes.Interval;

import java.util.*;

/**
 * REST controller for Yahoo Finance API endpoints
 */
@RestController
@RequestMapping("/api/stocks")
public class StockController {
    
    private static final Logger logger = LoggerFactory.getLogger(StockController.class);
    
    private final YahooFinanceService yahooFinanceService;
    
    public StockController(YahooFinanceService yahooFinanceService) {
        this.yahooFinanceService = yahooFinanceService;
    }
    
    /**
     * GET /api/stocks/{symbol}/quote - Get real-time quote for a symbol
     */
    @GetMapping("/{symbol}/quote")
    public ResponseEntity<StockQuote> getQuote(@PathVariable String symbol) {
        try {
            StockQuote quote = yahooFinanceService.getStockQuote(symbol.toUpperCase());
            return ResponseEntity.ok(quote);
        } catch (YahooFinanceException e) {
            logger.error("Error fetching quote: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        } catch (RateLimitExceededException e) {
            logger.warn("Rate limit exceeded: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).build();
        }
    }
    
    /**
     * GET /api/stocks/{symbol}/history - Get historical quotes
     * Query params: from (date), to (date), interval (DAILY/WEEKLY/MONTHLY)
     */
    @GetMapping("/{symbol}/history")
    public ResponseEntity<List<HistoricalQuote>> getHistory(
            @PathVariable String symbol,
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd") Date from,
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd") Date to,
            @RequestParam(defaultValue = "DAILY") String interval) {
        
        try {
            Calendar calFrom = Calendar.getInstance();
            calFrom.setTime(from);
            
            Calendar calTo = Calendar.getInstance();
            calTo.setTime(to);
            
            Interval intervalEnum = Interval.valueOf(interval.toUpperCase());
            
            List<HistoricalQuote> quotes = yahooFinanceService.getHistoricalQuotes(
                    symbol.toUpperCase(), calFrom, calTo, intervalEnum);
            
            return ResponseEntity.ok(quotes);
        } catch (IllegalArgumentException e) {
            logger.error("Invalid interval: {}", interval);
            return ResponseEntity.badRequest().build();
        } catch (YahooFinanceException e) {
            logger.error("Error fetching history: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        } catch (RateLimitExceededException e) {
            logger.warn("Rate limit exceeded: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).build();
        }
    }
    
    /**
     * POST /api/stocks/quotes - Get quotes for multiple symbols
     * Request body: { "symbols": ["AAPL", "GOOGL", "MSFT"] }
     */
    @PostMapping("/quotes")
    public ResponseEntity<List<StockQuote>> getMultipleQuotes(
            @RequestBody Map<String, List<String>> request) {
        
        try {
            List<String> symbols = request.get("symbols");
            if (symbols == null || symbols.isEmpty()) {
                return ResponseEntity.badRequest().build();
            }
            
            String[] symbolArray = symbols.stream()
                    .map(String::toUpperCase)
                    .toArray(String[]::new);
            
            List<StockQuote> quotes = yahooFinanceService.getMultipleQuotes(symbolArray);
            return ResponseEntity.ok(quotes);
        } catch (YahooFinanceException e) {
            logger.error("Error fetching multiple quotes: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        } catch (RateLimitExceededException e) {
            logger.warn("Rate limit exceeded: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).build();
        }
    }
    
    /**
     * Exception handler for unhandled exceptions
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, String>> handleException(Exception e) {
        logger.error("Unhandled exception: {}", e.getMessage(), e);
        Map<String, String> error = new HashMap<>();
        error.put("error", "Internal server error");
        error.put("message", e.getMessage());
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}
