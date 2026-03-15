package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.exception.IllegalRequestException;
import java.util.Locale;
import java.util.Set;
import org.springframework.stereotype.Component;

/**
 * Validates and normalizes FX currency pair input.
 */
@Component
public class CurrencyPairNormalizer {

    private final Set<String> supportedPairs;

    /**
     * Creates the normalizer.
     *
     * @param appProperties application properties with supported pairs
     */
    public CurrencyPairNormalizer(final AppProperties appProperties) {
        this.supportedPairs = Set.copyOf(appProperties.supportedPairs());
    }

    /**
     * Converts base and quote inputs to canonical BASE/QUOTE form.
     *
     * @param base base currency
     * @param quote quote currency
     * @return normalized pair
     */
    public String normalize(final String base, final String quote) {
        if (base == null || quote == null || base.isBlank() || quote.isBlank()) {
            throw new IllegalRequestException("Both base and quote are required");
        }
        String normalizedBase = base.trim().toUpperCase(Locale.ROOT);
        String normalizedQuote = quote.trim().toUpperCase(Locale.ROOT);
        if (normalizedBase.length() != 3 || normalizedQuote.length() != 3) {
            throw new IllegalRequestException("Currencies must be 3-letter ISO-like codes");
        }
        String pair = normalizedBase + "/" + normalizedQuote;
        if (!supportedPairs.contains(pair)) {
            throw new IllegalRequestException("Unsupported currency pair: " + pair);
        }
        return pair;
    }
}
