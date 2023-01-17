import datetime
import json

from alpaca.trading.enums import OrderSide
from kafka import KafkaConsumer

from config import REDPANDA_BROKERS, REDPANDA_CONSUMER_GROUP
from utils import alpaca_utils

TOPIC = "trade-signals"
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=REDPANDA_BROKERS,
    group_id=REDPANDA_CONSUMER_GROUP,
    auto_offset_reset="latest",
    value_deserializer=lambda value: json.loads(value.decode("utf-8"))
    # add more configs here if you'd like
)

try:
    for msg in consumer:
        # get the JSON deserialized value
        value = msg.value

        # see if too much time has elapsed between the trade signal and the current time.
        # we don't want to trade with old signals
        record_time = datetime.datetime.fromtimestamp(msg.timestamp / 1000)
        now = datetime.datetime.now()
        diff_minutes = int((now - record_time).total_seconds() / 60)
        if diff_minutes >= 10:
            print(
                f"Trade signal consumed successfully, but the signal has expired. Simulate news using the the simulate_news script, or wait until more recent news is seen for this symbol."
            )
            continue

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
        alpaca_utils.submit_market_order("TSLA", 1, side)
except:
    print("Could not consume from topic: {self.topic}")
    raise
