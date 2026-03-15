package com.github.dimitryivaniuta.gateway.fxrate.provider;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.domain.ProviderRate;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Clock;
import java.time.Instant;
import java.util.List;
import org.springframework.stereotype.Component;

/**
 * Deterministic stub provider used for local development and tests.
 *
 * <p>In production this adapter should be replaced by a bank-approved upstream provider integration.
 */
@Component
public class StubFxProviderClient implements FxProviderClient {

    private final AppProperties appProperties;
    private final Clock clock;

    /**
     * Creates the stub provider.
     *
     * @param appProperties application properties
     * @param clock application clock
     */
    public StubFxProviderClient(final AppProperties appProperties, final Clock clock) {
        this.appProperties = appProperties;
        this.clock = clock;
    }

    /**
     * Returns pseudo-deterministic rates for configured pairs.
     *
     * @return provider rate list
     */
    @Override
    public List<ProviderRate> fetchLatestRates() {
        Instant now = Instant.now(clock).truncatedTo(java.time.temporal.ChronoUnit.SECONDS);
        return appProperties.supportedPairs().stream()
                .map(pair -> new ProviderRate(pair, deriveRate(pair, now), now, appProperties.provider().name()))
                .toList();
    }

    private BigDecimal deriveRate(final String pair, final Instant now) {
        int base = Math.abs((pair + now.toString()).hashCode());
        return BigDecimal.valueOf((base % 50_000) / 100_000.0 + 0.500000)
                .setScale(6, RoundingMode.HALF_UP);
    }
}
