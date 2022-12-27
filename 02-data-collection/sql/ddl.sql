CREATE OR REPLACE TABLE price_updates (
    symbol VARCHAR,
    `open` FLOAT,
    high FLOAT,
    low FLOAT,
    `close` FLOAT,
    volume DECIMAL,
    trade_count FLOAT,
    vwap DECIMAL,
    `timestamp` BIGINT,
    time_ltz AS TO_TIMESTAMP_LTZ(`timestamp`, 3),
    -- declare time_ltz as event time attribute and use 5 seconds delayed watermark strategy
    WATERMARK FOR time_ltz AS time_ltz - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'price-updates',
    'properties.bootstrap.servers' = 'redpanda-1:29092',
    'properties.group.id' = 'test-group2',
    'properties.auto.offset.reset' = 'earliest',
    'format' = 'json'
);

CREATE OR REPLACE TABLE market_news (
    id BIGINT,
    author VARCHAR,
    headline VARCHAR,
    source VARCHAR,
    summary VARCHAR,
    `url` VARCHAR,
    symbol VARCHAR,
    timestamp_ms BIGINT,
    time_ltz AS TO_TIMESTAMP_LTZ(timestamp_ms, 3),
    -- declare time_ltz as event time attribute and use 5 seconds delayed watermark strategy
    WATERMARK FOR time_ltz AS time_ltz - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'market-news',
    'properties.bootstrap.servers' = 'redpanda-1:29092',
    'properties.group.id' = 'test-group2',
    'properties.auto.offset.reset' = 'earliest',
    'format' = 'json'
);
