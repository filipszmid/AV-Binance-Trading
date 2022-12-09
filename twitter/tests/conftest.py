import pytest

from twitter.tweety import init_tweety_api, get_tweets, remove_RT_tweets


@pytest.fixture(name="api")
def twitter_api():
    return init_tweety_api()


@pytest.fixture(name="sample_data")
def sample_data():
    df = get_tweets(about="Bitcoin", number=100)
    df = remove_RT_tweets(df)
    return df
