package com.github.dimitryivaniuta.gateway.fxrate;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import java.net.URI;
import java.time.Duration;
import java.util.List;

/**
 * Test helper factory for application properties.
 */
public final class TestConfigFactory {

    private TestConfigFactory() {
    }

    /**
     * Creates a default application properties instance for tests.
     *
     * @return properties instance
     */
    public static AppProperties defaultProperties() {
        return new AppProperties(
                Duration.ofSeconds(30),
                Duration.ofMinutes(5),
                new AppProperties.Provider("stub-provider", URI.create("https://provider.example.internal"), "stub"),
                new AppProperties.Kafka(false, "fx-rate-events", "fx-test"),
                new AppProperties.ScheduledIngestion(true, Duration.ofSeconds(60)),
                new AppProperties.Admin(true, "X-Admin-Api-Key", "test-admin-key"),
                new AppProperties.Lock(true, 845001L),
                List.of("EUR/USD", "USD/PLN"));
    }
}
