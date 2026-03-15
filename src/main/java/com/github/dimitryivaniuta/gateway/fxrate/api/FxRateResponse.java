package com.github.dimitryivaniuta.gateway.fxrate.api;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSource;
import java.math.BigDecimal;
import java.time.Duration;
import java.time.Instant;

/**
 * HTTP response DTO for a latest FX rate lookup.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param fresh whether the rate is still within freshness SLA
 * @param fallbackUsed whether a last-known-good fallback was used
 * @param provider provider identifier
 * @param source logical origin used to serve the response
 * @param age age of the rate relative to current service time
 */
public record FxRateResponse(
        String currencyPair,
        BigDecimal rate,
        Instant asOfTime,
        boolean fresh,
        boolean fallbackUsed,
        String provider,
        FxRateSource source,
        Duration age) {
}
