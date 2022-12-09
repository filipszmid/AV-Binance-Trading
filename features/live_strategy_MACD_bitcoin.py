from core.binance import init_client
from core.contants import Currencies
from core.strategies import strategy_MACD

client = init_client()
while True:
    strategy_MACD(client, Currencies.Bitcoin, 0.001)
