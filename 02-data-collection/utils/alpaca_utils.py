from datetime import datetime

# --------------------------------------------
# Alpaca's new, official SDK imports are below
# ---------------------------------------------
from alpaca.data.historical import (CryptoHistoricalDataClient,
                                    StockHistoricalDataClient)
from alpaca.data.live import CryptoDataStream, StockDataStream
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, OrderStatus, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
# --------------------------------------------
#  Alpaca's legacy SDK imports are below
# --------------------------------------------
# Note: Alpaca is planning to move away from the alpaca-trade-api-python client
# in 2023, but we include it in this project since at the time of this writing
# (12/22), it was the only way to access the news API via an official Alpaca SDK
from alpaca_trade_api.common import URL
from alpaca_trade_api.rest import REST, Sort
from alpaca_trade_api.stream import Stream

from config import (ALPACA_API_KEY, ALPACA_DATA_FEED, ALPACA_PAPER,
                    ALPACA_SECRET_KEY, ALPACA_URL)


def get_trading_client():
    return TradingClient(api_key=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY)


def get_legacy_stream_client():
    return Stream(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        base_url=URL(ALPACA_URL),
        data_feed=ALPACA_DATA_FEED,
    )


def get_legacy_rest_client():
    return REST(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        base_url=URL("https://data.alpaca.markets/v1beta1/"),
    )


def get_clock():
    return get_trading_client().get_clock()


def get_crypto_historical_client():
    return CryptoHistoricalDataClient(
        api_key=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY
    )


def get_crypto_live_client():
    return CryptoDataStream(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
    )


def get_stock_historical_client():
    return StockHistoricalDataClient(
        api_key=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY
    )


def get_stock_live_client():
    return StockDataStream(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
    )


def get_live_client(*symbols, crypto=False):
    if crypto:
        return get_crypto_live_client()
    return get_stock_live_client()


def get_historical_news_data(symbol, start, end, limit=1000, include_content=False):
    api = get_legacy_rest_client()
    return api.get_news(
        symbol=symbol,
        start=start,
        end=end,
        limit=limit,
        sort=Sort.Asc,
        include_content=False,
    )


def get_historical_prices(
    symbols, start, end, crypto=False, granularity=TimeFrame.Minute
):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    if crypto:
        client = get_crypto_historical_client()

        request_params = CryptoBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=granularity,
            start=start_date,
            end=end_date,
        )

        bars = client.get_crypto_bars(request_params).df

    else:  # get historical stock data
        client = get_stock_historical_client()

        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=granularity,
            start=start_date,
            end=end_date,
        )

        bars = client.get_stock_bars(request_params).df

    return bars


def has_position(symbol):
    return symbol in get_trading_client().get_all_positions()


def get_pending_order_count(symbol):
    count = 0
    orders = get_trading_client().get_orders()
    for order in orders:
        if order.status == OrderStatus.ACCEPTED and order.filled_at is None:
            count += 1
    return count


def submit_market_order(symbol, qty, side):
    position_open = has_position(symbol)
    pending_orders = get_pending_order_count(symbol)
    if position_open and side == OrderSide.BUY:
        print("order not placed. position already open")
        return
    elif not position_open and side == OrderSide.SELL:
        print("order not placed. no positions to close")
        return
    elif pending_orders:
        print("order not placed. current orders pending")
        return
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=TimeInForce.FOK,
    )
    return get_trading_client().submit_order(order_data=market_order_data)
