from av_crypto_trading.core import contants, strategies

while True:
    strategies.strategy_trailing_stop_loss(
        currency=contants.Currencies.Bitcoin, quantity=0.001
    )
