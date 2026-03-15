package com.github.dimitryivaniuta.gateway.fxrate.security;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.when;

import com.github.dimitryivaniuta.gateway.fxrate.TestConfigFactory;
import com.github.dimitryivaniuta.gateway.fxrate.exception.UnauthorizedException;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.core.UriInfo;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

/**
 * Tests for admin API key protection.
 */
class AdminApiKeyRequestFilterTest {

    /**
     * Verifies an admin request is rejected when the header is missing.
     */
    @Test
    void shouldRejectMissingApiKeyForAdminRequest() {
        AdminApiKeyRequestFilter filter = new AdminApiKeyRequestFilter(TestConfigFactory.defaultProperties());
        ContainerRequestContext context = Mockito.mock(ContainerRequestContext.class);
        UriInfo uriInfo = Mockito.mock(UriInfo.class);
        when(context.getUriInfo()).thenReturn(uriInfo);
        when(uriInfo.getPath()).thenReturn("api/v1/fx-rates/admin/ingestions/run");

        assertThrows(UnauthorizedException.class, () -> filter.filter(context));
    }

    /**
     * Verifies a correct admin API key allows the request.
     */
    @Test
    void shouldAllowValidApiKeyForAdminRequest() {
        AdminApiKeyRequestFilter filter = new AdminApiKeyRequestFilter(TestConfigFactory.defaultProperties());
        ContainerRequestContext context = Mockito.mock(ContainerRequestContext.class);
        UriInfo uriInfo = Mockito.mock(UriInfo.class);
        when(context.getUriInfo()).thenReturn(uriInfo);
        when(uriInfo.getPath()).thenReturn("api/v1/fx-rates/admin/ingestions/run");
        when(context.getHeaderString("X-Admin-Api-Key")).thenReturn("test-admin-key");

        assertDoesNotThrow(() -> filter.filter(context));
    }
}
