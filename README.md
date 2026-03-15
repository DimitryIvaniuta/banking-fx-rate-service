# banking-fx-rate-service

Production-grade FX Rate Service for banking/reporting workloads. It ingests multi-currency FX rates from an external provider by scheduled polling or Kafka streaming, stores immutable history in PostgreSQL, serves consistent latest and historical rates through JAX-RS endpoints, caches latest rates in Redis with TTL, and always returns a rate with `asOfTime` by falling back to the last known good record when fresh data is unavailable.

## GitHub repository description

Banking FX Rate Service (Java 21, Spring Boot 4, JAX-RS, PostgreSQL, Redis, Kafka KRaft): scheduled/streaming FX ingestion, immutable history, Redis latest-rate cache, freshness SLA and last-known-good fallback, idempotent persistence, advisory-lock protected polling, Actuator/Prometheus health monitoring, Flyway, tests, and Postman collection.

## What was improved in this revision

This revision upgrades the original implementation with production-grade hardening:

- **Idempotent ingestion**: duplicate provider/Kafka events are deduplicated with a database unique constraint and repository-level duplicate detection.
- **Deterministic reporting query**: new `latest-as-of` endpoint returns the latest rate effective at or before a requested instant.
- **Multi-instance safety**: scheduled/manual ingestion is protected by a PostgreSQL advisory lock to reduce duplicate polling across replicas.
- **Admin endpoint protection**: operational admin endpoints are protected with an API key filter.
- **Kafka reliability**: manual acknowledgment and bounded retry replace auto-commit behavior.
- **Operational tracing**: every response includes `X-Correlation-Id`, and public API responses disable downstream HTTP caching via `Cache-Control: no-store`.
- **Safer pair validation**: requests are limited to configured supported currency pairs.
- **Richer response metadata**: latest-rate responses now include `source` and `age`.

## Why this design

- **Consistency-first**: immutable FX history table plus deterministic `latest <= requested time` query.
- **Always return a rate**: stale-provider conditions fall back to the last known good DB record.
- **Operational safety**: Redis cache is an optimization, PostgreSQL remains the source of truth.
- **Banking-friendly observability**: actuator health, Prometheus metrics, freshness indicators, structured correlation IDs.
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
- Deterministic `latest-as-of` endpoint for reporting replay and backdated lookups
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
  "provider": "stub-provider",
  "source": "CACHE",
  "age": "PT12S"
}
```

### Get latest rate as of a requested effective time

`GET /api/v1/fx-rates/latest-as-of?base=EUR&quote=USD&at=2026-03-15T10:15:00Z`

### Get history

`GET /api/v1/fx-rates/history?base=EUR&quote=USD&from=2026-03-01T00:00:00Z&to=2026-03-15T23:59:59Z`

### Trigger manual ingestion

`POST /api/v1/fx-rates/admin/ingestions/run`

Required header when admin API key protection is enabled:

`X-Admin-Api-Key: change-me-in-production`

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
- `app.fx.admin.api-key-enabled`
- `app.fx.admin.api-key-header-name`
- `app.fx.admin.api-key`
- `app.fx.lock.enabled`
- `app.fx.lock.advisory-lock-id`

## Production notes

- Keep Redis TTL **shorter** than freshness SLA to avoid serving misleadingly fresh cache data.
- Use PostgreSQL as system of record and Redis only as cache.
- In real production, replace `StubFxProviderClient` with a bank-approved provider adapter.
- Rotate the admin API key through a secret manager, never through committed plain-text values.
- Consider an explicit DLT producer if Kafka streaming is a primary ingestion path.
- Consider table partitioning for multi-year retention.
- Consider stronger admin auth (mTLS or OAuth2) in regulated environments.

## Project structure

```text
src/main/java/com/github/dimitryivaniuta/gateway/fxrate
  api/            JAX-RS resources and DTOs
  config/         Jersey, scheduling, Kafka, Redis and app properties
  domain/         Entities and domain models
  exception/      Typed exceptions and mappers
  health/         Custom health indicators
  provider/       External provider adapters and ingestion DTOs
  repository/     Spring Data repositories
  security/       Admin operational endpoint protection
  service/        Query, ingestion, locking and cache orchestration
  web/            Correlation-id filter
```

## Postman

Import:

- `postman/FX-Rate-Service.postman_collection.json`
- `postman/FX-Rate-Service.local.postman_environment.json`

## Verification note

This repository is prepared to build with Maven and includes a Maven Wrapper, tests, Docker Compose, Flyway migrations, and Postman assets. In this chat environment I could not execute Maven because the container has no Maven installation and no outbound network access to download dependencies, so runtime verification here is limited to static consistency review.
