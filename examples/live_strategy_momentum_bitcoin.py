from av_crypto_trading.core import contants, strategies

while True:
    strategies.strategy_momentum(currency=contants.Currencies.Bitcoin, quantity=0.001)
