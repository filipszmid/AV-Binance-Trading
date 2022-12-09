import pandas as pd
import pytest

from core.binance import init_client
from core.contants import Currencies
from core.streams import start_coin_streaming_to_database, read_database
from core.converters import name_data


@pytest.fixture()
def client():
    return init_client()


@pytest.fixture
def example_data(client):
    data = client.get_historical_klines("BTCUSDT", "1m", "30 m ago UTC")
    data = pd.DataFrame(data)
    return data


@pytest.fixture()
def example_named_data(example_data):
    return name_data(example_data)


@pytest.fixture
def base_url_binance():
    return "https://api.binance.com"


@pytest.fixture
def base_url_kucoin():
    return "https://api.kucoin.com"
