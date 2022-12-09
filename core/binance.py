import os
import time

import pandas as pd
from binance import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

from core.contants import Decision
from core.converters import name_data, order_price
from core.utils import set_pandas_to_print_all_values


def get_minute_data(
    client: Client, currency: str, interval: str = "1m", lookback: str = "30"
) -> pd.DataFrame:
    data = None
    while not data:
        try:
            data = client.get_historical_klines(
                currency, interval, lookback + " m ago UTC"
            )
        except BinanceAPIException as error:
            print(error)
            time.sleep(60)
    data = pd.DataFrame(data)
    data = name_data(data)
    return data


def init_client() -> Client:
    load_dotenv()
    api_key = os.environ["api_key"]
    api_secret = os.environ["api_secret"]

    set_pandas_to_print_all_values()

    client = Client(api_key, api_secret, testnet=True)
    return client


def get_balance(client: Client, symbol: str) -> dict:
    balance_information = client.get_account()["balances"]
    for balance in balance_information:
        if balance["asset"] == symbol:
            return balance


def make_order(
    client: Client, currency: str, decision: Decision, quantity: float
) -> dict:
    print("\n---------------------------------------------------")
    print(f"    Starting an {decision.value} order for: {currency} ")
    order = client.create_order(
        symbol=currency,
        side=decision.value,
        type="MARKET",
        quantity=quantity,
    )
    print(
        f"      Order: {order['symbol']} {order['side']} successfully created for {order_price(order)} price:"
    )
    print(f"    {order}")
    print("---------------------------------------------------\n")
    return order


def get_top_currency(client: Client) -> str:
    """messy algorithm for getting top raising currency convertable to USDT"""
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


def get_historical_data_with_ST_LT(
    client: Client, currency: str, LT: int = 18, ST: int = 7
) -> pd.DataFrame:
    """Can be executed by cron once per day"""
    if LT > 18:
        print(
            "Be careful it may do not return minimum amount of records to calculate LT rolling sum"
        )
    df = pd.DataFrame(
        client.get_historical_klines(
            currency, "1d", str(LT) + " days ago UTC", "1 day ago UTC"
        )
    )

    closes = pd.DataFrame(df[4])
    closes.columns = ["close"]
    closes["ST"] = closes.close.rolling(ST - 1).sum()
    closes["LT"] = closes.close.rolling(LT - 1).sum()
    closes.dropna(inplace=True)
    return closes
