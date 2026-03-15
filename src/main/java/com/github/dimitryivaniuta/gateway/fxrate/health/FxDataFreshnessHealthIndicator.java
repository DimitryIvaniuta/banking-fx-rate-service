package com.github.dimitryivaniuta.gateway.fxrate.health;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.service.FxRateQueryService;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

/**
 * Reports freshness of stored FX data for configured currency pairs.
 */
@Component("fxDataFreshness")
public class FxDataFreshnessHealthIndicator implements HealthIndicator {

    private final AppProperties appProperties;
    private final FxRateQueryService fxRateQueryService;
    private final Clock clock;

    /**
     * Creates the indicator.
     *
     * @param appProperties application properties
     * @param fxRateQueryService query service
     * @param clock application clock
     */
    public FxDataFreshnessHealthIndicator(
            final AppProperties appProperties,
            final FxRateQueryService fxRateQueryService,
            final Clock clock) {
        this.appProperties = appProperties;
        this.fxRateQueryService = fxRateQueryService;
        this.clock = clock;
    }

    /**
     * Executes the health check.
     *
     * @return health status with pair freshness details
     */
    @Override
    public Health health() {
        Map<String, Object> details = new LinkedHashMap<>();
        boolean anyMissing = false;
        boolean anyStale = false;
        Instant now = Instant.now(clock);

        for (String pair : appProperties.supportedPairs()) {
            Instant latest = fxRateQueryService.latestAsOfTime(pair);
            if (latest == null) {
                details.put(pair, "missing");
                anyMissing = true;
            } else {
                Duration age = Duration.between(latest, now);
                details.put(pair, age.toString());
                if (age.compareTo(appProperties.freshnessSla()) > 0) {
                    anyStale = true;
                }
            }
        }

        if (anyMissing) {
            return Health.down().withDetails(details).build();
        }
        if (anyStale) {
            return Health.status("DEGRADED").withDetails(details).build();
        }
        return Health.up().withDetails(details).build();
    }
}
