package com.github.dimitryivaniuta.gateway.fxrate.repository;

import static org.assertj.core.api.Assertions.assertThat;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import java.math.BigDecimal;
import java.time.Instant;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

/**
 * Data JPA tests for repository query behavior.
 */
@Testcontainers
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class FxRateRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:17");

    @Autowired
    private FxRateRepository repository;

    /**
     * Registers PostgreSQL Testcontainers connection properties.
     *
     * @param registry property registry
     */
    @DynamicPropertySource
    static void configure(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    /**
     * Verifies the latest rate query returns the newest row.
     */
    @Test
    void shouldFindLatestRate() {
        repository.save(FxRateEntity.builder()
                .currencyPair("EUR/USD")
                .rate(new BigDecimal("1.10"))
                .asOfTime(Instant.parse("2026-03-15T10:00:00Z"))
                .provider("stub-provider")
                .ingestedAt(Instant.parse("2026-03-15T10:00:01Z"))
                .build());
        repository.save(FxRateEntity.builder()
                .currencyPair("EUR/USD")
                .rate(new BigDecimal("1.11"))
                .asOfTime(Instant.parse("2026-03-15T11:00:00Z"))
                .provider("stub-provider")
                .ingestedAt(Instant.parse("2026-03-15T11:00:01Z"))
                .build());

        assertThat(repository.findTopByCurrencyPairOrderByAsOfTimeDesc("EUR/USD"))
                .isPresent()
                .get()
                .extracting(FxRateEntity::getRate)
                .isEqualTo(new BigDecimal("1.11"));
    }

    /**
     * Verifies duplicate detection lookup works for idempotent ingestion.
     */
    @Test
    void shouldDetectExistingProviderEvent() {
        repository.save(FxRateEntity.builder()
                .currencyPair("EUR/USD")
                .rate(new BigDecimal("1.10"))
                .asOfTime(Instant.parse("2026-03-15T10:00:00Z"))
                .provider("stub-provider")
                .ingestedAt(Instant.parse("2026-03-15T10:00:01Z"))
                .build());

        assertThat(repository.existsByCurrencyPairAndAsOfTimeAndProvider(
                "EUR/USD", Instant.parse("2026-03-15T10:00:00Z"), "stub-provider")).isTrue();
    }
}
