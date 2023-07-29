"""
Save the price-updates to a file so that students can choose
to not create an Alpaca account.

Usage:
python -m examples.alpaca.historical_prices_create_file

cat price-updates.txt | rpk topic produce price-updates -f '%k %v\n'
"""
import json

from alpaca.data.timeframe import TimeFrame

from config import BACKFILL_END, BACKFILL_START, CRYPTO, SYMBOLS
from data.providers import ALPACA, DATA_PROVIDER_KEY
from utils import alpaca_utils

# configs
OUTPUT_FILE = "price-updates.txt"

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

success_count = 0
error_count = 0

with open(OUTPUT_FILE, mode="w", newline="") as txt_file:
    # Iterate through the price updates and produce each record to Redpanda
    for i, row in enumerate(records):
        try:
            # Add an identifier for the data provider
            row[DATA_PROVIDER_KEY] = ALPACA

            # Rename keys that are reserved words in Flink since
            # we need to port this to Killercoda and there's a bug
            # with escaping reserved words
            row['price_open'] = row.pop('open')
            row['price_close'] = row.pop('close')
            row['timestamp_ms'] = row.pop('timestamp')

            # Convert the JSON record to a string
            json_record = json.dumps(row)

            # Write the line to the text file
            txt_file.write(f"{row['symbol']} {json_record}\n")

            if i > 0 and i % 100 == 0:
                print(f"Produced {i} records")

        except Exception as e:
            error_count += 1
            print(e)

print(f"Produced {i + 1} records to file: {OUTPUT_FILE}")
print(f"Encountered {error_count} errors")
