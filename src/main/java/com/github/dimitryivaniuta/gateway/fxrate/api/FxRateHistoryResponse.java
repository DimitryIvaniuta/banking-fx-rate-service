package com.github.dimitryivaniuta.gateway.fxrate.api;

import java.util.List;

/**
 * HTTP response DTO wrapping FX history items.
 *
 * @param items ordered list of historical rates
 */
public record FxRateHistoryResponse(List<FxRateHistoryResponseItem> items) {
}
