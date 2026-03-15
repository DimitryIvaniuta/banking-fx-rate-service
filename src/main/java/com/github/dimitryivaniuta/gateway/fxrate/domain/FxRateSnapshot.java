package com.github.dimitryivaniuta.gateway.fxrate.domain;

import java.math.BigDecimal;
import java.time.Duration;
import java.time.Instant;

/**
 * Service-level immutable representation of the latest usable FX rate.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param fresh whether the rate is still within freshness SLA
 * @param fallbackUsed whether the service had to use a last-known-good fallback
 * @param provider provider identifier
 * @param source logical origin used to serve the response
 * @param age age of the rate relative to current service time
 */
public record FxRateSnapshot(
        String currencyPair,
        BigDecimal rate,
        Instant asOfTime,
        boolean fresh,
        boolean fallbackUsed,
        String provider,
        FxRateSource source,
        Duration age) {
}
