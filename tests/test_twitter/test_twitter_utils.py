from av_crypto_trading.twitter import utils


def test_extract_tweets(sample_tweets) -> None:
    extracted_tweets = utils.extract_tweets(sample_tweets)

    assert len(extracted_tweets) == len(sample_tweets.tweets)
    assert extracted_tweets == list(sample_tweets.tweets)
    assert isinstance(extracted_tweets, list)


def test_clean_non_letter() -> None:
    words = ["1", "@", "%", "/", "*", "abc", "DEF", "abc@1#"]
    desired_output = ["1", "abc", "DEF", "abc1"]
    assert utils.clean_non_letter(words) == desired_output


def test_clean_non_training_words() -> None:
    words = ["Since", "is", "up", "In", "Crazy", "just", "9000%", "http://abcd"]
    desired_output = ["sinc", "crazi", "9000", "httpabcd"]
    assert utils.clean_non_training_words(words) == desired_output
