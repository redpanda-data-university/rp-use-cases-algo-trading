-- Create the price updates table
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

-- Create the market news table
CREATE OR REPLACE TABLE market_news (
    id BIGINT,
    author VARCHAR,
    headline VARCHAR,
    source VARCHAR,
    summary VARCHAR,
    `url` VARCHAR,
    symbol VARCHAR,
    sentiment DECIMAL,
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

-- Generate trade signals
CREATE TABLE raw_trade_signals (
  strategy STRING,
  strategy_version STRING,
  symbol VARCHAR(255) NOT NULL,
  close_price DOUBLE PRECISION,
  shares BIGINT,
  signal VARCHAR(4),
  metadata STRING,
  time_ltz TIMESTAMP(3),
    -- declare time_ltz as event time attribute and use 5 seconds delayed watermark strategy
    WATERMARK FOR time_ltz AS time_ltz - INTERVAL '5' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'trade-signals',
  'properties.bootstrap.servers' = 'redpanda-1:29092',
  'properties.group.id' = 'signals-consumer',
  'properties.auto.offset.reset' = 'earliest',
  'format' = 'json'
);

-- Insert into trade signals
INSERT INTO raw_trade_signals
WITH sentiment_strategy_signals AS (
    SELECT
        'sentiment' as strategy,
        '0.1.0' as strategy_version,
        price_updates.symbol,
        price_updates.`close` as close_price,
        5 as shares,
        CASE
            WHEN market_news.sentiment > 0.4 THEN 'BUY'
            WHEN market_news.sentiment < -0.4 THEN 'SELL'
            ELSE 'HOLD'
        END as signal,
        JSON_OBJECT(
            'headline' VALUE headline,
            'sentiment' VALUE sentiment
        ) AS metadata,
        price_updates.time_ltz as time_ltz
    FROM market_news
    JOIN price_updates
    ON price_updates.symbol = market_news.symbol
    -- use minute-level precision for the join
    AND DATE_FORMAT(price_updates.time_ltz, 'yyyy-MM-dd HH:mm:00') = DATE_FORMAT(market_news.time_ltz, 'yyyy-MM-dd HH:mm:00')
)
SELECT *
FROM sentiment_strategy_signals
WHERE signal IN ('BUY', 'SELL');


-- Single position trade signals
CREATE TABLE single_position_trade_signals (
  strategy STRING,
  strategy_version STRING,
  symbol VARCHAR(255) NOT NULL,
  close_price DOUBLE PRECISION,
  amount DOUBLE PRECISION,
  shares BIGINT,
  signal VARCHAR(4),
  metadata STRING,
  time_ltz TIMESTAMP(3),
    -- declare time_ltz as event time attribute and use 5 seconds delayed watermark strategy
    WATERMARK FOR time_ltz AS time_ltz - INTERVAL '5' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'trade-signals',
  'properties.bootstrap.servers' = 'redpanda-1:29092',
  'properties.group.id' = 'signals-consumer',
  'properties.auto.offset.reset' = 'earliest',
  'format' = 'json'
);

INSERT INTO single_position_trade_signals
WITH
    buy_sell AS (
        SELECT
            strategy,
            strategy_version,
            symbol,
            close_price,
            shares,
            signal,
            metadata,
            time_ltz,
            LAG(signal) OVER (PARTITION BY symbol ORDER BY time_ltz) as prev_signal
        FROM raw_trade_signals
    ),
    trades AS (
        SELECT
            strategy,
            strategy_version,
            symbol,
            close_price,
            shares,
            signal,
            metadata,
            time_ltz,
            CASE WHEN signal = 'SELL' THEN 5 ELSE -5 END as adjusted_shares
        FROM buy_sell
        WHERE 
            (signal = 'SELL' OR prev_signal <>'BUY') AND (signal = 'BUY' OR prev_signal <> 'SELL')
    )
    SELECT 
        strategy,
        strategy_version,
        symbol,
        close_price,
        close_price * adjusted_shares as amount,
        shares,
        signal,
        metadata,
        time_ltz
    FROM trades
    ORDER BY time_ltz;

-- Calculate profit and loss for a strategy (doesn't take broker fees into account)
SELECT
    SUM(amount) as profit_and_loss,
    COUNT(*) as trades,
    MAX(amount) as max_amount
FROM single_position_trade_signals
WHERE strategy = 'sentiment'
AND strategy_version = '0.1.0'
AND symbol = 'TSLA';

-- Break even test
SELECT
  SUM(amount)
FROM (VALUES
  ('TSLA', 'BUY', -100, '2022-09-14 09:54:00.000'),
  ('TSLA', 'SELL', 80, '2022-09-14 10:02:00.000'),
  ('TSLA', 'BUY', -140.0, '2022-09-14 10:05:00.000'),
  ('TSLA', 'SELL', 160.0, '2022-09-14 10:12:00.000')
) AS NameTable(symbol, signal, amount, time_ltz);

-- Profit test
SELECT
  SUM(amount)
FROM (VALUES
  ('TSLA', 'BUY', -100, '2022-09-14 09:54:00.000'),
  ('TSLA', 'SELL', 140, '2022-09-14 10:02:00.000'), -- $40 profit
  ('TSLA', 'BUY', -110.0, '2022-09-14 10:05:00.000'),
  ('TSLA', 'SELL', 110.0, '2022-09-14 10:12:00.000')
) AS NameTable(symbol, signal, amount, time_ltz);
