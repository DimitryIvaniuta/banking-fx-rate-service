package com.github.dimitryivaniuta.gateway.fxrate.provider;

import com.github.dimitryivaniuta.gateway.fxrate.domain.ProviderRate;
import java.util.List;

/**
 * Abstraction over an upstream FX market data provider.
 */
public interface FxProviderClient {

    /**
     * Pulls the latest available rates for supported currency pairs.
     *
     * @return provider rate list
     */
    List<ProviderRate> fetchLatestRates();
}
