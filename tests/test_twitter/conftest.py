import pandas as pd
import pytest

from av_crypto_trading.twitter.tweety import init_tweety_api, remove_RT_tweets


@pytest.fixture(name="api")
def twitter_api():
    return init_tweety_api()


@pytest.fixture(name="sample_tweets")
def get_sample_tweets():
    # df = get_tweets(about="Bitcoin", number=100)
    df = pd.DataFrame(
        {
            "tweets": ["tweet1", "tweet2", "tweet3","tweet1", "tweet2", "tweet3"],
            "likes": [1, 2, 3,4,5,1],
            "time": ["today", "yesterday", "today","today", "yesterday", "yesterday"],
        }
    )
    df = remove_RT_tweets(df)

    return df
