import pandas as pd
import plotly.graph_objects as go


class GraphicsService:
    def __init__(self):
        self.figure = go.Figure()
        self.dataframe = pd.DataFrame

    def plot_high_low(self, dataframe):
        self.dataframe = dataframe
        self.figure.add_trace(
            go.Candlestick(
                x=dataframe.index,
                open=dataframe["open"],
                high=dataframe["high"],
                low=dataframe["low"],
                close=dataframe["close"],
            ),
        )

    def plot_arg(self, args):
        self.figure.add_trace(
            go.Scatter(
                x=self.dataframe.index,
                y=self.dataframe[args],
                line=dict(color="purple", width=1),
            ),
        )

    def plot_line(self, value):
        self.figure.add_trace(
            go.Scatter(
                x=self.dataframe.index,
                y=[value] * len(self.dataframe.index),
                line=dict(color="red", width=1),
            ),
        )

    def show(self):
        self.figure.show()
