package com.financial.analytics.ingestion.model;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Entity representing market data for ClickHouse storage
 */
public class MarketData {
    
    private String symbol;
    private LocalDateTime timestamp;
    private LocalDate date;
    private BigDecimal open;
    private BigDecimal high;
    private BigDecimal low;
    private BigDecimal close;
    private Long volume;
    private BigDecimal adjustedClose;
    private LocalDateTime createdAt;
    
    public MarketData() {
        this.createdAt = LocalDateTime.now();
    }
    
    public MarketData(String symbol, LocalDateTime timestamp, LocalDate date,
                     BigDecimal open, BigDecimal high, BigDecimal low,
                     BigDecimal close, Long volume, BigDecimal adjustedClose) {
        this.symbol = symbol;
        this.timestamp = timestamp;
        this.date = date;
        this.open = open;
        this.high = high;
        this.low = low;
        this.close = close;
        this.volume = volume;
        this.adjustedClose = adjustedClose;
        this.createdAt = LocalDateTime.now();
    }
    
    public String getSymbol() {
        return symbol;
    }
    
    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }
    
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
    
    public LocalDate getDate() {
        return date;
    }
    
    public void setDate(LocalDate date) {
        this.date = date;
    }
    
    public BigDecimal getOpen() {
        return open;
    }
    
    public void setOpen(BigDecimal open) {
        this.open = open;
    }
    
    public BigDecimal getHigh() {
        return high;
    }
    
    public void setHigh(BigDecimal high) {
        this.high = high;
    }
    
    public BigDecimal getLow() {
        return low;
    }
    
    public void setLow(BigDecimal low) {
        this.low = low;
    }
    
    public BigDecimal getClose() {
        return close;
    }
    
    public void setClose(BigDecimal close) {
        this.close = close;
    }
    
    public Long getVolume() {
        return volume;
    }
    
    public void setVolume(Long volume) {
        this.volume = volume;
    }
    
    public BigDecimal getAdjustedClose() {
        return adjustedClose;
    }
    
    public void setAdjustedClose(BigDecimal adjustedClose) {
        this.adjustedClose = adjustedClose;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    @Override
    public String toString() {
        return "MarketData{" +
                "symbol='" + symbol + '\'' +
                ", timestamp=" + timestamp +
                ", date=" + date +
                ", open=" + open +
                ", high=" + high +
                ", low=" + low +
                ", close=" + close +
                ", volume=" + volume +
                ", adjustedClose=" + adjustedClose +
                ", createdAt=" + createdAt +
                '}';
    }
}
