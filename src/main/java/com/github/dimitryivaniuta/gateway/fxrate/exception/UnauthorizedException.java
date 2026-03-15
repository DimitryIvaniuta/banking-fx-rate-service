package com.github.dimitryivaniuta.gateway.fxrate.exception;

/**
 * Raised when an operation requires admin authorization and the request is not authorized.
 */
public class UnauthorizedException extends RuntimeException {

    /**
     * Creates the exception.
     *
     * @param message error description
     */
    public UnauthorizedException(final String message) {
        super(message);
    }
}
