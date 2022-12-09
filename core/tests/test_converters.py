import os

import numpy as np
import pandas as pd
import pytest
from sqlalchemy.engine.create import create_engine

from core.binance import init_client, get_minute_data
from core.contants import Currencies

from core.converters import (
    all_crypto_price_cumulative_returns,
    get_symbol_price_from,
    price_cumulative_return,
    add_MACD_EMA,
    check_MACD_positive_price_over_EMA,
    add_FastSMA_SlowSMA,
)
import datetime as dt


def fix_paths():
    """
    There are problems with working dirs, when invoking function from other place,
    Working dir is set to function working dir.
    This fix_paths set the current working directory to current file directory.
    """
    # TODO: Make this function able to invoke from different files
    # TODO: Close Figures during tests
    # TODO: Resolve env problems with fb prophet
    # TODO: Git ignore exclude symbols?
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


@pytest.fixture
def engine_crypto_binance():
    c = os.getcwd()
    print(c)

    fix_paths()
    c = os.getcwd()
    print(c)
    engine = create_engine("sqlite:///../../database/Crypto.db")
    data = {
        "Price": [100.000, 123.120],
        "Time": [dt.datetime.utcnow(), dt.datetime.utcnow()],
    }
    data = pd.DataFrame(data)
    data[["Time", "Price"]].to_sql("BTCUSDT", engine, index=False, if_exists="append")
    return engine


@pytest.fixture
def engine_crypto_ubwa():
    fix_paths()
    engine = create_engine("sqlite:///../../database/CryptoLive.db")
    data = {
        "Price": [100.000, 123.120],
        "Time": [dt.datetime.utcnow(), dt.datetime.utcnow()],
    }
    data = pd.DataFrame(data)
    data[["Time", "Price"]].to_sql("BTCUSDT", engine, index=False, if_exists="append")
    return engine


def test_get_top_worst_crypto_from_minute(engine_crypto_ubwa):
    engine = engine_crypto_ubwa

    all_crypto_returns = all_crypto_price_cumulative_returns(engine, 1)

    top = all_crypto_returns.Performence.nlargest(10)
    worst = all_crypto_returns.Performence.nsmallest(10)

    assert not top.empty
    assert not worst.empty


@pytest.mark.parametrize("lookback", [1, 15, 30])
def test_get_crypto_price_from(lookback, engine_crypto_ubwa):
    df = get_symbol_price_from(engine_crypto_ubwa, "BTCUSDT", lookback)
    assert not df.empty


def test_get_price_cumulative_return(engine_crypto_ubwa):
    cum_ret = price_cumulative_return(
        get_symbol_price_from(engine_crypto_ubwa, "BTCUSDT", 100)
    )
    assert cum_ret != 0.0


def test_check_MACD_positive_price_over_EMA(engine_crypto_binance):
    """
    This test need to be run with full database Crypto.db
    If there will be not enough records it drop full dataframe
    and will do nothing
    """
    df = pd.read_sql("BTCUSDT", engine_crypto_binance)
    assert not df.empty
    add_MACD_EMA(df)
    print(np.sign(df.tail(2).MACD))
    print(np.sign(df.MACD).diff())
    check_MACD_positive_price_over_EMA(df)


def test_check_MACD_positive_price_over_EMA_all_crypto(engine_crypto_binance):
    """
    Test should be run on full database
    """

    symbols = pd.read_sql(
        """SELECT name FROM sqlite_master WHERE type='table'""", engine_crypto_binance
    ).name

    symbols = symbols[
        ~(
            symbols.str.contains(
                "UP|DOWN|BULL|BEAR|TUSD|GBP|BUSD|EUR|PAXG|USDC|AUD|SLP", regex=True
            )
        )
    ]
    for symbol in symbols:
        df = pd.read_sql(symbol, engine_crypto_binance)

        # taking record every 1 min - can be useful for macd
        # df = df.set_index("Time").resample("1min").first()
        # https://youtu.be/07FUXpcy9FI?list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&t=863

        add_MACD_EMA(df)
        print(f"Check for {symbol}...")
        if check_MACD_positive_price_over_EMA(df):
            print(
                f"""\n**********************************\n
    You should consider buying: {symbol}\n
    Price over EMA and MACD positive\n
    **********************************\n"""
            )


def test_add_FastSMA_Slow_SMA():
    client = init_client()
    data = get_minute_data(
        client=client, currency=Currencies.Bitcoin, interval="1h", lookback="4500"
    )
    add_FastSMA_SlowSMA(data)
    assert not data.FastSMA.empty
    assert not data.SlowSMA.empty
