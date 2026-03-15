package com.github.dimitryivaniuta.gateway.fxrate.service;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * Triggers periodic provider polling when scheduled ingestion is enabled.
 */
@Component
@ConditionalOnProperty(prefix = "app.fx.scheduled-ingestion", name = "enabled", havingValue = "true", matchIfMissing = true)
public class FxRatePollingScheduler {

    private final FxRateIngestionService fxRateIngestionService;
    private final FxIngestionLockService fxIngestionLockService;

    /**
     * Creates the scheduler.
     *
     * @param fxRateIngestionService ingestion service
     * @param fxIngestionLockService advisory lock service
     */
    public FxRatePollingScheduler(
            final FxRateIngestionService fxRateIngestionService,
            final FxIngestionLockService fxIngestionLockService) {
        this.fxRateIngestionService = fxRateIngestionService;
        this.fxIngestionLockService = fxIngestionLockService;
    }

    /**
     * Executes a scheduled provider polling cycle.
     */
    @Scheduled(fixedDelayString = "${app.fx.scheduled-ingestion.fixed-delay:PT60S}")
    public void poll() {
        fxIngestionLockService.runWithLock("scheduled-provider-poll", fxRateIngestionService::ingestFromProvider);
    }
}
