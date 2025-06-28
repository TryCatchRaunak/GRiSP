import os
import requests
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from crewai_tools import BaseTool

# Ensure VADER lexicon is downloaded
nltk.download('vader_lexicon')


class TwitterSentimentTool(BaseTool):
    name = "TwitterSentimentTool"
    description = "Fetches recent tweets based on a query and performs sentiment analysis."

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

    def _fetch_tweets(self, query: str, max_results: int = 10) -> list:
        if not self.bearer_token:
            return ["Error: Twitter Bearer Token is missing."]

        headers = {
            "Authorization": f"Bearer {self.bearer_token}"
        }

        search_url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "text,lang",
        }

        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code != 200:
            return [f"Error: Unable to fetch tweets. Status code: {response.status_code}"]

        data = response.json()
        return [tweet["text"] for tweet in data.get("data", []) if tweet.get("lang") == "en"]

    def _run(self, query: str) -> str:
        tweets = self._fetch_tweets(query)
        if not tweets or "Error:" in tweets[0]:
            return tweets[0]  # Return the error message

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

        total = sum(scores.values())
        result = "\n".join([
            f"Sentiment Analysis of {total} recent tweets about '{query}':",
            f"👍 Positive: {scores['POSITIVE']}",
            f"😐 Neutral:  {scores['NEUTRAL']}",
            f"👎 Negative: {scores['NEGATIVE']}"
        ])
        return result