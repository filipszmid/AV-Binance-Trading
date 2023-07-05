from unittest import mock

import numpy as np
import pandas as pd
import pytest

from av_crypto_trading.core import contants, converters, database_api, strategies

# TODO: Close Figures during tests


def test_check_MACD_positive_price_over_EMA_all_crypto(
    example_currencies: pd.Series, test_data_db: pd.DataFrame
):
    """Run a check for every interesting cryptocurrency."""
    currencies = example_currencies[
        ~(
            example_currencies.str.contains(
                "UP|DOWN|BULL|BEAR|TUSD|GBP|BUSD|EUR|PAXG|USDC|AUD|SLP", regex=True
            )
        )
    ]
    currencies = currencies[(currencies.str.contains("USDT", regex=True))]
    for currency in currencies:
        df = test_data_db[test_data_db.symbol == currency]
        # taking record every 1 min - can be useful for macd
        # df = df.set_index("Time").resample("1min").first()
        # https://youtu.be/07FUXpcy9FI?list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&t=863

        converters.add_MACD_EMA(df)
        print(f"Check for {currency}...")
        if strategies.check_MACD_positive_price_over_EMA(df):
            print(
                f"""\n**********************************\n
    You should consider buying: {currency}\n
    Price over EMA and MACD positive\n
    **********************************\n"""
            )


@mock.patch.object(database_api, "get_currency_price_from_lookback")
def test_get_top_worst_crypto_from_minute(mock_currency_price, example_currencies):
    mock_currency_price.return_value = pd.DataFrame({"close": [1.0, 2.0]})
    all_crypto_returns = converters.all_crypto_price_cumulative_returns(
        example_currencies, 1
    )

    top = all_crypto_returns.Performance.nlargest(1)
    worst = all_crypto_returns.Performance.nsmallest(1)

    assert not top.empty
    assert not worst.empty


def test_get_price_cumulative_return(test_data_db):
    cum_ret = converters.price_cumulative_return(test_data_db)
    assert cum_ret != 0.0


def test_check_MACD_positive_price_over_EMA(test_data_db):
    df = test_data_db[test_data_db.symbol == contants.Currencies.Bitcoin.value]
    assert not df.empty
    converters.add_MACD_EMA(df)
    assert not np.sign(df.tail(2).MACD).empty
    assert not np.sign(df.MACD).diff().empty
    strategies.check_MACD_positive_price_over_EMA(df)


@pytest.mark.parametrize("lookback", [5, 10, 40])
@mock.patch.object(pd, "read_sql")
def test_get_crypto_price_from(mock_read_sql, lookback, example_klines_data):
    mock_read_sql.return_value = example_klines_data
    df = database_api.get_currency_price_from_lookback("BTCUSDT", lookback)
    assert not df.empty
    mock_read_sql.assert_called_once()


def test_add_FastSMA_Slow_SMA(test_data_db):
    converters.add_FastSMA_SlowSMA(test_data_db)
    assert not test_data_db.FastSMA.empty
    assert not test_data_db.SlowSMA.empty
