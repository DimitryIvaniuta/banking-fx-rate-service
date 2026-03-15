package com.github.dimitryivaniuta.gateway.fxrate.health;

import com.github.dimitryivaniuta.gateway.fxrate.provider.FxProviderClient;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

/**
 * Checks whether the upstream provider can currently be reached.
 */
@Component("fxProvider")
public class FxProviderHealthIndicator implements HealthIndicator {

    private final FxProviderClient fxProviderClient;

    /**
     * Creates the indicator.
     *
     * @param fxProviderClient provider client
     */
    public FxProviderHealthIndicator(final FxProviderClient fxProviderClient) {
        this.fxProviderClient = fxProviderClient;
    }

    /**
     * Executes the health check.
     *
     * @return health status
     */
    @Override
    public Health health() {
        try {
            int size = fxProviderClient.fetchLatestRates().size();
            return Health.up().withDetail("providerCount", size).build();
        } catch (Exception exception) {
            return Health.down(exception).build();
        }
    }
}
