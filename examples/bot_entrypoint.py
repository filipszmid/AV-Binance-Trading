import time

from av_crypto_trading.core import contants, orchestrator

bot = orchestrator.Bot()
# bot.run_strategy_on_multiple_coins(0.001)

bot.run_on_one_coin(currency=contants.Currencies.Bitcoin, quantity=0.001)
# time.sleep(10)
# bot.shut_down()
# strategy.run_forever()
