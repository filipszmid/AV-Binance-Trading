import yfinance as yf

from .fixtures import *


@pytest.fixture
def backtest_data():
    symbol = "BTC-USD"  # AAPL
    return yf.download(symbol, start="2018-01-01")
