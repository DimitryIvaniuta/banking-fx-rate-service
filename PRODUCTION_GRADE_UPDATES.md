# Production-grade updates implemented

## Implemented improvements

1. Idempotent ingestion with DB uniqueness on `(currency_pair, as_of_time, provider)`.
2. Deterministic `latest-as-of` API for reporting consistency.
3. PostgreSQL advisory lock around scheduled/manual ingestion to reduce duplicate polling across replicas.
4. Admin API key protection for operational endpoints.
5. Kafka consumer changed to manual acknowledgment with bounded retry and auto-commit disabled.
6. Correlation ID response header and MDC logging hook.
7. `Cache-Control: no-store` added at HTTP layer for sensitive time-based responses.
8. Supported pair whitelist enforcement.
9. Latest response enriched with `source` and `age`.
10. Postman collection updated for secured admin calls and as-of queries.
11. Docker Compose hardened with restart policies, persistent Postgres volume, and healthchecks.
12. Tests updated for new behavior.

## Still recommended for a next iteration

- Replace stub provider with a real HTTP adapter plus timeouts, auth rotation, and provider-specific schema validation.
- Add explicit Kafka DLT publishing if streaming ingestion becomes primary.
- Add OAuth2 or mTLS for admin endpoints in regulated deployments.
- Add OpenAPI/Swagger documentation.
- Add partitioning and retention strategy for long-lived FX history.
- Add deployment manifests (Helm/Kubernetes) and CI pipeline.

## Verification boundary in this environment

The project was upgraded and statically reviewed, but a full Maven build was not executed here because the execution environment has no outbound dependency download access.
