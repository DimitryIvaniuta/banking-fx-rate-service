package com.github.dimitryivaniuta.gateway.fxrate.security;

import com.github.dimitryivaniuta.gateway.fxrate.config.AppProperties;
import com.github.dimitryivaniuta.gateway.fxrate.exception.UnauthorizedException;
import jakarta.annotation.Priority;
import jakarta.ws.rs.Priorities;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerRequestFilter;
import jakarta.ws.rs.ext.Provider;
import org.springframework.stereotype.Component;

/**
 * Protects admin endpoints with a simple API key suitable for internal operational use.
 */
@Component
@Provider
@Priority(Priorities.AUTHENTICATION)
public class AdminApiKeyRequestFilter implements ContainerRequestFilter {

    private final AppProperties appProperties;

    /**
     * Creates the filter.
     *
     * @param appProperties application properties
     */
    public AdminApiKeyRequestFilter(final AppProperties appProperties) {
        this.appProperties = appProperties;
    }

    /**
     * Verifies the configured admin API key when the request targets an admin endpoint.
     *
     * @param requestContext JAX-RS request context
     */
    @Override
    public void filter(final ContainerRequestContext requestContext) {
        String path = requestContext.getUriInfo().getPath();
        if (!path.startsWith("api/v1/fx-rates/admin") || !appProperties.admin().apiKeyEnabled()) {
            return;
        }

        String actual = requestContext.getHeaderString(appProperties.admin().apiKeyHeaderName());
        String expected = appProperties.admin().apiKey();
        if (expected == null || expected.isBlank() || !expected.equals(actual)) {
            throw new UnauthorizedException("Admin API key is missing or invalid");
        }
    }
}
