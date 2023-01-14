from utils import alpaca_utils
from alpaca.trading.enums import OrderSide
from config import REDPANDA_BROKERS, REDPANDA_CONSUMER_GROUP

from kafka import KafkaConsumer
import json

TOPIC = "raw-trade-signals"
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=REDPANDA_BROKERS,
<<<<<<<< HEAD:03-strategy-testing/examples/alpaca/submit_orders.py
    group_id=REDPANDA_CONSUMER_GROUP + "-dev2",
========
    group_id=REDPANDA_CONSUMER_GROUP + "4",
>>>>>>>> 9c63b19557f2d7485aabd6e0ddf00f47e13c1fd6:02-data-collection/examples/alpaca/submit_order.py
    auto_offset_reset="earliest",
    value_deserializer=lambda value: json.loads(value.decode("utf-8"))
    # add more configs here if you'd like
)

try:
    for msg in consumer:
        # get the JSON deserialized value
        value = msg.value

<<<<<<<< HEAD:03-strategy-testing/examples/alpaca/submit_orders.py
        # see if too much time has elapsed between the trade signal and the current time.
        # we don't want to trade with old signals
        record_time = datetime.datetime.fromtimestamp(msg.timestamp / 1000)
        now = datetime.datetime.now()
        diff_minutes = int(
            (now - record_time).total_seconds() / 60
        )
        if diff_minutes >= 10:
           print(f"Trade signal consumed successfully, but the signal has expired. Simulate news using the the simulate_news script, or wait until more recent news is seen for this symbol.")
           continue

========
>>>>>>>> 9c63b19557f2d7485aabd6e0ddf00f47e13c1fd6:02-data-collection/examples/alpaca/submit_order.py
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
