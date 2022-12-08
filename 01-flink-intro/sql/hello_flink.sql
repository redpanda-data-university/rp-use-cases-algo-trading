SET 'pipeline.name' = 'Hello, Flink (Streaming)';

CREATE TABLE names (name VARCHAR, event_time TIMESTAMP(3)) WITH (
    'connector' = 'kafka',
    'topic' = 'names',
    'properties.bootstrap.servers' = 'redpanda-1:29092',
    'properties.group.id' = 'test-group',
    'properties.auto.offset.reset' = 'earliest',
    'format' = 'json'
);

CREATE TABLE greetings WITH (
    'connector' = 'kafka',
    'topic' = 'greetings',
    'properties.bootstrap.servers' = 'redpanda-1:29092',
    'format' = 'json'
) AS
SELECT
    CONCAT('Hello, ', name) as greeting,
    PROCTIME() as processing_time
FROM
    names;
