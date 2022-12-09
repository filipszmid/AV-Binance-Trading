from datetime import datetime
from pydantic import BaseModel
import numpy as np
import pandas as pd


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
            mask = (self.df["%K"].shift(i) < 20) & (self.df["%D"].shift(i) < 20)
            dfx = dfx.append(mask, ignore_index=True)
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


class ProfitReport(BaseModel):
    currency: str
    quantity: float
    buy_order_time: str
    buy_order_price: int
    sell_order_time: str
    sell_order_price: float
    difference_currency: float
    PLN: float
