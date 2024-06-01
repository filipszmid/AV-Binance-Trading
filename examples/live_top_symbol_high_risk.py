from av_crypto_trading.core.binance_api import init_client
from av_crypto_trading.core.strategies import strategy_top_symbol_high_risk

client = init_client()

strategy_top_symbol_high_risk(buy_for=200)
