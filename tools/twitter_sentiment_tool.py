import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

class TwitterSentimentTool:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_tweets(self, tweets: list):
        scores = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
        for tweet in tweets:
            sentiment = self.analyzer.polarity_scores(tweet)
            compound = sentiment["compound"]
            if compound >= 0.05:
                scores["POSITIVE"] += 1
            elif compound <= -0.05:
                scores["NEGATIVE"] += 1
            else:
                scores["NEUTRAL"] += 1
        return scores
