from core.utils import set_pandas_to_print_all_values

from av_crypto_trading.core.streams import (
    start_all_crypto_streaming_to_database,
    start_all_crypto_streaming_to_master_db,
)

set_pandas_to_print_all_values()

# start_all_crypto_streaming_to_database()
start_all_crypto_streaming_to_master_db()
