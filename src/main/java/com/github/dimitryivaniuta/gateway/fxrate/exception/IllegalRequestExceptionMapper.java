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
