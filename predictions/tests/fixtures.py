import pytest

from core.binance import init_client
from core.contants import Currencies, Companies
from predictions.data_extractors import get_hist_data_binance, get_hist_data_yahoo


@pytest.fixture()
def client():
    return init_client()


@pytest.fixture
def example_data_binance(client):
    return get_hist_data_binance(Currencies.Bitcoin, 20)


@pytest.fixture()
def example_data_yahoo():
    return get_hist_data_yahoo(Companies.Tesla, 10)


@pytest.fixture()
def example_data_yahoo_btc():
    return get_hist_data_yahoo(Companies.Bitcoin, 20)
