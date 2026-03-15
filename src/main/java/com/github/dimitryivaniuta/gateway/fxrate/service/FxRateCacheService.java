package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import java.util.Optional;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

/**
 * Encapsulates Redis latest-rate cache access.
 */
@Service
public class FxRateCacheService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final AppProperties appProperties;

    /**
     * Creates the cache service.
     *
     * @param redisTemplate redis template
     * @param appProperties application properties
     */
    public FxRateCacheService(final RedisTemplate<String, Object> redisTemplate, final AppProperties appProperties) {
        this.redisTemplate = redisTemplate;
        this.appProperties = appProperties;
    }

    /**
     * Returns a cached latest-rate snapshot if present.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @return snapshot if present and deserializable
     */
    public Optional<FxRateSnapshot> getLatest(final String currencyPair) {
        Object value = redisTemplate.opsForValue().get(key(currencyPair));
        return value instanceof FxRateSnapshot snapshot ? Optional.of(snapshot) : Optional.empty();
    }

    /**
     * Stores a latest-rate snapshot with TTL.
     *
     * @param snapshot snapshot to cache
     */
    public void putLatest(final FxRateSnapshot snapshot) {
        redisTemplate.opsForValue().set(key(snapshot.currencyPair()), snapshot, appProperties.cacheTtl());
    }

    /**
     * Removes a cached entry.
     *
     * @param currencyPair pair in BASE/QUOTE format
     */
    public void evict(final String currencyPair) {
        redisTemplate.delete(key(currencyPair));
    }

    private String key(final String currencyPair) {
        return "fx:latest:" + currencyPair;
    }
}
