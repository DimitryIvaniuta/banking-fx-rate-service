package com.github.dimitryivaniuta.gateway.fxrate.config;

import com.github.dimitryivaniuta.gateway.fxrate.api.FxRateAdminResource;
import com.github.dimitryivaniuta.gateway.fxrate.api.FxRateResource;
import com.github.dimitryivaniuta.gateway.fxrate.exception.GenericExceptionMapper;
import com.github.dimitryivaniuta.gateway.fxrate.exception.IllegalRequestExceptionMapper;
import com.github.dimitryivaniuta.gateway.fxrate.exception.RateNotFoundExceptionMapper;
import com.github.dimitryivaniuta.gateway.fxrate.exception.UnauthorizedExceptionMapper;
import com.github.dimitryivaniuta.gateway.fxrate.security.AdminApiKeyRequestFilter;
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
        register(AdminApiKeyRequestFilter.class);
        register(RateNotFoundExceptionMapper.class);
        register(IllegalRequestExceptionMapper.class);
        register(UnauthorizedExceptionMapper.class);
        register(GenericExceptionMapper.class);
    }
}
