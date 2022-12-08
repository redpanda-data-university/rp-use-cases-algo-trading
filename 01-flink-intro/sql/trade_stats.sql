SET 'pipeline.name' = 'Trade Stats';

CREATE TABLE trades (
    symbol VARCHAR,
    price DOUBLE,
    size DOUBLE,
    proc_time AS PROCTIME()  -- processing time
    -- event_time TIMESTAMP(3), -- event time
    -- WATERMARK FOR event_time AS event_time - INTERVAL '10' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'trades',
    'properties.bootstrap.servers' = 'redpanda-1:29092',
    'properties.group.id' = 'test-group',
    'properties.auto.offset.reset' = 'earliest',
    'format' = 'json'
);

CREATE TABLE trade_stats WITH (
    'connector' = 'kafka',
    'topic' = 'trade-stats',
    'properties.bootstrap.servers' = 'redpanda-1:29092',
    'format' = 'json'
) AS
SELECT
    symbol,
    AVG(price) AS avg_price,
    AVG(size) AS avg_size,
    TUMBLE_START(proc_time, INTERVAL '60' SECONDS) AS window_start,
    TUMBLE_END(proc_time, INTERVAL '60' SECONDS) AS window_end
FROM trades
GROUP BY
    TUMBLE(proc_time, INTERVAL '60' SECONDS),
    symbol;
