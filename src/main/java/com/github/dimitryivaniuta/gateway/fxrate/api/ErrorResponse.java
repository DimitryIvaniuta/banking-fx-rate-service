package com.github.dimitryivaniuta.gateway.fxrate.api;

import java.time.Instant;

/**
 * Standardized API error payload.
 *
 * @param timestamp error creation time
 * @param message human-readable message
 */
public record ErrorResponse(Instant timestamp, String message) {
}
