import json

from kafka import KafkaProducer

from config import REDPANDA_BROKERS, SYMBOLS
from data.providers import ALPACA, DATA_PROVIDER_KEY
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
async def news_callback(row):
    # The SDK returns a NewsV2 object. row._raw allows us to access the record
    # in dictionary form
    article = row._raw

    # Covert the timestamp to milliseconds
    timestamp_ms = int(row.created_at.timestamp() * 1000)
    article["timestamp_ms"] = timestamp_ms

    # Add an identifier for the data provider
    article[DATA_PROVIDER_KEY] = ALPACA

    # The article may relate to multiple symbols. Produce a separate record
    # each matched search symbol.
    article_symbols = article.pop("symbols")

    for search_symbol in SYMBOLS:
        if not search_symbol in article_symbols:
            continue

        article["symbol"] = search_symbol

        # Produce the news article to Redpanda
        try:
            future = redpanda_client.send(
                REDPANDA_TOPIC,
                key=search_symbol,
                value=article,
                timestamp_ms=timestamp_ms,
            )

            # Block until the message is sent (or timeout).
            _ = future.get(timeout=10)

        except Exception as e:
            print(e)


stream = alpaca_utils.get_legacy_stream_client()
stream.subscribe_news(news_callback, *SYMBOLS)

stream.run()
