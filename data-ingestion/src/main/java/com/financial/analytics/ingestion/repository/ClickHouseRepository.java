package com.financial.analytics.ingestion.repository;

import com.financial.analytics.ingestion.model.MarketData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Repository;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

/**
 * Repository for storing market data in ClickHouse
 * Uses JDBC for data persistence
 */
@Repository
public class ClickHouseRepository {
    
    private static final Logger logger = LoggerFactory.getLogger(ClickHouseRepository.class);
    
    @Value("${clickhouse.url:jdbc:clickhouse://localhost:8123/financial_data}")
    private String clickhouseUrl;
    
    @Value("${clickhouse.username:default}")
    private String username;
    
    @Value("${clickhouse.password:}")
    private String password;
    
    private static final String INSERT_SQL = 
            "INSERT INTO market_data (symbol, timestamp, date, open, high, low, close, volume, adjusted_close, created_at) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
    
    /**
     * Save a single market data record
     * 
     * @param marketData Market data to save
     * @throws SQLException if database operation fails
     */
    public void save(MarketData marketData) throws SQLException {
        logger.debug("Saving market data for symbol: {}", marketData.getSymbol());
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(INSERT_SQL)) {
            
            setStatementParameters(stmt, marketData);
            stmt.executeUpdate();
            
            logger.info("Successfully saved market data for {}", marketData.getSymbol());
            
        } catch (SQLException e) {
            logger.error("Error saving market data for {}: {}", marketData.getSymbol(), e.getMessage());
            throw e;
        }
    }
    
    /**
     * Save multiple market data records in batch
     * 
     * @param marketDataList List of market data to save
     * @return Number of records saved
     */
    public int saveBatch(List<MarketData> marketDataList) {
        if (marketDataList == null || marketDataList.isEmpty()) {
            logger.warn("No market data to save");
            return 0;
        }
        
        logger.info("Saving batch of {} market data records", marketDataList.size());
        
        int savedCount = 0;
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(INSERT_SQL)) {
            
            for (MarketData marketData : marketDataList) {
                try {
                    setStatementParameters(stmt, marketData);
                    stmt.addBatch();
                } catch (SQLException e) {
                    logger.error("Error preparing batch for {}: {}", marketData.getSymbol(), e.getMessage());
                }
            }
            
            int[] results = stmt.executeBatch();
            savedCount = results.length;
            
            logger.info("Successfully saved {} market data records", savedCount);
            
        } catch (SQLException e) {
            logger.error("Error executing batch save: {}", e.getMessage());
        }
        
        return savedCount;
    }
    
    /**
     * Check if market data exists for a symbol and date
     * 
     * @param symbol Stock symbol
     * @param date Date to check
     * @return true if data exists
     */
    public boolean exists(String symbol, java.time.LocalDate date) {
        String sql = "SELECT COUNT(*) FROM market_data WHERE symbol = ? AND date = ?";
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            
            stmt.setString(1, symbol);
            stmt.setDate(2, Date.valueOf(date));
            
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                return rs.getInt(1) > 0;
            }
            
        } catch (SQLException e) {
            logger.error("Error checking existence for {} on {}: {}", symbol, date, e.getMessage());
        }
        
        return false;
    }
    
    /**
     * Get market data for a symbol within a date range
     * 
     * @param symbol Stock symbol
     * @param fromDate Start date
     * @param toDate End date
     * @return List of market data
     */
    public List<MarketData> findBySymbolAndDateRange(String symbol, 
                                                     java.time.LocalDate fromDate, 
                                                     java.time.LocalDate toDate) {
        String sql = "SELECT * FROM market_data WHERE symbol = ? AND date BETWEEN ? AND ? ORDER BY date";
        List<MarketData> results = new ArrayList<>();
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            
            stmt.setString(1, symbol);
            stmt.setDate(2, Date.valueOf(fromDate));
            stmt.setDate(3, Date.valueOf(toDate));
            
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                results.add(mapResultSetToMarketData(rs));
            }
            
        } catch (SQLException e) {
            logger.error("Error querying market data: {}", e.getMessage());
        }
        
        return results;
    }
    
    /**
     * Set prepared statement parameters from MarketData object
     */
    private void setStatementParameters(PreparedStatement stmt, MarketData marketData) throws SQLException {
        stmt.setString(1, marketData.getSymbol());
        stmt.setTimestamp(2, Timestamp.valueOf(marketData.getTimestamp()));
        stmt.setDate(3, Date.valueOf(marketData.getDate()));
        stmt.setBigDecimal(4, marketData.getOpen());
        stmt.setBigDecimal(5, marketData.getHigh());
        stmt.setBigDecimal(6, marketData.getLow());
        stmt.setBigDecimal(7, marketData.getClose());
        stmt.setLong(8, marketData.getVolume());
        stmt.setBigDecimal(9, marketData.getAdjustedClose());
        stmt.setTimestamp(10, Timestamp.valueOf(marketData.getCreatedAt()));
    }
    
    /**
     * Map ResultSet to MarketData object
     */
    private MarketData mapResultSetToMarketData(ResultSet rs) throws SQLException {
        MarketData marketData = new MarketData();
        marketData.setSymbol(rs.getString("symbol"));
        marketData.setTimestamp(rs.getTimestamp("timestamp").toLocalDateTime());
        marketData.setDate(rs.getDate("date").toLocalDate());
        marketData.setOpen(rs.getBigDecimal("open"));
        marketData.setHigh(rs.getBigDecimal("high"));
        marketData.setLow(rs.getBigDecimal("low"));
        marketData.setClose(rs.getBigDecimal("close"));
        marketData.setVolume(rs.getLong("volume"));
        marketData.setAdjustedClose(rs.getBigDecimal("adjusted_close"));
        marketData.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
        return marketData;
    }
    
    /**
     * Get database connection
     */
    private Connection getConnection() throws SQLException {
        return DriverManager.getConnection(clickhouseUrl, username, password);
    }
}
