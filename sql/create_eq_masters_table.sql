CREATE TABLE eq_masters (
    scrip_code UInt32,
    trading_symbol String,
    ticker String,
    description String,
    instrument_type UInt8,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (scrip_code, trading_symbol)
PARTITION BY toYYYYMM(created_at);
