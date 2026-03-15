package com.github.dimitryivaniuta.gateway.fxrate.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.github.dimitryivaniuta.gateway.fxrate.TestConfigFactory;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSource;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

/**
 * Tests for latest query behavior.
 */
class FxRateQueryServiceTest {

    /**
     * Verifies fresh database data is returned without fallback.
     */
    @Test
    void shouldReturnFreshRateWithoutFallback() {
        CurrencyPairNormalizer normalizer = new CurrencyPairNormalizer(TestConfigFactory.defaultProperties());
        FxRateCacheService cacheService = Mockito.mock(FxRateCacheService.class);
        FxRatePersistenceService persistenceService = Mockito.mock(FxRatePersistenceService.class);
        Clock clock = Clock.fixed(Instant.parse("2026-03-15T12:00:00Z"), ZoneOffset.UTC);

        when(cacheService.getLatest("EUR/USD")).thenReturn(Optional.empty());
        when(persistenceService.findLatest("EUR/USD"))
                .thenReturn(Optional.of(FxRateEntity.builder()
                        .currencyPair("EUR/USD")
                        .rate(new BigDecimal("1.123400"))
                        .asOfTime(Instant.parse("2026-03-15T11:58:00Z"))
                        .provider("stub-provider")
                        .build()));

        FxRateQueryService service = new FxRateQueryService(
                normalizer,
                cacheService,
                persistenceService,
                TestConfigFactory.defaultProperties(),
                clock,
                new SimpleMeterRegistry());

        var result = service.getLatest("eur", "usd");

        assertTrue(result.fresh());
        assertFalse(result.fallbackUsed());
        assertEquals(FxRateSource.DATABASE_FRESH, result.source());
        verify(cacheService).putLatest(result);
    }

    /**
     * Verifies stale database data is returned as last known good fallback.
     */
    @Test
    void shouldReturnLastKnownGoodFallbackWhenStale() {
        CurrencyPairNormalizer normalizer = new CurrencyPairNormalizer(TestConfigFactory.defaultProperties());
        FxRateCacheService cacheService = Mockito.mock(FxRateCacheService.class);
        FxRatePersistenceService persistenceService = Mockito.mock(FxRatePersistenceService.class);
        Clock clock = Clock.fixed(Instant.parse("2026-03-15T12:00:00Z"), ZoneOffset.UTC);

        when(cacheService.getLatest("EUR/USD")).thenReturn(Optional.empty());
        when(persistenceService.findLatest("EUR/USD"))
                .thenReturn(Optional.of(FxRateEntity.builder()
                        .currencyPair("EUR/USD")
                        .rate(new BigDecimal("1.120000"))
                        .asOfTime(Instant.parse("2026-03-15T11:40:00Z"))
                        .provider("stub-provider")
                        .build()));

        FxRateQueryService service = new FxRateQueryService(
                normalizer,
                cacheService,
                persistenceService,
                TestConfigFactory.defaultProperties(),
                clock,
                new SimpleMeterRegistry());

        var result = service.getLatest("EUR", "USD");

        assertFalse(result.fresh());
        assertTrue(result.fallbackUsed());
        assertEquals(FxRateSource.DATABASE_FALLBACK, result.source());
    }

    /**
     * Verifies cached values are served as cache-origin responses.
     */
    @Test
    void shouldReturnCachedRateWhenAvailable() {
        CurrencyPairNormalizer normalizer = new CurrencyPairNormalizer(TestConfigFactory.defaultProperties());
        FxRateCacheService cacheService = Mockito.mock(FxRateCacheService.class);
        FxRatePersistenceService persistenceService = Mockito.mock(FxRatePersistenceService.class);
        Clock clock = Clock.fixed(Instant.parse("2026-03-15T12:00:00Z"), ZoneOffset.UTC);

        when(cacheService.getLatest("EUR/USD")).thenReturn(Optional.of(new FxRateSnapshot(
                "EUR/USD",
                new BigDecimal("1.123400"),
                Instant.parse("2026-03-15T11:59:50Z"),
                true,
                false,
                "stub-provider",
                FxRateSource.DATABASE_FRESH,
                java.time.Duration.ofSeconds(10))));

        FxRateQueryService service = new FxRateQueryService(
                normalizer,
                cacheService,
                persistenceService,
                TestConfigFactory.defaultProperties(),
                clock,
                new SimpleMeterRegistry());

        var result = service.getLatest("EUR", "USD");

        assertEquals(FxRateSource.CACHE, result.source());
    }
}
