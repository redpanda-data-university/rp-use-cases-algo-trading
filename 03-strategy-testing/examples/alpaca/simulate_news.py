# Positive: Tesla, Nio Battery-Supplier CATL Expects Q3 Net Profit To Triple, Shares Jump 6%
# Negative: Tesla Analyst Warns Situation Could Turn Uglier
import json
from time import time

from kafka import KafkaProducer
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

from config import REDPANDA_BROKERS

# Create a sentiment analyzer
sia = SIA()

# Script-level onfigs
REDPANDA_TOPIC = "market-news"

# Get a Redpanda client instance
redpanda_client = KafkaProducer(
    bootstrap_servers=REDPANDA_BROKERS,
    key_serializer=str.encode,
    value_serializer=lambda m: json.dumps(m).encode("utf-8"),
)


def get_sentiment(text):
    scores = sia.polarity_scores(text)
    return scores["compound"]


while True:
    # print a separator to improve readability between multiple records
    print("-" * 30)

    # collect some inputs
    symbol = input("Symbol (e.g. TSLA) > ")
    headline = input("Fake headline > ")

    if not symbol or not headline:
        print("Both fields are required")
        continue

    # Create a dummy article
    article = {}
    article["symbol"] = symbol
    article["headline"] = headline
    article["timestamp_ms"] = int(time() * 1000)
    article["data_provider"] = "news simulator"
    article["sentiment"] = get_sentiment(article["headline"])

    # Produce the simulated news article to Redpanda
    try:
        future = redpanda_client.send(
            REDPANDA_TOPIC,
            key=article["symbol"],
            value=article,
            timestamp_ms=article["timestamp_ms"],
        )

        # Block until the message is sent (or timeout).
        _ = future.get(timeout=10)

        print("Produced news record")

    except Exception as e:
        print(e)
