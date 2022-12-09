import pandas as pd
from matplotlib import pyplot as plt

from graphics.graphics_service import GraphicsService


def plot_frame(data: pd.DataFrame) -> None:
    g = GraphicsService()
    g.plot_high_low(data)
    g.show()


def plot_df_price(data: pd.DataFrame) -> None:
    plt.interactive(False)
    data.Price.plot()
    plt.show()
