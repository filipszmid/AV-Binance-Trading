import logging
import os
from unittest import mock
from unittest.mock import Mock

import pandas as pd
import pytest
import pytest_mock
import requests
import yfinance as yf
from dotenv import load_dotenv
from sqlalchemy import create_engine

from av_crypto_trading.core import binance_api, contants

logger = logging.getLogger(__name__)
load_dotenv()
test_on_live_services = os.getenv("TEST_ON_LIVE_SERVICES", "False") == "True"


@pytest.fixture(name="binance_client_mock")
def get_binance_client(mocker: pytest_mock.MockerFixture) -> mock.NonCallableMagicMock:
    """Get mock of binance.Client class.

    :param mocker: MockerFixture used to patch bigquery.Client object
    """
    client = mocker.patch("binance.Client", autospec=True).return_value
    return client


if not test_on_live_services:
    logger.debug("Testing on fake crypto test data.")

    @pytest.fixture(name="mock_requests")
    def get_requests_mock(
        mocker: pytest_mock.MockerFixture,
    ) -> mock.NonCallableMagicMock:
        """
        Get mock of requests package.

        :param mocker: MockerFixture used to patch requests api object
        """
        logger.debug("Testing on mocs as requests service.")
        requests_mock = mocker.patch("requests.api", autospec=True).return_value
        requests_mock.get = Mock(return_value=Mock(status_code=200, text="Response"))
        return requests_mock

    @pytest.fixture(name="crypto_test_data")
    def get_crypto_test_data():
        """
        Fake crypto data.
        Real data from db can be obtained by:
                engine = create_engine("sqlite:///../../AV_CRYPTO_TRADING.db")
                df = pd.read_sql(
                    f\"""
                        SELECT * from {contants.Tables.cryptocurrencies}
                        WHERE symbol = '{contants.Currencies.Bitcoin}'
                      \""",
                    engine,
                ).set_index("timestamp")
        """

        df = pd.read_csv("../test_data_stream.csv")
        df = df.rename(columns=str.lower)
        return df

    @pytest.fixture
    def backtest_data():
        """
        Fake data used for backtesting fixture.
        Real data can be obtained by invoking:
            df = yf.download("BTC-USD", start="2018-01-01") # AAPL
            df.rename(columns={"close": "Close"}, inplace=True)
        """

        df = pd.read_csv("../../tests/test_daily_data.csv")
        # df.rename(columns={"Close": "close"}, inplace=True)
        df = df.rename(columns=str.lower)
        return df

    @pytest.fixture
    def example_klines_data():
        """
        Fake klines data
        Real data can be obtained by invoking:
            df=pd.DataFrame(client.get_historical_klines("BTCUSDT", "1m", "30 m ago UTC"))
        """
        df = pd.read_csv("../../tests/test_data_minute_klines.csv")
        df = df.rename(columns=str.lower)
        return df


else:

    @pytest.fixture(name="mock_requests")
    def get_requests_mock() -> mock.NonCallableMagicMock:
        """
        Get mock of requests package.

        :param mocker: MockerFixture used to patch requests api object
        """
        return requests

    @pytest.fixture(name="crypto_test_data")
    def get_crypto_test_data():
        engine = create_engine("sqlite:///../../AV_CRYPTO_TRADING.db")
        df = pd.read_sql(
            f"""
                SELECT * from {contants.Tables.cryptocurrencies}
                WHERE symbol = '{contants.Currencies.Bitcoin}'
              """,
            engine,
        ).set_index("timestamp")
        df = df.rename(columns=str.lower)
        return df

    @pytest.fixture
    def backtest_data():
        df = yf.download("BTC-USD", start="2018-01-01")  # AAPL
        df = df.rename(columns=str.lower)
        return df

    @pytest.fixture
    def example_klines_data():
        client = binance_api.init_client()
        data = client.get_historical_klines("BTCUSDT", "1m", "30 m ago UTC")
        df = pd.DataFrame(data)
        return df
