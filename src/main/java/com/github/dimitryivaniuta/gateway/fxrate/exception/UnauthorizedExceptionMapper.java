package com.github.dimitryivaniuta.gateway.fxrate.exception;

import com.github.dimitryivaniuta.gateway.fxrate.api.ErrorResponse;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import java.time.Instant;

/**
 * Maps {@link UnauthorizedException} to a 401 response.
 */
@Provider
public class UnauthorizedExceptionMapper implements ExceptionMapper<UnauthorizedException> {

    /**
     * Converts the exception to a JAX-RS response.
     *
     * @param exception source exception
     * @return HTTP 401 response
     */
    @Override
    public Response toResponse(final UnauthorizedException exception) {
        return Response.status(Response.Status.UNAUTHORIZED)
                .entity(new ErrorResponse(Instant.now(), exception.getMessage()))
                .build();
    }
}
