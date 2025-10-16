package com.financial.analytics.api.service;

import com.financial.analytics.api.exception.RateLimitExceededException;
import com.financial.analytics.api.exception.YahooFinanceException;
import com.financial.analytics.api.model.HistoricalQuote;
import com.financial.analytics.api.model.StockQuote;
import io.github.resilience4j.ratelimiter.RateLimiter;
import io.github.resilience4j.ratelimiter.RequestNotPermitted;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import yahoofinance.Stock;
import yahoofinance.YahooFinance;
import yahoofinance.histquotes.Interval;

import java.io.IOException;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Service for fetching stock data from Yahoo Finance API
 * Includes rate limiting and comprehensive error handling
 */
@Service
public class YahooFinanceService {
    
    private static final Logger logger = LoggerFactory.getLogger(YahooFinanceService.class);
    
    private final RateLimiter rateLimiter;
    
    public YahooFinanceService(RateLimiter yahooFinanceRateLimiter) {
        this.rateLimiter = yahooFinanceRateLimiter;
    }
    
    /**
     * Fetch real-time quote for a stock symbol
     * 
     * @param symbol Stock symbol (e.g., "AAPL")
     * @return StockQuote with current data
     * @throws YahooFinanceException if API call fails
     * @throws RateLimitExceededException if rate limit is exceeded
     */
    public StockQuote getStockQuote(String symbol) {
        logger.info("Fetching stock quote for symbol: {}", symbol);
        
        try {
            return rateLimiter.executeSupplier(() -> {
                try {
                    Stock stock = YahooFinance.get(symbol);
                    
                    if (stock == null || stock.getQuote() == null) {
                        throw new YahooFinanceException("No data available for symbol: " + symbol);
                    }
                    
                    return convertToStockQuote(stock);
                    
                } catch (IOException e) {
                    logger.error("Error fetching stock quote for {}: {}", symbol, e.getMessage());
                    throw new YahooFinanceException("Failed to fetch stock quote for " + symbol, e);
                }
            });
        } catch (RequestNotPermitted e) {
            logger.warn("Rate limit exceeded for symbol: {}", symbol);
            throw new RateLimitExceededException("Rate limit exceeded. Please try again later.");
        }
    }
    
    /**
     * Fetch historical quotes for a stock symbol
     * 
     * @param symbol Stock symbol
     * @param from Start date
     * @param to End date
     * @param interval Data interval (DAILY, WEEKLY, MONTHLY)
     * @return List of historical quotes
     * @throws YahooFinanceException if API call fails
     * @throws RateLimitExceededException if rate limit is exceeded
     */
    public List<HistoricalQuote> getHistoricalQuotes(
            String symbol, Calendar from, Calendar to, Interval interval) {
        
        logger.info("Fetching historical quotes for symbol: {} from {} to {}", 
                    symbol, from.getTime(), to.getTime());
        
        try {
            return rateLimiter.executeSupplier(() -> {
                try {
                    Stock stock = YahooFinance.get(symbol, from, to, interval);
                    
                    if (stock == null || stock.getHistory() == null) {
                        throw new YahooFinanceException("No historical data available for symbol: " + symbol);
                    }
                    
                    return stock.getHistory().stream()
                            .map(hq -> convertToHistoricalQuote(symbol, hq))
                            .collect(Collectors.toList());
                    
                } catch (IOException e) {
                    logger.error("Error fetching historical quotes for {}: {}", symbol, e.getMessage());
                    throw new YahooFinanceException("Failed to fetch historical quotes for " + symbol, e);
                }
            });
        } catch (RequestNotPermitted e) {
            logger.warn("Rate limit exceeded for symbol: {}", symbol);
            throw new RateLimitExceededException("Rate limit exceeded. Please try again later.");
        }
    }
    
    /**
     * Fetch quotes for multiple symbols in one call
     * 
     * @param symbols Array of stock symbols
     * @return List of stock quotes
     * @throws YahooFinanceException if API call fails
     * @throws RateLimitExceededException if rate limit is exceeded
     */
    public List<StockQuote> getMultipleQuotes(String[] symbols) {
        logger.info("Fetching quotes for {} symbols", symbols.length);
        
        try {
            return rateLimiter.executeSupplier(() -> {
                try {
                    java.util.Map<String, Stock> stocks = YahooFinance.get(symbols);
                    
                    List<StockQuote> quotes = new ArrayList<>();
                    for (Stock stock : stocks.values()) {
                        if (stock != null && stock.getQuote() != null) {
                            quotes.add(convertToStockQuote(stock));
                        }
                    }
                    
                    return quotes;
                    
                } catch (IOException e) {
                    logger.error("Error fetching multiple quotes: {}", e.getMessage());
                    throw new YahooFinanceException("Failed to fetch multiple quotes", e);
                }
            });
        } catch (RequestNotPermitted e) {
            logger.warn("Rate limit exceeded for multiple quotes request");
            throw new RateLimitExceededException("Rate limit exceeded. Please try again later.");
        }
    }
    
    /**
     * Convert Yahoo Finance Stock to our StockQuote model
     */
    private StockQuote convertToStockQuote(Stock stock) {
        yahoofinance.quotes.stock.StockQuote yQuote = stock.getQuote();
        
        StockQuote quote = new StockQuote();
        
        quote.setSymbol(stock.getSymbol());
        quote.setName(stock.getName());
        quote.setPrice(yQuote.getPrice());
        quote.setChange(yQuote.getChange());
        quote.setChangeInPercent(yQuote.getChangeInPercent());
        quote.setDayHigh(yQuote.getDayHigh());
        quote.setDayLow(yQuote.getDayLow());
        quote.setOpen(yQuote.getOpen());
        quote.setPreviousClose(yQuote.getPreviousClose());
        quote.setVolume(yQuote.getVolume());
        
        if (yQuote.getLastTradeTime() != null) {
            quote.setTimestamp(LocalDateTime.ofInstant(
                    yQuote.getLastTradeTime().toInstant(), 
                    ZoneId.systemDefault()));
        }
        
        return quote;
    }
    
    /**
     * Convert Yahoo Finance HistoricalQuote to our HistoricalQuote model
     */
    private HistoricalQuote convertToHistoricalQuote(
            String symbol, yahoofinance.histquotes.HistoricalQuote yQuote) {
        
        LocalDateTime timestamp = LocalDateTime.ofInstant(
                yQuote.getDate().toInstant(), 
                ZoneId.systemDefault());
        
        return new HistoricalQuote(
                symbol,
                timestamp,
                yQuote.getOpen(),
                yQuote.getHigh(),
                yQuote.getLow(),
                yQuote.getClose(),
                yQuote.getVolume(),
                yQuote.getAdjClose()
        );
    }
}
