package com.financial.analytics.ingestion.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for SchedulerService
 */
@ExtendWith(MockitoExtension.class)
class SchedulerServiceTest {
    
    @Mock
    private DataIngestionService dataIngestionService;
    
    @InjectMocks
    private SchedulerService schedulerService;
    
    private String[] testSymbols;
    
    @BeforeEach
    void setUp() {
        testSymbols = new String[]{"AAPL", "GOOGL", "MSFT"};
        
        // Set properties using reflection
        ReflectionTestUtils.setField(schedulerService, "symbols", testSymbols);
        ReflectionTestUtils.setField(schedulerService, "historyDays", 7);
        ReflectionTestUtils.setField(schedulerService, "alertEnabled", true);
        ReflectionTestUtils.setField(schedulerService, "alertThreshold", 3);
    }
    
    @Test
    void testScheduledDailyIngestion_Success() {
        // Arrange
        when(dataIngestionService.ingestHistoricalDataBatch(any(String[].class), eq(7)))
            .thenReturn(100);
        
        // Act
        schedulerService.scheduledDailyIngestion();
        
        // Assert
        verify(dataIngestionService, times(1)).ingestHistoricalDataBatch(testSymbols, 7);
        assertEquals(0, schedulerService.getConsecutiveFailures());
    }
    
    @Test
    void testScheduledDailyIngestion_Failure() {
        // Arrange
        when(dataIngestionService.ingestHistoricalDataBatch(any(String[].class), eq(7)))
            .thenThrow(new RuntimeException("Network error"));
        
        // Act & Assert
        assertThrows(RuntimeException.class, () -> schedulerService.scheduledDailyIngestion());
        verify(dataIngestionService, times(1)).ingestHistoricalDataBatch(testSymbols, 7);
        assertEquals(1, schedulerService.getConsecutiveFailures());
    }
    
    @Test
    void testScheduledDailyIngestion_MultipleFailures() {
        // Arrange
        when(dataIngestionService.ingestHistoricalDataBatch(any(String[].class), eq(7)))
            .thenThrow(new RuntimeException("Network error"));
        
        // Act - Simulate multiple failures
        for (int i = 0; i < 3; i++) {
            try {
                schedulerService.scheduledDailyIngestion();
            } catch (RuntimeException e) {
                // Expected
            }
        }
        
        // Assert
        assertEquals(3, schedulerService.getConsecutiveFailures());
    }
    
    @Test
    void testScheduledDailyIngestion_RecoveryAfterFailure() {
        // Arrange
        when(dataIngestionService.ingestHistoricalDataBatch(any(String[].class), eq(7)))
            .thenThrow(new RuntimeException("Network error"))
            .thenReturn(100);
        
        // Act - First call fails
        try {
            schedulerService.scheduledDailyIngestion();
        } catch (RuntimeException e) {
            // Expected
        }
        assertEquals(1, schedulerService.getConsecutiveFailures());
        
        // Act - Second call succeeds
        schedulerService.scheduledDailyIngestion();
        
        // Assert - Counter should be reset
        assertEquals(0, schedulerService.getConsecutiveFailures());
    }
    
    @Test
    void testScheduledIntradayIngestion_Success() {
        // Arrange
        when(dataIngestionService.ingestCurrentQuote(anyString()))
            .thenReturn(true);
        
        // Act
        schedulerService.scheduledIntradayIngestion();
        
        // Assert
        verify(dataIngestionService, times(testSymbols.length))
            .ingestCurrentQuote(anyString());
    }
    
    @Test
    void testScheduledIntradayIngestion_PartialFailure() {
        // Arrange
        when(dataIngestionService.ingestCurrentQuote("AAPL")).thenReturn(true);
        when(dataIngestionService.ingestCurrentQuote("GOOGL")).thenReturn(false);
        when(dataIngestionService.ingestCurrentQuote("MSFT")).thenReturn(true);
        
        // Act
        schedulerService.scheduledIntradayIngestion();
        
        // Assert
        verify(dataIngestionService, times(testSymbols.length))
            .ingestCurrentQuote(anyString());
    }
    
    @Test
    void testScheduledIntradayIngestion_CompleteFailure() {
        // Arrange - Make all symbols throw exceptions during individual ingestion
        when(dataIngestionService.ingestCurrentQuote(anyString()))
            .thenThrow(new RuntimeException("Service unavailable"));
        
        // Act - Should not throw exception as errors are caught per symbol
        assertDoesNotThrow(() -> schedulerService.scheduledIntradayIngestion());
        
        // Assert - Verify all symbols were attempted
        verify(dataIngestionService, times(testSymbols.length))
            .ingestCurrentQuote(anyString());
    }
    
    @Test
    void testResetConsecutiveFailures() {
        // Arrange - Set some failures
        when(dataIngestionService.ingestHistoricalDataBatch(any(String[].class), eq(7)))
            .thenThrow(new RuntimeException("Network error"));
        
        try {
            schedulerService.scheduledDailyIngestion();
        } catch (RuntimeException e) {
            // Expected
        }
        
        assertEquals(1, schedulerService.getConsecutiveFailures());
        
        // Act
        schedulerService.resetConsecutiveFailures();
        
        // Assert
        assertEquals(0, schedulerService.getConsecutiveFailures());
    }
    
    @Test
    void testRecoverDailyIngestion() {
        // Arrange
        Exception testException = new RuntimeException("All retries exhausted");
        
        // Act & Assert - Should not throw exception
        assertDoesNotThrow(() -> schedulerService.recoverDailyIngestion(testException));
    }
    
    @Test
    void testRecoverIntradayIngestion() {
        // Arrange
        Exception testException = new RuntimeException("All retries exhausted");
        
        // Act & Assert - Should not throw exception
        assertDoesNotThrow(() -> schedulerService.recoverIntradayIngestion(testException));
    }
}
