import unicorn_binance_websocket_api

from core.contants import Currencies
from core.streams import read_database, start_coin_streaming_to_database, fix_paths
from graphics.utils import plot_df_price
import os


def test_fix_patch():
    current_working_dir = os.getcwd()
    fix_paths()
    file_working_dir = os.getcwd()
    assert current_working_dir != file_working_dir


def test_read_stream(client):
    start_coin_streaming_to_database(currency=Currencies.Bitcoin, end=2)
    df = read_database(Currencies.Bitcoin)
    assert df is not None
    plot_df_price(df)


def test_unicorn_binance_api_stream():
    ubwa = unicorn_binance_websocket_api.BinanceWebSocketApiManager(
        exchange="binance.com"
    )
    ubwa.create_stream(["kline_1m"], ["btcusdt", "ethusdt"], output="UnicornFy")
    first_row = ubwa.pop_stream_data_from_stream_buffer()
    while True:
        oldest_data_from_stream_buffer = ubwa.pop_stream_data_from_stream_buffer()
        if oldest_data_from_stream_buffer:
            print(oldest_data_from_stream_buffer)
            assert oldest_data_from_stream_buffer
            break
