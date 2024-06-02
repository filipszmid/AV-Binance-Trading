from av_crypto_trading.core.contants import Currencies
from av_crypto_trading.core.strategies import strategy_trend

while True:
    strategy_trend(currencies=Currencies.Bitcoin, quantity=0.001)
