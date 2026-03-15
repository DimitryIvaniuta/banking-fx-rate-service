package com.github.dimitryivaniuta.gateway.fxrate.api;

import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateHistoryItem;
import com.github.dimitryivaniuta.gateway.fxrate.domain.FxRateSnapshot;
import com.github.dimitryivaniuta.gateway.fxrate.service.FxRateQueryService;
import jakarta.validation.constraints.NotBlank;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import java.time.Instant;
import java.util.List;
import org.springframework.stereotype.Component;

/**
 * JAX-RS resource exposing public FX read APIs.
 */
@Component
@Path("/api/v1/fx-rates")
@Produces(MediaType.APPLICATION_JSON)
public class FxRateResource {

    private final FxRateQueryService fxRateQueryService;

    /**
     * Creates the resource.
     *
     * @param fxRateQueryService query service
     */
    public FxRateResource(final FxRateQueryService fxRateQueryService) {
        this.fxRateQueryService = fxRateQueryService;
    }

    /**
     * Returns the latest usable FX rate for the requested pair.
     *
     * @param base base currency
     * @param quote quote currency
     * @return latest rate response
     */
    @GET
    @Path("/latest")
    public FxRateResponse latest(
            @QueryParam("base") @NotBlank final String base,
            @QueryParam("quote") @NotBlank final String quote) {
        return toResponse(fxRateQueryService.getLatest(base, quote));
    }

    /**
     * Returns the latest known rate effective at or before the requested instant.
     *
     * @param base base currency
     * @param quote quote currency
     * @param at effective-time upper bound in ISO-8601 format
     * @return deterministic historical snapshot response
     */
    @GET
    @Path("/latest-as-of")
    public FxRateResponse latestAsOf(
            @QueryParam("base") @NotBlank final String base,
            @QueryParam("quote") @NotBlank final String quote,
            @QueryParam("at") final String at) {
        return toResponse(fxRateQueryService.getLatestAsOf(base, quote, Instant.parse(at)));
    }

    /**
     * Returns historical FX rates for the requested time window.
     *
     * @param base base currency
     * @param quote quote currency
     * @param from lower bound inclusive
     * @param to upper bound inclusive
     * @return history response
     */
    @GET
    @Path("/history")
    public FxRateHistoryResponse history(
            @QueryParam("base") @NotBlank final String base,
            @QueryParam("quote") @NotBlank final String quote,
            @QueryParam("from") final String from,
            @QueryParam("to") final String to) {
        List<FxRateHistoryItem> items = fxRateQueryService.getHistory(base, quote, Instant.parse(from), Instant.parse(to));
        return new FxRateHistoryResponse(items.stream()
                .map(item -> new FxRateHistoryResponseItem(item.currencyPair(), item.rate(), item.asOfTime(), item.provider()))
                .toList());
    }

    private FxRateResponse toResponse(final FxRateSnapshot snapshot) {
        return new FxRateResponse(
                snapshot.currencyPair(),
                snapshot.rate(),
                snapshot.asOfTime(),
                snapshot.fresh(),
                snapshot.fallbackUsed(),
                snapshot.provider(),
                snapshot.source(),
                snapshot.age());
    }
}
