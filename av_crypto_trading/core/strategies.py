import datetime
import inspect
import os
import time

import numpy as np
import pandas as pd
import ta
from binance import Client

from av_crypto_trading import schemas
from av_crypto_trading.core import (
    binance_api,
    contants,
    converters,
    database_api,
    utils,
)


def fix_paths() -> None:
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


def check_MACD_positive_price_over_EMA(df: pd.DataFrame) -> bool:
    """Checks if last record MACD is over EMA."""
    if (
        df.close.tail(1).values > df.EMA.tail(1).values
        and np.sign(df.MACD).diff().tail(1).values == 2
    ):
        print("MACD crossed to positive and Close price above EMA")
        return True


class Signals:
    def __init__(self, df, lags):
        """
        add_indicators_Stoch_RSI_MACD(df)
        signal = Signals(df, 25)
        signal.decide()
        print(df[df.buy == 1])
        """
        self.df = df
        self.lags = lags

    def get_trigger(self):
        dfx = pd.DataFrame()
        for i in range(self.lags + 1):
            # mask = (self.df["%K"].shift(i) < 20) & (self.df["%D"].shift(i) < 20)
            # dfx = dfx.append(mask, ignore_index=True)
            dfx = pd.concat(
                [
                    (self.df["%K"].shift(i) < 20) & (self.df["%D"].shift(i) < 20)
                    for i in range(self.lags + 1)
                ],
                ignore_index=True,
            )
        return dfx.sum(axis=0)

    def decide(self):
        self.df["trigger"] = np.where(self.get_trigger(), 1, 0)
        self.df["buy"] = np.where(
            self.df.trigger
            & (self.df["%K"].between(20, 80))
            & (self.df["%D"].between(20, 80))
            & (self.df.rsi > 50)
            & (self.df.macd > 0),
            1,
            0,
        )


@utils.report_strategy
def strategy_naive(
    currency: contants.Currencies, quantity: float, db: bool = True
) -> schemas.ProfitReportDataclass:
    """
    strategy_naive(client, Currencies.Bitcoin, 0.001)
    Buy when asset fell more then 0.2% in the last 30 min
    sell if asset rises by more than 0.15% or falls further by 0.15%
    """
    open_position = False
    while True:
        df = binance_api.get_minute_data(
            currency=currency, interval="1m", lookback="40", db=db
        )
        if not open_position:
            # if some problems ensure all fields in database have correct formats
            cuml_ret = list((df.open.pct_change() + 1).cumprod() - 1)
            if cuml_ret[-1] < -0.002:
                buy_order = binance_api.make_order(
                    currency=currency,
                    decision=contants.Decision.BUY,
                    quantity=quantity,
                )
                open_position = True
            utils.print_iter(value=cuml_ret[-1], lower="< -0.002")
        else:
            since_buy = df.iloc[df.index > buy_order["transaction_time"]]
            if len(since_buy) > 0:
                since_buy_ret = (since_buy.open.pct_change() + 1).cumprod() - 1
                utils.print_iter(
                    value=since_buy_ret[-1],
                    greater="> 0.0015",
                    lower="< -0.0015",
                )
                if since_buy_ret[-1] > 0.0015 or since_buy_ret[-1] < -0.0015:
                    sell_order = binance_api.make_order(
                        currency=currency,
                        decision=contants.Decision.SELL,
                        quantity=quantity,
                    )
                    return database_api.get_profit_report(
                        buy_order, sell_order, currency, quantity
                    )


@utils.report_strategy
def strategy_trend(
    currency: contants.Currencies,
    quantity: float,
    db: bool = True,
) -> schemas.ProfitReportDataclass:
    """
    !! This strategy working with live data stream. !!
    Trend following strategy:
         -Buy if the crypto was rising by x %
         -Exit when profit is above 0.15 or loss is crossing -0.15%
    strategy_trend(client, Currencies.Bitcoin, 0.001, 60, 0.001)
    https://www.youtube.com/watch?v=rc_Y6rdBqXM&list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&index=3
    """
    sleep = 0.01
    look_back = 60
    entry = 0.001
    frame = inspect.currentframe()
    open_position = False
    while True:
        df = binance_api.get_minute_data(
            currency=currency, interval="1m", lookback="40", db=db
        )
        if not df.empty:
            if not open_position:
                look_back_period = df.iloc[-look_back:]
                cumulative_return = (
                    look_back_period.close.pct_change() + 1
                ).cumprod() - 1
                utils.print_iter(
                    frame=frame,
                    value=cumulative_return[cumulative_return.last_valid_index()],
                    greater=entry,
                    sleep=sleep,
                )
                if cumulative_return[cumulative_return.last_valid_index()] > entry:
                    buy_order = binance_api.make_order(
                        currency=currency,
                        decision=contants.Decision.BUY,
                        quantity=quantity,
                    )
                    open_position = True

            else:
                since_buy = df[
                    df.timestamp >= pd.to_datetime(buy_order["transaction_time"])
                ]
                if len(since_buy) > 1:
                    since_buy_return = (since_buy.close.pct_change() + 1).cumprod() - 1
                    last_entry = since_buy_return[since_buy_return.last_valid_index()]
                    utils.print_iter(
                        frame=frame,
                        value=last_entry,
                        greater=0.0015,
                        lower=-0.0015,
                        sleep=sleep,
                    )
                    if last_entry > 0.0015 or last_entry < -0.0015:
                        sell_order = binance_api.make_order(
                            currency=currency,
                            decision=contants.Decision.SELL,
                            quantity=quantity,
                        )
                        return database_api.get_profit_report(
                            buy_order, sell_order, currency, quantity
                        )


# @run_async
@utils.report_strategy
def strategy_momentum(
    currency: contants.Currencies,
    quantity: float,
    db: bool = True,
) -> schemas.ProfitReportDataclass:
    """
    run_async(strategy_momentum_data_stream(currency=Currencies.Bitcoin, quantity=0.001))
    Strategy based on live data_frame updates,
    ! If the currency is not found it will wait !
    https://youtu.be/nQkaJ207xYI
    """
    open_position = False
    while True:
        df = binance_api.get_minute_data(
            currency=currency, interval="1m", lookback="40", db=db
        )
        if len(df) > 30:
            if not open_position:
                utils.print_iter(
                    value=ta.momentum.roc(df.close, 30).iloc[-1],
                    greater="> 0",
                    value_2=ta.momentum.roc(df.close, 30).iloc[-2],
                )
                if (
                    ta.momentum.roc(df.close, 30).iloc[-1] > 0
                    and ta.momentum.roc(df.close, 30).iloc[-2]
                ):
                    buy_order = binance_api.make_order(
                        currency=currency,
                        decision=contants.Decision.BUY,
                        quantity=quantity,
                    )
                    open_position = True
            if open_position:
                sub_df = df[
                    df.timestamp >= pd.to_datetime(buy_order["transaction_time"])
                ]
                if len(sub_df) > 1:
                    sub_df["highest"] = sub_df.close.cummax()
                    sub_df["trailingstop"] = sub_df["highest"] * 0.9

                    utils.print_iter(
                        value=sub_df.iloc[-1].close,
                        lower=sub_df.iloc[-1].trailingstop,
                        value_2=df.iloc[-1].close / buy_order["price"],
                        greater_2="> 1.002",
                    )
                    if (
                        sub_df.iloc[-1].close < sub_df.iloc[-1].trailingstop
                        or df.iloc[-1].close / buy_order["price"] > 1.002
                    ):
                        sell_order = binance_api.make_order(
                            currency=currency,
                            decision=contants.Decision.SELL,
                            quantity=quantity,
                        )
                        return database_api.get_profit_report(
                            buy_order, sell_order, currency, quantity
                        )


@utils.report_strategy
def strategy_trailing_stop_loss(
    currency: contants.Currencies,
    quantity: float,
    db: bool = True,
) -> schemas.ProfitReportDataclass:
    """
    strategy_trailing_stop_loss(
        currency=Currencies.Bitcoin, quantity=0.001)

    Trailing Stop Loss algorithm:
    Price |  Benchmark | Trailing Stop (5% Loss)   |  Sell (Price<TS)
    100        100          95                          No
    120        120          114                         No
    110        120          114                         Yes

    https://youtu.be/V6z1ME3-0_I
    """
    entry = -0.0015
    look_back = 60
    margin = 0.995
    open_position = False

    while True:
        if not open_position:
            df = binance_api.get_minute_data(
                currency=currency, interval="1m", lookback=str(look_back), db=db
            )
            cumulative_return = (df.close.pct_change() + 1).cumprod() - 1
            utils.print_iter(
                value=cumulative_return[cumulative_return.last_valid_index()],
                less=entry,
            )
            if True or cumulative_return[cumulative_return.last_valid_index()] < entry:
                buy_order = binance_api.make_order(
                    currency=currency,
                    decision=contants.Decision.BUY,
                    quantity=quantity,
                )
                open_position = True

        if open_position:
            sub_df = database_api.get_crypto_from_starting_time(
                currency, buy_order["transaction_time"]
            )
            sub_df["Benchmark"] = sub_df.close.cummax()
            sub_df["TSL"] = sub_df.Benchmark * margin
            utils.print_iter(
                value_price=sub_df.close.iloc[-1]
                if not sub_df.empty
                else "empty close",
                less_than_TSL=sub_df["TSL"].iloc[-1]
                if not sub_df.empty
                else "empty TSL",
            )
            # checks if in the last row the condition is true and return index of row
            if sub_df[sub_df.close < sub_df.TSL].last_valid_index():
                sell_order = binance_api.make_order(
                    currency=currency,
                    decision=contants.Decision.SELL,
                    quantity=quantity,
                )
                return database_api.get_profit_report(
                    buy_order, sell_order, currency, quantity
                )


@utils.report_strategy
def strategy_MACD(
    currency: contants.Currencies,
    quantity: float,
    db: bool = True,
) -> schemas.ProfitReportDataclass:
    """
    Buy when MACD diff is crossing above 0
    Sell when MACD diff is crossing below 0
    This strategy is based on 1 min live data frame updates
    Need to be 40m UTC! ta.macd_diff works strange.
    MACD algorithm:
        https://youtu.be/JzdVPnCSSuo
    Implementation:
        https://youtu.be/lNvJXKXUQ_U
    """
    frame = inspect.currentframe()
    open_position = False
    while True:
        df = binance_api.get_minute_data(
            currency=currency, interval="1m", lookback="40", db=db
        )
        if not open_position:
            utils.print_iter(
                frame=frame,
                value_1=ta.trend.macd_diff(df.close).iloc[-1]
                if not df.empty
                else "Empty DF",
                greater_than_1=0,
                value_2=ta.trend.macd_diff(df.close).iloc[-2]
                if not df.empty
                else "Empty DF",
                less_than_2=0,
            )
        else:
            utils.print_iter(
                frame=frame,
                value_1=ta.trend.macd_diff(df.close).iloc[-1]
                if not df.empty
                else "Empty DF",
                less_than_1=0,
                value_2=ta.trend.macd_diff(df.close).iloc[-2]
                if not df.empty
                else "Empty DF",
                greater_than_2=0,
            )
        if not df.empty:
            if (
                not open_position
                and ta.trend.macd_diff(df.close).iloc[-1] > 0
                and ta.trend.macd_diff(df.close).iloc[-2] < 0
            ):
                buy_order = binance_api.make_order(
                    currency=currency,
                    decision=contants.Decision.BUY,
                    quantity=quantity,
                )
                open_position = True
            elif (
                open_position
                and ta.trend.macd_diff(df.close).iloc[-1] < 0
                and ta.trend.macd_diff(df.close).iloc[-2] > 0
            ):

                sell_order = binance_api.make_order(
                    currency=currency,
                    decision=contants.Decision.SELL,
                    quantity=quantity,
                )
                return database_api.get_profit_report(
                    buy_order, sell_order, currency, quantity
                )


@utils.report_strategy
def strategy_Stoch_RSI_MACD(
    client: Client,
    currency: contants.Currencies,
    quantity: float,
    db: bool = True,
) -> schemas.ProfitReportDataclass:
    """
    Stoch RSI MACD strategy
    -Stochastic (%K, and %D line) between 20 and 80 RSI above 50
    -MACD above signal line (MACD diff larger 0)
    Before that triggering condition must be fulfilled:
    -In the last n time steps the %K and %D lines have to cross below 20

    Stop Loss-> certain amount of buying price
    Target Profit-> 1.005 * Buying price

    https://youtu.be/X50-c54BWV8
    """
    stop_loss = 0.995
    target_profit = 1.005
    open_position = False
    while True:
        if not open_position:
            df = binance_api.get_minute_data(
                currency=currency, interval="1m", lookback="100", db=db
            )
            converters.add_indicators_Stoch_RSI_MACD(df)
            signals = Signals(df, 25)
            signals.decide()
            utils.print_iter(
                currnt_signal=df.buy.iloc[-1],
                should_be=1,
                current_close=df.close.iloc[-1],
            )
            if df.buy.iloc[-1]:
                buy_order = binance_api.make_order(
                    currency=currency,
                    decision=contants.Decision.BUY,
                    quantity=quantity,
                )

                open_position = True
        if open_position:
            time.sleep(0.5)
            df = binance_api.get_minute_data(
                currency=currency, interval="1m", lookback="2", db=db
            )
            buy_price = buy_order["price"]
            utils.print_iter(
                value=df.close.iloc[-1],
                greater_than=buy_price * target_profit,
                stop_loss=buy_price * stop_loss,
            )

            if (
                df.close.iloc[-1] <= buy_price * stop_loss
                or df.close.iloc[1] >= target_profit * buy_price
            ):
                sell_order = binance_api.make_order(
                    currency=currency,
                    decision=contants.Decision.SELL,
                    quantity=quantity,
                )
                return database_api.get_profit_report(
                    buy_order, sell_order, currency, quantity
                )


# @run_async
@utils.report_strategy
def strategy_top_symbol_high_risk(
    client: Client,
    buy_for: int,
    db: bool = True,
) -> schemas.ProfitReportDataclass:
    """
    High risk strategy buy alt coin for amount in dollars
    Screen for the best performing coin on the whole Binance platform
    Buy if the coin is still climbing
    Sell with target profit or Stop Loss

    strategy_top_symbol_high_risk(client, 200) - in dollars
    https://youtu.be/g04GeHe-dJw
    """
    stop_loss = (0.985,)
    target = (1.02,)
    open_position = False
    while True:
        if not open_position:
            currency = binance_api.get_top_currency()
            print(f"Starting risky strategy on: {currency}")
            df = binance_api.get_minute_data(
                currency=currency, interval="1m", lookback="120", db=db
            )
            quantity = converters.get_quantity(buy_for, df.close.iloc[-1])

            if ((df.close.pct_change() + 1).cumprod()).iloc[-1] > 1:
                answer = input(f"Input: y or n -> do you wanna buy: {currency}? ")
                if answer == "n":
                    break
                #:TODO some of the currencies do not allow to buy for low amount - errors with quantity
                buy_order = binance_api.make_order(
                    currency=currency, decision=contants.Decision.BUY, quantity=quantity
                )

                buy_price = buy_order["price"]
                open_position = True
            utils.print_iter(
                value=((df.close.pct_change() + 1).cumprod()).iloc[-1],
                greater_than=1,
                currency=currency,
                think_about_buying=quantity,
                sleep=4,
                every=1,
            )
        else:
            sub_df = database_api.get_crypto_from_starting_time(
                currency, buy_order["transaction_time"]
            )
            utils.print_iter(
                value=sub_df.close.values[-1],
                greater_than=buy_price * target,
                stop_loss=buy_price * stop_loss,
            )
            if (
                sub_df.close.values[-1] <= buy_price * stop_loss
                or sub_df.close.values[-1] >= buy_price * target
            ):
                sell_order = binance_api.make_order(
                    currency=currency,
                    decision=contants.Decision.SELL,
                    quantity=quantity,
                )
                return database_api.get_profit_report(
                    buy_order, sell_order, currency, quantity
                )


# @run_async


@utils.report_strategy
def strategy_SMA_crossover(
    currency: contants.Currencies, quantity: float, db: bool = True
) -> schemas.ProfitReportDataclass:
    """
    Strategy makes sense when short term average is greater than long term average at this moment
    otherwise it can take very long time
    https://www.binance.com/en/futures/BTCUSDT

    https://youtu.be/aWgJYd5kVfo
    """
    open_position = False
    target_profit = 1.02
    stop_loss = 0.98
    ST, LT = 7, 18
    df = binance_api.get_historicals(currency, "1d", str(LT), "1")
    historicals = converters.add_ST_LT(df, LT)
    starting_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=120)
    while True:
        sub_df = database_api.get_crypto_from_starting_time(currency, starting_time)
        if not sub_df.empty:
            last_close_price = sub_df.close.iloc[-1]
            live_ST, live_LT = converters.live_SMA(historicals, sub_df)
            if not open_position:
                if live_ST[-1] > live_LT[-1]:
                    buy_order = binance_api.make_order(
                        currency=currency,
                        decision=contants.Decision.BUY,
                        quantity=quantity,
                    )
                    buy_price = buy_order["price"]
                    open_position = True
                utils.print_iter(
                    last_close_price=last_close_price,
                    live_ST=live_ST[-1],
                    should_be_greater_than_live_LT=live_LT[-1],
                )
            if open_position:
                if (
                    last_close_price < stop_loss * buy_price
                    or last_close_price > target_profit * buy_price
                ):
                    sell_order = binance_api.make_order(
                        currency=currency,
                        decision=contants.Decision.SELL,
                        quantity=quantity,
                    )
                    return database_api.get_profit_report(
                        buy_order, sell_order, currency, quantity
                    )
                utils.print_iter(
                    value=last_close_price,
                    greater_than=target_profit * buy_price,
                    or_less_than=stop_loss * buy_price,
                )


@utils.report_strategy
def strategy_FastSMA_SlowSMA_long_interval(
    currency: contants.Currencies, quantity: float, db: bool = True
) -> schemas.ProfitReportDataclass:
    """
    Need to create file position_check.csv with coins which I want to trade
    Coins need to exist in binance.
    Strategy checks:     if FastSMA > SlowSMA -> buy investment
                    else if SlowSMA > FastSMA -> sell everything what invested that coin
    Strategy checks data from 75 hours back with interval 1h.
    https://www.youtube.com/watch?v=_BrPshkROhs&list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&index=23&ab_channel=Algovibes
    """
    # :TODO backtest? https://www.youtube.com/watch?v=HB1CLz0Z1NY&ab_channel=Algovibes
    open_position = False
    while True:
        #:TODO returns not much data, only 4 records
        df = binance_api.get_minute_data(
            currency=currency, interval="1h", lookback="45000", db=db
        )

        converters.add_FastSMA_SlowSMA(df)
        last_row = df.iloc[-1]
        if not open_position:
            if last_row.FastSMA > last_row.SlowSMA:
                buy_order = binance_api.make_order(
                    currency=currency, decision=contants.Decision.BUY, quantity=quantity
                )
            utils.print_iter(
                value=last_row.FastSMA,
                greater_than=last_row.SlowSMA,
                coin=currency,
                every=1,
            )
        else:
            if last_row.SlowSMA > last_row.FastSMA:
                # quantity = positions[
                #     positions.currency == currency
                # ].quantity.values[0]
                sell_order = binance_api.make_order(
                    currency=currency,
                    decision=contants.Decision.SELL,
                    quantity=quantity,
                )
                return database_api.get_profit_report(
                    buy_order, sell_order, currency, quantity
                )
            utils.print_iter(
                value=last_row.SlowSMA,
                greater_than=last_row.FastSMA,
                currency=currency,
                every=1,
            )
