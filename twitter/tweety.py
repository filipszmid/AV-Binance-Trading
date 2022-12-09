import os

import pandas as pd
import tweepy
from dotenv import load_dotenv


def init_tweety_api():
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


def get_tweets(about: str, number: int) -> pd.DataFrame:
    api = init_tweety_api()
    tweets, likes, time = [], [], []

    for i in tweepy.Cursor(api.user_timeline, id=about, tweet_mode="extended").items(
        number
    ):
        tweets.append(i.full_text)
        likes.append(i.favorite_count)
        time.append(i.created_at)

    df = pd.DataFrame({"tweets": tweets, "likes": likes, "time": time})
    return df


def remove_RT_tweets(df: pd.DataFrame) -> pd.DataFrame:
    df = df[~df.tweets.str.contains("RT")]
    df.reset_index(drop=True)
    return df


def get_top_like_tweets(df: pd.DataFrame, number: int = 5) -> pd.DataFrame:
    return df.loc[df.likes.nlargest(number).index]
