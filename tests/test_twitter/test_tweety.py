from unittest import mock
from unittest.mock import Mock

import tweepy

from av_crypto_trading.core import utils
from av_crypto_trading.twitter import tweety


def test_init_tweety_api() -> None:
    api = tweety.init_tweety_api()
    assert api


@mock.patch.object(tweepy, "Cursor")
def test_get_tweets(mock_cursor) -> None:
    tweet_text, num_likes, date = "text", 100, "today"
    mock_cursor.return_value = Mock(
        items=Mock(
            return_value=[
                Mock(full_text=tweet_text, favorite_count=num_likes, created_at=date)
            ]
        )
    )
    df = tweety.get_tweets(about="Bitcoin", number=1)
    assert len(df) == 1
    assert len(df.columns) == 3
    assert df.tweets[0] == tweet_text
    assert df.likes[0] == num_likes
    assert df.time[0] == date


def test_get_top_like_tweets(sample_tweets) -> None:
    df = tweety.remove_RT_tweets(sample_tweets)
    tweets = tweety.get_top_like_tweets(df)
    assert len(tweets) == 5
    assert tweets.likes.iloc[0] > tweets.likes.iloc[1]
