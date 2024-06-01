import pandas as pd
import pytest

from av_crypto_trading.core.utils import unix_to_date

# if __name__=="__main__":
#     client=init_client()
#     data = client.get_historical_klines("BTCUSDT", "1m", "30 m ago UTC")
#     data = pd.DataFrame(data)
#     data.to_csv("test_minute_data.csv")


@pytest.fixture
def base_url_binance():
    return "https://api.binance.com"


@pytest.fixture
def base_url_kucoin():
    return "https://api.kucoin.com"


@pytest.fixture
def order_dict():
    return {
        "description": "",
        "currency": "",
        "transaction_time": unix_to_date(1685996195124),
        "origin_quantity": 10.0,
        "executed_quantity": 10.0,
        "cumulative_quote_quantity": 10.0,
        "status": "",
        "type": "",
        "side": "",
        "price": 20.0,
        "quantity": 20.0,
        "commision": 20.0,
        "commision_asset": 30.0,
        "trade_id": 23000,
    }


@pytest.fixture
def test_data_db():
    df = pd.read_csv("../../tests/test_data_db.csv")
    return df


@pytest.fixture
def example_currencies() -> list:
    return pd.Series(["BTCUSDT", "ETHUSDT"])
