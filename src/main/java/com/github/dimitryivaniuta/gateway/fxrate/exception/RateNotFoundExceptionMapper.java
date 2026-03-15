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
