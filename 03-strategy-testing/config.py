import os

from dotenv import load_dotenv

# Save your configs in .env
load_dotenv()

# Alpaca configs
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_PAPER = os.getenv("ALPACA_PAPER", True)
ALPACA_DATA_FEED = "iex"  # should be 'sip' if you have PRO subscription
ALPACA_URL = (
    "https://paper-api.alpaca.markets" if ALPACA_PAPER else "https://api.alpaca.markets"
)

# Redpanda configs
REDPANDA_BROKERS = os.getenv("REDPANDA_BROKERS", "localhost:9092")
REDPANDA_CONSUMER_GROUP = os.getenv("REDPANDA_CONSUMER_GROUP", "test")

# Data pull configs
BACKFILL_START = "2022-09-01"
BACKFILL_END = "2023-01-01"

# Symbols to pull data for (backfill and live).
# Note: Crypto symbols are formatted like so: "BTC/USD", "ETH/USD", etc
SYMBOLS = ["TSLA"]
ADDITIONAL_TEXT_FILTERS = ["Tesla"]

# Set to True if you are pulling for Crypto symbols (see the SYMBOLS
# list above). Note: you cannot pull data for crypto and stock symbols
# at the same time. So run a separate backfill if you need both.
CRYPTO = False
