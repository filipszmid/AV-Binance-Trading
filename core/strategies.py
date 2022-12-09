import json
import os
import time

import pandas as pd
import ta
import websockets
from binance import Client
from core.binance import (
    make_order,
    get_minute_data,
    get_top_currency,
    get_historical_data_with_ST_LT,
    init_client,
)
from core.contants import Decision
from core.streams import stream_name
from core.utils import (
    print_iter,
    get_database,
    log_to_file,
    run_async,
)
from core.converters import (
    name_data,
    create_frame_symbol_time_price,
    order_price,
    cut_df_records_to_order_time,
    profit_report,
    print_last_price_record,
    add_indicators_Stoch_RSI_MACD,
    get_quantity,
    live_SMA,
    add_FastSMA_SlowSMA,
)
from core.models import Signals, ProfitReport


def fix_paths():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


@log_to_file
def strategy_naive(client: Client, currency: str, quantity: float) -> ProfitReport:
    """
    strategy_naive(client, Currencies.Bitcoin, 0.001)
    Buy when asset fell more then 0.2% in the last 30 min
    sell if asset rises by more than 0.15% or falls further by 0.15%
    """
    open_position = False
    while True:
        data = client.get_historical_klines(currency, "1m", "30 m ago UTC")
        data = pd.DataFrame(data)
        df = name_data(data)
        if not open_position:
            cuml_ret = (df.open.pct_change() + 1).cumprod() - 1
            if cuml_ret[-1] < -0.002:
                buy_order = make_order(
                    client=client,
                    currency=currency,
                    decision=Decision.BUY,
                    quantity=quantity,
                )
                open_position = True

            print_iter(value=cuml_ret[-1], lower="< -0.002")
        else:
            since_buy = df.loc[
                df.index > pd.to_datetime(buy_order["transactTime"], unit="ms")
            ]
            if len(since_buy) > 0:
                since_buy_ret = (since_buy.open.pct_change() + 1).cumprod() - 1
                print_iter(
                    value=since_buy_ret[-1],
                    greater="> 0.0015",
                    lower="< -0.0015",
                )
                if since_buy_ret[-1] > 0.0015 or since_buy_ret[-1] < -0.0015:
                    sell_order = make_order(
                        client=client,
                        currency=currency,
                        decision=Decision.SELL,
                        quantity=quantity,
                    )
                    return profit_report(buy_order, sell_order, currency, quantity)


@log_to_file
def strategy_trend(
    client: Client,
    currency: str,
    entry: float,
    look_back: int,
    quantity: float,
) -> ProfitReport:
    """
    !! This strategy working with live data stream. !!
    Trend following strategy:
         -Buy if the crypto was rising by x %
         -Exit when profit is above 0.15 or loss is crossing -0.15%
    strategy_trend(client, Currencies.Bitcoin, 0.001, 60, 0.001)
    https://www.youtube.com/watch?v=rc_Y6rdBqXM&list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&index=3
    """
    engine = get_database(currency)
    open_position = False
    while True:
        data_frame = pd.read_sql(currency, engine)
        if not open_position:
            look_back_period = data_frame.iloc[-look_back:]
            cumulative_return = (look_back_period.Price.pct_change() + 1).cumprod() - 1
            print_iter(
                value=cumulative_return[cumulative_return.last_valid_index()],
                greater=entry,
            )
            if cumulative_return[cumulative_return.last_valid_index()] > entry:
                buy_order = make_order(
                    client=client,
                    currency=currency,
                    decision=Decision.BUY,
                    quantity=quantity,
                )
                open_position = True

        if open_position:
            since_buy = cut_df_records_to_order_time(data_frame, buy_order)
            if len(since_buy) > 1:
                since_buy_return = (since_buy.Price.pct_change() + 1).cumprod() - 1
                last_entry = since_buy_return[since_buy_return.last_valid_index()]
                print_iter(value=last_entry, greater=0.0015, lower=-0.0015)
                if last_entry > 0.0015 or last_entry < -0.0015:
                    sell_order = make_order(
                        client=client,
                        currency=currency,
                        decision=Decision.SELL,
                        quantity=quantity,
                    )
                    return profit_report(buy_order, sell_order, currency, quantity)


@log_to_file
@run_async
async def strategy_momentum(
    client: Client, currency: str, quantity: float
) -> ProfitReport:
    """
    run_async(strategy_momentum_data_stream(currency=Currencies.Bitcoin, quantity=0.001))
    Strategy based on live data_frame updates,
    ! If the currency is not found it will wait !
    https://youtu.be/nQkaJ207xYI
    """
    name = stream_name(currency)
    stream = websockets.connect(name)
    df = pd.DataFrame()
    open_position = False

    async with stream as receiver:
        while True:
            data = await receiver.recv()
            data = json.loads(data)["data"]
            df = df.append(create_frame_symbol_time_price(data))
            if len(df) > 30:
                if not open_position:
                    print_iter(
                        value=ta.momentum.roc(df.Price, 30).iloc[-1],
                        greater="> 0",
                        value_2=ta.momentum.roc(df.Price, 30).iloc[-2],
                    )
                    if (
                        ta.momentum.roc(df.Price, 30).iloc[-1] > 0
                        and ta.momentum.roc(df.Price, 30).iloc[-2]
                    ):
                        buy_order = make_order(
                            client=client,
                            currency=currency,
                            decision=Decision.BUY,
                            quantity=quantity,
                        )
                        open_position = True
                if open_position:
                    sub_df = cut_df_records_to_order_time(df, buy_order)
                    if len(sub_df) > 1:
                        sub_df["highest"] = sub_df.Price.cummax()
                        sub_df["trailingstop"] = sub_df["highest"] * 0.9

                        print_iter(
                            value=sub_df.iloc[-1].Price,
                            lower=sub_df.iloc[-1].trailingstop,
                            value_2=df.iloc[-1].Price / order_price(buy_order),
                            greater_2="> 1.002",
                        )
                        if (
                            sub_df.iloc[-1].Price < sub_df.iloc[-1].trailingstop
                            or df.iloc[-1].Price / order_price(buy_order) > 1.002
                        ):
                            sell_order = make_order(
                                client=client,
                                currency=currency,
                                decision=Decision.SELL,
                                quantity=quantity,
                            )
                            return profit_report(
                                buy_order, sell_order, currency, quantity
                            )
            print_last_price_record(data_frame=df)


@log_to_file
def strategy_trailing_stop_loss(
    client: Client, currency: str, quantity: float, entry: float, look_back: int
) -> ProfitReport:
    """
    strategy_trailing_stop_loss(
        currency=Currencies.Bitcoin, quantity=0.001, entry=-0.0015, look_back=60)

    Trailing Stop Loss algorithm:
    Price |  Benchmark | Trailing Stop (5% Loss)   |  Sell (Price<TS)
    100        100          95                          No
    120        120          114                         No
    110        120          114                         Yes

    https://youtu.be/V6z1ME3-0_I
    """
    margin = 0.995
    open_position = False
    engine = get_database(currency)
    while True:
        if not open_position:
            data_frame = pd.read_sql(currency, engine)
            look_back_period = data_frame.iloc[-look_back:]
            cumulative_return = (look_back_period.Price.pct_change() + 1).cumprod() - 1
            print_iter(
                value=cumulative_return[cumulative_return.last_valid_index()],
                less=entry,
            )
            if cumulative_return[cumulative_return.last_valid_index()] < entry:
                buy_order = make_order(
                    client=client,
                    currency=currency,
                    decision=Decision.BUY,
                    quantity=quantity,
                )
                open_position = True

        if open_position:
            data_frame = pd.read_sql(
                f"""SELECT * FROM {currency} WHERE \
            Time>= '{pd.to_datetime(buy_order['transactTime'],unit='ms')}'""",
                engine,
            )
            data_frame["Benchmark"] = data_frame.Price.cummax()
            data_frame["TSL"] = data_frame.Benchmark * margin
            print_iter(
                value_price=data_frame.Price.last_valid_index(),
                less_than_TSL=data_frame["TSL"].last_valid_index(),
            )
            if data_frame[data_frame.Price < data_frame.TSL].last_valid_index():
                sell_order = make_order(
                    client=client,
                    currency=currency,
                    decision=Decision.SELL,
                    quantity=quantity,
                )
                return profit_report(buy_order, sell_order, currency, quantity)


@log_to_file
def strategy_MACD(client: Client, currency: str, quantity: float) -> ProfitReport:
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
    open_position = False
    while True:
        df = get_minute_data(client, currency, "1m", "40m")
        if not open_position:
            print_iter(
                value_1=ta.trend.macd_diff(df.close).iloc[-1],
                greater_than_1=0,
                value_2=ta.trend.macd_diff(df.close).iloc[-2],
                less_than_2=0,
            )
        else:
            print_iter(
                value_1=ta.trend.macd_diff(df.close).iloc[-1],
                less_than_1=0,
                value_2=ta.trend.macd_diff(df.close).iloc[-2],
                greater_than_2=0,
            )

        if (
            not open_position
            and ta.trend.macd_diff(df.close).iloc[-1] > 0
            and ta.trend.macd_diff(df.close).iloc[-2] < 0
        ):
            buy_order = make_order(
                client=client,
                currency=currency,
                decision=Decision.BUY,
                quantity=quantity,
            )
            open_position = True
        elif (
            open_position
            and ta.trend.macd_diff(df.close).iloc[-1] < 0
            and ta.trend.macd_diff(df.close).iloc[-2] > 0
        ):
            sell_order = make_order(
                client=client,
                currency=currency,
                decision=Decision.SELL,
                quantity=quantity,
            )
            return profit_report(buy_order, sell_order, currency, quantity)


@log_to_file
def strategy_Stoch_RSI_MACD(
    client: Client, currency: str, quantity: float
) -> ProfitReport:
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
            df = get_minute_data(client, currency, "1m", "100")
            add_indicators_Stoch_RSI_MACD(df)
            signals = Signals(df, 25)
            signals.decide()
            print_iter(
                currnt_signal=df.buy.iloc[-1],
                should_be=1,
                current_close=df.close.iloc[-1],
            )
            if df.buy.iloc[-1]:
                buy_order = make_order(
                    client=client,
                    currency=currency,
                    decision=Decision.BUY,
                    quantity=quantity,
                )

                open_position = True
        if open_position:
            time.sleep(0.5)
            df = get_minute_data(client, currency, "1m", "2")
            buy_price = order_price(buy_order)
            print_iter(
                value=df.close.iloc[-1],
                should_be=buy_price * target_profit,
                stop_loss=buy_price * stop_loss,
            )

            if (
                df.close[-1] <= buy_price * stop_loss
                or df.close[1] >= target_profit * buy_price
            ):
                sell_order = make_order(
                    client=client,
                    currency=currency,
                    decision=Decision.SELL,
                    quantity=quantity,
                )
                return profit_report(buy_order, sell_order, currency, quantity)


@run_async
async def strategy_top_symbol_high_risk(
    client: Client, buy_for: int, stop_loss: float = 0.985, target: float = 1.02
) -> ProfitReport:
    """
    High risk strategy buy alt coin for amount in dollars
    Screen for the best performing coin on the whole Binance platform
    Buy if the coin is still climbing
    Sell with target profit or Stop Loss

    ! some of the currencies do not allow to buy for low amount- errors with quantity !
    strategy_top_symbol_high_risk(client, 200) - in dollars
    https://youtu.be/g04GeHe-dJw
    """
    open_position = False
    while True:
        if not open_position:
            currency = get_top_currency(client)
            df = get_minute_data(client, currency, "1m", "120")
            quantity = get_quantity(buy_for, df.close.iloc[-1])
            name = stream_name(currency)
            stream = websockets.connect(name)

            if ((df.close.pct_change() + 1).cumprod()).iloc[-1] > 1:
                answer = input(f"Input: y or n -> do you wanna buy: {currency}? ")
                if answer == "n":
                    break
                buy_order = make_order(client, currency, Decision.BUY, quantity)

                buy_price = order_price(buy_order)
                open_position = True
                data_stream = pd.DataFrame()
            print_iter(
                value=((df.close.pct_change() + 1).cumprod()).iloc[-1],
                greater_than=1,
                currency=currency,
                think_about_buying=quantity,
                sleep=4,
                every=1,
            )
        else:
            async with stream as receiver:
                data = await receiver.recv()
                data = json.loads(data)["data"]

                data_stream = data_stream.append(create_frame_symbol_time_price(data))
                print_iter(
                    value=data_stream.Price.values,
                    target=buy_price * target,
                    stop_loss=buy_price * stop_loss,
                )
                if (
                    data_stream.Price.values[-1] <= buy_price * stop_loss
                    or data_stream.Price.values[-1] >= buy_price * target
                ):
                    sell_order = make_order(client, currency, Decision.SELL, quantity)
                    return profit_report(buy_order, sell_order, currency, quantity)


@log_to_file
@run_async
async def strategy_SMA_crossover(
    client: Client, currency: str, quantity: float
) -> ProfitReport:
    """Strategy make sense when short term average is greater than long term average at this moment
    otherwise it can take very long time
    https://www.binance.com/en/futures/BTCUSDT

    https://youtu.be/aWgJYd5kVfo
    """
    open_position = False
    target_profit = 1.02
    stop_loss = 0.98
    ST, LT = 7, 18
    # df = pd.DataFrame()
    historicals = get_historical_data_with_ST_LT(client, currency, LT)
    while True:
        name = stream_name(currency)
        stream = websockets.connect(name)
        async with stream as receiver:
            data = await receiver.recv()
            data = json.loads(data)["data"]
            if data:
                df = create_frame_symbol_time_price(data)
                # df = df.append(create_frame_symbol_time_price(data))
                live_ST, live_LT = live_SMA(historicals, df)
                if live_ST > live_LT and not open_position:
                    buy_order = make_order(client, currency, Decision.BUY, quantity)
                    buy_price = order_price(buy_order)
                    open_position = True
                if not open_position:
                    print_iter(
                        last_df_price=df.iloc[-1].Price,
                        live_ST=live_ST[-1],
                        should_be_greater_than_live_LT=live_LT[-1],
                        every=1,
                    )
                if open_position:
                    if (
                        df.Price[0] < stop_loss * buy_price
                        or df.Price[0] > target_profit * buy_price
                    ):
                        sell_order = make_order(
                            client, currency, Decision.SELL, quantity
                        )
                        return profit_report(buy_order, sell_order, currency, quantity)
                    print_iter(
                        value=df.Price[0],
                        greater_than=target_profit * buy_price,
                        or_less_than=stop_loss * buy_price,
                        every=10,
                    )


class Strategy_FastSMA_SlowSMA_Many_Coins:
    def __init__(
        self,
    ):
        """
        For this strategy there put a position_check.csv file in database dir
        The file should contain following structure:
            currency,position,quantity
            BTCUSDT,0,0
            ETHUSDT,0,0
        https://www.youtube.com/watch?v=_BrPshkROhs&list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&index=23&ab_channel=Algovibes
        """
        # :TODO https://www.youtube.com/watch?v=HB1CLz0Z1NY&ab_channel=Algovibes
        fix_paths()
        self.client = init_client()
        self.positions = pd.read_csv("../database/position_check.csv")
        print("Strategy Fast SMA Slow SMA on coins: ")
        print(self.positions)

    def change_position(self, currency, order, buy=True):
        if buy:
            self.positions.loc[self.positions.currency == currency, "position"] = 1
            self.positions.loc[self.positions.currency == currency, "quantity"] = float(
                order["executedQty"]
            )
        else:
            self.positions.loc[self.positions.currency == currency, "position"] = 0
            self.positions.loc[self.positions.currency == currency, "quantity"] = 0
        self.positions.to_csv("database/position_check.csv", index=False)

    def strategy_FastSMA_Slow_SMA(self, investment=100):
        """
        Need to create file position_check.csv with coins which I want to trade
        Coins need to exist in binance.
        Strategy checks:     if FastSMA > SlowSMA -> buy investment
                        else if SlowSMA > FastSMA -> sell everything what invested that coin
        Strategy checks data from 75 hours back with interval 1h.
        """
        for coin in self.positions[self.positions.position == 1].currency:
            df = get_minute_data(
                client=self.client, currency=coin, interval="1h", lookback="4500"
            )
            add_FastSMA_SlowSMA(df)
            last_row = df.iloc[-1]
            if last_row.SlowSMA > last_row.FastSMA:
                quantity = self.positions[
                    self.positions.currency == coin
                ].quantity.values[0]
                sell_order = make_order(self.client, coin, Decision.SELL, quantity)
                self.change_position(coin, sell_order, buy=False)

            print_iter(
                value=last_row.SlowSMA,
                greater_than=last_row.FastSMA,
                coin=coin,
                every=9,
            )

        for coin in self.positions[self.positions.position == 0].currency:
            df = get_minute_data(
                client=self.client, currency=coin, interval="1h", lookback="4500"
            )

            add_FastSMA_SlowSMA(df)
            last_row = df.iloc[-1]
            if last_row.FastSMA > last_row.SlowSMA:
                buy_order = make_order(self.client, coin, Decision.BUY, investment)
                self.change_position(coin, buy_order, buy=True)

            print_iter(
                value=last_row.FastSMA,
                greater_than=last_row.SlowSMA,
                coin=coin,
                every=9,
            )

    def run_forever(self):
        while True:
            try:
                self.strategy_FastSMA_Slow_SMA()
                # :TODO test and make profit_report
            except:
                continue

    def run_once(self):
        self.strategy_FastSMA_Slow_SMA()
