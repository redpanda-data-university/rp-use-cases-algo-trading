from utils import alpaca_utils
from alpaca.trading.enums import OrderSide
from config import REDPANDA_BROKERS, REDPANDA_CONSUMER_GROUP

from kafka import KafkaConsumer
import json

TOPIC = "trade-signals"
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=REDPANDA_BROKERS,
    group_id=REDPANDA_CONSUMER_GROUP + "4",
    auto_offset_reset="earliest",
    value_deserializer=lambda value: json.loads(value.decode("utf-8"))
    # add more configs here if you'd like
)

try:
    for msg in consumer:
        # get the JSON deserialized value
        value = msg.value

        # extract the signal info
        symbol = value["symbol"]
        qty = value["shares"]
        signal = value["signal"]

        # convert the signal into an order side
        if signal == "BUY":
            side = OrderSide.BUY
        elif signal == "SELL":
            side = OrderSide.SELL
        else:
            # unknown signal
            continue

        # try to submit the order
        print(f"Submitting {side} order for {qty} shares of {symbol}")
        alpaca_utils.submit_market_order("TSLA", 1, OrderSide.BUY)
except:
    print("Could not consume from topic: {self.topic}")
    raise
