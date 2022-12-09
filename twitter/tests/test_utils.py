from twitter.utils import extract_tweets, clean_non_training_words, clean_non_letter


def test_extract_tweets(sample_data) -> None:
    words = extract_tweets(sample_data)
    assert len(words) > 10


def test_clean_non_letter() -> None:
    words = ["1", "@", "%", "/", "*", "abc", "DEF", "abc@1#"]
    desired_output = ["1", "abc", "DEF", "abc1"]
    assert clean_non_letter(words) == desired_output


def test_clean_non_training_words() -> None:
    words = ["Since", "is", "up", "In", "Crazy", "just", "9000%", "http://abcd"]
    desired_output = ["sinc", "crazi", "9000", "httpabcd"]
    assert clean_non_training_words(words) == desired_output
