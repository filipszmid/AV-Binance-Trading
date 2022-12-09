from core.binance import init_client
from core.contants import Currencies
from core.strategies import strategy_momentum

client = init_client()
while True:
    strategy_momentum(client=client, currency=Currencies.Bitcoin, quantity=0.001)
