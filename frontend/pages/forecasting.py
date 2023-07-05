import pandas as pd
import streamlit as st

from av_crypto_trading.core import contants
from av_crypto_trading.predictions import data_extractors, models

# st.global_settings.timezone = "America/New_York"
st.title("Data forecaster")
currency = st.selectbox(
    "Pick the currency",
    [company.value for company in contants.Companies],
)
if st.button("Forecast"):
    df = data_extractors.get_hist_data_yahoo(currency, 267)
    # df = data_extractors.get_hist_data_binance(currency, 200, "1h")
    fig = models.predict_fb(df=df, forward_period=365)
    st.pyplot(fig)
