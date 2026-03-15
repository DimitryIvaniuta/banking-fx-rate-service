CREATE TABLE fx_rates (
    id BIGSERIAL PRIMARY KEY,
    currency_pair VARCHAR(16) NOT NULL,
    rate NUMERIC(20, 10) NOT NULL,
    as_of_time TIMESTAMP WITH TIME ZONE NOT NULL,
    provider VARCHAR(64) NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_fx_rates_pair_asof_desc ON fx_rates(currency_pair, as_of_time DESC);
CREATE INDEX idx_fx_rates_asof_desc ON fx_rates(as_of_time DESC);
