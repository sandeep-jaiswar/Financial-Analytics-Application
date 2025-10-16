package com.financial.analytics.ingestion.service;

import com.financial.analytics.ingestion.model.MarketData;
import com.financial.analytics.ingestion.repository.ClickHouseRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import yahoofinance.Stock;
import yahoofinance.YahooFinance;
import yahoofinance.histquotes.HistoricalQuote;
import yahoofinance.histquotes.Interval;

import java.io.IOException;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

/**
 * Service for ingesting market data from Yahoo Finance and storing in ClickHouse
 */
@Service
public class DataIngestionService {
    
    private static final Logger logger = LoggerFactory.getLogger(DataIngestionService.class);
    
    private final ClickHouseRepository repository;
    
    @Value("${ingestion.symbols:AAPL,GOOGL,MSFT,AMZN,TSLA}")
    private String[] symbols;
    
    @Value("${ingestion.history.days:30}")
    private int historyDays;
    
    public DataIngestionService(ClickHouseRepository repository) {
        this.repository = repository;
    }
    
    /**
     * Ingest historical data for a single symbol
     * 
     * @param symbol Stock symbol
     * @param days Number of days of history to fetch
     * @return Number of records saved
     */
    public int ingestHistoricalData(String symbol, int days) {
        logger.info("Starting historical data ingestion for {} ({} days)", symbol, days);
        
        try {
            Calendar to = Calendar.getInstance();
            Calendar from = Calendar.getInstance();
            from.add(Calendar.DAY_OF_YEAR, -days);
            
            Stock stock = YahooFinance.get(symbol, from, to, Interval.DAILY);
            
            if (stock == null || stock.getHistory() == null || stock.getHistory().isEmpty()) {
                logger.warn("No historical data available for {}", symbol);
                return 0;
            }
            
            List<MarketData> marketDataList = new ArrayList<>();
            
            for (HistoricalQuote quote : stock.getHistory()) {
                MarketData marketData = convertToMarketData(symbol, quote);
                marketDataList.add(marketData);
            }
            
            int savedCount = repository.saveBatch(marketDataList);
            logger.info("Ingested {} historical records for {}", savedCount, symbol);
            
            return savedCount;
            
        } catch (IOException e) {
            logger.error("Error fetching historical data for {}: {}", symbol, e.getMessage());
            return 0;
        }
    }
    
    /**
     * Ingest historical data for multiple symbols
     * 
     * @param symbols Array of stock symbols
     * @param days Number of days of history
     * @return Total number of records saved
     */
    public int ingestHistoricalDataBatch(String[] symbols, int days) {
        logger.info("Starting batch historical data ingestion for {} symbols", symbols.length);
        
        int totalSaved = 0;
        
        for (String symbol : symbols) {
            try {
                int saved = ingestHistoricalData(symbol.trim(), days);
                totalSaved += saved;
                
                // Sleep to avoid rate limiting
                Thread.sleep(1000);
                
            } catch (InterruptedException e) {
                logger.warn("Ingestion interrupted for {}", symbol);
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        logger.info("Batch ingestion complete. Total records saved: {}", totalSaved);
        return totalSaved;
    }
    
    /**
     * Ingest current/live quote for a symbol
     * 
     * @param symbol Stock symbol
     * @return true if saved successfully
     */
    public boolean ingestCurrentQuote(String symbol) {
        logger.info("Fetching current quote for {}", symbol);
        
        try {
            Stock stock = YahooFinance.get(symbol);
            
            if (stock == null || stock.getQuote() == null) {
                logger.warn("No quote available for {}", symbol);
                return false;
            }
            
            MarketData marketData = new MarketData();
            marketData.setSymbol(symbol);
            marketData.setTimestamp(LocalDateTime.now());
            marketData.setDate(LocalDate.now());
            marketData.setOpen(stock.getQuote().getOpen());
            marketData.setHigh(stock.getQuote().getDayHigh());
            marketData.setLow(stock.getQuote().getDayLow());
            marketData.setClose(stock.getQuote().getPrice());
            marketData.setVolume(stock.getQuote().getVolume());
            marketData.setAdjustedClose(stock.getQuote().getPrice());
            
            repository.save(marketData);
            logger.info("Successfully saved current quote for {}", symbol);
            
            return true;
            
        } catch (IOException e) {
            logger.error("Error fetching current quote for {}: {}", symbol, e.getMessage());
            return false;
        } catch (SQLException e) {
            logger.error("Error saving current quote for {}: {}", symbol, e.getMessage());
            return false;
        }
    }
    
    /**
     * Convert Yahoo Finance HistoricalQuote to MarketData entity
     */
    private MarketData convertToMarketData(String symbol, HistoricalQuote quote) {
        LocalDateTime timestamp = LocalDateTime.ofInstant(
                quote.getDate().toInstant(),
                ZoneId.systemDefault());
        
        LocalDate date = timestamp.toLocalDate();
        
        return new MarketData(
                symbol,
                timestamp,
                date,
                quote.getOpen(),
                quote.getHigh(),
                quote.getLow(),
                quote.getClose(),
                quote.getVolume(),
                quote.getAdjClose()
        );
    }
}
