package com.github.dimitryivaniuta.gateway.fxrate.domain;

import java.math.BigDecimal;
import java.time.Instant;

/**
 * Provider-side FX rate value received from polling or streaming adapters.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param provider provider identifier
 */
public record ProviderRate(String currencyPair, BigDecimal rate, Instant asOfTime, String provider) {
}
