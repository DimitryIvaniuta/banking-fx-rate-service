package com.github.dimitryivaniuta.gateway.fxrate.provider;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.github.dimitryivaniuta.gateway.fxrate.TestConfigFactory;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import org.junit.jupiter.api.Test;

/**
 * Tests for the deterministic stub provider.
 */
class StubFxProviderClientTest {

    /**
     * Verifies the stub returns one rate per configured pair.
     */
    @Test
    void shouldReturnConfiguredPairs() {
        StubFxProviderClient client = new StubFxProviderClient(
                TestConfigFactory.defaultProperties(),
                Clock.fixed(Instant.parse("2026-03-15T12:00:00Z"), ZoneOffset.UTC));
        assertEquals(2, client.fetchLatestRates().size());
    }
}
