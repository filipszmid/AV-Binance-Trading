import os

import unicorn_binance_websocket_api

from av_crypto_trading.core import streams


def test_fix_patch():
    current_working_dir = os.getcwd()
    streams.fix_paths()
    file_working_dir = os.getcwd()
    assert current_working_dir != file_working_dir


def test_unicorn_binance_api_stream():
    i = 5
    ubwa = unicorn_binance_websocket_api.BinanceWebSocketApiManager(
        exchange="binance.com"
    )
    ubwa.create_stream(["kline_1m"], ["btcusdt", "ethusdt"], output="UnicornFy")
    first_row = ubwa.pop_stream_data_from_stream_buffer()
    while i > 0:
        oldest_data_from_stream_buffer = ubwa.pop_stream_data_from_stream_buffer()
        if oldest_data_from_stream_buffer:
            print(oldest_data_from_stream_buffer)
            assert oldest_data_from_stream_buffer
        i -= 1
    ubwa.stop_manager_with_all_streams()


# load_dotenv()
# test_on_live_services = os.getenv("TEST_ON_LIVE_SERVICES", "False") == "True"
# if test_on_live_services:
#
#     def test_read_stream():
#         #probably to delete
#         streams.start_coin_streaming_to_database(
#             currency=contants.Currencies.Bitcoin, end=2
#         )
#         df = streams.read_database(contants.Currencies.Bitcoin)
#         assert df is not None
#         utils.plot_df_price(df)
#
#     def test_data_stream():
#         data = streams.coin_stream(
#             streams.stream_name(contants.Currencies.Bitcoin), end=1
#         )
