package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSource;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import jakarta.annotation.PostConstruct;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import org.springframework.stereotype.Component;

/**
 * Performs a lightweight startup warm-up to prefill latest-rate cache from PostgreSQL.
 */
@Component
public class StartupWarmupService {

    private final AppProperties appProperties;
    private final FxRatePersistenceService fxRatePersistenceService;
    private final FxRateCacheService fxRateCacheService;
    private final Clock clock;

    /**
     * Creates the warm-up service.
     *
     * @param appProperties application properties
     * @param fxRatePersistenceService persistence service
     * @param fxRateCacheService cache service
     * @param clock application clock
     */
    public StartupWarmupService(
            final AppProperties appProperties,
            final FxRatePersistenceService fxRatePersistenceService,
            final FxRateCacheService fxRateCacheService,
            final Clock clock) {
        this.appProperties = appProperties;
        this.fxRatePersistenceService = fxRatePersistenceService;
        this.fxRateCacheService = fxRateCacheService;
        this.clock = clock;
    }

    /**
     * Preloads latest database values into Redis when available.
     */
    @PostConstruct
    public void warmup() {
        appProperties.supportedPairs().forEach(pair -> fxRatePersistenceService.findLatest(pair)
                .ifPresent(entity -> {
                    Duration age = Duration.between(entity.getAsOfTime(), Instant.now(clock));
                    fxRateCacheService.putLatest(new FxRateSnapshot(
                            entity.getCurrencyPair(),
                            entity.getRate(),
                            entity.getAsOfTime(),
                            age.compareTo(appProperties.freshnessSla()) <= 0,
                            false,
                            entity.getProvider(),
                            FxRateSource.DATABASE_FRESH,
                            age));
                }));
    }
}
