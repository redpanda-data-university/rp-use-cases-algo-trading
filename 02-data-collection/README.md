## Chapter 2 - Data Collection
In Chapter 2 of the Algorithmic Trading course, we explore how to collect various forms of market data (stock and crypto prices, market news, etc) and store that data in Redpanda.

## Setup
1. Clone this repository and `cd` into the current directory.
    ```sh
    cd 02-data-collection/
    ```
2. Create a Python virtual environment and install all dependencies.
    ```sh
    # create a virtual environment
    python3 -m venv .

    # activate the environment
    source bin/activate

    # install dependencies
    pip install -r requirements.txt
    ```
   
3. Start the Redpanda and Flink clusters.

    ```sh
    # start the containers
    docker-compose up -d

    # set the rpk alias
    alias rpk="docker exec -ti redpanda-1 rpk"

    # create the source topics
    rpk topic create price-updates market-news
    ```
    
    After running the commands...
    - The Flink web interface will be available at: http://localhost:8081.
    - The Redpanda console will be available at: http://localhost:8080.

4. [Sign up for an Alpaca account][alpaca-signup].
5. Create an API key from [the Alpaca Paper Trading dashboard][alpaca-paper-trading].
6. Replace the following lines in the [.env](.env) file with your API key and secret

    ```python
    ALPACA_API_KEY="<YOUR_ALPACA_KEY_ID>"
    ALPACA_SECRET_KEY="<YOUR_ALPACA_SECRET_KEY>"
    ```

[alpaca-signup]: https://alpaca.markets/
[alpaca-paper-trading]: https://app.alpaca.markets/paper/dashboard/overview

## Producing Data
Make sure to follow all of the steps in the **Setup** section first before running these commands.

1. Pull historical price data for the symbols and time range listed in the [config file](config/__init__.py).
    ```sh
    python -m examples.alpaca.historical_prices
    
    # example output
    Pulling historical data for symbols: ['AAPL', 'COIN']
    Produced 670 records to Redpanda topic: price-updates
    ```

2. Pull historical market news for the symbols and time range listed in the [config file](config/__init__.py).

    ```sh
    python -m examples.alpaca.historical_news
    
    # example output
    Pulling historical news data for symbols: ['AAPL', 'COIN']
    Produced 426 records to Redpanda topic: market-news
    ```

3. Pull live price data for the symbols listed in the [config file](config/__init__.py). Note: this will only work if running during trading hours.

    ```sh
    python -m examples.alpaca.live_prices
    ```

4. Pull live news for the symbols listed in the [config file](config/__init__.py). Note: this may not pull anything immediately.

    ```sh
    python -m examples.alpaca.live_news
    ```
    
## Creating Flink Tables
To work with the market data in Flink, first open a Flink SQL client with the following command:

```sh
docker-compose run sql-client
```

Then, run the following statements, individually, from the SQL prompt:

```sql
CREATE OR REPLACE TABLE price_updates (
    symbol VARCHAR,
    `open` FLOAT,
    high FLOAT,
    low FLOAT,
    `close` FLOAT,
    volume DECIMAL,
    trade_count FLOAT,
    vwap DECIMAL,
    minutely_return DECIMAL,
    cumulative_return DECIMAL,
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
```

Now, you can start working with the data. Here are some simple `SELECT` queries to get you started:


```sql
SELECT time_ltz, symbol, `close` FROM price_updates ;

SELECT time_ltz, symbol, headline FROM market_news ;
```

We'll dig more into the data itself in the next lesson.
