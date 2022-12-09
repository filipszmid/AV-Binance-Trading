import asyncio

from core.contants import Currencies
from core.converters import name_data
from core.streams import coin_stream, stream_name
from core.binance import init_client


def test_name_data(example_data):
    example_data = name_data(example_data)
    example_data.open.plot()


def test_init_client():
    client = init_client()
    account_information = client.get_account()["balances"]
    assert account_information


def test_data_stream():
    data = coin_stream(stream_name(Currencies.Bitcoin), end=1)
