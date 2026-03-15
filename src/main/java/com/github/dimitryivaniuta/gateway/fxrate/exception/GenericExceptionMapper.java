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
