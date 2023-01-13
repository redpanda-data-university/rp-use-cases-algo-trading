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
4. Open a Flink SQL client with the following command:
  ```sh
  docker-compose run sql-client
  ```

## Create Trade Signals
Create trade signals based on the sentiment of Tesla (TSLA) headlines. To do this, run the queries in the [sql/strategy.sql](03-strategy-testing/sql/strategy.sql) file. Read the query comments to understand what each step is doing.

This will populate a table called `single_position_trade_signals` with all of the trade signals.

```sql
SELECT * FROM single_position_trade_signals LIMIT 10 ;
```
Once you have executed all of the queries, you can exit the Flink SQL client by typing `QUIT;`. The queries will continue to run in Flink, which you can see from the Flink UI:

http://localhost:8081/#/job/running

Flink will store all of the trade signals in a topic called `trade-signals`. You can inspect this topic from a separate shell using the following command:

```sh
rpk topic consume trade-signals -n 3
```

## Clean up
Once you are finished, clean up your environment like so:

```sh
docker-compose down --volumes --remove-orphans
```
