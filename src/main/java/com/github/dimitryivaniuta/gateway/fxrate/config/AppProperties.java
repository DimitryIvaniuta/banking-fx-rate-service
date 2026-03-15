package com.github.dimitryivaniuta.gateway.fxrate.config;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import java.net.URI;
import java.time.Duration;
import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

/**
 * Strongly typed application properties used by the FX Rate Service.
 */
@Validated
@ConfigurationProperties(prefix = "app.fx")
public record AppProperties(
        @NotNull Duration cacheTtl,
        @NotNull Duration freshnessSla,
        @NotNull Provider provider,
        @NotNull Kafka kafka,
        @NotNull ScheduledIngestion scheduledIngestion,
        @NotNull Admin admin,
        @NotNull Lock lock,
        @NotEmpty List<@NotBlank String> supportedPairs) {

    /**
     * Provider-specific properties.
     */
    public record Provider(@NotBlank String name, @NotNull URI baseUrl, String apiKey) {
    }

    /**
     * Kafka ingestion properties.
     */
    public record Kafka(boolean enabled, @NotBlank String topic, @NotBlank String consumerGroupId) {
    }

    /**
     * Scheduled polling properties.
     */
    public record ScheduledIngestion(boolean enabled, @NotNull Duration fixedDelay) {
    }

    /**
     * Admin endpoint security properties.
     */
    public record Admin(boolean apiKeyEnabled, @NotBlank String apiKeyHeaderName, String apiKey) {
    }

    /**
     * Distributed lock configuration.
     */
    public record Lock(boolean enabled, long advisoryLockId) {
    }
}
