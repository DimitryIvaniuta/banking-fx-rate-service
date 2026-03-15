package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSource;
import com.github.dimitryivaniuta.gateway.fxrate.domain.ProviderRate;
import com.github.dimitryivaniuta.gateway.fxrate.provider.FxProviderClient;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Orchestrates provider polling and streaming ingestion.
 */
@Service
public class FxRateIngestionService {

    private final FxProviderClient fxProviderClient;
    private final FxRatePersistenceService fxRatePersistenceService;
    private final FxRateCacheService fxRateCacheService;
    private final Clock clock;
    private final AppProperties appProperties;
    private final Counter ingestionCounter;

    /**
     * Creates the ingestion service.
     *
     * @param fxProviderClient provider client
     * @param fxRatePersistenceService persistence service
     * @param fxRateCacheService cache service
     * @param clock application clock
     * @param meterRegistry meter registry
     */
    public FxRateIngestionService(
            final FxProviderClient fxProviderClient,
            final FxRatePersistenceService fxRatePersistenceService,
            final FxRateCacheService fxRateCacheService,
            final Clock clock,
            final AppProperties appProperties,
            final MeterRegistry meterRegistry) {
        this.fxProviderClient = fxProviderClient;
        this.fxRatePersistenceService = fxRatePersistenceService;
        this.fxRateCacheService = fxRateCacheService;
        this.clock = clock;
        this.appProperties = appProperties;
        this.ingestionCounter = Counter.builder("fx.ingestion.records").register(meterRegistry);
    }

    /**
     * Executes a scheduled provider polling cycle when enabled.
     *
     * @return insertion count
     */
    @Transactional
    public int ingestFromProvider() {
        List<ProviderRate> providerRates = fxProviderClient.fetchLatestRates();
        providerRates.forEach(this::ingestStreamedRate);
        return providerRates.size();
    }

    /**
     * Persists one rate and refreshes the latest-rate cache.
     *
     * @param providerRate provider rate
     */
    public void ingestStreamedRate(final ProviderRate providerRate) {
        FxRateEntity entity = fxRatePersistenceService.saveIfAbsent(providerRate);
        Duration age = Duration.between(entity.getAsOfTime(), Instant.now(clock));
        boolean fresh = age.compareTo(appProperties.freshnessSla()) <= 0;
        fxRateCacheService.putLatest(new FxRateSnapshot(
                entity.getCurrencyPair(),
                entity.getRate(),
                entity.getAsOfTime(),
                fresh,
                false,
                entity.getProvider(),
                FxRateSource.DATABASE_FRESH,
                age));
        ingestionCounter.increment();
    }
}
