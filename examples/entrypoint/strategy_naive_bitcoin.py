from av_crypto_trading.core.contants import Currencies
from av_crypto_trading.core.strategies import strategy_naive

while True:
    strategy_naive(currency=Currencies.Bitcoin, quantity=0.001, db=False)
