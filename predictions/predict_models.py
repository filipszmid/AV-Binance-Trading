import pandas as pd

from fbprophet import Prophet
from matplotlib import pyplot as plt


def predict_fb(df: pd.DataFrame, forward_period: int) -> None:
    """
    https://www.youtube.com/watch?v=GkF1MDesMTs&t=4s
    "GOOG" - Google
    "TSLA" - Tesla
    going back for Google 20 years
    Predicting 365 days forward
    """
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=forward_period)
    forecast = model.predict(future)

    model.plot(forecast)
    plt.show()
