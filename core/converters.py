import datetime as dt

import numpy as np
import pandas as pd
import ta

from core.models import ProfitReport
from core.utils import unix_to_date, round_to_full


def name_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.iloc[:, :6]
    dataframe.columns = ["Time", "open", "high", "low", "close", "volume"]
    dataframe = dataframe.set_index("Time")
    dataframe.index = pd.to_datetime(dataframe.index, unit="ms")
    dataframe = dataframe.astype(float)
    return dataframe


def create_frame_symbol_time_price(data: dict) -> pd.DataFrame:
    df = pd.DataFrame([data])
    df = df.loc[:, ["s", "E", "c"]]  # previously p was c?
    df.columns = ["symbol", "Time", "Price"]
    df.Price = df.Price.astype(float)
    df.Time = pd.to_datetime(df.Time, unit="ms")
    return df


def order_price(order: dict) -> float:
    return float(order["fills"][0]["price"])


def cut_df_records_to_order_time(df: pd.DataFrame, order: dict) -> pd.DataFrame:
    return df[df.Time >= pd.to_datetime(order["transactTime"], unit="ms")]


def profit_report(
    buy_order: dict, sell_order: dict, currency: str, quantity: float
) -> ProfitReport:
    buy_price = order_price(buy_order)  # * 1.075
    sell_price = order_price(sell_order)  # * 0.925

    difference = (sell_price - buy_price) / buy_price
    # difference = (sell_price - buy_price) * quantity
    if difference > 0:
        print(f"You made {difference:.5f} profit on {currency}! :)")
    else:
        print(f"You made {difference:.5f} loss on {currency}! :(")
    return ProfitReport(
        currency=currency,
        quantity=quantity,
        buy_order_time=unix_to_date(buy_order["transactTime"]),
        buy_order_price=order_price(buy_order),
        sell_order_time=unix_to_date(sell_order["transactTime"]),
        sell_order_price=order_price(sell_order),
        difference_currency=difference,
        PLN=(quantity * buy_price) * difference,
    )


def print_last_price_record(data_frame: pd.DataFrame) -> None:
    print(f"{data_frame.iloc[-1].Time} : {data_frame.iloc[-1].Price}")


def add_indicators_Stoch_RSI_MACD(df):
    df["%K"] = ta.momentum.stoch(df.high, df.low, df.close, window=14)
    df["%D"] = df["%K"].rolling(3).mean()
    df["rsi"] = ta.momentum.rsi(df.close, window=14)
    df["macd"] = ta.trend.macd_diff(df.close)
    df.dropna(inplace=True)


def get_quantity(buy_for: int, price: float) -> float:
    return round_to_full(buy_for / price)


def live_SMA(hist: pd.DataFrame, live: pd.DataFrame, LT: int = 18, ST: int = 7):
    live_ST = (hist["ST"].values + live.Price.values) / ST
    live_LT = (hist["LT"].values + live.Price.values) / LT
    return live_ST, live_LT


def get_symbol_price_from(engine, symbol: str, lookback: int) -> pd.DataFrame:
    now = dt.datetime.utcnow()
    before = now - dt.timedelta(minutes=lookback)
    qry_str = f"""SELECT * FROM '{symbol}' WHERE time>= '{before}'"""
    df = pd.read_sql(qry_str, engine)
    return df


def price_cumulative_return(df: pd.DataFrame) -> float:
    cumulative_return = (df.Price.pct_change() + 1).prod() - 1
    return cumulative_return


def all_crypto_price_cumulative_returns(engine, lookback: int = 1) -> pd.DataFrame:
    symbols = pd.read_sql(
        'SELECT name FROM sqlite_master WHERE type="table"', engine
    ).name.to_list()
    returns = []
    for symbol in symbols:
        returns.append(
            price_cumulative_return(get_symbol_price_from(engine, symbol, lookback))
        )
    return pd.DataFrame(returns, symbols, columns=["Performence"])


def add_MACD_EMA(df: pd.DataFrame):
    df["MACD"] = ta.trend.macd_diff(df.Price)
    df["EMA"] = ta.trend.ema_indicator(df.Price, window=100)
    df.dropna(inplace=True)  # remove all Nan Be careful! can delete whole df


def check_MACD_positive_price_over_EMA(df: pd.DataFrame):
    """
    Screemer for technical indicators
    https://youtu.be/07FUXpcy9FI?list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN
    """
    if (
        df.Price.tail(1).values > df.EMA.tail(1).values
        and np.sign(df.MACD).diff().tail(1).values == 2
    ):
        print("MACD crossed to positive and Price above EMA")
        return True


def add_FastSMA_SlowSMA(df):
    df["FastSMA"] = df.close.rolling(5).mean()
    df["SlowSMA"] = df.close.rolling(75).mean()
