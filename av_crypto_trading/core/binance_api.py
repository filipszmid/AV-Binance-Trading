import datetime
import os
import time

import pandas as pd
from binance import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

from av_crypto_trading.core import contants, converters, database_api, utils


def init_client() -> Client:
    load_dotenv()
    api_key = os.environ["api_key"]
    api_secret = os.environ["api_secret"]

    utils.set_pandas_to_print_all_values()

    client = Client(api_key, api_secret, testnet=True)
    return client


client = init_client()


def get_minute_data(
    currency: contants.Currencies,
    interval: str = "1m",
    lookback: str = "30",
    db: bool = True,
) -> pd.DataFrame:
    """
    Returns crypto data,
        - when db=False from binance api
        - when db=True from database (should run in parallel with all crypto stream)
    """
    if not db:
        df = None
        while not df:
            try:
                df = client.get_historical_klines(
                    currency, interval, lookback + " m ago UTC"
                )
            except BinanceAPIException as error:
                print(error)
                time.sleep(60)
        df = pd.DataFrame(df)
        df = converters.name_data(df)
    else:
        starting_time = datetime.datetime.utcnow() - datetime.timedelta(
            minutes=int(lookback)
        )
        df = database_api.get_crypto_from_starting_time(currency, starting_time)
        # df.set_index("timestamp", inplace=True)
    return df


def get_balance(symbol: str) -> dict:
    balance_information = client.get_account()["balances"]
    for balance in balance_information:
        if balance["asset"] == symbol:
            return balance


def make_order(
    currency: contants.Currencies,
    decision: contants.Decision,
    quantity: float,
) -> dict:
    """
    Invokes buy or sell order on binance api on spot trade market.
    Change positions in database and prints necessary information.
    """
    print("\n---------------------------------------------------")
    print(f"    Starting an {decision.value} order for: {currency} ")

    order = client.create_order(
        symbol=currency,
        side=decision.value,
        type="MARKET",
        # quoteOrderQty=quantity,
        quantity=quantity,
        # timeInForce="GTC"  #managing timeouts: https://dev.binance.vision/t/can-the-limit-order-be-placed-with-timeout/14397
    )
    print(
        f"      Order: {order['symbol']} {order['side']} successfully created for {order['price']} price:"
    )
    print(f"    {order}")
    print("---------------------------------------------------\n")
    parsed_order = converters.convert_order_to_dict(order)
    id = database_api.save_dict_to_db(parsed_order, contants.Tables.transactions)
    parsed_order["id"] = id
    database_api.change_position(currency, parsed_order, decision)

    return parsed_order


def get_top_currency() -> contants.Currencies:
    """Messy algorithm for getting top raising currency convertable to USDT"""
    all_pairs = pd.DataFrame(client.get_ticker())

    all_pairs["priceChangePercent"] = all_pairs["priceChangePercent"].astype(float)
    relev = all_pairs[all_pairs.symbol.str.contains("USDT")]
    non_relev = relev[
        ~((relev.symbol.str.contains("UP")) | (relev.symbol.str.contains("DOWN")))
    ]
    top_currency = non_relev[
        non_relev.priceChangePercent == non_relev.priceChangePercent.max()
    ]
    top_currency = top_currency.symbol.values[0]
    return top_currency


def get_historicals(
    currency: contants.Currencies, interval: str, start: str, end: str
) -> pd.DataFrame:
    """Returns historical data from binance."""
    df = pd.DataFrame(
        client.get_historical_klines(
            currency, interval, start + " days ago UTC", end + " day ago UTC"
        )
    )
    return df
