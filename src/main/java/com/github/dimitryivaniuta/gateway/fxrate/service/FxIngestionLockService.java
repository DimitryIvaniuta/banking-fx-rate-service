package com.github.dimitryivaniuta.gateway.fxrate.service;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import java.util.function.Supplier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

/**
 * Provides a PostgreSQL advisory lock to prevent duplicate scheduled ingestion across replicas.
 */
@Service
public class FxIngestionLockService {

    private final JdbcTemplate jdbcTemplate;
    private final AppProperties appProperties;

    /**
     * Creates the lock service.
     *
     * @param jdbcTemplate JDBC template
     * @param appProperties application properties
     */
    public FxIngestionLockService(final JdbcTemplate jdbcTemplate, final AppProperties appProperties) {
        this.jdbcTemplate = jdbcTemplate;
        this.appProperties = appProperties;
    }

    /**
     * Executes the supplied work only when the advisory lock is acquired.
     *
     * @param actionName logical action name for diagnostics
     * @param supplier work supplier
     * @return work result or 0 when another instance currently owns the lock
     */
    public int runWithLock(final String actionName, final Supplier<Integer> supplier) {
        if (!appProperties.lock().enabled()) {
            return supplier.get();
        }

        Boolean locked = jdbcTemplate.queryForObject(
                "select pg_try_advisory_lock(?)", Boolean.class, appProperties.lock().advisoryLockId());
        if (!Boolean.TRUE.equals(locked)) {
            return 0;
        }
        try {
            return supplier.get();
        } finally {
            jdbcTemplate.queryForObject(
                    "select pg_advisory_unlock(?)", Boolean.class, appProperties.lock().advisoryLockId());
        }
    }
}
