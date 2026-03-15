package com.github.dimitryivaniuta.gateway.fxrate.provider;

import com.github.dimitryivaniuta.gateway.fxrate.domain.ProviderRate;
import com.github.dimitryivaniuta.gateway.fxrate.service.FxRateIngestionService;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.stereotype.Component;

/**
 * Consumes streaming provider FX rates from Kafka when enabled.
 */
@Component
@ConditionalOnProperty(prefix = "app.fx.kafka", name = "enabled", havingValue = "true")
public class KafkaFxRateConsumer {

    private final FxRateIngestionService fxRateIngestionService;

    /**
     * Creates the consumer.
     *
     * @param fxRateIngestionService ingestion service
     */
    public KafkaFxRateConsumer(final FxRateIngestionService fxRateIngestionService) {
        this.fxRateIngestionService = fxRateIngestionService;
    }

    /**
     * Handles a provider message by persisting it and refreshing the latest-rate cache.
     *
     * @param message provider message
     * @param acknowledgment manual acknowledgment handle
     */
    @KafkaListener(topics = "${app.fx.kafka.topic}", containerFactory = "fxRateKafkaListenerContainerFactory")
    public void onMessage(final ProviderFxRateMessage message, final Acknowledgment acknowledgment) {
        fxRateIngestionService.ingestStreamedRate(new ProviderRate(
                message.currencyPair(),
                message.rate(),
                message.asOfTime(),
                message.provider()));
        acknowledgment.acknowledge();
    }
}
