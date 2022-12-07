# Redpanda University
[Redpanda University][rpu] is a series of courses that will teach you the basics of event streaming, and will help you gain hands-on experience with a new data streaming platform called [Redpanda][rp].

## RP Use Cases: Algorithmic Trading
This repository contains code examples for the Algorithmic Trading course from [Redpanda University][rpu]. The following lessons are included:

[rpu]: https://university.redpanda.com/

## Getting Started
To start the Redpanda and Flink clusters, run the following commands:

```sh
docker-compose build
docker-compose up -d
```

### Redpanda
Once the clusters are running, set the following alias so that any invocation of `rpk` uses the pre-installed version in your local Redpanda cluster:

```sh
alias rpk="docker exec -ti redpanda-1 rpk"
```

From here, you can use `rpk` to interact with the Redpanda cluster:

```sh
rpk cluster info
rpk create topic greetings
```

### Flink
The Flink web interface will be available at: http://localhost:8081

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
