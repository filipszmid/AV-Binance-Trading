import json
import os

import pandas as pd
import sqlalchemy
import unicorn_binance_websocket_api
import websockets

import frontend.database
from av_crypto_trading.core import database_api, utils, contants
from av_crypto_trading.core.converters import (
    convert_ubwa_stream_to_master_db,
    create_frame_symbol_time_price,
)


def fix_paths():
    """
    There are problems with working dirs, when invoking function from other place,
    Working dir is set to function working dir.
    This fix_paths set the current working directory to current file directory.
    """

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


@utils.run_async
async def crypto_stream_master_db(stream_url, end, database) -> None:
    """
    Same method as above but to AV_CRYPTO_TRADING db
    https://www.youtube.com/watch?v=07FUXpcy9FI&list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&index=17
    chyba najpierw to:
    https://www.youtube.com/watch?v=mDNIAkEZChg
    """
    stream = websockets.connect(stream_url)
    async with stream as receiver:
        while end != 0:
            df = await receiver.recv()
            msg = json.loads(df)
            symbol = [x for x in msg if x["s"].endswith("USDT")]
            frame = pd.DataFrame(symbol)
            frame.E = pd.to_datetime(frame.E, unit="ms")
            frontend.database.c = frontend.database.c.astype(float)
            for row in range(len(frame)):
                df = frame[row : row + 1]
                df.rename(
                    columns={
                        "e": "event_type",
                        "E": "timestamp",
                        "s": "symbol",
                        "c": "close",
                        "o": "open",
                        "h": "high",
                        "l": "low",
                        "v": "volume",
                        "q": "quote",
                    },
                    inplace=True,
                )
                df.to_sql("cryptocurrencies", database, index=False, if_exists="append")
                utils.print_iter(stream_response=df.to_dict("records"))
            end -= 1


def single_crypto_stream_name(currency: str) -> str:
    lower = currency.lower()
    return "wss://stream.binance.com:9443/stream?streams=" + lower + "@miniTicker"


def start_coin_streaming_to_database(currency: contants.Currencies, end: int = -1) -> None:
    fix_paths()
    database = sqlalchemy.create_engine(
        "sqlite:///../../database/" + currency.value + "-stream.db"
    )
    coin_stream(
        stream_name=single_crypto_stream_name(currency.value), end=end, database=database
    )


def start_all_crypto_streaming_to_master_db(end: int = -1) -> None:
    """Same as above but to AV_CRYPTO_TRADING database"""
    fix_paths()
    database = sqlalchemy.create_engine("sqlite:///../../AV_CRYPTO_TRADING.db")
    stream = "wss://stream.binance.com:9443/ws/!miniTicker@arr"
    # stream = "wss://stream.binance.com:9443/ws/ETH@aggTrade" #no values
    crypto_stream_master_db(
        stream_url=stream,
        end=end,
        database=database,
    )


@utils.run_async
async def coin_stream(stream_name: str, end: int = -1, database=None) -> None:
    stream = websockets.connect(stream_name)
    async with stream as receiver:
        while end != 0:
            print(end)
            data = await receiver.recv()
            data = json.loads(data)["data"]
            df = create_frame_symbol_time_price(data)
            if database:
                df.to_sql(data["s"], database, if_exists="append", index=False)
                print(f"{df.iloc[-1].Time} : {df.iloc[-1].Price}")
            end -= 1


def ubwa_stream_all_crypto_to_master_db():
    """
    Same as above but to master db.
    https://github.com/LUCIT-Systems-and-Development/unicorn-binance-websocket-api?tab=readme-ov-filehttps://github.com/LUCIT-Systems-and-Development/unicorn-binance-websocket-api?tab=readme-ov-file
    UBWA added licensing.
    """
    fix_paths()
    currencies = database_api.read_position_checks().currency
    ubwa = unicorn_binance_websocket_api.BinanceWebSocketApiManager(
        exchange="binance.com"
    )
    ubwa.create_stream(
        ["kline_1m"], [currency.lower() for currency in currencies], output="UnicornFy"
    )
    initial_value = ubwa.pop_stream_data_from_stream_buffer()
    while True:
        data = ubwa.pop_stream_data_from_stream_buffer()
        if data:
            if len(data) > 3:
                convert_ubwa_stream_to_master_db(data)