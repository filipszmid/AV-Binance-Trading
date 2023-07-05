import os

import pandas as pd
import pytest
from dotenv.main import load_dotenv

from av_crypto_trading.core.contants import Companies, Currencies
from av_crypto_trading.predictions.data_extractors import (
    get_hist_data_binance,
    get_hist_data_yahoo,
)

load_dotenv()
test_on_live_services = os.getenv("TEST_ON_LIVE_SERVICES", "False") == "True"

if not test_on_live_services:

    @pytest.fixture
    def example_data_binance():
        return pd.read_csv("../../tests/test_data_daily_klines_binance_btc_20.csv")

    @pytest.fixture
    def example_data_yahoo():
        return pd.read_csv("../../tests/test_data_daily_klines_yahoo_btc_20.csv")

    @pytest.fixture
    def example_data_yahoo_btc():
        print(os.getcwd())
        return pd.read_csv("../../tests/test_data_daily_klines_yahoo_tesla_10.csv")


else:

    @pytest.fixture
    def example_data_binance():
        return get_hist_data_binance(Currencies.Bitcoin, 20)

    @pytest.fixture
    def example_data_yahoo():
        return get_hist_data_yahoo(Companies.Tesla, 10)

    @pytest.fixture
    def example_data_yahoo_btc():
        return get_hist_data_yahoo(Companies.Bitcoin, 20)
