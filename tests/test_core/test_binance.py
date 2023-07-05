import hashlib
import hmac
import os
import time
from unittest import mock
from urllib.parse import urlencode, urljoin

import pandas as pd
from dotenv.main import load_dotenv

from av_crypto_trading.core import binance_api

# TODO: push to repo csv files, add env for tests tweepy


def fix_paths():
    """
    There are problems with working dirs, when invoking function from other place,
    Working dir is set to function working dir.
    This fix_paths set the current working directory to current file directory.
    """

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


fix_paths()


def test_get_balance_information():
    balance = binance_api.get_balance("BTC")
    assert balance


def test_place_order(binance_client_mock):
    print(binance_api.get_balance("BTC"))
    order = binance_client_mock.create_order(
        symbol="BTCUSDT", side="BUY", type="MARKET", quantity=0.001
    )
    print(order)
    print(binance_api.get_balance("BTC"))
    assert order
    order = binance_client_mock.create_order(
        symbol="BTCUSDT", side="SELL", type="MARKET", quantity=0.001
    )
    print(order)
    print(binance_api.get_balance("BTC"))
    assert order


def test_place_VALID_order_request_binance_spot():
    """
    Watch out! This will place a valid order, you will lose money!
    Uncomment last line.
    https://www.youtube.com/watch?v=0QKXso4PIc4&list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&index=19&ab_channel=Algovibes
    Binance REST API usage
    https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information
    """
    load_dotenv()
    api_key = os.environ["API_VALID_KEY"]
    api_secret = os.environ["API_VALID_SECRET"]
    base_url = "https://api.binance.com"

    headers = {"X-MBX-APIKEY": api_key}
    path = "api/v3/order"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",  # "LIMIT",
        # "timeInForce": "GTC",
        "quantity": 0.0003,  # ~10 dol
        # "price": 500.0,
        # "recvWindow": 5000,
        "timestamp": timestamp,
    }
    query_string = urlencode(params)
    params["signature"] = hmac.new(
        api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    url = urljoin(base_url, path)
    # response = requests.post(url, headers=headers, params=params)


def test_basic_exchange_info_request(
    mock_requests: mock.NonCallableMagicMock, base_url_binance
) -> None:
    path = "/api/v3/exchangeInfo"

    response = mock_requests.get(base_url_binance + path)

    assert response.status_code == 200
    assert response.text
    assert response.json()


def test_BTC_price_request_binance(
    mock_requests: mock.NonCallableMagicMock, base_url_binance
) -> None:
    path = "/api/v3/klines"
    params = "?symbol=BTCUSDT&interval=1m"
    response = mock_requests.get(base_url_binance + path + params)

    assert response.status_code == 200
    assert response.text

    response = mock_requests.get(
        base_url_binance + path, params={"symbol": "BTCUSDT", "interval": "1m"}
    )
    assert response.status_code == 200
    assert response.text


def test_BTC_price_request_kucoin(
    mock_requests: mock.NonCallableMagicMock, base_url_kucoin
):
    path = "/api/v1/market/histories"
    response = mock_requests.get(base_url_kucoin + path, params={"symbol": "BTC-USDT"})

    assert response.status_code == 200
    assert response.text
