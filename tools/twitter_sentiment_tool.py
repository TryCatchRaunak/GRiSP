import os
import requests
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from crewai.tools import BaseTool
from dotenv import load_dotenv
from typing import ClassVar

# Ensure VADER lexicon is downloaded
# We will explicitly call download and then check with data.find
try:
    # First, try to download (it will skip if already downloaded)
    nltk.download('vader_lexicon', quiet=True) 
    # Then, verify it's found (this is what was failing before)
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError: # Use LookupError directly
    print("VADER Lexicon not found after download attempt. Please run 'python -m nltk.downloader vader_lexicon' manually if issues persist.")
    # You might want to raise an error or exit here if the lexicon is absolutely critical
    # raise


# Load environment variables
load_dotenv()


class TwitterSentimentTool(BaseTool):
    # Add type annotations to 'name' and 'description'
    name: ClassVar[str] = "TwitterSentimentTool"
    description: ClassVar[str] = "Fetches recent tweets based on a query and performs sentiment analysis."

    def __init__(self):
        super().__init__()
        self.analyzer = SentimentIntensityAnalyzer()
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        # Optional: Add a check for the bearer token
        if not self.bearer_token:
            print("Warning: TWITTER_BEARER_TOKEN environment variable not set. Twitter API calls will fail.")

    def _fetch_tweets(self, query: str, max_results: int = 10) -> list:
        if not self.bearer_token:
            return ["Error: Twitter Bearer Token is missing. Please set the 'TWITTER_BEARER_TOKEN' environment variable."]

        headers = {
            "Authorization": f"Bearer {self.bearer_token}"
        }

        search_url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "text,lang",
        }

        try:
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            # Check for API errors reported by Twitter
            if 'errors' in data:
                error_messages = "; ".join([e.get('detail', e.get('message', 'Unknown Error')) for e in data['errors']])
                return [f"Twitter API error: {error_messages}"]
            
            # Check if 'data' key exists and is not empty
            if not data.get("data"):
                return [f"No recent tweets found for query: '{query}'."]

            # Filter for English tweets and return text
            return [tweet["text"] for tweet in data["data"] if tweet.get("lang") == "en"]

        except requests.exceptions.RequestException as e:
            return [f"Network or API error while fetching tweets for query '{query}': {str(e)}"]
        except Exception as e:
            return [f"An unexpected error occurred while fetching tweets for query '{query}': {str(e)}"]

    def _run(self, query: str) -> str:
        tweets = self._fetch_tweets(query)
        
        # Check if the result from _fetch_tweets is an error message
        if not tweets or (isinstance(tweets, list) and tweets and "Error:" in tweets[0]):
            return tweets[0] # Return the error message

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
        if total == 0:
            return f"Could not perform sentiment analysis for '{query}' as no relevant tweets were found or processed."
            
        result = "\n".join([
            f"Sentiment Analysis of {total} recent tweets about '{query}':",
            f"👍 Positive: {scores['POSITIVE']} ({scores['POSITIVE']/total:.1%})",
            f"😐 Neutral:  {scores['NEUTRAL']} ({scores['NEUTRAL']/total:.1%})",
            f"👎 Negative: {scores['NEGATIVE']} ({scores['NEGATIVE']/total:.1%})"
        ])
        return result