from av_crypto_trading.core import binance_api, converters


def test_name_data(example_klines_data):
    example_data = converters.name_data(example_klines_data)
    example_data.open.plot()


def test_init_client():
    client = binance_api.init_client()
    account_information = client.get_account()["balances"]
    assert account_information
