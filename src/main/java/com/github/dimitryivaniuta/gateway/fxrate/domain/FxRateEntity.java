package com.github.dimitryivaniuta.gateway.fxrate.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Immutable FX rate row persisted in PostgreSQL.
 *
 * <p>Each row represents the rate for one currency pair at a specific provider timestamp.
 * Historical rows are never updated, which simplifies auditing and deterministic replay.
 */
@Entity
@Table(
        name = "fx_rates",
        indexes = {
            @Index(name = "idx_fx_rates_pair_asof_desc", columnList = "currency_pair, as_of_time"),
            @Index(name = "idx_fx_rates_asof_desc", columnList = "as_of_time")
        })
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FxRateEntity {

    /** Primary key. */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Currency pair in BASE/QUOTE format, for example EUR/USD. */
    @Column(name = "currency_pair", nullable = false, length = 16)
    private String currencyPair;

    /** Numerical exchange rate. */
    @Column(name = "rate", nullable = false, precision = 20, scale = 10)
    private BigDecimal rate;

    /** Provider timestamp describing when the rate became effective. */
    @Column(name = "as_of_time", nullable = false)
    private Instant asOfTime;

    /** Provider identifier for auditability. */
    @Column(name = "provider", nullable = false, length = 64)
    private String provider;

    /** Internal ingestion timestamp. */
    @Column(name = "ingested_at", nullable = false)
    private Instant ingestedAt;
}
