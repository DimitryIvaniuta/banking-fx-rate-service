package com.github.dimitryivaniuta.gateway.fxrate.exception;

/**
 * Raised when request input is syntactically valid but semantically invalid.
 */
public class IllegalRequestException extends RuntimeException {

    /**
     * Creates the exception.
     *
     * @param message error description
     */
    public IllegalRequestException(final String message) {
        super(message);
    }
}
