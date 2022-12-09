"""
This should work with parallel with streaming all crypto to DB.
https://www.youtube.com/watch?v=yTg7msDp2Q8&list=PL9ATnizYJ7f8_opOpLnekEZNsNVUVbCZN&index=18&ab_channel=Algovibes
To run streamlit app:
streamlit run python.py
    ->localhost:8501

This file need to be in source root directory.
1) Database location
2) Streamlit don't see backwards directories
"""

import streamlit as st
import pandas as pd
import sqlalchemy

from core.converters import all_crypto_price_cumulative_returns

engine = sqlalchemy.create_engine("sqlite:///database/CryptoLive.db")


st.title("Welcome to the Live Binance return screener")
symbols = pd.read_sql(
    'SELECT name FROM sqlite_master WHERE type="table"', engine
).name.to_list()

all_crypto_returns = all_crypto_returns = all_crypto_price_cumulative_returns(engine)

lookback = st.selectbox(
    "Pick the lookback in minutes",
    [1, 15, 30],
)
if st.button("Update"):
    all_crypto_returns = all_crypto_price_cumulative_returns(engine, lookback)

top = all_crypto_returns.Performence.nlargest(10)
worst = all_crypto_returns.Performence.nsmallest(10)


cols = st.columns(2)
cols[0].title("Top Performers")
cols[0].dataframe(top)  # st.write(top)
cols[1].title("Worst Performers")
cols[1].dataframe(worst)  # st.write(worst)
