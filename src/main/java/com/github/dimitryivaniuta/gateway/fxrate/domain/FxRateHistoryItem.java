package com.github.dimitryivaniuta.gateway.fxrate.domain;

import java.math.BigDecimal;
import java.time.Instant;

/**
 * Immutable historical FX rate projection returned by history queries.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param provider provider identifier
 */
public record FxRateHistoryItem(String currencyPair, BigDecimal rate, Instant asOfTime, String provider) {
}
