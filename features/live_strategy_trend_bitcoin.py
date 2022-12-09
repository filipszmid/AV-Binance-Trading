from core.binance import init_client
from core.contants import Currencies
from core.strategies import strategy_trend

client = init_client()
while True:
    strategy_trend(client, Currencies.Bitcoin, 0.001, 60, 0.001)
