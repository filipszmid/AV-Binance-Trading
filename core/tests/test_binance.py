import hashlib
import hmac
import os
import time
from urllib.parse import urlencode, urljoin

import requests
from dotenv.main import load_dotenv

from core.binance import get_balance


def test_get_balance_information(client):
    balance = get_balance(client, "BTC")
    assert balance


def test_place_order(client):
    print(get_balance(client, "BTC"))
    order = client.create_order(
        symbol="BTCUSDT", side="BUY", type="MARKET", quantity=0.001
    )
    print(order)
    print(get_balance(client, "BTC"))
    assert order
    order = client.create_order(
        symbol="BTCUSDT", side="SELL", type="MARKET", quantity=0.001
    )
    print(order)
    print(get_balance(client, "BTC"))
    assert order


"""
Binance REST API usage
https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#exchange-information
"""


def test_place_VALID_order_request_binance_spot():
    """
    Watch out! This will place a valid order, you will lose money!
    Uncomment last line.
    https://www.youtube.com/watch?v=0QKXso4PIc4&list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&index=19&ab_channel=Algovibes
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


def test_basic_exchange_info_request(base_url_binance) -> None:
    path = "/api/v3/exchangeInfo"

    response = requests.get(base_url_binance + path)

    assert response.status_code == 200
    assert response.text
    assert response.json()


def test_BTC_price_request_binance(base_url_binance) -> None:
    path = "/api/v3/klines"
    params = "?symbol=BTCUSDT&interval=1m"
    response = requests.get(base_url_binance + path + params)

    assert response.status_code == 200
    assert response.text

    response = requests.get(
        base_url_binance + path, params={"symbol": "BTCUSDT", "interval": "1m"}
    )
    assert response.status_code == 200
    assert response.text


def test_BTC_price_request_kucoin(base_url_kucoin):
    path = "/api/v1/market/histories"
    response = requests.get(base_url_kucoin + path, params={"symbol": "BTC-USDT"})

    assert response.status_code == 200
    assert response.text


def test_reading_positions_csv():
    """
    Strategy_FastSMA_SlowSMA_Orchestrator uses position_check.csv
    This is how this file should be created
    """
    symbols = pd.read_csv("database/symbols_to_trade.csv").name.to_list()
    print(symbols)
    print(len(symbols))
    assert symbols

    df = pd.DataFrame(symbols)
    df.columns = ["Currency"]
    df["position"] = 0
    df["quantity"] = 0
    df.to_csv("database/position_check.csv", index=False)

    df = pd.read_csv("database/position_check.csv")
    print(df)
    assert df
