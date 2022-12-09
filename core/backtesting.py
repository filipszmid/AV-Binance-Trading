import numpy as np
import pandas as pd
from sqlalchemy import create_engine

"""
Algorithmic Trading in Python - Simple Moving Averages & Optimization
https://youtu.be/vWVZxiaaTCs
"""


def SMA_strategy(df, sma_1, sma_2):
    df = df.copy()

    """Can reample to check how strategy performs"""
    # df = df.resample("60min").ffill()  # 3min 15min 30min 60min
    # df.dropna(inplace=True)

    df["asset_return"] = np.log(df.Close.pct_change() + 1)
    df["SMA1"] = df.Close.rolling(sma_1).mean()
    df["SMA2"] = df.Close.rolling(sma_2).mean()
    df = df.dropna()
    df["position"] = np.where(df["SMA1"] > df["SMA2"], 1, 0)
    df["strategy_return"] = df["position"].shift(1) * df["asset_return"]
    return df


def performance(df):
    """
    Return is how the asset is acting
    we check if we can earn more within a strategy
    """
    return np.exp(df[["asset_return", "strategy_return"]].sum())


def backtest_params_SMA_short_long(df, SMA_short_list, SMA_long_list):
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
    This function calculates asset and strategy returns for all coins in symbols_to_trade_main.csv
    It reduces strategy income by 7.5% costs.
    If running this try resampling data in SMA_strategy by 5, 15, 30, 60 min -> different results across the timeline
    https://youtu.be/HB1CLz0Z1NY
    """
    #: TODO fix patchs here
    symbols = pd.read_csv("../../database/symbols_to_trade_main.csv").name.to_list()
    engine = create_engine("sqlite:///../../database/Crypto-backtest.db")

    for symbol in symbols:
        df = pd.read_sql(symbol, engine).set_index("Time")
        df.rename(columns={"close": "Close"}, inplace=True)
        trades = SMA_strategy(df, 7, 25).position.diff().value_counts().iloc[1:].sum()
        costs = trades * 0.00075
        asset_return = np.exp(SMA_strategy(df, 7, 25)["asset_return"].sum()) - 1
        strategy_return = (
            np.exp(SMA_strategy(df, 7, 25)["strategy_return"].sum()) - 1 - costs
        )
        print(
            f"{symbol}\n  asset_return: {asset_return} \n   strategy_return: {strategy_return}"
        )
