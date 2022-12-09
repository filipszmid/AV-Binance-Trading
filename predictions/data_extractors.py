from datetime import datetime

import pandas as pd
from pandas_datareader import data as reader

from core.binance import init_client
from core.converters import name_data


def disable_warnings() -> None:
    import warnings

    warnings.simplefilter(action="ignore", category=FutureWarning)


def get_hist_data_yahoo(name: str, back_period: int) -> pd.DataFrame:
    end = datetime.now()
    start = datetime(end.year - back_period, end.month, end.day)
    df = reader.get_data_yahoo(name, start, end)
    df = df.reset_index()
    df[["ds", "y"]] = df[["Date", "Adj Close"]]
    return df


def get_hist_data_binance(currency: str, back_period: int) -> pd.DataFrame:
    client = init_client()
    # years can not work - should change to days
    data = client.get_historical_klines(
        symbol=currency, interval="1d", start_str=str(back_period) + " years ago UTC"
    )
    df = pd.DataFrame(data)
    df = name_data(df)
    df = df.reset_index()
    df[["ds", "y"]] = df[["Time", "close"]]
    return df
