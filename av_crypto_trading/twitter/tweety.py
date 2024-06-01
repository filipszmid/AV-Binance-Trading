import os

import pandas as pd
import tweepy
from dotenv import load_dotenv


def init_tweety_api():
    """
    regenerate secrets:
    https://developer.twitter.com/en/apps
    Twitter blocks reading tweets with a free tier.
    Only posting tweets up to 1500.
    """
    load_dotenv()
    consumer_key = os.environ["consumer_key"]
    consumer_secret = os.environ["consumer_secret"]
    bearer_token = os.environ["bearer_token"]
    access_token = os.environ["access_token"]
    access_token_secret = os.environ["access_token_secret"]
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


api = init_tweety_api()


def get_tweets(about: str, number: int) -> pd.DataFrame:
    """Get last tweets with likes and timestamp."""
    tweets, likes, time = [], [], []
    cursor = tweepy.Cursor(api.user_timeline, id=about, tweet_mode="extended")

    for tweet in cursor.items(number):
        tweets.append(tweet.full_text)
        likes.append(tweet.favorite_count)
        time.append(tweet.created_at)
        # print(dir(tweet))

    df = pd.DataFrame({"tweets": tweets, "likes": likes, "time": time})
    return df


def remove_RT_tweets(df: pd.DataFrame) -> pd.DataFrame:
    """Remove reposted tweets."""
    df = df[~df.tweets.str.contains("RT")]
    df.reset_index(drop=True)
    return df


def get_top_like_tweets(df: pd.DataFrame, number: int = 5) -> pd.DataFrame:
    return df.loc[df.likes.nlargest(number).index]
