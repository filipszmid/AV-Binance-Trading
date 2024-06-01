import pandas as pd
from matplotlib import pyplot as plt

from av_crypto_trading.graphics.graphics_service import GraphicsService


def plot_df_high_low(data: pd.DataFrame) -> None:
    g = GraphicsService()
    g.plot_high_low(data)
    g.show()


def plot_df_price(data: pd.DataFrame) -> None:
    plt.interactive(False)
    data.close.plot()
    plt.show()
