package com.financial.analytics.api.model;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Represents a real-time stock quote
 */
public class StockQuote {
    
    private String symbol;
    private String name;
    private BigDecimal price;
    private BigDecimal change;
    private BigDecimal changeInPercent;
    private BigDecimal dayHigh;
    private BigDecimal dayLow;
    private BigDecimal open;
    private BigDecimal previousClose;
    private Long volume;
    private LocalDateTime timestamp;
    
    public StockQuote() {
    }
    
    public StockQuote(String symbol, String name, BigDecimal price) {
        this.symbol = symbol;
        this.name = name;
        this.price = price;
    }
    
    public String getSymbol() {
        return symbol;
    }
    
    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public BigDecimal getPrice() {
        return price;
    }
    
    public void setPrice(BigDecimal price) {
        this.price = price;
    }
    
    public BigDecimal getChange() {
        return change;
    }
    
    public void setChange(BigDecimal change) {
        this.change = change;
    }
    
    public BigDecimal getChangeInPercent() {
        return changeInPercent;
    }
    
    public void setChangeInPercent(BigDecimal changeInPercent) {
        this.changeInPercent = changeInPercent;
    }
    
    public BigDecimal getDayHigh() {
        return dayHigh;
    }
    
    public void setDayHigh(BigDecimal dayHigh) {
        this.dayHigh = dayHigh;
    }
    
    public BigDecimal getDayLow() {
        return dayLow;
    }
    
    public void setDayLow(BigDecimal dayLow) {
        this.dayLow = dayLow;
    }
    
    public BigDecimal getOpen() {
        return open;
    }
    
    public void setOpen(BigDecimal open) {
        this.open = open;
    }
    
    public BigDecimal getPreviousClose() {
        return previousClose;
    }
    
    public void setPreviousClose(BigDecimal previousClose) {
        this.previousClose = previousClose;
    }
    
    public Long getVolume() {
        return volume;
    }
    
    public void setVolume(Long volume) {
        this.volume = volume;
    }
    
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
    
    @Override
    public String toString() {
        return "StockQuote{" +
                "symbol='" + symbol + '\'' +
                ", name='" + name + '\'' +
                ", price=" + price +
                ", change=" + change +
                ", changeInPercent=" + changeInPercent +
                ", dayHigh=" + dayHigh +
                ", dayLow=" + dayLow +
                ", open=" + open +
                ", previousClose=" + previousClose +
                ", volume=" + volume +
                ", timestamp=" + timestamp +
                '}';
    }
}
