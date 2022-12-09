from graphics.utils import plot_frame, plot_df_price


def test_plot_frame_with_high_low(example_named_data):
    plot_frame(example_named_data)


def test_plot_df_price(example_named_data):
    example_named_data.rename(columns={"close": "Price"}, inplace=True)
    plot_df_price(example_named_data)
