from typing import List

import pytest

from graphics.histograms import top_used_words, hist_top_entities
from twitter.tweety import remove_RT_tweets, get_tweets
from twitter.utils import clean_non_training_words, extract_tweets


@pytest.fixture(name="tweets")
def dirt_tweets() -> List:
    df = get_tweets(about="Bitcoin", number=500)
    df = remove_RT_tweets(df)
    words = extract_tweets(df)
    return words


@pytest.fixture(name="words")
def clear_word_list(tweets) -> List:
    words = clean_non_training_words(tweets)
    return words


def test_hist_top_used_words(words):
    top_used_words(words)


@pytest.mark.parametrize("entity", ["ORG", "PERSON"])
def test_hist_top_entities(entity, tweets):
    hist_top_entities(tweets, entity)
