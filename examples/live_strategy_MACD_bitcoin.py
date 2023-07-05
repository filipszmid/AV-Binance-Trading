from av_crypto_trading.core.contants import Currencies
from av_crypto_trading.core.strategies import strategy_MACD

# while True:
strategy_MACD(Currencies.Bitcoin, 0.01)
