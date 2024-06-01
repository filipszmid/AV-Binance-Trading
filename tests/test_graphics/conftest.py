import pandas as pd
import pytest

from av_crypto_trading.core.binance_api import init_client
from av_crypto_trading.core.converters import name_data
from av_crypto_trading.graphics.graphics_service import GraphicsService


@pytest.fixture
def client():
    return init_client()


@pytest.fixture
def graphics_service_fixture():
    return GraphicsService()


@pytest.fixture
def example_data(client):
    data = client.get_historical_klines("BTCUSDT", "1m", "30 m ago UTC")
    data = pd.DataFrame(data)
    return data


@pytest.fixture
def example_named_data(example_data):
    return name_data(example_data)
