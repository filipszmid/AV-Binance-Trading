from typing import List

import pandas as pd
import seaborn as sns
import spacy
from matplotlib import pyplot as plt

from av_crypto_trading.twitter.utils import clean_non_letter

"""pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm
https://stackoverflow.com/questions/49964028/spacy-oserror-cant-find-model-en"""
#: TODO poetry doesn't load this module uncomment
nlp = spacy.load("en_core_web_sm")
FONT_SIZE = 20


def top_used_words(words: List, number: int = 20) -> None:
    """
    Function draw a histogram with top used words

    :param words List of words.
    """

    df2 = pd.DataFrame(words)
    df2 = df2[0].value_counts()
    df2 = df2[
        :number,
    ]

    fig = plt.figure(figsize=(20, 7))
    plot = sns.barplot(y=df2.values, x=df2.index, alpha=1)
    plt.xticks(fontsize=FONT_SIZE, rotation=70)
    # plt.tight_layout()
    plt.title("Top Words Overall", fontsize=FONT_SIZE)
    plt.ylabel("Word from Tweet", fontsize=FONT_SIZE)
    plt.xlabel("Count of Words", fontsize=FONT_SIZE)
    # plt.show()
    return fig


def hist_top_entities(words: List, entity: str = "ORG"):
    """
    Histogram of top used organisations
        -ORG: organisations
        -PERSON: persons
    Print "label" for more

    Can be helpfull? Not sure
    # def show_ents(doc):
    #     if doc.ents:
    #         for ent in doc.ents:
    #             print(
    #                 ent.text + " - " + ent.label_ + " - " + str(spacy.explain(ent.label_))
    #
    """
    words = clean_non_letter(words)
    empty_string = " "
    stem = empty_string.join(words)

    stem = nlp(stem)
    label = [(X.text, X.label_) for X in stem.ents]
    df6 = pd.DataFrame(label, columns=["Word", "Entity"])
    df7 = df6.where(df6["Entity"] == entity)
    df7 = df7["Word"].value_counts()

    dfx = df7[
        :20,
    ]
    fig = plt.figure(figsize=(20, 7))
    sns.barplot(y=dfx.values, x=dfx.index, alpha=1)
    plt.xticks(fontsize=FONT_SIZE, rotation=70)
    # plt.tight_layout()
    plt.title("Top " + entity + " Mentioned", fontsize=FONT_SIZE)
    plt.ylabel("Word from Tweet", fontsize=FONT_SIZE)
    plt.xlabel("Count of Words", fontsize=FONT_SIZE)
    # plt.show()
    return fig
