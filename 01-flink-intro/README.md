## Chapter 1 - Flink Introduction
In Chapter 1 of the Algorithmic Trading course, we explore how to use Flink for creating Redpanda-backed stream processing pipelines.

The queries we executed are located in the [sql][sql] directory. There are two ways to execute these queries, which you can see in the sections below. However, before you execute the queries, be sure to create the source / sink topics:

```sh
# start the containers
docker-compose up -d

# set the rpk alias
alias rpk="docker exec -ti redpanda-1 rpk"

# create the source / sink topics
rpk topic create names greetings trade trade-stats
```

If you want to pre-populate the source topics, run:

```sh
rpk topic produce names

# from the prompt, copy/paste the following records
{"name": "Flink", "event_time": "2022-12-06 02:00:00"}
{"name": "Redpanda", "event_time": "2022-12-06 03:00:00"}
{"name": "Alpaca", "event_time":"2022-12-06 04:00:00"}
```

```sh
rpk topic produce trades

# from the prompt, copy/paste the following records
{"symbol": "ETH/USD", "price": 1263.44, "size": 0.5723, "timestamp": "2022-12-06 01:58:46.924000+00:00"}
{"symbol": "ETH/USD", "price": 1263.2, "size": 0.37298, "timestamp": "2022-12-06 01:58:46.924000+00:00"}
{"symbol": "ETH/USD", "price": 1263.42, "size": 0.08, "timestamp": "2022-12-06 01:59:55.040000+00:00"}
{"symbol": "ETH/USD", "price": 1263.31, "size": 0.01597, "timestamp": "2022-12-06 02:01:03.077000+00:00"}
{"symbol": "ETH/USD", "price": 1263.26, "size": 0.3, "timestamp": "2022-12-06 02:01:05.632000+00:00"}
{"symbol": "ETH/USD", "price": 1263.47, "size": 0.4, "timestamp": "2022-12-06 02:01:38.093000+00:00"}
{"symbol": "ETH/USD", "price": 1263.48, "size": 0.78, "timestamp": "2022-12-06 02:01:38.093000+00:00"}
{"symbol": "ETH/USD", "price": 1263.56, "size": 1.45261, "timestamp": "2022-12-06 02:01:38.093000+00:00"}
{"symbol": "ETH/USD", "price": 1263.56, "size": 2.37243, "timestamp": "2022-12-06 02:01:40.091000+00:00"}
{"symbol": "ETH/USD", "price": 1263.89, "size": 0.26019, "timestamp": "2022-12-06 02:01:40.091000+00:00"}
{"symbol": "ETH/USD", "price": 1263.92, "size": 0.70452, "timestamp": "2022-12-06 02:01:41.091000+00:00"}
{"symbol": "ETH/USD", "price": 1263.97, "size": 1.9281, "timestamp": "2022-12-06 02:01:41.091000+00:00"}
```

### Run queries from the CLI
Start a Flink SQL CLI session:

```sh
docker-compose run sql-client
```

You will be dropped into a prompt:

```sql
Flink SQL>
```

From here, simply copy and paste [the queries][sql]. After submitting the query, you can check the job status at http://localhost:8081/.

### Run queries from a file
The queries have already been mounted into the Flink containers, so you'll just need to uncomment the appropriate sections from the [docker-compose.yaml][docker-compose] file.

```yaml
  sql-client:
    container_name: sql-client
    build:
      context: .
      dockerfile: Dockerfile
    command:
      - /opt/flink/bin/sql-client.sh
      - embedded
      - -l
      - /opt/sql-client/lib

      # uncomment to run the "Hello, Flink" pipeline from a file
      # - -f
      # - /etc/sql/hello_flink.sql

      # uncomment to run the "Trade Stats" pipeline from a file
      # - -f
      # - /etc/sql/trade_stats.sql
```

Then, submit the jobs via the SQL client using the following command:

```sh
docker-compose run sql-client
```

After submitting the job, visit http://localhost:8081/ to check the status.

[sql]: sql
[docker-compose]: docker-compose.yaml
