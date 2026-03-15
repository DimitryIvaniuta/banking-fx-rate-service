package com.github.dimitryivaniuta.gateway.fxrate.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.github.dimitryivaniuta.gateway.fxrate.TestConfigFactory;
import com.github.dimitryivaniuta.gateway.fxrate.exception.IllegalRequestException;
import org.junit.jupiter.api.Test;

/**
 * Tests for {@link CurrencyPairNormalizer}.
 */
class CurrencyPairNormalizerTest {

    private final CurrencyPairNormalizer normalizer = new CurrencyPairNormalizer(TestConfigFactory.defaultProperties());

    /**
     * Verifies canonical pair formatting.
     */
    @Test
    void shouldNormalizePair() {
        assertEquals("EUR/USD", normalizer.normalize("eur", "usd"));
    }

    /**
     * Verifies invalid currency length rejection.
     */
    @Test
    void shouldRejectInvalidCurrencyLength() {
        assertThrows(IllegalRequestException.class, () -> normalizer.normalize("EURO", "USD"));
    }

    /**
     * Verifies unsupported pairs are rejected.
     */
    @Test
    void shouldRejectUnsupportedPair() {
        assertThrows(IllegalRequestException.class, () -> normalizer.normalize("GBP", "PLN"));
    }
}
