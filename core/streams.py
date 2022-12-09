import json
import os

import pandas as pd
import sqlalchemy
import unicorn_binance_websocket_api
import websockets

from core.utils import (
    run_async,
)
from core.converters import create_frame_symbol_time_price, print_last_price_record


def fix_paths():
    """
    There are problems with working dirs, when invoking function from other place,
    Working dir is set to function working dir.
    This fix_paths set the current working directory to current file directory.
    """

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


@run_async
async def crypto_stream(stream_url, end, database) -> None:
    """
    https://www.youtube.com/watch?v=07FUXpcy9FI&list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&index=17
    chyba najpierw to:
    https://www.youtube.com/watch?v=mDNIAkEZChg
    """
    stream = websockets.connect(stream_url)
    async with stream as receiver:
        while end != 0:
            data = await receiver.recv()
            msg = json.loads(data)
            symbol = [x for x in msg if x["s"].endswith("USDT")]
            frame = pd.DataFrame(symbol)[["E", "s", "c"]]
            frame.E = pd.to_datetime(frame.E, unit="ms")
            frame.c = frame.c.astype(float)
            for row in range(len(frame)):
                data = frame[row : row + 1]
                data.rename(
                    columns={"E": "Time", "s": "Symbol", "c": "Price"}, inplace=True
                )
                data[["Time", "Price"]].to_sql(
                    data["Symbol"].values[0], database, index=False, if_exists="append"
                )
                print(data)
            end -= 1


def stream_name(currency: str) -> str:
    lower = currency.lower()
    return "wss://stream.binance.com:9443/stream?streams=" + lower + "@miniTicker"


def start_coin_streaming_to_database(currency: str, end: int = -1) -> None:
    fix_paths()
    database = sqlalchemy.create_engine(
        "sqlite:///../database/" + currency + "-stream.db"
    )
    coin_stream(stream_name=stream_name(currency), end=end, database=database)


def start_all_crypto_streaming_to_database(end: int = -1) -> None:
    fix_paths()
    database = sqlalchemy.create_engine("sqlite:///../database/Crypto.db")
    stream = "wss://stream.binance.com:9443/ws/!miniTicker@arr"
    crypto_stream(
        stream_url=stream,
        end=end,
        database=database,
    )


@run_async
async def coin_stream(stream_name: str, end: int = -1, database=None) -> None:
    stream = websockets.connect(stream_name)
    async with stream as receiver:
        while end != 0:
            data = await receiver.recv()
            data = json.loads(data)["data"]
            df = create_frame_symbol_time_price(data)
            if database:
                df.to_sql(data["s"], database, if_exists="append", index=False)
                print_last_price_record(df)
            end -= 1


def read_database(currency: str) -> pd.DataFrame:
    # be carefull with creating engine all the time?
    fix_paths()
    database = sqlalchemy.create_engine(
        "sqlite:///../database/" + currency + "-stream.db"
    )
    dataframe = pd.read_sql(currency, database)
    return dataframe


def convert_ubwa_stream_to_sql(engine, data: pd.DataFrame) -> None:
    time = data["event_time"]
    coin = data["symbol"]
    price = data["kline"]["close_price"]
    df = pd.DataFrame([[time, price]], columns=["Time", "Price"])
    df.Time = pd.to_datetime(df.Time, unit="ms")
    df.Price = df.Price.astype(float)
    df.to_sql(coin, engine, index=False, if_exists="append")
    print(coin)


def ubwa_stream_all_crypto():
    fix_paths()

    engine = sqlalchemy.create_engine("sqlite:///../database/CryptoLive.db")

    symbols = pd.read_csv("../database/symbols.csv").name.to_list()
    ubwa = unicorn_binance_websocket_api.BinanceWebSocketApiManager(
        exchange="binance.com"
    )
    ubwa.create_stream(
        ["kline_1m"], [symbol.lower() for symbol in symbols], output="UnicornFy"
    )
    initial_value = ubwa.pop_stream_data_from_stream_buffer()
    while True:
        data = ubwa.pop_stream_data_from_stream_buffer()
        if data:
            if len(data) > 3:
                convert_ubwa_stream_to_sql(engine, data)
