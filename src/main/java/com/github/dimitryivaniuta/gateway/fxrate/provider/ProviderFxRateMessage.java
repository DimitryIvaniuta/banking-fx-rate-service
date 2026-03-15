package com.github.dimitryivaniuta.gateway.fxrate.provider;

import java.math.BigDecimal;
import java.time.Instant;

/**
 * Kafka payload representing a provider-emitted FX rate.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param provider provider identifier
 */
public record ProviderFxRateMessage(String currencyPair, BigDecimal rate, Instant asOfTime, String provider) {
}
