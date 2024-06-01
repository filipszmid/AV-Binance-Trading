from av_crypto_trading.core.contants import Currencies
from av_crypto_trading.core.strategies import strategy_MACD

# while True:
strategy_MACD(currency=Currencies.Bitcoin, quantity=0.01)
