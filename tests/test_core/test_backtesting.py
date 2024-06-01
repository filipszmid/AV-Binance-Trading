import os
from unittest import mock
from unittest.mock import Mock

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from av_crypto_trading.core import backtesting, binance_api, database_api, utils


def test_plot_positions_backtest(backtest_data):
    """
    Figure that shows when I was on position and where I don't
    """
    df = backtesting.SMA_strategy(backtest_data, 20, 50)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax2 = ax.twinx()
    ax.plot(df[["close", "SMA1", "SMA2"]])
    ax2.plot(df["position"], color="k")
    fig.show()


def test_SMA_strategy(backtest_data):
    """In this test position and strategy_return will be empty"""
    utils.set_pandas_to_print_all_values()
    df = backtesting.SMA_strategy(backtest_data, 20, 50)
    print("\n" + str(df.head()))
    assert not df.empty
    assert not df["asset_return"].empty
    assert not df["SMA1"].empty
    assert not df["SMA2"].empty
    assert not df["position"].empty
    assert not df["strategy_return"].empty


def test_performance(backtest_data):
    p = backtesting.performance(backtesting.SMA_strategy(backtest_data, 20, 50))
    print("\n" + str(p))
    assert p.strategy_return > p.asset_return


def test_backtest_params_SMA_short_long(backtest_data):
    """set SMA how You want, just need to be the same length"""
    SMA_short_list = range(30, 101, 5)
    SMA_long_list = range(130, 201, 5)

    assert len(SMA_short_list) == len(SMA_long_list)

    df = backtesting.backtest_params_SMA_short_long(
        backtest_data, SMA_short_list, SMA_long_list
    )
    print("\n" + str(df.head()))
    assert not df.asset_return.empty
    assert not df.strategy_return.empty
    assert not df.edge.empty


def test_read_fstring_to_dataframe():
    import io

    data = """
Time,open,high,low,close,volume
2022-05-04 06:04:00,38127.16,38127.16,38101.82,38101.82,0.206997
2022-05-04 06:05:00,38101.82,38127.16,37800.63,38127.16,0.020966
2022-05-04 06:06:00,38127.16,38127.16,38127.16,38127.16,0.003297
2022-05-04 06:07:00,38127.16,38127.16,38127.16,38127.16,0.050000
2022-05-04 06:08:00,38127.16,38127.16,38127.16,38127.16,0.002210
        """
    utils.set_pandas_to_print_all_values()
    test_data = pd.read_csv(io.StringIO(data), sep=",")
    assert not test_data.empty
    print(test_data.columns)
    assert list(test_data.columns) == ["Time", "open", "high", "low", "close", "volume"]
    assert isinstance(test_data, pd.DataFrame)


def test_calculate_backtest_coin_strategy_return_with_cost(crypto_test_data):
    df = backtesting.SMA_strategy(crypto_test_data, 7, 25)
    assert not df.empty
    print(df.head())
    returns = (
        np.exp(
            backtesting.SMA_strategy(crypto_test_data, 7, 25)[
                ["asset_return", "strategy_return"]
            ].sum()
        )
        - 1
    )
    print(returns)
    assert not returns.empty
    costs = (
        backtesting.SMA_strategy(crypto_test_data, 7, 25)
        .position.diff()
        .value_counts()
        .iloc[1:]
        .sum()
        * 0.00075
    )  # how many times position changes * percent = trading costs

    print(f"Cost of that strategy: {costs}")
    assert costs


@mock.patch.object(database_api, "read_position_checks")
@mock.patch.object(binance_api, "get_minute_data")
def test_backtest_SMA_strategy_multiply_coins(
    mock_get_minute_data, mock_read_positions, crypto_test_data
):
    mock_get_minute_data.return_value = crypto_test_data
    mock_read_positions.return_value = pd.DataFrame(
        {"currency": ["BTCUSDT", "ETHUSDT"]}
    )
    backtesting.backtest_SMA_strategy_multiply_coins()
