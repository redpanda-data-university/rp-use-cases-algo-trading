import json
import sys

from kafka import KafkaProducer

from config import CRYPTO, REDPANDA_BROKERS, SYMBOLS
from data.providers import ALPACA, DATA_PROVIDER_KEY
from utils import alpaca_utils

# configs
REDPANDA_TOPIC = "price-updates"

# Pull live data from Alpaca
print(f"Pulling live data for symbols: {SYMBOLS}")

# Make sure the market is open. Otherwise, we can't pull live data
market_clock = alpaca_utils.get_clock()
if not market_clock.is_open:
    print(
        "Can't pull live data because the market is not open. Please try again when the market is open."
    )
    sys.exit(0)

# Get a Alpaca client instance
alpaca_client = alpaca_utils.get_live_client(crypto=CRYPTO)

# Get a Redpanda client instance
redpanda_client = KafkaProducer(
    bootstrap_servers=REDPANDA_BROKERS,
    key_serializer=str.encode,
    value_serializer=lambda m: json.dumps(m).encode("utf-8"),
)

# An async handler that gets called whenever new data is seen
async def data_handler(data):
    record = data.dict()

    # Format the timestamp to milliseconds
    timestamp_ms = int(record["timestamp"].timestamp() * 1000)
    record["timestamp"] = timestamp_ms

    # Add an identifier for the data provider
    record[DATA_PROVIDER_KEY] = ALPACA

    # Produce the record to Redpanda
    _ = redpanda_client.send(
        REDPANDA_TOPIC,
        key=record["symbol"],
        value=record,
        timestamp_ms=record["timestamp"],
    )

    print(f"Produced record to Redpanda topic: {REDPANDA_TOPIC}. Record: {record}")


alpaca_client.subscribe_bars(data_handler, *SYMBOLS)
# subscribe_bars, subscribe_updated_bars, subscribe_daily_bars, subscribe_trades, subscribe_quotes

alpaca_client.run()
