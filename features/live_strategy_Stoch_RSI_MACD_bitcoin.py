from core.binance import init_client
from core.contants import Currencies
from core.strategies import strategy_Stoch_RSI_MACD

client = init_client()
while True:
    strategy_Stoch_RSI_MACD(client, Currencies.Bitcoin, 0.001)
