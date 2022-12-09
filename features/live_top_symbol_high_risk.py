from core.binance import init_client
from core.strategies import strategy_top_symbol_high_risk

client = init_client()

strategy_top_symbol_high_risk(client, 200)
