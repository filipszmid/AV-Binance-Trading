import tweepy

from core.utils import set_pandas_to_print_all_values
from twitter.tweety import (
    init_tweety_api,
    get_tweets,
    remove_RT_tweets,
    get_top_like_tweets,
)


def test_init_tweety_api() -> None:
    api = init_tweety_api()
    assert api


def test_read_tweet_by_id(api) -> None:
    cursor = tweepy.Cursor(api.user_timeline, id="BTC", tweet_mode="extended").items(1)
    print(cursor)
    for i in cursor:
        print(i.full_text)
        print(dir(i))
    assert cursor


def test_get_tweets() -> None:
    df = get_tweets(about="Bitcoin", number=100)
    assert len(df) == 100
    assert len(df.columns) == 3


def test_get_top_like_tweets() -> None:
    set_pandas_to_print_all_values()
    df = get_tweets(about="Bitcoin", number=50)
    df = remove_RT_tweets(df)
    most_like = get_top_like_tweets(df)
    print(most_like.columns)
    # chce sprawdzic czy 1 rekord bedzie mial wiecej lajkow niz 2
    # print(most_like["likes"].loc[1])
    # print(most_like.likes[1])
    assert len(most_like) == 5
    # assert most_like.likes[0] > most_like.likes[1]
