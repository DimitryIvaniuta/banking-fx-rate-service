ALTER TABLE fx_rates
    ADD CONSTRAINT uk_fx_rates_pair_asof_provider UNIQUE (currency_pair, as_of_time, provider);
