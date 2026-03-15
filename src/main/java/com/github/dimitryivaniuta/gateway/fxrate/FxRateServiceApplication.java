package com.github.dimitryivaniuta.gateway.fxrate;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Boots the FX Rate Service application.
 *
 * <p>The application exposes JAX-RS endpoints through Jersey, persists immutable FX history
 * in PostgreSQL, caches latest rates in Redis, consumes optional streaming updates from Kafka,
 * and exposes operational endpoints through Spring Boot Actuator.
 */
@SpringBootApplication
@EnableScheduling
@ConfigurationPropertiesScan
public class FxRateServiceApplication {

    /**
     * Starts the application.
     *
     * @param args raw command line arguments
     */
    public static void main(final String[] args) {
        SpringApplication.run(FxRateServiceApplication.class, args);
    }
}
