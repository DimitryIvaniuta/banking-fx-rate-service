package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateHistoryItem;
import com.github.dimitryivaniuta.gateway.fxrate.domain.ProviderRate;
import com.github.dimitryivaniuta.gateway.fxrate.repository.FxRateRepository;
import java.time.Clock;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Encapsulates PostgreSQL read/write access for FX rates.
 */
@Service
public class FxRatePersistenceService {

    private final FxRateRepository fxRateRepository;
    private final Clock clock;

    /**
     * Creates the persistence service.
     *
     * @param fxRateRepository repository
     * @param clock application clock
     */
    public FxRatePersistenceService(final FxRateRepository fxRateRepository, final Clock clock) {
        this.fxRateRepository = fxRateRepository;
        this.clock = clock;
    }

    /**
     * Persists one provider rate as an immutable historical row when it is not a duplicate.
     *
     * @param providerRate provider rate
     * @return persisted entity or the existing matching entity when the event was already stored
     */
    @Transactional
    public FxRateEntity saveIfAbsent(final ProviderRate providerRate) {
        if (fxRateRepository.existsByCurrencyPairAndAsOfTimeAndProvider(
                providerRate.currencyPair(), providerRate.asOfTime(), providerRate.provider())) {
            return fxRateRepository.findByCurrencyPairAndAsOfTimeAndProvider(
                            providerRate.currencyPair(), providerRate.asOfTime(), providerRate.provider())
                    .orElseThrow();
        }

        FxRateEntity entity = FxRateEntity.builder()
                .currencyPair(providerRate.currencyPair())
                .rate(providerRate.rate())
                .asOfTime(providerRate.asOfTime())
                .provider(providerRate.provider())
                .ingestedAt(Instant.now(clock))
                .build();
        try {
            return fxRateRepository.save(entity);
        } catch (DataIntegrityViolationException exception) {
            return fxRateRepository.findByCurrencyPairAndAsOfTimeAndProvider(
                            providerRate.currencyPair(), providerRate.asOfTime(), providerRate.provider())
                    .orElseThrow();
        }
    }

    /**
     * Returns the latest known rate for a pair.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @return latest row if present
     */
    @Transactional(readOnly = true)
    public Optional<FxRateEntity> findLatest(final String currencyPair) {
        return fxRateRepository.findTopByCurrencyPairOrderByAsOfTimeDesc(currencyPair);
    }

    /**
     * Returns the latest known rate not newer than the provided instant.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @param asOf upper bound
     * @return latest eligible row if present
     */
    @Transactional(readOnly = true)
    public Optional<FxRateEntity> findLatestAsOf(final String currencyPair, final Instant asOf) {
        return fxRateRepository.findByCurrencyPairAndAsOfTimeLessThanEqualOrderByAsOfTimeDesc(currencyPair, asOf, PageRequest.of(0, 1))
                .stream()
                .findFirst();
    }

    /**
     * Returns ordered historical rows for a currency pair and time range.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @param from lower bound inclusive
     * @param to upper bound inclusive
     * @return history list
     */
    @Transactional(readOnly = true)
    public List<FxRateHistoryItem> findHistory(final String currencyPair, final Instant from, final Instant to) {
        return fxRateRepository.findByCurrencyPairAndAsOfTimeBetweenOrderByAsOfTimeAsc(currencyPair, from, to)
                .stream()
                .map(entity -> new FxRateHistoryItem(entity.getCurrencyPair(), entity.getRate(), entity.getAsOfTime(), entity.getProvider()))
                .toList();
    }
}
