package com.github.dimitryivaniuta.gateway.fxrate.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Registers Jackson modules shared by HTTP, Kafka and cache serialization.
 */
@Configuration
public class JacksonConfig {

    /**
     * Creates a Jackson object mapper with Java Time support.
     *
     * @return configured object mapper
     */
    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper().registerModule(new JavaTimeModule()).findAndRegisterModules();
    }
}
