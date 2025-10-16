package com.financial.analytics.ingestion.repository;

import com.financial.analytics.ingestion.model.MarketData;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for ClickHouseRepository
 * Note: These tests require a running ClickHouse instance or use H2 for testing
 */
@SpringBootTest
@TestPropertySource(properties = {
    "clickhouse.url=jdbc:h2:mem:testdb",
    "clickhouse.username=sa",
    "clickhouse.password="
})
class ClickHouseRepositoryTest {
    
    @Autowired(required = false)
    private ClickHouseRepository repository;
    
    private MarketData testData;
    
    @BeforeEach
    void setUp() {
        // Create test market data
        testData = new MarketData();
        testData.setSymbol("TEST");
        testData.setTimestamp(LocalDateTime.now());
        testData.setDate(LocalDate.now());
        testData.setOpen(new BigDecimal("100.00"));
        testData.setHigh(new BigDecimal("105.00"));
        testData.setLow(new BigDecimal("99.00"));
        testData.setClose(new BigDecimal("103.00"));
        testData.setVolume(1000000L);
        testData.setAdjustedClose(new BigDecimal("103.00"));
    }
    
    @Test
    void testMarketDataCreation() {
        // Test that MarketData object is created correctly
        assertNotNull(testData);
        assertEquals("TEST", testData.getSymbol());
        assertEquals(new BigDecimal("100.00"), testData.getOpen());
        assertNotNull(testData.getCreatedAt());
    }
    
    @Test
    void testSaveBatch_EmptyList() {
        if (repository == null) {
            // Skip if no ClickHouse connection available
            return;
        }
        
        List<MarketData> emptyList = new ArrayList<>();
        int result = repository.saveBatch(emptyList);
        
        assertEquals(0, result);
    }
    
    @Test
    void testSaveBatch_WithData() {
        if (repository == null) {
            // Skip if no ClickHouse connection available
            return;
        }
        
        List<MarketData> dataList = new ArrayList<>();
        dataList.add(testData);
        
        // This test will fail without a proper ClickHouse connection
        // but verifies the method logic
        assertDoesNotThrow(() -> repository.saveBatch(dataList));
    }
    
    @Test
    void testMarketDataToString() {
        String str = testData.toString();
        
        assertNotNull(str);
        assertTrue(str.contains("TEST"));
        assertTrue(str.contains("100.00"));
    }
}
