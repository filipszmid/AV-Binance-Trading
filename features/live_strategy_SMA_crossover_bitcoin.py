from core.binance import init_client

from core.contants import Currencies
from core.strategies import strategy_SMA_crossover

client = init_client()

strategy_SMA_crossover(client, Currencies.Bitcoin, 0.001)
