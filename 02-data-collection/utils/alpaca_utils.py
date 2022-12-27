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
    return CryptoDataStream(api_key=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY,)


def get_stock_historical_client():
    return StockHistoricalDataClient(
        api_key=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY
    )


def get_stock_live_client():
    return StockDataStream(api_key=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY,)


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

    # df = append_summary_metrics(bars)

    # flatten the multi-index to just a timestamp to ease plotting and joining
    # df.index = df.index.get_level_values(1)
    return bars


def append_summary_metrics(df):
    # minutely return is the percent change of minute price
    df["minutely_return"] = df["close"].pct_change()

    # cumulative return is the product of each minutely return
    # (1 + return_1) * (1 + return_2) * …
    df["cumulative_return"] = df["minutely_return"].add(1).cumprod().sub(1)
    return df
