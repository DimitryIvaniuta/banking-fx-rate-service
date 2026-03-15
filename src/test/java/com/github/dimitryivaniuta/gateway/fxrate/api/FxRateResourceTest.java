package com.github.dimitryivaniuta.gateway.fxrate.api;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSource;
import com.github.dimitryivaniuta.gateway.fxrate.service.FxRateQueryService;
import java.math.BigDecimal;
import java.time.Duration;
import java.time.Instant;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

/**
 * Resource-level unit tests for latest FX responses.
 */
class FxRateResourceTest {

    /**
     * Verifies the resource maps service response fields correctly.
     */
    @Test
    void shouldMapServiceSnapshotToResponse() {
        FxRateQueryService service = Mockito.mock(FxRateQueryService.class);
        when(service.getLatest("EUR", "USD")).thenReturn(new FxRateSnapshot(
                "EUR/USD",
                new BigDecimal("1.120000"),
                Instant.parse("2026-03-15T12:00:00Z"),
                true,
                false,
                "stub-provider",
                FxRateSource.CACHE,
                Duration.ofSeconds(10)));

        FxRateResponse response = new FxRateResource(service).latest("EUR", "USD");
        assertEquals("EUR/USD", response.currencyPair());
        assertEquals(FxRateSource.CACHE, response.source());
    }
}
