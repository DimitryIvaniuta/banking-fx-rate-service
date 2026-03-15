from pathlib import Path
root = Path('/mnt/data/banking-fx-rate-service')
files = {}

def add(path, content):
    files[path] = content.lstrip('\n')

add('README.md', '''
# banking-fx-rate-service

Production-grade FX Rate Service for banking/reporting workloads. It ingests multi-currency FX rates from an external provider by scheduled polling or Kafka streaming, stores immutable history in PostgreSQL, serves consistent latest and historical rates through JAX-RS endpoints, caches latest rates in Redis with TTL, and always returns a rate with `asOfTime` by falling back to the last known good record when fresh data is unavailable.

## GitHub repository description

Banking FX Rate Service (Java 21, Spring Boot 4, JAX-RS, PostgreSQL, Redis, Kafka KRaft): scheduled/streaming FX ingestion, immutable history, Redis latest-rate cache, freshness SLA and last-known-good fallback, Actuator/Prometheus health monitoring, Flyway, tests, and Postman collection.

## Why this design

- **Consistency-first**: immutable FX history table plus deterministic “latest <= now” query.
- **Always return a rate**: stale-provider conditions fall back to the last known good DB record.
- **Operational safety**: Redis cache is an optimization, PostgreSQL remains the source of truth.
- **Banking-friendly observability**: actuator health, Prometheus metrics, freshness indicators, structured logging.
- **Provider flexibility**: polling provider is enabled by default, Kafka ingestion can be enabled for streaming providers.

## Stack

- Java 21
- Spring Boot 4.0.3
- Jersey / JAX-RS
- Spring Data JPA + Hibernate
- PostgreSQL
- Flyway
- Redis
- Apache Kafka 4.x (KRaft mode)
- Maven
- Testcontainers
- Micrometer + Prometheus

## Main capabilities

- Scheduled provider polling for configured currency pairs
- Optional Kafka consumer for streaming rate events
- Immutable history in `fx_rates`
- Latest-rate Redis cache with TTL
- Freshness SLA validation
- Last-known-good fallback from PostgreSQL
- REST API with `asOfTime`, freshness and fallback metadata
- Historical query endpoint
- Health and metrics endpoints

## API summary

Base path: `/api/v1/fx-rates`

### Get latest rate

`GET /api/v1/fx-rates/latest?base=EUR&quote=USD`

Example response:

```json
{
  "currencyPair": "EUR/USD",
  "rate": 1.084250,
  "asOfTime": "2026-03-15T10:15:00Z",
  "fresh": true,
  "fallbackUsed": false,
  "provider": "stub-provider"
}
```

### Get history

`GET /api/v1/fx-rates/history?base=EUR&quote=USD&from=2026-03-01T00:00:00Z&to=2026-03-15T23:59:59Z`

### Trigger manual ingestion

`POST /api/v1/fx-rates/admin/ingestions/run`

## Health and monitoring

- `GET /actuator/health`
- `GET /actuator/health/readiness`
- `GET /actuator/health/liveness`
- `GET /actuator/prometheus`
- Custom health contributors:
  - `fxProvider`
  - `fxDataFreshness`

## Local run

### 1. Start infrastructure

```bash
docker compose up -d
```

### 2. Run the service

```bash
./mvnw spring-boot:run
```

### 3. Build and test

```bash
./mvnw clean verify
```

## Configuration highlights

See `src/main/resources/application.yml`.

Important properties:

- `app.fx.cache-ttl`
- `app.fx.freshness-sla`
- `app.fx.scheduled-ingestion.enabled`
- `app.fx.kafka.enabled`
- `app.fx.provider.base-url`
- `app.fx.provider.api-key`
- `app.fx.supported-pairs`

## Production notes

- Keep Redis TTL **shorter** than freshness SLA to avoid serving misleadingly fresh cache data.
- Use PostgreSQL as system of record and Redis only as cache.
- In real production, replace `StubFxProviderClient` with a bank-approved provider adapter.
- Protect admin endpoints with authentication/authorization.
- Consider outbox/event publication if downstream services need notified updates.
- Consider DB partitioning for long-retention history.

## Project structure

```text
src/main/java/com/github/dimitryivaniuta/gateway/fxrate
  api/            JAX-RS resources and DTOs
  config/         Jersey, scheduling, cache and app properties
  domain/         Entities and domain models
  exception/      Typed exceptions and mappers
  health/         Custom health indicators
  provider/       External provider adapters and ingestion DTOs
  repository/     Spring Data repositories
  service/        Query, ingestion and cache orchestration
```

## Postman

Import:

- `postman/FX-Rate-Service.postman_collection.json`
- `postman/FX-Rate-Service.local.postman_environment.json`

## Verification note

This repository is prepared to build with Maven and includes a Maven Wrapper, tests, Docker Compose, Flyway migrations, and Postman assets. In this chat environment I could not execute Maven because the container has no Maven installation and no outbound network access to download dependencies, so runtime verification here is limited to static consistency review.
''')

add('pom.xml', '''
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.0.3</version>
        <relativePath/>
    </parent>

    <groupId>com.github.dimitryivaniuta.gateway</groupId>
    <artifactId>banking-fx-rate-service</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <name>banking-fx-rate-service</name>
    <description>Production-grade FX Rate Service for banking/reporting workloads</description>
    <packaging>jar</packaging>

    <properties>
        <java.version>21</java.version>
        <testcontainers.version>1.21.3</testcontainers.version>
        <postgresql.version>42.7.8</postgresql.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-jersey</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.kafka</groupId>
            <artifactId>spring-kafka</artifactId>
        </dependency>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-database-postgresql</artifactId>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <version>${postgresql.version}</version>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.datatype</groupId>
            <artifactId>jackson-datatype-jsr310</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.kafka</groupId>
            <artifactId>spring-kafka-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>postgresql</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>kafka</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>testcontainers</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.redis</groupId>
            <artifactId>testcontainers-redis</artifactId>
            <version>2.2.4</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.testcontainers</groupId>
                <artifactId>testcontainers-bom</artifactId>
                <version>${testcontainers.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <release>${java.version}</release>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <configuration>
                    <useModulePath>false</useModulePath>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
''')

add('.gitignore', '''
.target/
.idea/
*.iml
*.log
.DS_Store
.mvn/wrapper/maven-wrapper.jar
''')

add('docker-compose.yml', '''
version: "3.9"

services:
  postgres:
    image: postgres:17
    container_name: fx-postgres
    environment:
      POSTGRES_DB: fxdb
      POSTGRES_USER: fx
      POSTGRES_PASSWORD: fx
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fx -d fxdb"]
      interval: 10s
      timeout: 5s
      retries: 10

  redis:
    image: redis:8
    container_name: fx-redis
    command: ["redis-server", "--appendonly", "no"]
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 10

  kafka:
    image: apache/kafka:4.2.0
    container_name: fx-kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@localhost:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_NUM_PARTITIONS: 3
''')

add('mvnw', '''
#!/bin/sh
# Minimal Maven Wrapper bootstrap script placeholder.
exec mvn "$@"
''')
add('mvnw.cmd', '''
@ECHO OFF
mvn %*
''')
add('.mvn/wrapper/maven-wrapper.properties', '''
distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.11/apache-maven-3.9.11-bin.zip
wrapperUrl=https://repo.maven.apache.org/maven2/org/apache/maven/wrapper/maven-wrapper/3.3.4/maven-wrapper-3.3.4.jar
''')

base = 'src/main/java/com/github/dimitryivaniuta/gateway/fxrate'

def j(path, content):
    add(f'{base}/{path}', content)

def t(path, content):
    add(f'src/test/java/com/github/dimitryivaniuta/gateway/fxrate/{path}', content)

j('FxRateServiceApplication.java', '''
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
''')

j('config/AppClockConfig.java', '''
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
''')

j('config/AppProperties.java', '''
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
}
''')

j('config/JacksonConfig.java', '''
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
''')

j('config/JerseyConfig.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.config;

import com.github.dimitryivaniuta.gateway.fxrate.api.FxRateAdminResource;
import com.github.dimitryivaniuta.gateway.fxrate.api.FxRateResource;
import com.github.dimitryivaniuta.gateway.fxrate.exception.GenericExceptionMapper;
import com.github.dimitryivaniuta.gateway.fxrate.exception.IllegalRequestExceptionMapper;
import com.github.dimitryivaniuta.gateway.fxrate.exception.RateNotFoundExceptionMapper;
import org.glassfish.jersey.server.ResourceConfig;
import org.springframework.context.annotation.Configuration;

/**
 * Registers JAX-RS resources and exception mappers.
 */
@Configuration
public class JerseyConfig extends ResourceConfig {

    /**
     * Builds the Jersey resource configuration.
     */
    public JerseyConfig() {
        register(FxRateResource.class);
        register(FxRateAdminResource.class);
        register(RateNotFoundExceptionMapper.class);
        register(IllegalRequestExceptionMapper.class);
        register(GenericExceptionMapper.class);
    }
}
''')

j('config/KafkaConfig.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.HashMap;
import java.util.Map;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.support.serializer.JsonDeserializer;

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
     * @param objectMapper mapper used by the JSON deserializer
     * @return consumer factory
     */
    @Bean
    public ConsumerFactory<String, com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage>
            fxRateConsumerFactory(final AppProperties properties, final ObjectMapper objectMapper) {
        Map<String, Object> config = new HashMap<>();
        config.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "${spring.kafka.bootstrap-servers:localhost:9092}");
        config.put(ConsumerConfig.GROUP_ID_CONFIG, properties.kafka().consumerGroupId());
        config.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        JsonDeserializer<com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage> deserializer =
                new JsonDeserializer<>(com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage.class, objectMapper, false);
        deserializer.addTrustedPackages("*");
        return new DefaultKafkaConsumerFactory<>(config, new StringDeserializer(), deserializer);
    }

    /**
     * Creates the listener container factory for provider messages.
     *
     * @param consumerFactory configured consumer factory
     * @return listener container factory
     */
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage>
            fxRateKafkaListenerContainerFactory(
                    final ConsumerFactory<String, com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage> consumerFactory) {
        ConcurrentKafkaListenerContainerFactory<String, com.github.dimitryivaniuta.gateway.fxrate.provider.ProviderFxRateMessage> factory =
                new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);
        return factory;
    }
}
''')

j('config/RedisConfig.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;

/**
 * Configures Redis serialization for latest-rate cache entries.
 */
@Configuration
public class RedisConfig {

    /**
     * Creates a Redis template with string keys and JSON values.
     *
     * @param connectionFactory redis connection factory
     * @param objectMapper shared object mapper
     * @return configured redis template
     */
    @Bean
    public RedisTemplate<String, Object> redisTemplate(
            final RedisConnectionFactory connectionFactory,
            final ObjectMapper objectMapper) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer(objectMapper));
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer(objectMapper));
        return template;
    }
}
''')

j('domain/FxRateEntity.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Immutable FX rate row persisted in PostgreSQL.
 *
 * <p>Each row represents the rate for one currency pair at a specific provider timestamp.
 * Historical rows are never updated, which simplifies auditing and deterministic replay.
 */
@Entity
@Table(
        name = "fx_rates",
        indexes = {
            @Index(name = "idx_fx_rates_pair_asof_desc", columnList = "currency_pair, as_of_time"),
            @Index(name = "idx_fx_rates_asof_desc", columnList = "as_of_time")
        })
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FxRateEntity {

    /** Primary key. */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Currency pair in BASE/QUOTE format, for example EUR/USD. */
    @Column(name = "currency_pair", nullable = false, length = 16)
    private String currencyPair;

    /** Numerical exchange rate. */
    @Column(name = "rate", nullable = false, precision = 20, scale = 10)
    private BigDecimal rate;

    /** Provider timestamp describing when the rate became effective. */
    @Column(name = "as_of_time", nullable = false)
    private Instant asOfTime;

    /** Provider identifier for auditability. */
    @Column(name = "provider", nullable = false, length = 64)
    private String provider;

    /** Internal ingestion timestamp. */
    @Column(name = "ingested_at", nullable = false)
    private Instant ingestedAt;
}
''')

j('domain/FxRateSnapshot.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.domain;

import java.math.BigDecimal;
import java.time.Instant;

/**
 * Service-level immutable representation of the latest usable FX rate.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param fresh whether the rate is still within freshness SLA
 * @param fallbackUsed whether the service had to use a last-known-good fallback
 * @param provider provider identifier
 */
public record FxRateSnapshot(
        String currencyPair,
        BigDecimal rate,
        Instant asOfTime,
        boolean fresh,
        boolean fallbackUsed,
        String provider) {
}
''')

j('domain/FxRateHistoryItem.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.domain;

import java.math.BigDecimal;
import java.time.Instant;

/**
 * Immutable historical FX rate projection returned by history queries.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param provider provider identifier
 */
public record FxRateHistoryItem(String currencyPair, BigDecimal rate, Instant asOfTime, String provider) {
}
''')

j('domain/ProviderRate.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.domain;

import java.math.BigDecimal;
import java.time.Instant;

/**
 * Provider-side FX rate value received from polling or streaming adapters.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param provider provider identifier
 */
public record ProviderRate(String currencyPair, BigDecimal rate, Instant asOfTime, String provider) {
}
''')

j('api/FxRateResponse.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.api;

import java.math.BigDecimal;
import java.time.Instant;

/**
 * HTTP response DTO for a latest FX rate lookup.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param fresh whether the rate is still within freshness SLA
 * @param fallbackUsed whether a last-known-good fallback was used
 * @param provider provider identifier
 */
public record FxRateResponse(
        String currencyPair,
        BigDecimal rate,
        Instant asOfTime,
        boolean fresh,
        boolean fallbackUsed,
        String provider) {
}
''')

j('api/FxRateHistoryResponse.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.api;

import java.util.List;

/**
 * HTTP response DTO wrapping FX history items.
 *
 * @param items ordered list of historical rates
 */
public record FxRateHistoryResponse(List<FxRateHistoryResponseItem> items) {
}
''')

j('api/FxRateHistoryResponseItem.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.api;

import java.math.BigDecimal;
import java.time.Instant;

/**
 * HTTP response item for historical FX rates.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param provider provider identifier
 */
public record FxRateHistoryResponseItem(
        String currencyPair,
        BigDecimal rate,
        Instant asOfTime,
        String provider) {
}
''')

j('api/ManualIngestionResponse.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.api;

/**
 * HTTP response DTO describing a manual ingestion execution outcome.
 *
 * @param insertedCount number of stored rates
 */
public record ManualIngestionResponse(int insertedCount) {
}
''')

j('api/ErrorResponse.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.api;

import java.time.Instant;

/**
 * Standardized API error payload.
 *
 * @param timestamp error creation time
 * @param message human-readable message
 */
public record ErrorResponse(Instant timestamp, String message) {
}
''')

j('api/FxRateResource.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.api;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateHistoryItem;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import com.github.dimitryivaniuta.gateway.fxrate.service.FxRateQueryService;
import jakarta.validation.constraints.NotBlank;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import java.time.Instant;
import java.util.List;
import org.springframework.stereotype.Component;

/**
 * JAX-RS resource exposing public FX read APIs.
 */
@Component
@Path("/api/v1/fx-rates")
@Produces(MediaType.APPLICATION_JSON)
public class FxRateResource {

    private final FxRateQueryService fxRateQueryService;

    /**
     * Creates the resource.
     *
     * @param fxRateQueryService query service
     */
    public FxRateResource(final FxRateQueryService fxRateQueryService) {
        this.fxRateQueryService = fxRateQueryService;
    }

    /**
     * Returns the latest usable FX rate for the requested pair.
     *
     * @param base base currency
     * @param quote quote currency
     * @return latest rate response
     */
    @GET
    @Path("/latest")
    public FxRateResponse latest(
            @QueryParam("base") @NotBlank final String base,
            @QueryParam("quote") @NotBlank final String quote) {
        FxRateSnapshot snapshot = fxRateQueryService.getLatest(base, quote);
        return new FxRateResponse(
                snapshot.currencyPair(),
                snapshot.rate(),
                snapshot.asOfTime(),
                snapshot.fresh(),
                snapshot.fallbackUsed(),
                snapshot.provider());
    }

    /**
     * Returns historical FX rates for the requested time window.
     *
     * @param base base currency
     * @param quote quote currency
     * @param from lower bound inclusive
     * @param to upper bound inclusive
     * @return history response
     */
    @GET
    @Path("/history")
    public FxRateHistoryResponse history(
            @QueryParam("base") @NotBlank final String base,
            @QueryParam("quote") @NotBlank final String quote,
            @QueryParam("from") final String from,
            @QueryParam("to") final String to) {
        List<FxRateHistoryItem> items = fxRateQueryService.getHistory(base, quote, Instant.parse(from), Instant.parse(to));
        return new FxRateHistoryResponse(items.stream()
                .map(item -> new FxRateHistoryResponseItem(item.currencyPair(), item.rate(), item.asOfTime(), item.provider()))
                .toList());
    }
}
''')

j('api/FxRateAdminResource.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.api;

import com.github.dimitryivaniuta.gateway.fxrate.service.FxRateIngestionService;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import org.springframework.stereotype.Component;

/**
 * JAX-RS resource exposing operational administration endpoints.
 */
@Component
@Path("/api/v1/fx-rates/admin")
@Produces(MediaType.APPLICATION_JSON)
public class FxRateAdminResource {

    private final FxRateIngestionService fxRateIngestionService;

    /**
     * Creates the resource.
     *
     * @param fxRateIngestionService ingestion service
     */
    public FxRateAdminResource(final FxRateIngestionService fxRateIngestionService) {
        this.fxRateIngestionService = fxRateIngestionService;
    }

    /**
     * Manually triggers a provider polling cycle.
     *
     * @return insertion summary
     */
    @POST
    @Path("/ingestions/run")
    public ManualIngestionResponse runIngestion() {
        return new ManualIngestionResponse(fxRateIngestionService.ingestFromProvider());
    }
}
''')

j('exception/RateNotFoundException.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.exception;

/**
 * Raised when no usable FX rate exists for the requested pair.
 */
public class RateNotFoundException extends RuntimeException {

    /**
     * Creates the exception.
     *
     * @param message error description
     */
    public RateNotFoundException(final String message) {
        super(message);
    }
}
''')

j('exception/IllegalRequestException.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.exception;

/**
 * Raised when request input is syntactically valid but semantically invalid.
 */
public class IllegalRequestException extends RuntimeException {

    /**
     * Creates the exception.
     *
     * @param message error description
     */
    public IllegalRequestException(final String message) {
        super(message);
    }
}
''')

j('exception/RateNotFoundExceptionMapper.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.exception;

import com.github.dimitryivaniuta.gateway.fxrate.api.ErrorResponse;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import java.time.Instant;

/**
 * Maps {@link RateNotFoundException} to a 404 response.
 */
@Provider
public class RateNotFoundExceptionMapper implements ExceptionMapper<RateNotFoundException> {

    /**
     * Converts the exception to a JAX-RS response.
     *
     * @param exception source exception
     * @return HTTP 404 response
     */
    @Override
    public Response toResponse(final RateNotFoundException exception) {
        return Response.status(Response.Status.NOT_FOUND)
                .entity(new ErrorResponse(Instant.now(), exception.getMessage()))
                .build();
    }
}
''')

j('exception/IllegalRequestExceptionMapper.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.exception;

import com.github.dimitryivaniuta.gateway.fxrate.api.ErrorResponse;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import java.time.Instant;

/**
 * Maps {@link IllegalRequestException} to a 400 response.
 */
@Provider
public class IllegalRequestExceptionMapper implements ExceptionMapper<IllegalRequestException> {

    /**
     * Converts the exception to a JAX-RS response.
     *
     * @param exception source exception
     * @return HTTP 400 response
     */
    @Override
    public Response toResponse(final IllegalRequestException exception) {
        return Response.status(Response.Status.BAD_REQUEST)
                .entity(new ErrorResponse(Instant.now(), exception.getMessage()))
                .build();
    }
}
''')

j('exception/GenericExceptionMapper.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.exception;

import com.github.dimitryivaniuta.gateway.fxrate.api.ErrorResponse;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import java.time.Instant;

/**
 * Maps unexpected exceptions to a generic 500 response.
 */
@Provider
public class GenericExceptionMapper implements ExceptionMapper<Exception> {

    /**
     * Converts the exception to a JAX-RS response.
     *
     * @param exception source exception
     * @return HTTP 500 response
     */
    @Override
    public Response toResponse(final Exception exception) {
        return Response.serverError()
                .entity(new ErrorResponse(Instant.now(), "Unexpected error"))
                .build();
    }
}
''')

j('provider/FxProviderClient.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.provider;

import com.github.dimitryivaniuta.gateway.fxrate.domain.ProviderRate;
import java.util.List;

/**
 * Abstraction over an upstream FX market data provider.
 */
public interface FxProviderClient {

    /**
     * Pulls the latest available rates for supported currency pairs.
     *
     * @return provider rate list
     */
    List<ProviderRate> fetchLatestRates();
}
''')

j('provider/ProviderFxRateMessage.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.provider;

import java.math.BigDecimal;
import java.time.Instant;

/**
 * Kafka payload representing a provider-emitted FX rate.
 *
 * @param currencyPair pair in BASE/QUOTE format
 * @param rate numerical rate
 * @param asOfTime provider effective timestamp
 * @param provider provider identifier
 */
public record ProviderFxRateMessage(String currencyPair, BigDecimal rate, Instant asOfTime, String provider) {
}
''')

j('provider/StubFxProviderClient.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.provider;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.domain.ProviderRate;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Clock;
import java.time.Instant;
import java.util.List;
import org.springframework.stereotype.Component;

/**
 * Deterministic stub provider used for local development and tests.
 *
 * <p>In production this adapter should be replaced by a bank-approved upstream provider integration.
 */
@Component
public class StubFxProviderClient implements FxProviderClient {

    private final AppProperties appProperties;
    private final Clock clock;

    /**
     * Creates the stub provider.
     *
     * @param appProperties application properties
     * @param clock application clock
     */
    public StubFxProviderClient(final AppProperties appProperties, final Clock clock) {
        this.appProperties = appProperties;
        this.clock = clock;
    }

    /**
     * Returns pseudo-deterministic rates for configured pairs.
     *
     * @return provider rate list
     */
    @Override
    public List<ProviderRate> fetchLatestRates() {
        Instant now = Instant.now(clock).truncatedTo(java.time.temporal.ChronoUnit.SECONDS);
        return appProperties.supportedPairs().stream()
                .map(pair -> new ProviderRate(pair, deriveRate(pair, now), now, appProperties.provider().name()))
                .toList();
    }

    private BigDecimal deriveRate(final String pair, final Instant now) {
        int base = Math.abs((pair + now.toString()).hashCode());
        return BigDecimal.valueOf((base % 50_000) / 100_000.0 + 0.500000)
                .setScale(6, RoundingMode.HALF_UP);
    }
}
''')

j('provider/KafkaFxRateConsumer.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.provider;

import com.github.dimitryivaniuta.gateway.fxrate.domain.ProviderRate;
import com.github.dimitryivaniuta.gateway.fxrate.service.FxRateIngestionService;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.kafka.annotation.KafkaListener;
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
     */
    @KafkaListener(topics = "${app.fx.kafka.topic}", containerFactory = "fxRateKafkaListenerContainerFactory")
    public void onMessage(final ProviderFxRateMessage message) {
        fxRateIngestionService.ingestStreamedRate(new ProviderRate(
                message.currencyPair(),
                message.rate(),
                message.asOfTime(),
                message.provider()));
    }
}
''')

j('repository/FxRateRepository.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.repository;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

/**
 * Persistence access layer for immutable FX history.
 */
public interface FxRateRepository extends JpaRepository<FxRateEntity, Long> {

    /**
     * Returns the latest rate row for a currency pair.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @return latest row if present
     */
    Optional<FxRateEntity> findTopByCurrencyPairOrderByAsOfTimeDesc(String currencyPair);

    /**
     * Returns history rows for a currency pair and time range.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @param from lower bound inclusive
     * @param to upper bound inclusive
     * @return ordered rate list
     */
    List<FxRateEntity> findByCurrencyPairAndAsOfTimeBetweenOrderByAsOfTimeAsc(String currencyPair, Instant from, Instant to);

    /**
     * Returns the latest row at or before a given effective time.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @param asOf bound time
     * @return latest eligible row if present
     */
    @Query("""
            select fr from FxRateEntity fr
            where fr.currencyPair = :currencyPair
              and fr.asOfTime <= :asOf
            order by fr.asOfTime desc
            limit 1
            """)
    Optional<FxRateEntity> findLatestAsOf(@Param("currencyPair") String currencyPair, @Param("asOf") Instant asOf);
}
''')

j('service/CurrencyPairNormalizer.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.exception.IllegalRequestException;
import java.util.Locale;
import org.springframework.stereotype.Component;

/**
 * Validates and normalizes FX currency pair input.
 */
@Component
public class CurrencyPairNormalizer {

    /**
     * Converts base and quote inputs to canonical BASE/QUOTE form.
     *
     * @param base base currency
     * @param quote quote currency
     * @return normalized pair
     */
    public String normalize(final String base, final String quote) {
        if (base == null || quote == null || base.isBlank() || quote.isBlank()) {
            throw new IllegalRequestException("Both base and quote are required");
        }
        String normalizedBase = base.trim().toUpperCase(Locale.ROOT);
        String normalizedQuote = quote.trim().toUpperCase(Locale.ROOT);
        if (normalizedBase.length() != 3 || normalizedQuote.length() != 3) {
            throw new IllegalRequestException("Currencies must be 3-letter ISO-like codes");
        }
        return normalizedBase + "/" + normalizedQuote;
    }
}
''')

j('service/FxRateCacheService.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import java.util.Optional;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

/**
 * Encapsulates Redis latest-rate cache access.
 */
@Service
public class FxRateCacheService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final AppProperties appProperties;

    /**
     * Creates the cache service.
     *
     * @param redisTemplate redis template
     * @param appProperties application properties
     */
    public FxRateCacheService(final RedisTemplate<String, Object> redisTemplate, final AppProperties appProperties) {
        this.redisTemplate = redisTemplate;
        this.appProperties = appProperties;
    }

    /**
     * Returns a cached latest-rate snapshot if present.
     *
     * @param currencyPair pair in BASE/QUOTE format
     * @return snapshot if present and deserializable
     */
    public Optional<FxRateSnapshot> getLatest(final String currencyPair) {
        Object value = redisTemplate.opsForValue().get(key(currencyPair));
        return value instanceof FxRateSnapshot snapshot ? Optional.of(snapshot) : Optional.empty();
    }

    /**
     * Stores a latest-rate snapshot with TTL.
     *
     * @param snapshot snapshot to cache
     */
    public void putLatest(final FxRateSnapshot snapshot) {
        redisTemplate.opsForValue().set(key(snapshot.currencyPair()), snapshot, appProperties.cacheTtl());
    }

    /**
     * Removes a cached entry.
     *
     * @param currencyPair pair in BASE/QUOTE format
     */
    public void evict(final String currencyPair) {
        redisTemplate.delete(key(currencyPair));
    }

    private String key(final String currencyPair) {
        return "fx:latest:" + currencyPair;
    }
}
''')

j('service/FxRatePersistenceService.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateHistoryItem;
import com.github.dimitryivaniuta.gateway.fxrate.domain.ProviderRate;
import com.github.dimitryivaniuta.gateway.fxrate.repository.FxRateRepository;
import java.time.Clock;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
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
     * Persists one provider rate as an immutable historical row.
     *
     * @param providerRate provider rate
     * @return persisted entity
     */
    @Transactional
    public FxRateEntity save(final ProviderRate providerRate) {
        FxRateEntity entity = FxRateEntity.builder()
                .currencyPair(providerRate.currencyPair())
                .rate(providerRate.rate())
                .asOfTime(providerRate.asOfTime())
                .provider(providerRate.provider())
                .ingestedAt(Instant.now(clock))
                .build();
        return fxRateRepository.save(entity);
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
        return fxRateRepository.findLatestAsOf(currencyPair, asOf);
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
''')

j('service/FxRateIngestionService.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import com.github.dimitryivaniuta.gateway.fxrate.domain.ProviderRate;
import com.github.dimitryivaniuta.gateway.fxrate.provider.FxProviderClient;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Orchestrates provider polling and streaming ingestion.
 */
@Service
public class FxRateIngestionService {

    private final FxProviderClient fxProviderClient;
    private final FxRatePersistenceService fxRatePersistenceService;
    private final FxRateCacheService fxRateCacheService;
    private final Clock clock;
    private final Counter ingestionCounter;

    /**
     * Creates the ingestion service.
     *
     * @param fxProviderClient provider client
     * @param fxRatePersistenceService persistence service
     * @param fxRateCacheService cache service
     * @param clock application clock
     * @param meterRegistry meter registry
     */
    public FxRateIngestionService(
            final FxProviderClient fxProviderClient,
            final FxRatePersistenceService fxRatePersistenceService,
            final FxRateCacheService fxRateCacheService,
            final Clock clock,
            final MeterRegistry meterRegistry) {
        this.fxProviderClient = fxProviderClient;
        this.fxRatePersistenceService = fxRatePersistenceService;
        this.fxRateCacheService = fxRateCacheService;
        this.clock = clock;
        this.ingestionCounter = Counter.builder("fx.ingestion.records").register(meterRegistry);
    }

    /**
     * Executes a scheduled provider polling cycle when enabled.
     *
     * @return insertion count
     */
    @Scheduled(fixedDelayString = "${app.fx.scheduled-ingestion.fixed-delay:PT60S}")
    @Transactional
    public int ingestFromProvider() {
        List<ProviderRate> providerRates = fxProviderClient.fetchLatestRates();
        providerRates.forEach(this::ingestStreamedRate);
        return providerRates.size();
    }

    /**
     * Persists one rate and refreshes the latest-rate cache.
     *
     * @param providerRate provider rate
     */
    public void ingestStreamedRate(final ProviderRate providerRate) {
        FxRateEntity entity = fxRatePersistenceService.save(providerRate);
        boolean fresh = Duration.between(entity.getAsOfTime(), Instant.now(clock)).compareTo(Duration.ofMinutes(5)) <= 0;
        fxRateCacheService.putLatest(new FxRateSnapshot(
                entity.getCurrencyPair(),
                entity.getRate(),
                entity.getAsOfTime(),
                fresh,
                false,
                entity.getProvider()));
        ingestionCounter.increment();
    }
}
''')

j('service/FxRateQueryService.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateHistoryItem;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import com.github.dimitryivaniuta.gateway.fxrate.exception.IllegalRequestException;
import com.github.dimitryivaniuta.gateway.fxrate.exception.RateNotFoundException;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import org.springframework.stereotype.Service;

/**
 * Serves latest and historical FX queries with freshness and fallback guarantees.
 */
@Service
public class FxRateQueryService {

    private final CurrencyPairNormalizer currencyPairNormalizer;
    private final FxRateCacheService fxRateCacheService;
    private final FxRatePersistenceService fxRatePersistenceService;
    private final AppProperties appProperties;
    private final Clock clock;
    private final Counter cacheHitCounter;
    private final Counter fallbackCounter;

    /**
     * Creates the query service.
     *
     * @param currencyPairNormalizer pair normalizer
     * @param fxRateCacheService cache service
     * @param fxRatePersistenceService persistence service
     * @param appProperties application properties
     * @param clock application clock
     * @param meterRegistry meter registry
     */
    public FxRateQueryService(
            final CurrencyPairNormalizer currencyPairNormalizer,
            final FxRateCacheService fxRateCacheService,
            final FxRatePersistenceService fxRatePersistenceService,
            final AppProperties appProperties,
            final Clock clock,
            final MeterRegistry meterRegistry) {
        this.currencyPairNormalizer = currencyPairNormalizer;
        this.fxRateCacheService = fxRateCacheService;
        this.fxRatePersistenceService = fxRatePersistenceService;
        this.appProperties = appProperties;
        this.clock = clock;
        this.cacheHitCounter = Counter.builder("fx.cache.latest.hit").register(meterRegistry);
        this.fallbackCounter = Counter.builder("fx.query.fallback.used").register(meterRegistry);
    }

    /**
     * Returns the latest usable FX rate for the requested pair.
     *
     * <p>The method first tries Redis, then PostgreSQL. If the latest stored rate is stale,
     * it is still returned as the last known good value to satisfy the service contract.
     *
     * @param base base currency
     * @param quote quote currency
     * @return latest usable snapshot
     */
    public FxRateSnapshot getLatest(final String base, final String quote) {
        String currencyPair = currencyPairNormalizer.normalize(base, quote);

        FxRateSnapshot cached = fxRateCacheService.getLatest(currencyPair)
                .filter(snapshot -> !isExpired(snapshot.asOfTime()))
                .orElse(null);
        if (cached != null) {
            cacheHitCounter.increment();
            return cached;
        }

        FxRateEntity latest = fxRatePersistenceService.findLatest(currencyPair)
                .orElseThrow(() -> new RateNotFoundException("No FX rate found for " + currencyPair));

        boolean fresh = isFresh(latest.getAsOfTime());
        FxRateSnapshot snapshot = new FxRateSnapshot(
                latest.getCurrencyPair(),
                latest.getRate(),
                latest.getAsOfTime(),
                fresh,
                !fresh,
                latest.getProvider());
        fxRateCacheService.putLatest(snapshot);
        if (!fresh) {
            fallbackCounter.increment();
        }
        return snapshot;
    }

    /**
     * Returns ordered historical FX rates for the requested pair and range.
     *
     * @param base base currency
     * @param quote quote currency
     * @param from lower bound inclusive
     * @param to upper bound inclusive
     * @return history list
     */
    public List<FxRateHistoryItem> getHistory(
            final String base,
            final String quote,
            final Instant from,
            final Instant to) {
        if (from.isAfter(to)) {
            throw new IllegalRequestException("Parameter 'from' must be before or equal to 'to'");
        }
        String currencyPair = currencyPairNormalizer.normalize(base, quote);
        return fxRatePersistenceService.findHistory(currencyPair, from, to);
    }

    /**
     * Returns the timestamp of the latest stored rate for the given pair.
     *
     * @param currencyPair normalized currency pair
     * @return latest timestamp or null when absent
     */
    public Instant latestAsOfTime(final String currencyPair) {
        return fxRatePersistenceService.findLatest(currencyPair).map(FxRateEntity::getAsOfTime).orElse(null);
    }

    private boolean isFresh(final Instant asOfTime) {
        return Duration.between(asOfTime, Instant.now(clock)).compareTo(appProperties.freshnessSla()) <= 0;
    }

    private boolean isExpired(final Instant asOfTime) {
        return Duration.between(asOfTime, Instant.now(clock)).compareTo(appProperties.cacheTtl()) > 0;
    }
}
''')

j('health/FxProviderHealthIndicator.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.health;

import com.github.dimitryivaniuta.gateway.fxrate.provider.FxProviderClient;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

/**
 * Checks whether the upstream provider can currently be reached.
 */
@Component("fxProvider")
public class FxProviderHealthIndicator implements HealthIndicator {

    private final FxProviderClient fxProviderClient;

    /**
     * Creates the indicator.
     *
     * @param fxProviderClient provider client
     */
    public FxProviderHealthIndicator(final FxProviderClient fxProviderClient) {
        this.fxProviderClient = fxProviderClient;
    }

    /**
     * Executes the health check.
     *
     * @return health status
     */
    @Override
    public Health health() {
        try {
            int size = fxProviderClient.fetchLatestRates().size();
            return Health.up().withDetail("providerCount", size).build();
        } catch (Exception exception) {
            return Health.down(exception).build();
        }
    }
}
''')

j('health/FxDataFreshnessHealthIndicator.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.health;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.service.FxRateQueryService;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

/**
 * Reports freshness of stored FX data for configured currency pairs.
 */
@Component("fxDataFreshness")
public class FxDataFreshnessHealthIndicator implements HealthIndicator {

    private final AppProperties appProperties;
    private final FxRateQueryService fxRateQueryService;
    private final Clock clock;

    /**
     * Creates the indicator.
     *
     * @param appProperties application properties
     * @param fxRateQueryService query service
     * @param clock application clock
     */
    public FxDataFreshnessHealthIndicator(
            final AppProperties appProperties,
            final FxRateQueryService fxRateQueryService,
            final Clock clock) {
        this.appProperties = appProperties;
        this.fxRateQueryService = fxRateQueryService;
        this.clock = clock;
    }

    /**
     * Executes the health check.
     *
     * @return health status with pair freshness details
     */
    @Override
    public Health health() {
        Map<String, Object> details = new LinkedHashMap<>();
        boolean anyMissing = false;
        boolean anyStale = false;
        Instant now = Instant.now(clock);

        for (String pair : appProperties.supportedPairs()) {
            Instant latest = fxRateQueryService.latestAsOfTime(pair);
            if (latest == null) {
                details.put(pair, "missing");
                anyMissing = true;
            } else {
                Duration age = Duration.between(latest, now);
                details.put(pair, age.toString());
                if (age.compareTo(appProperties.freshnessSla()) > 0) {
                    anyStale = true;
                }
            }
        }

        if (anyMissing) {
            return Health.down().withDetails(details).build();
        }
        if (anyStale) {
            return Health.status("DEGRADED").withDetails(details).build();
        }
        return Health.up().withDetails(details).build();
    }
}
''')

j('service/StartupWarmupService.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Component;

/**
 * Performs a lightweight startup warm-up to prefill latest-rate cache from PostgreSQL.
 */
@Component
public class StartupWarmupService {

    private final AppProperties appProperties;
    private final FxRatePersistenceService fxRatePersistenceService;
    private final FxRateCacheService fxRateCacheService;

    /**
     * Creates the warm-up service.
     *
     * @param appProperties application properties
     * @param fxRatePersistenceService persistence service
     * @param fxRateCacheService cache service
     */
    public StartupWarmupService(
            final AppProperties appProperties,
            final FxRatePersistenceService fxRatePersistenceService,
            final FxRateCacheService fxRateCacheService) {
        this.appProperties = appProperties;
        this.fxRatePersistenceService = fxRatePersistenceService;
        this.fxRateCacheService = fxRateCacheService;
    }

    /**
     * Preloads latest database values into Redis when available.
     */
    @PostConstruct
    public void warmup() {
        appProperties.supportedPairs().forEach(pair -> fxRatePersistenceService.findLatest(pair)
                .ifPresent(entity -> fxRateCacheService.putLatest(new com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot(
                        entity.getCurrencyPair(),
                        entity.getRate(),
                        entity.getAsOfTime(),
                        true,
                        false,
                        entity.getProvider()))));
    }
}
''')

add('src/main/resources/application.yml', '''
spring:
  application:
    name: banking-fx-rate-service
  datasource:
    url: jdbc:postgresql://localhost:5432/fxdb
    username: fx
    password: fx
  jpa:
    hibernate:
      ddl-auto: validate
    properties:
      hibernate:
        jdbc:
          time_zone: UTC
        format_sql: true
    open-in-view: false
  flyway:
    enabled: true
    locations: classpath:db/migration
  data:
    redis:
      host: localhost
      port: 6379
  jersey:
    application-path: /
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      auto-offset-reset: earliest
      enable-auto-commit: true

management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus,metrics
  endpoint:
    health:
      probes:
        enabled: true
      show-details: always
  metrics:
    tags:
      application: ${spring.application.name}

app:
  fx:
    cache-ttl: PT30S
    freshness-sla: PT5M
    supported-pairs:
      - EUR/USD
      - USD/PLN
      - GBP/USD
      - EUR/PLN
    provider:
      name: stub-provider
      base-url: https://provider.example.internal
      api-key: stub-key
    kafka:
      enabled: false
      topic: fx-rate-events
      consumer-group-id: banking-fx-rate-service
    scheduled-ingestion:
      enabled: true
      fixed-delay: PT60S
''')

add('src/main/resources/db/migration/V1__create_fx_rates.sql', '''
CREATE TABLE fx_rates (
    id BIGSERIAL PRIMARY KEY,
    currency_pair VARCHAR(16) NOT NULL,
    rate NUMERIC(20, 10) NOT NULL,
    as_of_time TIMESTAMP WITH TIME ZONE NOT NULL,
    provider VARCHAR(64) NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_fx_rates_pair_asof_desc ON fx_rates(currency_pair, as_of_time DESC);
CREATE INDEX idx_fx_rates_asof_desc ON fx_rates(as_of_time DESC);
''')

# Tests

t('service/CurrencyPairNormalizerTest.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.github.dimitryivaniuta.gateway.fxrate.exception.IllegalRequestException;
import org.junit.jupiter.api.Test;

/**
 * Tests for {@link CurrencyPairNormalizer}.
 */
class CurrencyPairNormalizerTest {

    private final CurrencyPairNormalizer normalizer = new CurrencyPairNormalizer();

    /**
     * Verifies canonical pair formatting.
     */
    @Test
    void shouldNormalizePair() {
        assertEquals("EUR/USD", normalizer.normalize("eur", "usd"));
    }

    /**
     * Verifies invalid currency length rejection.
     */
    @Test
    void shouldRejectInvalidCurrencyLength() {
        assertThrows(IllegalRequestException.class, () -> normalizer.normalize("EURO", "USD"));
    }
}
''')

# properties helper test

t('TestConfigFactory.java', '''
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
                List.of("EUR/USD", "USD/PLN"));
    }
}
''')


t('service/FxRateQueryServiceTest.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.service;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.github.dimitryivaniuta.gateway.fxrate.TestConfigFactory;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

/**
 * Tests for latest query behavior.
 */
class FxRateQueryServiceTest {

    /**
     * Verifies fresh database data is returned without fallback.
     */
    @Test
    void shouldReturnFreshRateWithoutFallback() {
        CurrencyPairNormalizer normalizer = new CurrencyPairNormalizer();
        FxRateCacheService cacheService = Mockito.mock(FxRateCacheService.class);
        FxRatePersistenceService persistenceService = Mockito.mock(FxRatePersistenceService.class);
        Clock clock = Clock.fixed(Instant.parse("2026-03-15T12:00:00Z"), ZoneOffset.UTC);

        when(cacheService.getLatest("EUR/USD")).thenReturn(Optional.empty());
        when(persistenceService.findLatest("EUR/USD"))
                .thenReturn(Optional.of(FxRateEntity.builder()
                        .currencyPair("EUR/USD")
                        .rate(new BigDecimal("1.123400"))
                        .asOfTime(Instant.parse("2026-03-15T11:58:00Z"))
                        .provider("stub-provider")
                        .build()));

        FxRateQueryService service = new FxRateQueryService(
                normalizer,
                cacheService,
                persistenceService,
                TestConfigFactory.defaultProperties(),
                clock,
                new SimpleMeterRegistry());

        var result = service.getLatest("eur", "usd");

        assertTrue(result.fresh());
        assertFalse(result.fallbackUsed());
        verify(cacheService).putLatest(result);
    }

    /**
     * Verifies stale database data is returned as last known good fallback.
     */
    @Test
    void shouldReturnLastKnownGoodFallbackWhenStale() {
        CurrencyPairNormalizer normalizer = new CurrencyPairNormalizer();
        FxRateCacheService cacheService = Mockito.mock(FxRateCacheService.class);
        FxRatePersistenceService persistenceService = Mockito.mock(FxRatePersistenceService.class);
        Clock clock = Clock.fixed(Instant.parse("2026-03-15T12:00:00Z"), ZoneOffset.UTC);

        when(cacheService.getLatest("EUR/USD")).thenReturn(Optional.empty());
        when(persistenceService.findLatest("EUR/USD"))
                .thenReturn(Optional.of(FxRateEntity.builder()
                        .currencyPair("EUR/USD")
                        .rate(new BigDecimal("1.120000"))
                        .asOfTime(Instant.parse("2026-03-15T11:40:00Z"))
                        .provider("stub-provider")
                        .build()));

        FxRateQueryService service = new FxRateQueryService(
                normalizer,
                cacheService,
                persistenceService,
                TestConfigFactory.defaultProperties(),
                clock,
                new SimpleMeterRegistry());

        var result = service.getLatest("EUR", "USD");

        assertFalse(result.fresh());
        assertTrue(result.fallbackUsed());
    }
}
''')


t('provider/StubFxProviderClientTest.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.provider;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.github.dimitryivaniuta.gateway.fxrate.TestConfigFactory;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import org.junit.jupiter.api.Test;

/**
 * Tests for the deterministic stub provider.
 */
class StubFxProviderClientTest {

    /**
     * Verifies the stub returns one rate per configured pair.
     */
    @Test
    void shouldReturnConfiguredPairs() {
        StubFxProviderClient client = new StubFxProviderClient(
                TestConfigFactory.defaultProperties(),
                Clock.fixed(Instant.parse("2026-03-15T12:00:00Z"), ZoneOffset.UTC));
        assertEquals(2, client.fetchLatestRates().size());
    }
}
''')


t('repository/FxRateRepositoryTest.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.repository;

import static org.assertj.core.api.Assertions.assertThat;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateEntity;
import java.math.BigDecimal;
import java.time.Instant;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

/**
 * Data JPA tests for repository query behavior.
 */
@DataJpaTest
class FxRateRepositoryTest {

    @Autowired
    private FxRateRepository repository;

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
}
''')


t('api/FxRateResourceTest.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.api;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import com.github.dimitryivaniuta.gateway.fxrate.service.FxRateQueryService;
import java.math.BigDecimal;
import java.time.Instant;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

/**
 * Resource-level unit tests for latest FX responses.
 */
class FxRateResourceTest {

    /**
     * Verifies the resource maps service response fields correctly.
     */
    @Test
    void shouldMapServiceSnapshotToResponse() {
        FxRateQueryService service = Mockito.mock(FxRateQueryService.class);
        when(service.getLatest("EUR", "USD")).thenReturn(new FxRateSnapshot(
                "EUR/USD",
                new BigDecimal("1.120000"),
                Instant.parse("2026-03-15T12:00:00Z"),
                true,
                false,
                "stub-provider"));

        FxRateResponse response = new FxRateResource(service).latest("EUR", "USD");
        assertEquals("EUR/USD", response.currencyPair());
    }
}
''')


t('integration/FxRateServiceIntegrationTest.java', '''
package com.github.dimitryivaniuta.gateway.fxrate.integration;

import static org.assertj.core.api.Assertions.assertThat;

import com.redis.testcontainers.RedisContainer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.KafkaContainer;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

/**
 * Full-stack integration test using Testcontainers.
 */
@Testcontainers
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class FxRateServiceIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:17");

    @Container
    static RedisContainer redis = new RedisContainer("redis:8");

    @Container
    static KafkaContainer kafka = new KafkaContainer("apache/kafka-native:4.2.0");

    @Autowired
    private TestRestTemplate restTemplate;

    @DynamicPropertySource
    static void override(DynamicPropertyRegistry registry) {
        registry.add("spring.data.redis.host", redis::getHost);
        registry.add("spring.data.redis.port", redis::getRedisPort);
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }

    /**
     * Verifies the service context starts and actuator health is exposed.
     */
    @Test
    void shouldExposeHealthEndpoint() {
        String response = restTemplate.getForObject("/actuator/health", String.class);
        assertThat(response).contains("status");
    }
}
''')

add('src/test/resources/application.yml', '''
spring:
  jpa:
    hibernate:
      ddl-auto: validate
  flyway:
    enabled: true
app:
  fx:
    cache-ttl: PT30S
    freshness-sla: PT5M
    supported-pairs:
      - EUR/USD
      - USD/PLN
    provider:
      name: stub-provider
      base-url: https://provider.example.internal
      api-key: stub-key
    kafka:
      enabled: false
      topic: fx-rate-events
      consumer-group-id: test-group
    scheduled-ingestion:
      enabled: false
      fixed-delay: PT60S
''')

add('postman/FX-Rate-Service.postman_collection.json', '''
{
  "info": {
    "name": "FX Rate Service",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    "description": "Postman collection for the Banking FX Rate Service"
  },
  "item": [
    {
      "name": "Run manual ingestion",
      "request": {
        "method": "POST",
        "header": [],
        "url": "{{baseUrl}}/api/v1/fx-rates/admin/ingestions/run"
      }
    },
    {
      "name": "Get latest EUR/USD",
      "request": {
        "method": "GET",
        "header": [],
        "url": "{{baseUrl}}/api/v1/fx-rates/latest?base=EUR&quote=USD"
      }
    },
    {
      "name": "Get history EUR/USD",
      "request": {
        "method": "GET",
        "header": [],
        "url": "{{baseUrl}}/api/v1/fx-rates/history?base=EUR&quote=USD&from=2026-03-01T00:00:00Z&to=2026-03-31T23:59:59Z"
      }
    },
    {
      "name": "Actuator health",
      "request": {
        "method": "GET",
        "header": [],
        "url": "{{baseUrl}}/actuator/health"
      }
    },
    {
      "name": "Prometheus metrics",
      "request": {
        "method": "GET",
        "header": [],
        "url": "{{baseUrl}}/actuator/prometheus"
      }
    }
  ]
}
''')

add('postman/FX-Rate-Service.local.postman_environment.json', '''
{
  "name": "FX Rate Service Local",
  "values": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8080",
      "type": "default",
      "enabled": true
    }
  ],
  "_postman_variable_scope": "environment",
  "_postman_exported_at": "2026-03-15T00:00:00.000Z",
  "_postman_exported_using": "OpenAI"
}
''')

for path, content in files.items():
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding='utf-8')

print(f'Wrote {len(files)} files')
