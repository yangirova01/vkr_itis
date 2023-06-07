import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt
import numpy as np
import re
import string
from nltk.stem import PorterStemmer
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.pipeline import Pipeline
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
from sklearn.base import BaseEstimator, TransformerMixin

from pprint import pprint

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

stop_words_ru = nltk.corpus.stopwords.words("russian")



from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

def lower(text):
    return text.lower()

def tokenization(text):
    text = re.split('\W+', text)
    return text
def remove_punctuation(text):
    return [word for word in text if word not in string.punctuation]

def remove_stopwords(text,lang='ru'):
    stop_words_ru = nltk.corpus.stopwords.words("russian")
    text = [word for word in text if word not in stop_words_ru]
    return text

def stemming(text):
    ps = PorterStemmer()
    text = [ps.stem(word) for word in text]
    return text

def lemmatization(text):
    lem = nltk.stem.WordNetLemmatizer()
    text = [lem.lemmatize(word) for word in text]
    return text

def remove_numbers(text):
    text = [word for word in text if not word.isnumeric()]
    return text

def remove_short_words(text, min_len=3):
    text = [word for word in text if len(word) > min_len]
    return text

def remove_long_words(text, max_len=15):
    text = [word for word in text if len(word) < max_len]
    return text

def remove_empty(text):
    text = [word for word in text if word != '']
    return text

def remove_space(text):
    text = [word.strip() for word in text]
    return text

class PreprocessTransormer(BaseEstimator, TransformerMixin):
    def __init__(self, lower=True, tokenization=True, remove_punctuation=True, remove_stopwords=True, stemming=True, lemmatization=True, remove_numbers=True,
                 remove_short_words=True, remove_long_words=True, remove_empty=True, remove_space=True):
        self.lower = lower
        self.tokenization = tokenization
        self.remove_punctuation = remove_punctuation
        self.remove_stopwords = remove_stopwords
        self.stemming = stemming
        self.lemmatization = lemmatization
        self.remove_numbers = remove_numbers
        self.remove_short_words = remove_short_words
        self.remove_long_words = remove_long_words
        self.remove_empty = remove_empty
        self.remove_space = remove_space
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if self.lower:
            X = X.apply(lambda x: lower(x))
        if self.tokenization:
            X = X.apply(lambda x: tokenization(x))
        if self.remove_punctuation:
            X = X.apply(lambda x: remove_punctuation(x))
        if self.remove_stopwords:
            X = X.apply(lambda x: remove_stopwords(x))
        if self.stemming:
            X = X.apply(lambda x: stemming(x))
        if self.lemmatization:
            X = X.apply(lambda x: lemmatization(x))
        if self.remove_numbers:
            X = X.apply(lambda x: remove_numbers(x))
        if self.remove_short_words:
            X = X.apply(lambda x: remove_short_words(x))
        if self.remove_long_words:
            X = X.apply(lambda x: remove_long_words(x))
        if self.remove_empty:
            X = X.apply(lambda x: remove_empty(x))
        if self.remove_space:
            X = X.apply(lambda x: remove_space(x))

        return X





