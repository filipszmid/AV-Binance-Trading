"""Backtesting strategies module."""

import numpy as np
import pandas as pd

from av_crypto_trading.core import binance_api, database_api


def SMA_strategy(df, sma_1, sma_2):
    df = df.copy()

    # Can resample to check how strategy performs, different results
    # df = df.resample("60min").ffill()  # 3min 15min 30min 60min
    # df.dropna(inplace=True)

    df["asset_return"] = np.log(df.close.pct_change() + 1)
    df["SMA1"] = df.close.rolling(sma_1).mean()
    df["SMA2"] = df.close.rolling(sma_2).mean()
    df = df.dropna()
    df["position"] = np.where(df["SMA1"] > df["SMA2"], 1, 0)
    df["strategy_return"] = df["position"].shift(1) * df["asset_return"]
    return df


def performance(df):
    """Sums assets and strategy returns."""
    return np.exp(df[["asset_return", "strategy_return"]].sum())


def backtest_params_SMA_short_long(df, SMA_short_list, SMA_long_list):
    """
    Algorithmic Trading in Python - Simple Moving Averages & Optimization
    https://youtu.be/vWVZxiaaTCs
    """
    profits = []
    a, b = [], []
    for sma_short, sma_long in zip(SMA_short_list, SMA_long_list):
        profit = performance(SMA_strategy(df, sma_short, sma_long))
        profits.append(profit)
        a.append(sma_short)
        b.append(sma_long)

    columns = {"level_0": "SMA_short", "level_1": "SMA_long"}
    performance_for_params = (
        pd.DataFrame(profits, [a, b]).reset_index().rename(columns=columns)
    )
    performance_for_params["edge"] = (
        performance_for_params.strategy_return - performance_for_params.asset_return
    )
    return performance_for_params.sort_values("edge", ascending=False)


def backtest_SMA_strategy_multiply_coins():
    """
    Calculates asset and strategy returns for all coins in positions check table
    Income is reduced by 7.5% broker costs.
        https://youtu.be/HB1CLz0Z1NY
    """
    currencies = database_api.read_position_checks().currency
    for currency in currencies:
        # datetime.fromtimestamp(0)
        df = binance_api.get_minute_data(currency, lookback="100000000", db=False)
        # print(df)
        trades = SMA_strategy(df, 7, 25).position.diff().value_counts().iloc[1:].sum()
        costs = trades * 0.00075
        asset_return = np.exp(SMA_strategy(df, 7, 25)["asset_return"].sum()) - 1
        strategy_return = (
            np.exp(SMA_strategy(df, 7, 25)["strategy_return"].sum()) - 1 - costs
        )
        print(
            f"\n Backtesting report performed on: {currency}\n"
            f"\n  * asset_return: {asset_return} \n  * strategy_return: {strategy_return}"
        )
        if strategy_return > asset_return:
            print("\n Strategy is performing BETTER than holding")
        else:
            print("\n Strategy is performing WORSE than holding")


# backtest_SMA_strategy_multiply_coins()
