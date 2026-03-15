package com.github.dimitryivaniuta.gateway.fxrate.api;

import com.github.dimitryivaniuta.gateway.fxrate.service.FxIngestionLockService;
import com.github.dimitryivaniuta.gateway.fxrate.service.FxRateIngestionService;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import org.springframework.stereotype.Component;

/**
 * JAX-RS resource exposing operational administration endpoints.
 */
@Component
@Path("/api/v1/fx-rates/admin")
@Produces(MediaType.APPLICATION_JSON)
public class FxRateAdminResource {

    private final FxRateIngestionService fxRateIngestionService;
    private final FxIngestionLockService fxIngestionLockService;

    /**
     * Creates the resource.
     *
     * @param fxRateIngestionService ingestion service
     * @param fxIngestionLockService advisory lock service
     */
    public FxRateAdminResource(
            final FxRateIngestionService fxRateIngestionService,
            final FxIngestionLockService fxIngestionLockService) {
        this.fxRateIngestionService = fxRateIngestionService;
        this.fxIngestionLockService = fxIngestionLockService;
    }

    /**
     * Manually triggers a provider polling cycle.
     *
     * @return insertion summary
     */
    @POST
    @Path("/ingestions/run")
    public ManualIngestionResponse runIngestion() {
        return new ManualIngestionResponse(
                fxIngestionLockService.runWithLock("manual-provider-poll", fxRateIngestionService::ingestFromProvider));
    }
}
