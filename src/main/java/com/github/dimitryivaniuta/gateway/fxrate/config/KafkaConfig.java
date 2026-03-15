package com.github.dimitryivaniuta.gateway.fxrate.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.HashMap;
import java.util.Map;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.autoconfigure.kafka.KafkaProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.listener.ContainerProperties;
import org.springframework.kafka.listener.DefaultErrorHandler;
import org.springframework.kafka.support.serializer.JsonDeserializer;
import org.springframework.util.backoff.FixedBackOff;

/**
 * Configures optional Kafka consumption for streaming FX rate ingestion.
 */
@Configuration
@EnableKafka
@ConditionalOnProperty(prefix = "app.fx.kafka", name = "enabled", havingValue = "true")
public class KafkaConfig {

    /**
     * Creates a typed consumer factory for provider FX events.
     *
     * @param properties application properties
     * @param kafkaProperties Spring Kafka properties
     * @param objectMapper mapper used by the JSON deserializer
     * @return consumer factory
     */
    @Bean
    public ConsumerFactory<String, com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage>
            fxRateConsumerFactory(final AppProperties properties, final KafkaProperties kafkaProperties, final ObjectMapper objectMapper) {
        Map<String, Object> config = new HashMap<>(kafkaProperties.buildConsumerProperties());
        config.put(ConsumerConfig.GROUP_ID_CONFIG, properties.kafka().consumerGroupId());
        config.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        config.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        JsonDeserializer<com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage> deserializer =
                new JsonDeserializer<>(com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage.class, objectMapper, false);
        deserializer.addTrustedPackages("*");
        return new DefaultKafkaConsumerFactory<>(config, new StringDeserializer(), deserializer);
    }

    /**
     * Creates a common Kafka error handler with bounded retry.
     *
     * @return error handler
     */
    @Bean
    public DefaultErrorHandler kafkaErrorHandler() {
        return new DefaultErrorHandler(new FixedBackOff(1_000L, 3L));
    }

    /**
     * Creates the listener container factory for provider messages.
     *
     * @param consumerFactory configured consumer factory
     * @param errorHandler common error handler
     * @return listener container factory
     */
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage>
            fxRateKafkaListenerContainerFactory(
                    final ConsumerFactory<String, com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage> consumerFactory,
                    final DefaultErrorHandler errorHandler) {
        ConcurrentKafkaListenerContainerFactory<String, com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage> factory =
                new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);
        factory.setCommonErrorHandler(errorHandler);
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);
        return factory;
    }
}
