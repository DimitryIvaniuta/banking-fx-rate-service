package com.github.dimitryivaniuta.gateway.fxrate.repository;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Persistence access layer for immutable FX history.
 */
public interface FxRateRepository extends JpaRepository<FxRateEntity, Long> {

    /**
     * Returns the latest rate row for a currency pair.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @return latest row if present
     */
    Optional<FxRateEntity> findTopByCurrencyPairOrderByAsOfTimeDesc(String currencyPair);

    /**
     * Returns history rows for a currency pair and time range.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @param from lower bound inclusive
     * @param to upper bound inclusive
     * @return ordered rate list
     */
    List<FxRateEntity> findByCurrencyPairAndAsOfTimeBetweenOrderByAsOfTimeAsc(String currencyPair, Instant from, Instant to);

    /**
     * Returns latest rows at or before a given effective time using a pageable limit.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @param asOf bound time
     * @param pageable page request used to limit to one row
     * @return eligible rows ordered by newest first
     */
    List<FxRateEntity> findByCurrencyPairAndAsOfTimeLessThanEqualOrderByAsOfTimeDesc(
            String currencyPair, Instant asOf, Pageable pageable);

    /**
     * Checks whether the exact provider event has already been stored.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @param asOfTime provider effective timestamp
     * @param provider provider identifier
     * @return true when the event already exists
     */
    boolean existsByCurrencyPairAndAsOfTimeAndProvider(String currencyPair, Instant asOfTime, String provider);

    /**
     * Returns the exact stored provider event when present.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @param asOfTime provider effective timestamp
     * @param provider provider identifier
     * @return exact row if present
     */
    Optional<FxRateEntity> findByCurrencyPairAndAsOfTimeAndProvider(String currencyPair, Instant asOfTime, String provider);
}
