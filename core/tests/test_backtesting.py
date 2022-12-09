from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import tqdm
from core.backtesting import (
    SMA_strategy,
    performance,
    backtest_params_SMA_short_long,
    backtest_SMA_strategy_multiply_coins,
)
from core.binance import init_client, get_minute_data
from core.utils import set_pandas_to_print_all_values


def test_plot_positions_backtest(backtest_data):
    """
    Figure that shows when I was on position and where I don't
    """
    df = SMA_strategy(backtest_data, 20, 50)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax2 = ax.twinx()
    ax.plot(df[["Close", "SMA1", "SMA2"]])
    ax2.plot(df["position"], color="k")
    fig.show()


def test_SMA_strategy(backtest_data):
    """In this test position and strategy_return will be empty"""
    set_pandas_to_print_all_values()
    df = SMA_strategy(backtest_data, 20, 50)
    print("\n" + str(df.head()))
    assert not df.empty
    assert not df["asset_return"].empty
    assert not df["SMA1"].empty
    assert not df["SMA2"].empty
    assert not df["position"].empty
    assert not df["strategy_return"].empty


def test_performance(backtest_data):
    p = performance(SMA_strategy(backtest_data, 20, 50))
    print("\n" + str(p))
    assert p.strategy_return > p.asset_return


def test_backtest_params_SMA_short_long(backtest_data):
    """set SMA how You want, just need to be the same length"""

    SMA_short_list = range(30, 101, 5)
    SMA_long_list = range(130, 201, 5)

    assert len(SMA_short_list) == len(SMA_long_list)

    df = backtest_params_SMA_short_long(backtest_data, SMA_short_list, SMA_long_list)
    print("\n" + str(df.head()))
    assert not df.asset_return.empty
    assert not df.strategy_return.empty
    assert not df.edge.empty


def test_pull_minute_data_from_30_days():
    """
    This test need to have clean database and work a while
    on sandbox I receive max 8000 records
    look back period is in minutes 1440 -> 24h 43200 -> 30 days
    It doesn't work well inside test and should be run once to get crypto data for backtest.
    So copy and paste if You want data in db.
    """
    #: TODO mock get_min_data and sql
    # symbols = pd.read_csv("database/symbols_to_trade_main.csv").name.to_list()
    # engine = create_engine("sqlite:///database/Crypto-backtest.db")
    # client = init_client()
    # for symbol in tqdm(symbols):
    #     df = get_minute_data(
    #         client=client, currency=symbol, interval="1m", lookback="43200"
    #     )
    #     df.to_sql(symbol, engine)  # , index=False #removes time
    #
    # test_data = pd.read_sql("BTCUSDT", engine)
    # print(test_data)
    # assert test_data


def test_calculate_backtest_coin_strategy_return_with_cost():
    symbols = pd.read_csv("../../database/symbols_to_trade_main.csv").name.to_list()
    engine = create_engine("sqlite:///../../database/Crypto-backtest.db")
    test_data = pd.read_sql("BTCUSDT", engine).set_index("Time")
    test_data.rename(columns={"close": "Close"}, inplace=True)

    df = SMA_strategy(test_data, 7, 25)
    print(df.head())

    returns = (
        np.exp(
            SMA_strategy(test_data, 7, 25)[["asset_return", "strategy_return"]].sum()
        )
        - 1
    )
    print(returns)
    assert not returns.empty
    costs = (
        SMA_strategy(test_data, 7, 25).position.diff().value_counts().iloc[1:].sum()
        * 0.00075
    )  # how many times position changes * percent = trading costs

    print(f"Cost of that strategy: {costs}")
    assert costs


def test_backtest_SMA_strategy_multiply_coins():
    backtest_SMA_strategy_multiply_coins()
