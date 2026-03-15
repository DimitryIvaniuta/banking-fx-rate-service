package com.github.dimitryivaniuta.gateway.fxrate.config;

import java.time.Clock;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Exposes a shared UTC clock to make time-based logic deterministic and testable.
 */
@Configuration
public class AppClockConfig {

    /**
     * Creates the application clock.
     *
     * @return a UTC clock instance
     */
    @Bean
    public Clock appClock() {
        return Clock.systemUTC();
    }
}
