from typing import List
from unittest import mock

import matplotlib
import pandas as pd
import pytest

from av_crypto_trading.graphics import histograms
from av_crypto_trading.twitter import tweety, utils


@pytest.fixture(name="tweets")
def dirt_tweets() -> List:
    """
    Dirty tweets from tweety api fixtures
    real tweets can be obtained by invoking:
        df = tweety.get_tweets(about="Bitcoin", number=500)
    """
    df = pd.read_csv("../../tests/test_data_dirty_tweets.csv")
    df = tweety.remove_RT_tweets(df)
    words = utils.extract_tweets(df)
    return words


@pytest.fixture(name="words")
def clear_word_list(tweets) -> List:
    words = utils.clean_non_training_words(tweets)
    return words


@mock.patch.object(matplotlib.pyplot, "show")
def test_hist_top_used_words(_, words):
    histograms.top_used_words(words)


@pytest.mark.parametrize("entity", ["ORG", "PERSON"])
@mock.patch.object(matplotlib.pyplot, "show")
def test_hist_top_entities(_, entity, tweets):
    histograms.hist_top_entities(tweets, entity)
