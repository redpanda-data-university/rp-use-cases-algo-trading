-- Be sure to precreate the topics first with:
-- rpk topic create price-updates market-news trade-signals single-position-trade-signals

-- Create the price updates table if you haven't already.
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
    'properties.group.id' = 'dev',
    'properties.auto.offset.reset' = 'earliest',
    'format' = 'json'
);

-- Create the market news table if you haven't already.
CREATE OR REPLACE TABLE market_news (
    id BIGINT,
    author VARCHAR,
    headline VARCHAR,
    source VARCHAR,
    summary VARCHAR,
    data_provider VARCHAR,
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
    'properties.group.id' = 'dev',
    'properties.auto.offset.reset' = 'earliest',
    'format' = 'json'
);

-- Create a table for storing the raw trade signals. They are "raw" because they don't yet take
-- into account whether or not we currently have an open position when purchasing.
CREATE TABLE trade_signals (
  -- this table can hold trade signals from multiple strategies, so store the strategy name
  -- and version associated with each trade signal
  strategy STRING,
  strategy_version STRING,
  -- tthe stock symbol (e.g. TSLA) that the trade signal was generated for
  symbol VARCHAR(255) NOT NULL,
  -- the stock price at the time the trade signal was generated
  close_price DOUBLE PRECISION,
  -- the adjust amount (shares * close_price)
  amount DOUBLE PRECISION,
  -- the number of shares to sell or purchase
  shares BIGINT,
  -- a trade signal: BUY, SELL, or HOLD
  signal VARCHAR(4),
  -- additional metadata in the form of a JSON string "{\"headline\": \"TSLA exceeds Q4 expectations\"}"
  metadata STRING,
  data_provider STRING,
  -- the METADATA attribute ensures the ts for the Redpanda record is set to the time_ltz value
  time_ltz TIMESTAMP(3) METADATA FROM 'timestamp',
  -- declare time_ltz as event time attribute and use 5 seconds delayed watermark strategy
  WATERMARK FOR time_ltz AS time_ltz - INTERVAL '5' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'trade-signals',
  'properties.bootstrap.servers' = 'redpanda-1:29092',
  'properties.group.id' = 'dev',
  'properties.auto.offset.reset' = 'earliest',
  'format' = 'json'
);

-- Implement the sentiment strategy by creating the following signals:
-- BUY whenever sentiment > 0.4
-- SELL whenever sentiment < -0.4
INSERT INTO trade_signals
WITH 
  sentiment_strategy_signals AS (
    SELECT
        -- name and version of this strategy
        'sentiment' as strategy,
        '0.1.0' as strategy_version,
        market_news.symbol,
        -- include the close price so we can see what the stock price was at the time
        -- the signal was generated
        0 as close_price,
        -- configure the number of shares to buy or sell. this is our "stake"
        5 as shares,
        -- implement the logic for the sentiment strategy
        CASE
            WHEN market_news.sentiment > 0.4 THEN 'BUY'
            WHEN market_news.sentiment < -0.4 THEN 'SELL'
            ELSE 'HOLD'
        END as signal,
        -- capture some additional metadata about the article that triggered the trade
        -- signal. future strategies could have their own, unique metadata fields
        JSON_OBJECT(
            'headline' VALUE headline,
            'sentiment' VALUE sentiment
        ) AS metadata,
        data_provider,
        market_news.time_ltz as time_ltz
    FROM market_news
)
SELECT
  strategy,
  strategy_version,
  symbol,
  close_price,
  -- create a signed version of the amount (e.g. $500, -$500) based on the signal.
  -- this will help with backtesting later
  CASE
    WHEN signal = 'SELL' THEN close_price * shares
    ELSE close_price * shares * -1
  END as amount,
  shares,
  signal,
  metadata,
  data_provider,
  time_ltz
FROM sentiment_strategy_signals
WHERE signal IN ('BUY', 'SELL');


-- Create a table for storing the cleaned trade signals. The idea is to filter down
-- the raw trade signals so that we only BUY if we don't currently have a position in
-- the stock.
CREATE TABLE single_position_trade_signals (
  strategy STRING,
  strategy_version STRING,
  symbol VARCHAR(255) NOT NULL,
  close_price DOUBLE PRECISION,
  amount DOUBLE PRECISION,
  shares BIGINT,
  signal VARCHAR(4),
  metadata STRING,
  data_provider STRING,
  -- the METADATA attribute ensures the ts for the Redpanda record is set to the time_ltz value
  time_ltz TIMESTAMP(3) METADATA FROM 'timestamp',
  -- declare time_ltz as event time attribute and use 5 seconds delayed watermark strategy
  WATERMARK FOR time_ltz AS time_ltz - INTERVAL '5' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'single-position-trade-signals',
  'properties.bootstrap.servers' = 'redpanda-1:29092',
  'properties.group.id' = 'dev',
  'properties.auto.offset.reset' = 'earliest',
  'format' = 'json'
);

-- Insert the single-position trade signals. These will be the signals we actually act upon
INSERT INTO single_position_trade_signals
WITH
    raw_signals AS (
        SELECT
            *,
            -- get the signal of the record right before the current record
            LAG(signal) OVER (PARTITION BY symbol ORDER BY time_ltz) as prev_signal
        FROM trade_signals
    )
    SELECT
        strategy,
        strategy_version,
        symbol,
        close_price,
        amount,
        shares,
        signal,
        metadata,
        data_provider,
        time_ltz
    FROM raw_signals
    WHERE
        -- a BUY is valid anytime, as long as the previous signal wasn't a BUY.
        -- e.g. the previous_signal could be a SELL (open position) or NULL (no position)
        -- for a BUY signal to be issued
        (signal = 'BUY' AND prev_signal <> 'BUY')
        OR
        -- a SELL is valid only if the previous signal was a BUY
        (signal = 'SELL' AND prev_signal = 'BUY');

--------- (Optional) Bonus queries ---------

-- Calculate profit and loss for a strategy
-- Note: if you aren't using a commission free broker, you'll need to take
-- the broker fees into account (not shown below since we assume commission-free)
SELECT
    SUM(amount) as net_profit,
    COUNT(*) as trades
FROM single_position_trade_signals
WHERE strategy = 'sentiment'
AND strategy_version = '0.1.0'
AND symbol = 'TSLA'
AND data_provider = 'alpaca';

-- Intuition around the Profit / Loss query we showed earlier

-- Profit test
SELECT
  SUM(amount) as net_profit,
  COUNT(*) as trades
FROM (VALUES
  ('TSLA', 'BUY', -100, '2022-09-14 09:54:00.000'),
  ('TSLA', 'SELL', 140, '2022-09-14 10:02:00.000'), -- $40 profit
  ('TSLA', 'BUY', -110.0, '2022-09-14 10:05:00.000'),
  ('TSLA', 'SELL', 120.0, '2022-09-14 10:12:00.000') -- $10 profit
) AS NameTable(symbol, signal, amount, time_ltz);

-- Loss test
SELECT
  SUM(amount) as net_profit,
  COUNT(*) as trades
FROM (VALUES
  ('TSLA', 'BUY', -100, '2022-09-14 09:54:00.000'),
  ('TSLA', 'SELL', 90, '2022-09-14 10:02:00.000'), -- $10 loss
  ('TSLA', 'BUY', -110.0, '2022-09-14 10:05:00.000'),
  ('TSLA', 'SELL', 95.0, '2022-09-14 10:12:00.000') -- $15 loss
) AS NameTable(symbol, signal, amount, time_ltz);

-- Break even test
SELECT
  SUM(amount) as net_profit,
  COUNT(*) as trades
FROM (VALUES
  ('TSLA', 'BUY', -100, '2022-09-14 09:54:00.000'),
  ('TSLA', 'SELL', 80, '2022-09-14 10:02:00.000'), -- $20 loss
  ('TSLA', 'BUY', -140.0, '2022-09-14 10:05:00.000'),
  ('TSLA', 'SELL', 160.0, '2022-09-14 10:12:00.000') -- $20 gain
) AS NameTable(symbol, signal, amount, time_ltz);
