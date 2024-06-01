from datetime import datetime

import pandas as pd
import pytz
import yfinance as yf

from av_crypto_trading.core.binance_api import init_client
from av_crypto_trading.core.converters import name_data


def disable_warnings() -> None:
    import warnings

    warnings.simplefilter(action="ignore", category=FutureWarning)


def get_hist_data_yahoo(currency: str, back_period: int, interval: str = '1d') -> pd.DataFrame:
    # alternative way to get data from yahoo
    # from pandas_datareader import data as reader
    # df = reader.get_data_yahoo(name, start, end)

    # problems with timezone when trying to get BTCUSDT
    # tz = pytz.timezone("America/New_York")
    # start = tz.localize(datetime(2013, 1, 1))
    # end = tz.localize(datetime.today())

    end = datetime.now()
    start = datetime(end.year - back_period, end.month, end.day)
    # print(start)
    # print("--------------------------------------------")
    # print(end)
    # print("--------------------------------------------")
    df = yf.download(tickers=currency, start=start, end=end, interval=interval)
    df = df.reset_index()
    df[["ds", "y"]] = df[["Date", "Adj Close"]]
    return df


def get_hist_data_binance(
    currency: str, back_period: int, interval: str = "1m"
) -> pd.DataFrame:
    client = init_client()
    # years can not work - should change to days
    # initially it was interval 1 d and years ago UTC but I receive 1 record :D
    data = client.get_historical_klines(
        symbol=currency, interval=interval, start_str=str(back_period) + " days ago UTC"
    )
    df = pd.DataFrame(data)
    df = name_data(df)
    df = df.reset_index()
    df[["ds", "y"]] = df[["Time", "close"]]
    return df
