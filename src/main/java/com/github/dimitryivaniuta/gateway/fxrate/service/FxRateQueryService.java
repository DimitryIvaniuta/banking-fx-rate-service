package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateHistoryItem;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSource;
import com.github.dimitryivaniuta.gateway.fxrate.exception.IllegalRequestException;
import com.github.dimitryivaniuta.gateway.fxrate.exception.RateNotFoundException;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import org.springframework.stereotype.Service;

/**
 * Serves latest and historical FX queries with freshness and fallback guarantees.
 */
@Service
public class FxRateQueryService {

    private final CurrencyPairNormalizer currencyPairNormalizer;
    private final FxRateCacheService fxRateCacheService;
    private final FxRatePersistenceService fxRatePersistenceService;
    private final AppProperties appProperties;
    private final Clock clock;
    private final Counter cacheHitCounter;
    private final Counter fallbackCounter;

    /**
     * Creates the query service.
     *
     * @param currencyPairNormalizer pair normalizer
     * @param fxRateCacheService cache service
     * @param fxRatePersistenceService persistence service
     * @param appProperties application properties
     * @param clock application clock
     * @param meterRegistry meter registry
     */
    public FxRateQueryService(
            final CurrencyPairNormalizer currencyPairNormalizer,
            final FxRateCacheService fxRateCacheService,
            final FxRatePersistenceService fxRatePersistenceService,
            final AppProperties appProperties,
            final Clock clock,
            final MeterRegistry meterRegistry) {
        this.currencyPairNormalizer = currencyPairNormalizer;
        this.fxRateCacheService = fxRateCacheService;
        this.fxRatePersistenceService = fxRatePersistenceService;
        this.appProperties = appProperties;
        this.clock = clock;
        this.cacheHitCounter = Counter.builder("fx.cache.latest.hit").register(meterRegistry);
        this.fallbackCounter = Counter.builder("fx.query.fallback.used").register(meterRegistry);
    }

    /**
     * Returns the latest usable FX rate for the requested pair.
     *
     * <p>The method first tries Redis, then PostgreSQL. If the latest stored rate is stale,
     * it is still returned as the last known good value to satisfy the service contract.
     *
     * @param base base currency
     * @param quote quote currency
     * @return latest usable snapshot
     */
    public FxRateSnapshot getLatest(final String base, final String quote) {
        String currencyPair = currencyPairNormalizer.normalize(base, quote);

        FxRateSnapshot cached = fxRateCacheService.getLatest(currencyPair)
                .filter(snapshot -> !isExpired(snapshot.asOfTime()))
                .orElse(null);
        if (cached != null) {
            cacheHitCounter.increment();
            return new FxRateSnapshot(
                    cached.currencyPair(),
                    cached.rate(),
                    cached.asOfTime(),
                    isFresh(cached.asOfTime()),
                    !isFresh(cached.asOfTime()),
                    cached.provider(),
                    FxRateSource.CACHE,
                    rateAge(cached.asOfTime()));
        }

        return toSnapshot(fxRatePersistenceService.findLatest(currencyPair)
                .orElseThrow(() -> new RateNotFoundException("No FX rate found for " + currencyPair)));
    }

    /**
     * Returns the latest known rate effective at or before the requested instant.
     *
     * @param base base currency
     * @param quote quote currency
     * @param at requested effective time upper bound
     * @return consistent historical snapshot
     */
    public FxRateSnapshot getLatestAsOf(final String base, final String quote, final Instant at) {
        String currencyPair = currencyPairNormalizer.normalize(base, quote);
        FxRateEntity entity = fxRatePersistenceService.findLatestAsOf(currencyPair, at)
                .orElseThrow(() -> new RateNotFoundException("No FX rate found for " + currencyPair + " at or before " + at));
        return toSnapshot(entity);
    }

    /**
     * Returns ordered historical FX rates for the requested pair and range.
     *
     * @param base base currency
     * @param quote quote currency
     * @param from lower bound inclusive
     * @param to upper bound inclusive
     * @return history list
     */
    public List<FxRateHistoryItem> getHistory(
            final String base,
            final String quote,
            final Instant from,
            final Instant to) {
        if (from.isAfter(to)) {
            throw new IllegalRequestException("Parameter 'from' must be before or equal to 'to'");
        }
        String currencyPair = currencyPairNormalizer.normalize(base, quote);
        return fxRatePersistenceService.findHistory(currencyPair, from, to);
    }

    /**
     * Returns the timestamp of the latest stored rate for the given pair.
     *
     * @param currencyPair normalized currency pair
     * @return latest timestamp or null when absent
     */
    public Instant latestAsOfTime(final String currencyPair) {
        return fxRatePersistenceService.findLatest(currencyPair).map(FxRateEntity::getAsOfTime).orElse(null);
    }

    private FxRateSnapshot toSnapshot(final FxRateEntity latest) {
        boolean fresh = isFresh(latest.getAsOfTime());
        Duration age = rateAge(latest.getAsOfTime());
        FxRateSnapshot snapshot = new FxRateSnapshot(
                latest.getCurrencyPair(),
                latest.getRate(),
                latest.getAsOfTime(),
                fresh,
                !fresh,
                latest.getProvider(),
                fresh ? FxRateSource.DATABASE_FRESH : FxRateSource.DATABASE_FALLBACK,
                age);
        fxRateCacheService.putLatest(snapshot);
        if (!fresh) {
            fallbackCounter.increment();
        }
        return snapshot;
    }

    private boolean isFresh(final Instant asOfTime) {
        return rateAge(asOfTime).compareTo(appProperties.freshnessSla()) <= 0;
    }

    private boolean isExpired(final Instant asOfTime) {
        return rateAge(asOfTime).compareTo(appProperties.cacheTtl()) > 0;
    }

    private Duration rateAge(final Instant asOfTime) {
        return Duration.between(asOfTime, Instant.now(clock));
    }
}
