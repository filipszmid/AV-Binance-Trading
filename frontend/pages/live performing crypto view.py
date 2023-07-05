"""
This should work with parallel with streaming all crypto to DB.
https://www.youtube.com/watch?v=yTg7msDp2Q8&list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&index=18&ab_channel=Algovibes
To run streamlit app:
streamlit run python.py
    ->localhost:8501

This file need to be in source root directory.
1) Database location
2) Streamlit don't see backwards directories

Screemer for technical indicators
https://youtu.be/07FUXpcy9FI?list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN
"""

import streamlit as st

from av_crypto_trading.core import (
    contants,
    converters,
    database_api,
    orchestrator,
    streams,
    utils,
)

st.title("Live performing crypto view")

lookback = st.selectbox(
    "Pick the lookback in minutes",
    [5, 15, 30],
)

currencies = database_api.get_all_currencies()
all_crypto_returns = converters.all_crypto_price_cumulative_returns(currencies)

if st.button("Run stream"):
    bot = orchestrator.Bot()
    bot.run_on_one_coin(contants.Currencies.Bitcoin.value, 0.001)

if st.button("Update"):
    all_crypto_returns = converters.all_crypto_price_cumulative_returns(
        currencies, lookback
    )

top = all_crypto_returns.Performance.nlargest(10)
worst = all_crypto_returns.Performance.nsmallest(10)


cols = st.columns(2)
cols[0].title("Top")
cols[0].dataframe(top)  # st.write(top)
cols[1].title("Worst")
cols[1].dataframe(worst)  # st.write(worst)
