package com.github.dimitryivaniuta.gateway.fxrate.exception;

/**
 * Raised when no usable FX rate exists for the requested pair.
 */
public class RateNotFoundException extends RuntimeException {

    /**
     * Creates the exception.
     *
     * @param message error description
     */
    public RateNotFoundException(final String message) {
        super(message);
    }
}
