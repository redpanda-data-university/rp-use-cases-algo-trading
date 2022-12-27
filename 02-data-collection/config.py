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
BACKFILL_START = "2022-01-01"
BACKFILL_END = "2022-02-02"

# Set to True if you are pulling Crypto data. Note: you cannot
# pull data for crypto and stock symbols at the same time. So
# run a separate backfill if you need both.
CRYPTO = False

# Symbols to pull data for (backfill and live).
# Note: Crypto symbols are formatted like so: "BTC/USD", "ETH/USD", etc
SYMBOLS = ["AAPL", "COIN"]
