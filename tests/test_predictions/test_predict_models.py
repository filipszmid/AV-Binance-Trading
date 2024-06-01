from av_crypto_trading.predictions.models import predict_fb


def test_predict_from_binance(example_data_binance):
    predict_fb(df=example_data_binance, forward_period=50)


def test_predict_from_yahoo(example_data_yahoo_btc):
    # predict_fb(df=example_data_yahoo, forward_period=50)
    # predict_fb(df=example_data_yahoo, forward_period=365)
    predict_fb(df=example_data_yahoo_btc, forward_period=365)
