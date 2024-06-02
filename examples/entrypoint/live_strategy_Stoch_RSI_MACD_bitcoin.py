from av_crypto_trading.core.contants import Currencies
from av_crypto_trading.core.strategies import strategy_Stoch_RSI_MACD

while True:
    strategy_Stoch_RSI_MACD(currency=Currencies.Bitcoin, quantity=0.001)
