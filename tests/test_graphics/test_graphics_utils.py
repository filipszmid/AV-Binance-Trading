from unittest import mock

import matplotlib

from av_crypto_trading.graphics import utils


@mock.patch.object(matplotlib.pyplot, "show")
def test_plot_frame_with_high_low(_, example_named_data):
    utils.plot_df_high_low(example_named_data)


@mock.patch.object(matplotlib.pyplot, "show")
def test_plot_df_price(_, example_named_data):
    utils.plot_df_price(example_named_data)
