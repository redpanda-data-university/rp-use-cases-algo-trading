import json

from alpaca.data.timeframe import TimeFrame
from kafka import KafkaProducer

from config import (BACKFILL_END, BACKFILL_START, CRYPTO, REDPANDA_BROKERS,
                    SYMBOLS)
from data.providers import ALPACA, DATA_PROVIDER_KEY
from utils import alpaca_utils

# configs
REDPANDA_TOPIC = "price-updates"

# Pull historical data from Alpaca
print(f"Pulling historical data for symbols: {SYMBOLS}")

df = alpaca_utils.get_historical_prices(
    symbols=SYMBOLS,
    start=BACKFILL_START,
    end=BACKFILL_END,
    crypto=CRYPTO,
    granularity=TimeFrame.Minute,  # Minute, Hour, Day, Week, Month
)

# Convert the timestamp index to a column in the dataframe
df.reset_index(inplace=True)

# Convert the dataframe that Alpaca returns into a JSON list of price updates
records = json.loads(df.to_json(orient="records", index=True))

# Produce the records to Redpanda
redpanda_client = KafkaProducer(
    bootstrap_servers=REDPANDA_BROKERS,
    key_serializer=str.encode,
    value_serializer=lambda m: json.dumps(m).encode("utf-8"),
)

success_count = 0
error_count = 0

# Iterate through the price updates and produce each record to Redpanda
for i, row in enumerate(records):
    try:
        # Add an identifier for the data provider
        row[DATA_PROVIDER_KEY] = ALPACA

        # Produce the record to Redpanda
        future = redpanda_client.send(
            REDPANDA_TOPIC, key=row["symbol"], value=row, timestamp_ms=row["timestamp"]
        )

        # Block until the message is sent (or timeout).
        _ = future.get(timeout=10)

        if success_count > 0 and success_count % 100 == 0:
            print(f"Produced {i} records")

        success_count += 1
    except Exception as e:
        error_count += 1
        print(e)

print(f"Produced {success_count} records to Redpanda topic: {REDPANDA_TOPIC}")
print(f"Encountered {error_count} errors")
