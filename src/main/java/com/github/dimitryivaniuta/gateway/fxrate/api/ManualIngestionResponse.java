package com.github.dimitryivaniuta.gateway.fxrate.api;

/**
 * HTTP response DTO describing a manual ingestion execution outcome.
 *
 * @param insertedCount number of stored rates
 */
public record ManualIngestionResponse(int insertedCount) {
}
