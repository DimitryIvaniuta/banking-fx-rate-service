package com.github.dimitryivaniuta.gateway.fxrate.domain;

/**
 * Describes how the service produced the returned rate.
 */
public enum FxRateSource {
    /** Served directly from Redis latest-rate cache. */
    CACHE,
    /** Served from PostgreSQL and still within freshness SLA. */
    DATABASE_FRESH,
    /** Served from PostgreSQL as the last known good value after freshness SLA elapsed. */
    DATABASE_FALLBACK
}
