CREATE TABLE eq_ohlcv (
    ticker String,
    datetime DateTime,
    open Float32,
    high Float32,
    low Float32,
    close Float32,
    volume UInt64,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (ticker, datetime)
PARTITION BY toYYYYMM(datetime)