## Chapter 3 - Strategy Testing
In Chapter 3 of the Algorithmic Trading course, we explore how to develop and test a trading strategy with Redpanda and Flink SQL.

## Prerequisites
1. Complete the setup steps in the [Getting Started section](../README.md#getting-started)
2. Confirm you have a Python environment setup, the Docker services running, and an Alpaca API key saved in the [.env](../.env) file
3. Complete [the steps in Chapter 2](../02-data-collection/README.md), and ensure you have data in the source topics

  ```sh
  rpk topic consume price-updates -n 1
  rpk topic consume market-news -n 1
  ```
  
4. Create two additional topics to store trade signals:

  ```sh
  rpk topic create raw-trade-signals trade-signals
  ```
5. Open a Flink SQL client with the following command:
  ```sh
  docker-compose run sql-client
  ```

## Create Trade Signals
Create trade signals based on the sentiment of Tesla (TSLA) headlines. To do this, run the queries in the [sql/strategy.sql](sql/strategy.sql) file. Read the query comments to understand what each step is doing.

This will populate a table called `single_position_trade_signals` with all of the trade signals.

```sql
SELECT * FROM single_position_trade_signals LIMIT 10 ;
```
Once you have executed all of the queries, you can exit the Flink SQL client by typing `QUIT;`. The queries will continue to run in Flink, which you can see from the Flink UI:

http://localhost:8081/#/job/running

Flink will store all of the trade signals in a topic called `trade-signals`. You can inspect this topic from a separate shell using the following command:

```sh
rpk topic consume trade-signals -n 1
```

Here's an example record:

```json
{
  "strategy": "sentiment",
  "strategy_version": "0.1.0",
  "symbol": "TSLA",
  "close_price": 293.20001220703125,
  "amount": 1466.0000610351562,
  "shares": 5,
  "signal": "SELL",
  "metadata": "{\"headline\":\"Tesla, Meta, NVIDIA And Other Big Losers From Tuesday\",\"sentiment\":-1}"
}
```

## Submit Orders
To turn the trade signals into actual orders, you can run the following script:

```
python -m examples.alpaca.submit_orders
```

This script will read the trade signals you created with Redpanda and Flink SQL, and turn them into market order requests. You will likely see the following message the first time you run this script:

```
Trade signal consumed successfully, but the signal has expired.
Simulate news using the the simulate_news script, or wait until more recent news is seen for this symbol.
```

That's expected, since the trade signals were created from historical data and you don't want to submit orders if the signal has expired. See the next section for info on how to simulate a news article and submit an order from a fresh trade signal.

## Simulate News
With the `submit_orders` script still running, open a new tab, and run the following:

```sh
cd 03-strategy-testing

python -m examples.alpaca.simulate_news
```

When prompted, enter `TSLA` as the symbol, and either a positive or negative headline to trigger a trade signal. Here's an example of a postive headline that meets the positive sentiment threshold for generating a trade signal:

```
Tesla, Nio Battery-Supplier CATL Expects Q3 Net Profit To Triple, Shares Jump 6%
```

Here's an example of a negative headline that meets the negative sentiment threshold:

```
Tesla Analyst Warns Situation Could Turn Uglier
```

If you're running this during trading hours for TSLA, then you should see a market order get submitted in your Alpaca paper trading account.

## Clean up
Once you are finished, clean up your environment like so:

```sh
docker-compose down --volumes --remove-orphans
```
