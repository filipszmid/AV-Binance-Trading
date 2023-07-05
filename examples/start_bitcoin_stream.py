from av_crypto_trading.contants import Currencies
from av_crypto_trading.core.streams import start_coin_streaming_to_database

"""This is really strange bug but streams can connect do database ONLY from this file"""

start_coin_streaming_to_database(currency=Currencies.Bitcoin)
