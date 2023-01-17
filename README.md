# Redpanda University
[Redpanda University][rpu] is a series of courses that will teach you the basics of event streaming, and will help you gain hands-on experience with a new data streaming platform called [Redpanda][rp].

## RP Use Cases: Algorithmic Trading
This repository contains code examples for the Algorithmic Trading course from [Redpanda University][rpu]. The following chapters are included:

- [Chapter 1: Flink intro][flink-intro] (creating Redpanda-backed Flink pipelines)
- [Chapter 2: Data Collection][data-collection]
- [Chapter 3: Strategy Testing][strategy-testing]


[rp]: https://redpanda.com/
[rpu]: https://university.redpanda.com/

[flink-intro]: /01-flink-intro
[data-collection]: /02-data-collection
[strategy-testing]: /03-strategy-testing

## Getting Started
There are three steps you need to get started. It should take < 5 minutes.

1. Setup a Python environment
2. Start the Docker services
3. Get an Alpaca API key

See the follow sections for detailed instructions.

### Setup a Python Environment
A Python environment is needed to run the producer scripts to get the financial and market news data into Redpanda, and for running a separate consumer to process trade signals.

Create a Python virtual environment and install all dependencies.
```sh
# create a virtual environment
python3 -m venv .

# activate the environment
source bin/activate

# install dependencies
pip install -r requirements.txt
```

### Start the Docker Services
We need a Redpanda cluster to store the data, and a Flink cluster to create trade signals using Flink SQL. To start the Redpanda and Flink clusters, run the following commands:

```sh
docker-compose build
docker-compose up -d
```

#### Redpanda
Once the clusters are running, Redpanda console will be available at: http://localhost:8080.

To interact with Redpanda from the commandline, set the following alias so that any invocation of `rpk` uses the pre-installed version in your local Redpanda cluster:

```sh
alias rpk="docker exec -ti redpanda-1 rpk"
```

From here, you can use `rpk` to interact with the Redpanda cluster:

```sh
rpk cluster info
```

#### Flink
The Flink web interface will be available at: http://localhost:8081.

To start a Flink SQL client, run the following command:

```sql
docker-compose run sql-client
```

You can verify that everything is running properly in the Flink cluster by running the following SQL statements from the prompt:

```sql
SET 'pipeline.name' = 'Hello, Flink';

SELECT
  CONCAT('Hello, ', name) as greeting
FROM
  (VALUES ('Flink'), ('Redpanda'), ('Alpaca')) AS NameTable(name)
GROUP BY name;
```

Each chapter will contain a set of queries for you to execute. Please see in the [individual chapters](#rp-use-cases-algorithmic-trading) for more information.

### Get an Alpaca API Key
We're using Alpaca as the source for market data.

1. [Sign up for an Alpaca account here][alpaca-signup].
2. Create an API key from [the Alpaca Paper Trading dashboard][alpaca-paper-trading].
3. Replace the following lines in the [.env file](.env) with your API key and secret

    ```python
    ALPACA_API_KEY="<YOUR_ALPACA_KEY_ID>"
    ALPACA_SECRET_KEY="<YOUR_ALPACA_SECRET_KEY>"
    ```

[alpaca-signup]: https://alpaca.markets/
[alpaca-paper-trading]: https://app.alpaca.markets/paper/dashboard/overview
[python]: https://www.python.org/downloads/
