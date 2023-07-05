"""Data processing methods module."""

import datetime as dt

import pandas as pd
import ta

from av_crypto_trading.core import contants, database_api, utils


def name_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.iloc[:, :6]
    df.columns = ["Time", "open", "high", "low", "close", "volume"]
    df = df.set_index("Time")
    df.index = pd.to_datetime(df.index, unit="ms")
    df = df.astype(float)
    return df


def create_frame_symbol_time_price(data: dict) -> pd.DataFrame:
    #:TODO after refactor dead code
    df = pd.DataFrame([data])
    df = df.loc[:, ["s", "E", "c"]]  # previously p was c?
    df.columns = ["symbol", "Time", "Price"]
    df.Price = df.Price.astype(float)
    df.Time = pd.to_datetime(df.Time, unit="ms")
    return df


def add_indicators_Stoch_RSI_MACD(df):
    df["%K"] = ta.momentum.stoch(df.high, df.low, df.close, window=14)
    df["%D"] = df["%K"].rolling(3).mean()
    df["rsi"] = ta.momentum.rsi(df.close, window=14)
    df["macd"] = ta.trend.macd_diff(df.close)
    df.dropna(inplace=True)


def get_quantity(buy_for: int, price: float) -> float:
    return utils.round_to_full(buy_for / price)


def live_SMA(hist: pd.DataFrame, live: pd.DataFrame, LT: int = 18, ST: int = 7):
    live_ST = (hist["ST"].values + live.close.values) / ST
    live_LT = (hist["LT"].values + live.close.values) / LT
    return live_ST, live_LT


def price_cumulative_return(df: pd.DataFrame) -> float:
    cumulative_return = (df.close.pct_change() + 1).prod() - 1
    return cumulative_return


def all_crypto_price_cumulative_returns(
    currencies: list, lookback: int = 1
) -> pd.DataFrame:
    """Returns cumulative returns for symbols."""
    returns = []
    for currency in currencies:
        returns.append(
            price_cumulative_return(
                database_api.get_currency_price_from_lookback(currency, lookback)
            )
        )
    return pd.DataFrame(returns, currencies, columns=["Performance"])


def add_MACD_EMA(df: pd.DataFrame):
    df["MACD"] = ta.trend.macd_diff(df.close)
    df["EMA"] = ta.trend.ema_indicator(df.close, window=100)
    df.dropna(inplace=True)  # remove all Nan Be careful! can delete whole df


def add_FastSMA_SlowSMA(df):
    df["FastSMA"] = df.close.rolling(5).mean()
    df["SlowSMA"] = df.close.rolling(75).mean()


def convert_ubwa_stream_to_sql(engine, data: pd.DataFrame) -> None:
    #:TODO to delete
    time = data["event_time"]
    coin = data["symbol"]
    price = data["kline"]["close_price"]
    df = pd.DataFrame([[time, price]], columns=["Time", "Price"])
    df.Time = pd.to_datetime(df.Time, unit="ms")
    df.Price = df.Price.astype(float)
    df.to_sql(coin, engine, index=False, if_exists="append")
    print(coin)


def convert_ubwa_stream_to_master_db(data: dict) -> None:
    event_type = "ubwa_all_crypto-" + data["stream_type"]
    timestamp = data["event_time"]
    symbol = data["symbol"]
    open = data["kline"]["open_price"]
    high = data["kline"]["high_price"]
    low = data["kline"]["low_price"]
    close = data["kline"]["close_price"]
    volume = data["kline"]["base_volume"]
    quote = data["kline"]["quote"]
    df = pd.DataFrame(
        [[event_type, timestamp, symbol, open, high, low, close, volume, quote]],
        columns=[
            "event_type",
            "timestamp",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote",
        ],
    )
    df.timestamp = pd.to_datetime(df.timestamp, unit="ms")
    df.open = df.open.astype(float)
    df.high = df.high.astype(float)
    df.low = df.low.astype(float)
    df.close = df.close.astype(float)
    df.volume = df.volume.astype(float)
    df.quote = df.quote.astype(float)

    database_api.save_df_to_db(df, contants.Tables.cryptocurrencies)
    utils.print_iter(stream_response=df.to_dict("records"), every=500)


def convert_order_to_dict(order):
    local_date = dt.datetime.strptime(
        utils.unix_to_date(order["transactTime"]), "%Y-%m-%d %H:%M:%S"
    )
    # TODO: what if the Poland time change to GMT +1 ?
    # 120 -> 60 minutes
    gmt_transaction_time = local_date - dt.timedelta(minutes=120)
    order_dict = {
        "description": "",
        "currency": order["symbol"],
        "transaction_time": gmt_transaction_time,
        "origin_quantity": float(order["origQty"]),
        "executed_quantity": float(order["executedQty"]),
        "cumulative_quote_quantity": float(order["cummulativeQuoteQty"]),
        "status": order["status"],
        "type": order["type"],
        "side": order["side"],
        "price": float(order["fills"][0]["price"]),
        "quantity": float(order["fills"][0]["qty"]),
        "commision": float(order["fills"][0]["commission"]),
        "commision_asset": order["fills"][0]["commissionAsset"],
        "trade_id": order["fills"][0]["tradeId"],
    }
    return order_dict


def add_ST_LT(df: pd.DataFrame, LT: int = 18, ST: int = 7) -> pd.DataFrame:
    """Can be executed by cron once per day"""
    if LT > 18:
        print(
            "Be careful it may do not return minimum amount of records to calculate LT rolling sum"
        )
    closes = pd.DataFrame(df[4])
    closes.columns = ["close"]
    closes["ST"] = closes.close.rolling(ST - 1).sum()
    closes["LT"] = closes.close.rolling(LT - 1).sum()
    closes.dropna(inplace=True)
    return closes
