package com.github.dimitryivaniuta.gateway.fxrate.api;

import java.math.BigDecimal;
import java.time.Instant;

/**
 * HTTP response item for historical FX rates.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param provider provider identifier
 */
public record FxRateHistoryResponseItem(
        String currencyPair,
        BigDecimal rate,
        Instant asOfTime,
        String provider) {
}
