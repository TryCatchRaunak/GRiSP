import os
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from crewai.tools import BaseTool
from dotenv import load_dotenv
from typing import Optional # Import Optional, as ClassVar is not needed for instance attributes

# Load environment variables at the top-most level as soon as possible
load_dotenv()

# --- NLTK VADER Lexicon Download Logic ---
# Ensure VADER lexicon is downloaded
try:
    # First, try to download (it will skip if already downloaded)
    nltk.download('vader_lexicon', quiet=True) 
    # Then, verify it's found (this is what was failing before)
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError: # Use LookupError directly for missing data
    print("VADER Lexicon not found after download attempt. Please run 'python -m nltk.downloader vader_lexicon' manually if issues persist.")
    # It's usually good practice to exit or raise a hard error if a critical dependency isn;t met
    # For now, we'll let it continue, but the tool might fail if `analyzer` cannot be initialized
# --- End NLTK VADER Lexicon Download Logic ---


class TwitterSentimentTool(BaseTool):
    # These are Pydantic fields. They should be instance attributes for CrewAI tools.
    # 'name' and 'description' are standard for BaseTool.
    name: str = "TwitterSentimentTool"
    description: str = (
        "Fetches recent tweets based on a query and performs sentiment analysis. "
        "Returns a detailed sentiment breakdown (Positive, Neutral, Negative counts and percentages)."
    )

    # Declare instance attributes as Pydantic fields.
    # They are initialized to Optional[type] = None because they are set within __init__.
    analyzer: Optional[SentimentIntensityAnalyzer] = None
    bearer_token: Optional[str] = None
    
    # base_url can remain a class attribute if it's constant for all instances
    base_url: str = "https://api.twitter.com/2/tweets/search/recent"

    def __init__(self, **kwargs):
        # Always call the parent's __init__ method for BaseTool.
        # This handles Pydantic field initialization based on any kwargs passed to the constructor.
        super().__init__(**kwargs) 
        
        # Initialize instance-specific attributes here
        self.analyzer = SentimentIntensityAnalyzer()
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        # Add robust checks for critical dependencies
        if self.analyzer is None:
            raise RuntimeError("NLTK SentimentIntensityAnalyzer could not be initialized. VADER lexicon might be missing.")
        if not self.bearer_token:
            # Raise an error to prevent tool from being used without token
            raise ValueError("TWITTER_BEARER_TOKEN environment variable not set. Twitter API calls will fail.")

    def _fetch_tweets(self, query: str, max_results: int = 10) -> list:
        # Ensure token is present before making API call
        if not self.bearer_token:
            return ["Error: Twitter Bearer Token is missing. Please set the 'TWITTER_BEARER_TOKEN' environment variable."]

        headers = {
            "Authorization": f"Bearer {self.bearer_token}"
        }

        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "text,lang", # Request text and language
        }

        try:
            response = requests.get(self.base_url, headers=headers, params=params)
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
            # Ensure 'text' and 'lang' keys exist before accessing
            return [tweet["text"] for tweet in data["data"] if tweet.get("lang") == "en" and tweet.get("text")]

        except requests.exceptions.RequestException as e:
            return [f"Network or API error while fetching tweets for query '{query}': {str(e)}"]
        except Exception as e:
            return [f"An unexpected error occurred while fetching tweets for query '{query}': {str(e)}"]

    def _run(self, query: str) -> str:
        # Check if analyzer is initialized before using it
        if self.analyzer is None:
            return "Error: Sentiment analyzer is not initialized. Cannot perform sentiment analysis."
            
        tweets = self._fetch_tweets(query)
        
        # Check if the result from _fetch_tweets is an error message (list containing one error string)
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