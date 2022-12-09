import re
from typing import List

import pandas as pd
from nltk.stem.snowball import SnowballStemmer
import spacy

"""pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
https://stackoverflow.com/questions/49964028/spacy-oserror-cant-find-model-en"""
nlp = spacy.load("en_core_web_sm")


def extract_tweets(df: pd.DataFrame) -> List:
    """
    Function that takes a dataframe and extract to a list
    every value that is in .tweets column
    """
    list_of_sentences = [sentence for sentence in df.tweets]
    words = []
    for sentence in list_of_sentences:
        sentence_words = sentence.split()
        for w in sentence_words:
            words.append(w)
    return words


def clean_non_letter(words: List) -> List:
    words = [re.sub(r"[^A-Za-z0-9]+", "", x) for x in words]

    lines2 = []
    for word in words:
        if word != "":
            lines2.append(word)

    return lines2


def clean_non_training_words(words: List) -> List:
    s_stemmer = SnowballStemmer(language="english")
    lines2 = clean_non_letter(words)
    stem_1 = []
    for word in lines2:
        # since -> sinc, crazy -> crazi
        stem_1.append(s_stemmer.stem(word))

    stem_2 = []
    for word in stem_1:
        # don't want "is", "in", "for"
        if word not in nlp.Defaults.stop_words:
            stem_2.append(word)
    return stem_2
