import json
import sys

from kafka import KafkaProducer

from config import REDPANDA_BROKERS, SYMBOLS
from utils import alpaca_utils

# configs
REDPANDA_TOPIC = "market-news"

# Pull live data from Alpaca
print(f"Pulling live news data for symbols: {SYMBOLS}")

# Get a Redpanda client instance
redpanda_client = KafkaProducer(
    bootstrap_servers=REDPANDA_BROKERS,
    key_serializer=str.encode,
    value_serializer=lambda m: json.dumps(m).encode("utf-8"),
)

# An async handler that gets called whenever new data is seen
async def news_callback(data):
    print("news")
    print(data)
    print(type(data))
    # record = data.dict()

    # # format the timestamp to milliseconds
    # timestamp_ms = int(record["timestamp"].timestamp() * 1000)
    # record["timestamp"] = timestamp_ms

    # # produce to Redpanda
    # _ = redpanda_client.send(
    #     REDPANDA_TOPIC,
    #     key=record["symbol"],
    #     value=record,
    #     timestamp_ms=record["timestamp"],
    # )

    # print(f"Produced record to Redpanda topic: {REDPANDA_TOPIC}. Record: {record}")


stream = alpaca_utils.get_legacy_stream_client()
stream.subscribe_news(news_callback, *SYMBOLS)

stream.run()
