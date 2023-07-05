import streamlit as st

from av_crypto_trading.graphics import histograms
from av_crypto_trading.twitter import tweety, utils

st.title("Twitter analysis")

st.write("This page is overview of most recent Tweets.")

st.write("Select lookback period:")
lookback = st.selectbox(
    "Pick the lookback in minutes",
    [1, 15, 30, 60, 120, 360, 1200],
)

df = tweety.get_tweets(about="Crypto", number=100)

# df = pd.read_csv("tests/test_data_dirty_tweets.csv")

df = tweety.remove_RT_tweets(df)
tweets = utils.extract_tweets(df)
words = utils.clean_non_training_words(tweets)
hist_top_used_words = histograms.top_used_words(words)
hist_top_entities = histograms.hist_top_entities(words, "ORG")
st.pyplot(hist_top_used_words)
st.pyplot(hist_top_entities)

tweets = tweety.get_top_like_tweets(df)
st.dataframe(data=tweets)
