from core.binance import init_client
from core.contants import Currencies
from core.strategies import strategy_trailing_stop_loss

client = init_client()

while True:
    profit = strategy_trailing_stop_loss(
        client=client,
        currency=Currencies.Bitcoin,
        quantity=0.001,
        entry=-0.0015,
        look_back=60,
    )
